﻿from SoapRequests import *
from TaskMethods import *
from CardFramework import *   
from SQL import Sql
                                                                                                            
                                                                                                            
def ATMCashOut2402int_AllDataSet():
    """ Снятие со счета карты через операцию 2402 чужой АТМ """
    card = CardFramework()
    data_list = card.ReadDatasetFromDB('CardTrnCheck')  
    for row in data_list:
        if row['TRN_TYPE'] == '2402':
            name_file = f'{card.GetRandomNumber()}_ATM2402.json' 
            ATMCashOut2402int(row['VAL'], row['CLI_ACC'], row['IDN_CRD'], row['AMOUNT'], row['CARD_NUM'], row['CMS_PROCENT'], name_file)
                                                                                                            
                                                                                                            
                                                                                                            
def ATMCashOut2402int(val, acc_crd, card_idn, amount, card_code, cms_proc, name_file):
    soap = SoapRequests()
    task = TaskMethods()
    card = CardFramework()
    count = 1
    operation_type = 'outc'
    try:
        # создание отчета allure
        soap.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Продукт - КартаКарта", "Снятие через операцию 2402 чужой АТМ", name_file)
        #---------    
        soap.StartCapJob()
        # Присваеваем теущий баланс к переменной
        before_bln = soap.CheckAccBalance(acc_crd)
        Delay(2000) # Нужна небольшая задержка Перед отправкой запроса                                                  
        # Отправляем запрос на снятие с чужого АТМ
        response = soap.ATM_2402(card_idn, amount, val, 'INT')
        tran_id = response # достаем идентификатор транзакции
        Delay(2000) # Нужна небольшая задержка после отправки запроса
        soap.UpdateProcInterwal()    
        Delay(2000) # Нужна небольшая задержка после отправки запроса
        tran_id = response # достаем идентификатор транзакции)
        #------- Проверка статусов в EXTTRN и APTTRN
        soap.AptCheckStatus(tran_id, count, name_file)
        soap.ExtCheckStatus(tran_id, acc_crd, count, name_file)
        count += 1
        balance_need = card.CheckCorrectTransaction(cms_proc, None, before_bln, amount, acc_crd, operation_type, count, name_file, tran_id)
        # Ниже достаем айдишник С - файла, для дальнейщей активации
        card.GetProcFile(tran_id)
        #---------
    except Exception as error:
        # завершение формирование отчета
        task.AllureReportEnd(count, name_file, "failed", error)
    
