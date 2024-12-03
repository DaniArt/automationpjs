from CardFramework import *
from TaskMethods import *

def CreateArchiveInfo_AllDataSet():
    """ В данном автотесте формируется архивная выписка  """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:
        if row['ITER_CODE'] == '2':
            name_file = f'{NCRD.GetRandomNumber()}_CreateArchiveInfo.json'   
            CreateArchiveInfo(row['IDN_CARD'], name_file)

            
def CreateArchiveInfo(idn_card, name_file):
    try:
        count = 1
        NCRD = TaskMethods()
        # создание отчета allure
        NCRD.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Операции - СКС Договора", "Формирование архивной выписки", name_file)
        #---------   
        NCRD.TaskInput('NCRD')
        NCRD.WaitLoadWindow('frmFilterParams')
        NCRD.SetFilter(CARDIDN=idn_card) # Берем номер идентификатора из бд, для поиска нашей карты
        NCRD.WaitLoadWindow('NCrdList')
        # Выполнение операции
        NCRD.PerformingOperation('Сформировать архивную выписку', 'Выполнить операцию "Сформировать архивную выписку" ?', 'NCrdList', 'btnRunOperation')
        NCRD.ClickInputField("frmDynamicDialog", 'VCLObject("btnOK")', need_tab = False)
        NCRD.CheckOperEndWindow()
        #-------------------
        NCRD.WaitLoadWindow('NCrdList')
        # проверка записи в журнале операций
        NCRD.CheckOperJrn("Сформироватьархивнуювыписку", "NCrdList", 'VCLObject("btnOperJrn")', "frmOperJournal", ["NAME"], count, name_file)
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
