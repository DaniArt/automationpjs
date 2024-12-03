from SoapRequests import *
from TaskMethods import *
from CardFramework import *
                                                                                                            
                                                                                                            
def IronDeposit2424_AllDataSet():
    """ Пополнение 2424 Card Deposit """
    card = SoapRequests()
    data_list = card.ReadDatasetFromDB('iron_data')  
    for row in data_list:
        try:
            if row['IDN_CARD']:
                name_file = f'{card.GetRandomNumber()}_IronDeposit2424.json' 
                IronDeposit2424(row['VAL_CODE'], row['ACC_CRD'], row['IDN_CARD'], row['SUM_TRN'], row['CARDCODE'], name_file) 
            elif row['IDN_CARD'] is None:
                name_file = f'{card.GetRandomNumber()}_IronDeposit2424.json'
                card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Пополнение 2424 Card Debit Iron карта клиента {row['CLI_ID']}", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')                                                                              
                                                                                                            
                                                                                                            
def IronDeposit2424(valcode, acc_crd, idn_crd, amount, card_num, name_file):
    soap = SoapRequests()
    task = TaskMethods()
    card = CardFramework()
    count = 1
    operation_type = 'inc'
    try:
        # создание отчета allure
        soap.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Продукт - Iron карта", f"Пополнение 2424 Card Debit по счету {acc_crd}", name_file)
        #---------    
        soap.StartCapJob()
        # Присваеваем теущий баланс к переменной
        before_bln = soap.CheckAccBalance(acc_crd)
        Log.Message(before_bln)
        # Отправляем запрос на снятие с POS
        Delay(2000) # Нужна небольшая задержка Перед отправкой запроса
        response = soap.CardDeposit2424(acc_crd, card_num, valcode, amount)
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

