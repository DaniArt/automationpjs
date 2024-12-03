from CardFramework import *
from SQL import Sql
from SoapRequests import *


def WelcomeBonusCheck_AllDataSet():
    """ Отправка на акцептование карты клиента по всему датасету """
    NCRD = CardFramework()
    data_list = NCRD.ReadDatasetFromDB('CardTrnCheck')
    for row in data_list:
        if row['TRN_TYPE'] == '2416':
            name_file = f'{NCRD.GetRandomNumber()}_WelcomeBonusCheck.json'   
            WelcomeBonusCheck(row['IDN_CARD'], row['ACC_CRD'], row['SUM_TRN'], row['BON_CODE'], name_file)
  
def WelcomeBonusCheck(idn_crd, acc_crd, amount, bon_acc, name_file):
    soap = SoapRequests()
    # Создание главной иерархии json отчета
    new_path = soap.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    soap.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Выполнение операции покупки через POS2516", "Покупка через POS2416", soap.GetDateTimeMilli()]
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
    # Присваеваем теущий баланс к переменной
    before = soap.CheckAccBalance(acc_crd)
    # Отправляем запрос на снятие с нашего АТМ
    response = soap.POS2416(idn_crd, amount, 'KZT', 'LOCAL', '40330063')
    Delay(2000) # Нужна небольшая задержка после отправки запроса
    run_trn = f"""begin delete from apt_acc_intwait@cap where acc_id in (select acc_id from apt_trn@cap where status = '1'); commit; end;"""
    soap.OracleHandlerDB(run_trn, dml_query='True')    
    Delay(2000) # Нужна небольшая задержка после отправки запроса
    tran_id = response # достаем идентификатор транзакции
    #------- Проверка статусов в EXTTRN и APTTRN
    soap.AptCheckStatus(tran_id, count, name_file)
    soap.ExtCheckStatus(tran_id, acc_crd, count, name_file)
    # Проверка остатка
    select = f"""select n.balance from apt_trn@cap n where n.acc_id = '{check_acc}' ORDER BY n.EXTIME desc"""
    balance_now = Sql.SimpleQuery(select)
    balance_need = before - amount
    if balance_need == balance_now:
  #   Отчетность 2
      soap.AllureReportTemplate(abs_path, name_file, "Проверяем остаток баланса", "passed", {"message": f"Успешно отработано {type_trn} | текущий баланс клиента = {balance_now}"},
                                   None, None, new_path, "passed", 1, 3)
  #   --------------------------------------------------------------------------------------------------------------------------
      soap.AllureReportTemplate(abs_path, name_file, "Проверяем расчет остатка", "passed", {"message": f"{before}(баланс до) - {amount}(сумма покупки = {balance_now}(текущий баланс)"},
                                   None, None, new_path, "passed", 1, 4, rm = True)
  #   --------------------------------------------------------------------------------------------------------------------------
      Log.Event(f'Расчет остатка {before}(баланс до) - {amount}(сумма снятия) = {balance_need}(текущий баланс)')
      Log.Checkpoint(f'Успешно отработано снятие, текущий баланс клиента = {balance_now}')
      pre_activate_file = f""" begin Z_PKG_AUTO_TEST.p_activate_c_file_2416(c_id_code => {tran_id}); commit; end;""" # Активация записи в С файл
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
    else:
  #   Отчетность 2  
      soap.AllureReportTemplate(abs_path, name_file, "Проверяем остаток баланса", "passed", {"message": f"Ошибочно отработано {type_trn} | текущий баланс клиента = {balance_now}"},
                                   None, None, new_path, "passed", 1, 3)
  #   --------------------------------------------------------------------------------------------------------------------------
      soap.AllureReportTemplate(abs_path, name_file, "Проверяем расчет остатка", "passed", {"message": f"{before}(баланс до) - {amount}(сумма покупки = {balance_now}(текущий баланс)"},
                                   None, None, new_path, "passed", 1, 4, rm = True)
  #      # --------------------------------------------------------------------------------------------------------------------------      
      Log.Event(f'Расчет остатка {before}(баланс до) - {amount}(сумма снятия) = {balance_need}(текущий баланс)')
      Log.Warning(f'Ошибочно отработано снятие, текущий баланс клиента = {balance_now}')  
    
    # Проверка начисленного бонуса
    select = f"""select n.balance from apt_trn@cap n where n.acc_id = '{bon_acc}' ORDER BY n.EXTIME desc"""
    bon_amount = Sql.SimpleQuery(select)
    Log.Message(bon_amount)
    if bon_amount == 835 or bon_amount == 1101:
      Log.Checkpoint(f'Бонус расчитан коректно, начислено {bon_amount}')
    else:
      Log.Warning(f'Бонус расчитан не коректно, начислено {bon_amount}')