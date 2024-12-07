﻿from CardFramework import *
from SoapRequests import *
from SQL import Sql                    
                         
def BusinessCashout2401_AllDataSet():
   """ Снятие со счета карты через операцию 2401 """
   card = CardFramework()
   data_list = card.ReadDatasetFromDB('ndeacrd_data')  
   for row in data_list:
       try:
           if row['IDN_CARD']:
               name_file = f'{card.GetRandomNumber()}_BusinessCashout2401.json'
               BusinessCashout2401(row['IDN_CARD'], row['ACC_CRD'], row['SUM_TRN'], row['VAL_CODE'], name_file)
           elif row['IDN_CARD'] is None:
                name_file = f'{card.GetRandomNumber()}_BusinessCashout2401.json'
                card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Снятие со счета через операцию 2401 Business карта клиента {row['CLI_ID']}",
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
       except Exception as e:
           Log.Event('Возникла ошибка идем дальше')
                         
                         
                         
def BusinessCashout2401(card_idn, acc_crd, amount, val, name_file):
    soap = SoapRequests() 
    task = TaskMethods()
    card = CardFramework()
    count = 1
    operation_type = 'outc'
    try:
        # создание отчета allure
        soap.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Продукт - Business карта", f"Снятие со счета через операцию 2401 по счету {acc_crd}", name_file)
        #---------    
        soap.StartCapJob()
        # Присваеваем теущий баланс к переменной
        before_bln = soap.CheckAccBalance(acc_crd)
        Delay(2000) # Нужна небольшая задержка Перед отправкой запроса                                                  
        # Отправляем запрос на снятие с нашего АТМ
        response = soap.ATM2401(card_idn, amount, val)
        tran_id = response # достаем идентификатор транзакции
        Delay(2000) # Нужна небольшая задержка после отправки запроса
        soap.UpdateProcInterwal()    
        Delay(2000) # Нужна небольшая задержка после отправки запроса
        tran_id = response # достаем идентификатор транзакции)
        #------- Проверка статусов в EXTTRN и APTTRN
        soap.AptCheckStatus(tran_id, count, name_file)
        soap.ExtCheckStatus(tran_id, acc_crd, count, name_file)
        count += 1
        balance_need = card.CheckCorrectTransaction(None, None, 0, before_bln, amount, acc_crd, operation_type, count, name_file, tran_id)
        #---------
    except Exception as error:
        # завершение формирование отчета
        task.AllureReportEnd(count, name_file, "failed", error)
