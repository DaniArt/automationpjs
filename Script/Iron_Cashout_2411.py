from CardFramework import *
from SoapRequests import *
from SQL import Sql
                                                                                                            
                                                                                                            
def IronCashout2411_AllDataSet():
    """ Снятие со счета карты через операцию 2411 """
    card = CardFramework()
    data_list = card.ReadDatasetFromDB('iron_data')  
    for row in data_list:
        try:
            if row['IDN_CARD']:
                name_file = f'{card.GetRandomNumber()}_IronCashout2411.json'
                IronCashout2411(row['CLI_ACC'], row['IDN_CRD'], row['AMOUNT'],
                               row['CARD_NUM'], row['PSYS'], row['TERM_TYPE'],
                               row['MCC'], row['TYPE_TRN'], name_file)
            elif row['IDN_CARD'] is None:
                name_file = f'{card.GetRandomNumber()}_IronCashout2411.json'
                card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Снятие со счета карты через операцию 2411 Iron карта клиента {row['CLI_ID']}",
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
                                                                                                            
                                                                                                            
                                                                                                            
def IronCashout2411(acc_crd, idn_crd, amount, card_num, psys, term_id, mcc, type_trn, name_file):
    soap = SoapRequests()
    task = TaskMethods()
    card = CardFramework()
    count = 1
    operation_type = 'outc'
    try:
        # создание отчета allure
        soap.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Продукт - Iron карта", f"Снятие со счета карты через операцию 2411 по счету {acc_crd}", name_file)
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
        balance_need = card.CheckCorrectTransaction(None, None, 0, before_bln, amount, acc_crd, operation_type, count, name_file, tran_id)
        # Ниже достаем айдишник С - файла, для дальнейщей активации
        card.GetProcFile(tran_id)
        #---------
    except Exception as error:
        # завершение формирование отчета
        task.AllureReportEnd(count, name_file, "failed", error)                                                                     
    
