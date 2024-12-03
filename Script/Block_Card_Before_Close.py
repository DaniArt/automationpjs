from CardFramework import *
from TaskMethods import *

def BlockCardBeforeClose_AllDataSet():
    """ Блокировка карты перед закрытием """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:
        if row['ITER_CODE'] == '2':
            name_file = f'{NCRD.GetRandomNumber()}_BlockCardBeforeClose.json'   
            BlockCardBeforeClose(row['IDN_CARD'], name_file)

            
def BlockCardBeforeClose(idn_card, name_file):
    try:
        count = 1
        NCRD = TaskMethods()
        # создание отчета allure
        NCRD.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Операции - СКС Договора", "Блокировка карты перед закрытием", name_file)
        #---------   
        NCRD.TaskInput('NCRD')
        NCRD.WaitLoadWindow('frmFilterParams')
        NCRD.SetFilter(CARDIDN=idn_card) # Берем номер идентификатора из бд, для поиска нашей карты
        NCRD.WaitLoadWindow('NCrdList')
        # Выполнение операции
        NCRD.PerformingOperation('Блокировать карту', 'Выполнить операцию "Блокировать карту" ?', 'NCrdList', 'btnRunOperation')
        NCRD.inputData("frmDynamicDialog", "REASON", "41", need_tab = True)
        NCRD.inputData("frmDynamicDialog", "REASON_DSCR", "TEST", need_tab = True)
        NCRD.inputData("frmDynamicDialog", "VERIFY_TYPE", "3", need_tab = True)
        NCRD.ClickInputField("frmDynamicDialog", 'VCLObject("btnOK")', need_tab = False)
        NCRD.CheckOperEndWindow()
        #-------------------
        NCRD.WaitLoadWindow('NCrdList')
        # проверка записи в журнале операций
        NCRD.CheckOperJrn("Блокироватькарту", "NCrdList", 'VCLObject("btnOperJrn")', "frmOperJournal", ["NAME"], count, name_file)
        count += 1
        #---------
        # закрытие главного окна
        NCRD.CloseWindow("NCrdList")
        #---------
        # завершение формирование отчета
        NCRD.AllureReportEnd(count, name_file, "passed")
        count += 1
        #---------
    except Exception as error:
        # завершение формирование отчета
        NCRD.AllureReportEnd(count, name_file, "failed", error)
        #---------
