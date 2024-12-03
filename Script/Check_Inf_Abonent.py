from SoapRequests import *
from TaskMethods import *
from CardFramework import *


def CheckInfAbonent_AllDataSet():
    """ Регистрация договора информирования """
    card = TaskMethods()
    card.LoginInColvir()
    data_list = card.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
        try:
            if row['USER_ACC']:
                name_file = f'{card.GetRandomNumber()}_CheckInfAbonent.json'   
                CheckInfAbonent(row['CLI_ID'], name_file)
            elif row['USER_ACC'] is None:
                name_file = f'{card.GetRandomNumber()}_CheckInfAbonent.json'
                card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Проверка абонента рассылки по клиенту {row['CLI_ID']}", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')   
               
def CheckInfAbonent(cli_id, name_file):
    card = TaskMethods()
    try:
        # создание отчета allure
        card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Договор информирования", f"Проверка абонента рассылки по клиенту {cli_id}", name_file)
        # Поиск документа   
        card.FindDoc('INFABONENT', {"CLI_CODE": cli_id}, "frmInformAbonentsList")
        # Исполнение операции
        OpenInf = card.FindChildField("frmInformAbonentsList", "Name", 'VCLObject("btnBrowse")')
        OpenInf.Click()
        card.WaitLoadWindow('frmInformAbonentDtl', time_await=5000)
        LangCode = card.GetGridDataFields("frmInformAbonentDtl", "LNG_CODE")
        CodeLg = LangCode[0].replace("\'", '')
        card.CheckCorrectData(CodeLg, 'RU', 1, name_file, 'VCLObject("frmInformAbonentDtl")')
        card.CloseWindow("frmInformAbonentDtl")
        card.CloseWindow("frmInformAbonentsList")
        card.AllureReportEnd(1, name_file, "passsed")
    except Exception as error:
        # завершение формирование отчета
        card.AllureReportEnd(2, name_file, "failed", error)
        #---------
