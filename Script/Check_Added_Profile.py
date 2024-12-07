﻿from SoapRequests import *
from TaskMethods import *
from CardFramework import *


def CheckAddedProfile_AllDataSet():
    """ Проверка добавленного профиля в договоре информирования """
    card = TaskMethods()
    card.LoginInColvir()
    data_list = card.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
        try:
            if row['USER_ACC']:
                name_file = f'{card.GetRandomNumber()}_CheckAddedProfile.json'   
                CheckAddedProfile(row['CLI_ID'], row['TARIF_CODE'], row['USER_ACC'], name_file)
            elif row['USER_ACC'] is None:
                name_file = f'{card.GetRandomNumber()}_CheckAddedProfile.json'
                card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Проверка добавленного профиля в договоре информирования", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')   
               
def CheckAddedProfile(cli_id, tarif, cliacc, name_file):
    card = TaskMethods()
    try:
        # создание отчета allure
        card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Договор информирования", f"Проверка добавленного профиля в договоре информирования по клиенту {cli_id}", name_file)
        # Поиск документа   
        card.FindDoc('INFDEA', {"CLICODE": cli_id}, "frmInfDeaList")
        # Клик по просмотру договора
        browsebtn = card.FindChildField("frmInfDeaList", "Name", 'VCLObject("btnBrowse")')
        browsebtn.Click()
        profile_tab = card.FindChildField("InformDeaDtl", "Name", 'PageTab("Подключенные профили")')
        profile_tab.Click()
        # TO DO V
        Sys.Process("COLVIR").VCLObject("InformDeaDtl").VCLObject("pnlClient").VCLObject("pnlSupport").VCLObject("pnlBottom").VCLObject("tabDetail").VCLObject("tsLinkedProfiles").VCLObject("grLnkPrf").TextObject("Бесплатная СМС рассылка на рус.яз.").Click()
        DocName = card.GetGridDataFields("InformDeaDtl", "LONGNAME")
        CodeSc = DocName[0].replace("\'", '')
        card.CheckCorrectData(CodeSc, 'БесплатнаяСМСрассылканарус.яз.', 1, name_file, 'VCLObject("InformDeaDtl")')
        card.CloseWindow("InformDeaDtl")
        card.CloseWindow("frmInfDeaList")
    except Exception as error:
        # завершение формирование отчета
        card.AllureReportEnd(2, name_file, "failed", error)
        #---------
