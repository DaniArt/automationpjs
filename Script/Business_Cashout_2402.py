from CardFramework import *
from SoapRequests import *
from SQL import Sql
                                                                                                            
                                                                                                            
def BusinessCashout2402_AllDataSet():
    """ Снятие со счета карты через операцию 2402 чужой АТМ """
    card = CardFramework()
    data_list = card.ReadDatasetFromDB('ndeacrd_data')  
    for row in data_list:
        try:
            if row['IDN_CARD']:
                name_file = f'{card.GetRandomNumber()}_BusinessCashout2402.json'
                BusinessCashout2402(row['ACC_CRD'], row['IDN_CARD'], row['SUM_TRN'], row['VAL_CODE'], name_file)
            elif row['IDN_CARD'] is None:
                name_file = f'{card.GetRandomNumber()}_BusinessCashout2402.json'
                card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Снятие через операцию 2402 чужой АТМ Business карта клиента {row['CLI_ID']}",
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
                                                                                                            
                                                                                                            
                                                                                                            
def BusinessCashout2402(acc_crd, idn_crd, amount, val, name_file):
    soap = SoapRequests() 
    task = TaskMethods()
    card = CardFramework()
    count = 1
    operation_type = 'outc'
    try:
        # создание отчета allure
        soap.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Продукт - Business карта", f"Снятие через операцию 2402 чужой АТМ по счету {acc_crd}", name_file)
        #---------    
        soap.StartCapJob()
        # Присваеваем теущий баланс к переменной
        before_bln = soap.CheckAccBalance(acc_crd)
        Delay(2000) # Нужна небольшая задержка Перед отправкой запроса                                                  
        # Отправляем запрос на снятие с чужого АТМ
        response = soap.ATM_2402(idn_crd, amount, val, 'INT')
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
        # Ниже достаем айдишник С - файла, для дальнейщей активации
        card.GetProcFile(tran_id)
        #---------
    except Exception as error:
        # завершение формирование отчета
        task.AllureReportEnd(count, name_file, "failed", error)
