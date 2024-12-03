from CardFramework import *
from TaskMethods import *

def MakeCardMain_AllDataSet():
    """ Операция по выбору карты как основную """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:
        if row['ITER_CODE'] == '2':
            name_file = f'{NCRD.GetRandomNumber()}_MakeCardMain.json'   
            MakeCardMain(row['IDN_CARD'], name_file)

            
def MakeCardMain(idn_card, name_file):
    NCRD = TaskMethods()
    count = 1
    try:
        # создание отчета allure
        NCRD.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Операции - СКС Договора", "Сделать основной картой", name_file)
        # Поиск документа   
        NCRD.FindDoc("NCRD", {"CARDIDN": idn_card}, "NCrdList")
        # Выполнение операции
        NCRD.PerformingOperation('Сделать основной картой', 'Сделать основной картой', 'NCrdList', 'btnRunOperation')
        NCRD.ClickInputField("frmDynamicDialog", 'VCLObject("btnOK")', need_tab = False)
        NCRD.CheckOperEndWindow()
        #-------------------
        NCRD.WaitLoadWindow('NCrdList')
        # проверка записи в журнале операций
        NCRD.CheckOperJrn("Сделатьосновнойкартой", "NCrdList", 'VCLObject("btnOperJrn")', "frmOperJournal", ["NAME"], count, name_file)
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
