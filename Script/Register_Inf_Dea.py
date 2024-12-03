from SoapRequests import *
from TaskMethods import *
from CardFramework import *


def RegisterInfDea_AllDataSet():
    """ Регистрация договора информирования """
    card = TaskMethods()
    card.LoginInColvir()
    data_list = card.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
        try:
            if row['USER_ACC']:
                name_file = f'{card.GetRandomNumber()}_RegisterInfDea.json'   
                RegisterInfDea(row['CLI_ID'], name_file)
            elif row['USER_ACC'] is None:
                name_file = f'{card.GetRandomNumber()}_RegisterInfDea.json'
                card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Проверка создания регистрации информирования", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')   
               
def RegisterInfDea(cli_id, name_file):
    card = TaskMethods()
    try:
        # создание отчета allure
        card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Договор информирования", "Проверка регистрации договора информирования", name_file)
        # Поиск документа   
        card.FindDoc('INFDEA', {"CLICODE": cli_id}, "frmInfDeaList")
        # Исполнение операции
        card.PerformingOperation('Регистрация', 'Регистрация', 'frmInfDeaList', 'btnRunOperation')
        DocName = card.GetGridDataFields("frmInfDeaList", "STATNAME")
        CodeSc = DocName[0].replace("\'", '')
        card.CheckCorrectData(CodeSc, 'Зарегистрирован', 1, name_file, 'VCLObject("frmInfDeaList")')
        card.CloseWindow("frmInfDeaList")
    except Exception as error:
        # завершение формирование отчета
        card.AllureReportEnd(2, name_file, "failed", error)
        #---------
