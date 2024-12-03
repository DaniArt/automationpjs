from SoapRequests import *
from TaskMethods import *


def CreateInfDea_AllDataSet():
    """ Создание договора информирования """
    card = TaskMethods()
    card.LoginInColvir()
    data_list = card.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
        try:
            if row['USER_ACC']:
                name_file = f'{card.GetRandomNumber()}_CreateInfDea.json'   
                CreateInfDea(row['CLI_ID'], row['TARIF_CODE'], row['USER_ACC'], name_file)
            elif row['USER_ACC'] is None:
                name_file = f'{card.GetRandomNumber()}_CreateInfDea.json'
                card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Проверка создания договора информирования", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')   
               
def CreateInfDea(cli_id, tarif, cliacc, name_file):
    card = TaskMethods()
    try:
        # создание отчета allure
        card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Договор информирования", "Проверка создания договора информирования", name_file)
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
        card.inputData("InformDeaDtl", "edTRF_IDCAT", tarif, need_tab = True)
        card.inputData("InformDeaDtl", "edCMS_CODE", cliacc, need_tab = True)
        card.ClickInputField("InformDeaDtl", 'VCLObject("btnSave")', need_tab = False) 
        card.WaitLoadWindow('frmInfDeaList', time_await=5000)
        DocName = card.GetGridDataFields("frmInfDeaList", "STATNAME")
        CodeSc = DocName[0].replace("\'", '')
        card.CheckCorrectData(CodeSc, 'Введен', 1, name_file, 'VCLObject("frmInfDeaList")')
        card.CloseWindow("frmInfDeaList")
    except Exception as error:
        # завершение формирование отчета
        card.AllureReportEnd(2, name_file, "failed", error)
        #---------
