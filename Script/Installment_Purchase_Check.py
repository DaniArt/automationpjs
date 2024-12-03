from CardFramework import *
from SQL import Sql
from SoapRequests import *
  
  
def InstallmentPurchaseCheck_AllDataSet():
    """ Проверка покупки в рассрочку по всему датасету """
    CardDataset = CardFramework()
    data_list = CardDataset.ReadDatasetFromDB('CardTrnCheck')
    for row in data_list:
        if row['TRN_TYPE'] == '2416':
            name_file = f'{CardDataset.GetRandomNumber()}_InstallmentCheck.json'   
            InstallmentPurchaseCheck(row['IDN_CRD'], row['CLI_ACC'], row['AMOUNT'], 
                                     row['VAL'], row['CARD_NUM'], row['PSYS'], row['TERM_TYPE'], 
                                     row['MCC'], row['TYPE_TRN'], name_file)
  
def InstallmentPurchaseCheck(idn_crd, acc_crd, amount, val, card_num, psys, term_type, mcc, type_trn, name_file):
    ''' Проверка покупки в рассрочку '''
    soap = SoapRequests()
    # Создание главной иерархии json отчета
    new_path = soap.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    soap.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = [f"Выполнение операции {type_trn}", "Покупка через POS2416", soap.GetDateTimeMilli()]
    abs_path = soap.FindAbsPathFile(name_file) # Получение абсолютного пути файла
    soap.AddKeyValueJson(abs_path, key, value)
    def_dict = soap.GetDefaultDict(abs_path)
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
    soap.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", "Продукт - КартаКарта"]
    soap.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    # Начало работы автотеста
    Sql.StartCapJob()
    # Проверка баланса
    select = f"""select c.acc_id from apt_idn@cap c where c.code = '{acc_crd}'""" # Достаем идентификатора аккаунта
    check_acc = Sql.SimpleQuery(select)
    select = f"""select n.balance from apt_trn@cap n where n.acc_id = '{check_acc}' ORDER BY n.EXTIME desc""" # Получение баланса до пополнения
    before = Sql.SimpleQuery(select)
 
    # Отправляем запрос на покупку по POS2416
    response = soap.POS2416(idn_crd, amount, val, card_num, psys, term_type, mcc)
    Delay(2000) # Нужна небольшая задержка после отправки запроса
    run_trn = f"""begin delete from apt_acc_intwait@cap where acc_id in (select acc_id from apt_trn@cap where status = '1'); commit; end;"""
    soap.OracleHandlerDB(run_trn, dml_query='True')    
    Delay(2000) # Нужна небольшая задержка после отправки запроса
    tran_id = response # достаем идентификатор транзакции
    Log.Message(f'Идентификатор транзакции {tran_id}')
  
    # Проверяем тразакцию в задаче APTTRN
    select = f"""select (select LONGNAME from APR_STATUSTRN@cap where CODE='CAP_STATUS' and CONSTVAL=to_char(trn.STATUS)
    and LNG_ID=AP_LNG.GetActive@cap) STATUSNAME from APT_TRN@CAP trn where trn.ID = '{tran_id}'"""
    apttrn_status = Sql.SimpleQuery(select)
    while apttrn_status in ('Fixed','Выгружена в АБС, зафиксирована'):  #  Задержка для ожидания обработки транзакции   
      apttrn_status = Sql.SimpleQuery(select)
      sql_result = soap.OracleHandlerDB(select)
      Log.Event(f'Текущий статус транзакции: **{apttrn_status}**')
      Delay(3000)
      if apttrn_status == 'Выгружена в АБС, обработана':
  #     Отчетность 1
        soap.AllureReportTemplate(abs_path, name_file, f"Выполнение операции {type_trn}", "passed", {"message": f"Выгружена в АБС, обработана"},
                                     None, None, new_path, "passed", 1, 1)
  #     --------------------------------------------------------------------------------------------------------------------------   
        break 
    soap.CheckExpectedResult('Проверяем статус транзакции в задаче APTTRN',apttrn_status,'Выгружена в АБС, обработана',tran_id)

    # Проверяем тразакцию в задаче EXTTRTN
    select = f"""select decode(t.STATUS,0,'не обработана',1,'обработана',2,'ошибка обработки') as STATUS_NAME, proc_id
    from G_CAPTmpExtTrn t where  OBJ_CODE = '{acc_crd}' and id = '{tran_id}'"""
    sql_result = soap.OracleHandlerDB(select)
    exttrn_status,proc_id = Sql.SimpleLineQuery(select,2)
  #   Отчетность 1 2
    soap.AllureReportTemplate(abs_path, name_file, f"Выполнение операции {type_trn}", "passed", {"message": f"Выгружена в EXTTRN обработана"},
                                 None, None, new_path, "passed", 1, 2)
  #   --------------------------------------------------------------------------------------------------------------------------  
    soap.CheckExpectedResult('Проверяем статус транзакции в задаче EXTTRN',exttrn_status,'обработана',tran_id)
    
    # Проверка остатка
    select = f"""select n.balance from apt_trn@cap n where n.acc_id = '{check_acc}' ORDER BY n.EXTIME desc"""
    balance_now = Sql.SimpleQuery(select)
    balance_need = before - amount
    # Ниже условие для проверки типа покупки, в зависимости от неё запускается определенная процедура
    if psys == 'ON-US':
        pre_activate_file = f""" begin Z_PKG_AUTO_TEST.p_activate_c_file_2416_ON_US(c_id_code => {tran_id}); commit; end;""" # Активация записи в С файл
        soap.OracleHandlerDB(pre_activate_file, dml_query='True')
    else:
        pre_activate_file = f""" begin Z_PKG_AUTO_TEST.p_activate_c_file_2416LOCAL(c_id_code => {tran_id}); commit; end;""" # Активация записи в С файл
        soap.OracleHandlerDB(pre_activate_file, dml_query='True')
    
    Delay(1000) # Ожидание между запусками процедур
    # Ниже достаем айдишник С - файла, для дальнейщей активации
    proc_file = f"""select i.id 
                  from N_CRDIN i, N_CRDINDTL d, N_CRDINTRN n
                  where i.id = D.FILE_ID
                     and d.id = n.id
                     and n.trn_num = {tran_id}"""
                     
    file_id = Sql.SimpleQuery(proc_file) # Присваем в переменную
                     
    activate_file = f'begin update (select * from n_crdin where id = {file_id})set state = 1; Commit; end; '    
    soap.OracleHandlerDB(activate_file, dml_query='True')
      
    bon_take = f"select bonus_amount from bcm_user.bcm_bonus@cap where trn_id = {tran_id}" 
    bon_amount = Sql.SimpleQuery(bon_take)
    
    if balance_need == balance_now:
  #   Отчетность 2
      soap.AllureReportTemplate(abs_path, name_file, "Проверяем остаток баланса", "passed", {"message": f"Успешно отработано {type_trn} | текущий баланс клиента = {balance_now}, Начисленно бонусов = {bon_amount}"},
                                   None, None, new_path, "passed", 1, 3)
  #   --------------------------------------------------------------------------------------------------------------------------
      soap.AllureReportTemplate(abs_path, name_file, "Проверяем расчет остатка", "passed", {"message": f"{before}(баланс до) - {amount}(сумма покупки = {balance_now}(текущий баланс)"},
                                   None, None, new_path, "passed", 1, 4, rm = True)
  #   --------------------------------------------------------------------------------------------------------------------------
      Log.Event(f'Расчет остатка {before}(баланс до) - {amount}(сумма снятия) = {balance_need}(текущий баланс)')
      Log.Checkpoint(f'Успешно отработано снятие, текущий баланс клиента = {balance_now}')        
      
    else:
  #   Отчетность 2  
      soap.AllureReportTemplate(abs_path, name_file, "Проверяем остаток баланса", "passed", {"message": f"Ошибочно отработано {type_trn} | текущий баланс клиента = {balance_now}, Начисленно бонусов = {bon_amount}"},
                                   None, None, new_path, "passed", 1, 3)
  #   --------------------------------------------------------------------------------------------------------------------------
      soap.AllureReportTemplate(abs_path, name_file, "Проверяем расчет остатка", "passed", {"message": f"{before}(баланс до) - {amount}(сумма покупки = {balance_now}(текущий баланс)"},
                                   None, None, new_path, "passed", 1, 4, rm = True)
  #      # --------------------------------------------------------------------------------------------------------------------------     
      Log.Event(f'Расчет остатка {before}(баланс до) - {amount}(сумма снятия) = {balance_need}(текущий баланс)')
      Log.Warning(f'Ошибочно отработано снятие, текущий баланс клиента = {balance_now}')

