from SoapRequests import *
from TaskMethods import *
from CardFramework import *   
from SQL import Sql
                                                                                                            
                                                                                                            
def POSCashOut2411_AllDataSet():
    """ Снятие со счета карты через операцию 2411 """
    card = CardFramework()
    data_list = card.ReadDatasetFromDB('CardTrnCheck')  
    for row in data_list:
        if row['TRN_TYPE'] == '2411':
            name_file = f'{card.GetRandomNumber()}_POS2411.json' 
            POSCashOut2411(row['CLI_ACC'], row['IDN_CRD'], row['AMOUNT'],
                           row['CARD_NUM'], row['PSYS'], row['TERM_TYPE'],
                           row['MCC'], row['TYPE_TRN'], row['CMS_PROCENT'], name_file)
                                                                                                            
                                                                                                            
                                                                                                            
def POSCashOut2411(acc_crd, idn_crd, amount, card_num, psys, term_id, mcc, type_trn, cms_proc, name_file):
    soap = SoapRequests()
    task = TaskMethods()
    card = CardFramework()
    count = 1
    operation_type = 'outc'
    try:
        # создание отчета allure
        soap.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Продукт - КартаКарта", "Снятие со счета карты через операцию 2411", name_file)
        #---------    
        soap.StartCapJob()
        # Присваеваем теущий баланс к переменной
        before_bln = soap.CheckAccBalance(acc_crd)
        Delay(2000) # Нужна небольшая задержка Перед отправкой запроса       
        Sql.StartCapJob()
        # Отправляем запрос на через с POS
        response = soap.POS2411(idn_crd, amount, 'KZT', card_num, psys, term_id, mcc)
        tran_id = response # достаем идентификатор транзакции
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