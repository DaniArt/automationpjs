from SoapRequests import *
from TaskMethods import *
from CardFramework import *


def LinkProfileInfDea_AllDataSet():
    """ Добавление профиля в договоре информирования """
    card = TaskMethods()
    card.LoginInColvir()
    data_list = card.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
        try:
            if row['USER_ACC']:
                name_file = f'{card.GetRandomNumber()}_LinkProfileInfDea.json'   
                LinkProfileInfDea(row['CLI_ID'], row['TARIF_CODE'], row['USER_ACC'], name_file)
            elif row['USER_ACC'] is None:
                name_file = f'{card.GetRandomNumber()}_LinkProfileInfDea.json'
                card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Подвязка профиля в договоре информирования", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')   
               
def LinkProfileInfDea(cli_id, tarif, cliacc, name_file):
    card = TaskMethods()
    try:
        # создание отчета allure
        card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Договор информирования", f"Подвязка профиля в договоре информирования по клиенту {cli_id}", name_file)
        # Поиск документа   
        card.FindDoc('INFDEA', {"CLICODE": cli_id}, "frmInfDeaList")
        # Клик по просмотру договора
        browsebtn = card.FindChildField("frmInfDeaList", "Name", 'VCLObject("btnBrowse")')
        browsebtn.Click()
        parameters_tab = card.FindChildField("InformDeaDtl", "Name", 'PageTab("Подключенные профили")')
        parameters_tab.Click()
        Delay(3000)
        IsrtBtn = card.FindChildField("InformDeaDtl", "Name", 'VCLObject("btnInsertDtl")')
        IsrtBtn.Click()
        chooseTrf = card.FindChildField("frmInformProfileRef", "Name", 'TextObject("SMS_FREE_RU")')
        chooseTrf.Click()
        Delay(2000) 
        card.ClickInputField("frmInformProfileRef", 'VCLObject("btnOK")', need_tab = False)
        Delay(5000) 
        card.AllureReportEnd(1, name_file, "passed") 
        card.CloseWindow("InformDeaDtl")
        card.CloseWindow("frmInfDeaList")
    except Exception as error:
        # завершение формирование отчета
        card.AllureReportEnd(2, name_file, "failed", error)
        #---------
