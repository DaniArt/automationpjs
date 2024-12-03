from SoapRequests import *
from TaskMethods import *
from CardFramework import *


def ReCreateInfDea_AllDataSet():
    """ Проверка на наличие договора информирования при создании """
    card = TaskMethods()
    card.LoginInColvir()
    data_list = card.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
        try:
            if row['USER_ACC']:
                name_file = f'{card.GetRandomNumber()}_ReCreateInfDea.json'   
                ReCreateInfDea(row['CLI_ID'], row['TARIF_CODE'], row['USER_ACC'], name_file)
            elif row['USER_ACC'] is None:
                name_file = f'{card.GetRandomNumber()}_ReCreateInfDea.json'
                card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Проверка на наличие дог.инфор при пересоздании по клиенту", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')   
               
def ReCreateInfDea(cli_id, tarif, cliacc, name_file):
    card = TaskMethods()
    try:
        # создание отчета allure
        card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Договор информирования", f"Проверка на наличие дог.инфор при пересоздании по клиенту {cli_id}", name_file)
        # Поиск документа   
        card.TaskInput('INFDEA')
        card.InputEmptyFilter()
        card.WaitLoadWindow('frmInfDeaList', time_await=5000) 
        # Клик по созданию договора
        CreateBtn = card.FindChildField("frmInfDeaList", "Name", 'VCLObject("btnInsert")')
        CreateBtn.Click()
        card.inputData("frmVarDtlDialog", "edtKeyValue", '5510', need_tab = True)
        card.ClickInputField("frmVarDtlDialog", 'VCLObject("btnOK")', need_tab = False) 
        card.WaitLoadWindow('InformDeaDtl', time_await=5000) 
        # Заполненпие документа
        card.inputData("InformDeaDtl", "edCLI_CODE", cli_id, need_tab = True)
        find_window = Sys.Process("COLVIR").Dialog("Colvir Banking System")
        if find_window.Exists:
            card.AllureReportEnd(1, name_file, "passed")  
            find_window.close()     
        card.WaitLoadWindow('frmInfDeaList', time_await=5000)
        card.CloseWindow("frmInfDeaList")
    except Exception as error:
        # завершение формирование отчета
        card.AllureReportEnd(2, name_file, "failed", error)
        #---------
