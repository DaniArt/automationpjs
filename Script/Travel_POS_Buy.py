﻿from SoapRequests import *
from TaskMethods import *
from CardFramework import *   
  
  
def TravelPOSBuy_AllDataSet():
    """ Отправка запроса по покупке через POS2416 """
    NCRD = CardFramework()
    data_list = NCRD.ReadDatasetFromDB('travel_data')
    for row in data_list:
        try:
            if row['IDN_CARD']:
                name_file = f'{NCRD.GetRandomNumber()}_TravelPOSBuy.json'   
                TravelPOSBuy(row['IDN_CRD'], row['CLI_ACC'], row['AMOUNT'], 
                              row['VAL'], row['CARD_NUM'], row['PSYS'], row['TERM_TYPE'], 
                              row['MCC'], row['TYPE_TRN'], name_file)
            elif row['IDN_CARD'] is None:
                name_file = f'{NCRD.GetRandomNumber()}_TravelPOSBuy.json'
                NCRD.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Отправка запроса по покупке через POS2416 Travel карта клиента {row['CLI_ID']}", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
  
def TravelPOSBuy(idn_crd, acc_crd, amount, val, card_num, psys, term_type, mcc, type_trn, name_file):
    soap = SoapRequests()
    task = TaskMethods()
    card = CardFramework()
    count = 1
    operation_type = 'outc'
    try:
        # создание отчета allure
        soap.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Продукт - Travel карта", f"Отправка запроса по покупке через POS2416 по счету {acc_crd}", name_file)
        #---------    
        soap.StartCapJob()
        # Присваеваем теущий баланс к переменной
        before_bln = soap.CheckAccBalance(acc_crd)
        Delay(2000) # Нужна небольшая задержка Перед отправкой запроса       
        Sql.StartCapJob()
        # Отправляем запрос на покупку по POS2416
        response = soap.POS2416(idn_crd, amount, val, card_num, psys, term_type, mcc)
        tran_id = response # достаем идентификатор транзакции
        #------- Проверка статусов в EXTTRN и APTTRN
        soap.AptCheckStatus(tran_id, count, name_file)
        soap.ExtCheckStatus(tran_id, acc_crd, count, name_file)
        count += 1
        # Ниже условие для проверки типа покупки, в зависимости от неё запускается определенная процедура
        if tran_id is not None:
            pre_activate_file = f""" begin Z_PKG_AUTO_TEST.p_activate_c_file_2416_ON_US(c_id_code => {tran_id}); commit; end;""" # Активация записи в С файл
            soap.OracleHandlerDB(pre_activate_file, dml_query='True')
        else:
            pre_activate_file = f""" begin Z_PKG_AUTO_TEST.p_activate_c_file_2416LOCAL(c_id_code => {tran_id}); commit; end;""" # Активация записи в С файл
            soap.OracleHandlerDB(pre_activate_file, dml_query='True')
        # Проверка наличия бонуса
        bon_take = f"select bonus_amount from bcm_user.bcm_bonus@cap where trn_id = {tran_id}" 
        bon_amount = Sql.SimpleQuery(bon_take)
        
        balance_need = card.CheckCorrectTransaction(None, None, 0, before_bln, amount, acc_crd, operation_type, count, name_file, tran_id)
        Delay(2000) # Ожидание между запусками процедур
        # Ниже достаем айдишник С - файла, для дальнейщей активации
        card.GetProcFile(tran_id)
        #---------
    except Exception as error:
        # завершение формирование отчета
        task.AllureReportEnd(count, name_file, "failed", error)
    
