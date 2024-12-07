﻿from SoapRequests import *
from TaskMethods import *
from CardFramework import *


def UndoLinkProfile_AllDataSet():
    """ Отмена последнего профиля в договоре информирования """
    card = TaskMethods()
    card.LoginInColvir()
    data_list = card.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
        try:
            if row['USER_ACC']:
                name_file = f'{card.GetRandomNumber()}_UndoLinkProfile.json'   
                UndoLinkProfile(row['CLI_ID'], name_file)
            elif row['USER_ACC'] is None:
                name_file = f'{card.GetRandomNumber()}_UndoLinkProfile.json'
                card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Отмена последнего профиля в договоре информирования", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')   
               
def UndoLinkProfile(cli_id, name_file):
    card = TaskMethods()
    try:
        # создание отчета allure
        card.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Договор информирования", "Отмена последнего профиля в договоре информирования", name_file)
        # Поиск документа   
        card.FindDoc('INFDEA', {"CLICODE": cli_id}, "frmInfDeaList")
        # Исполнение операции
        card.PerformingOperation('Отмена привязки профиля', 'Отмена привязки профиля', 'frmInfDeaList', 'btnRunOperation')
                #---------
        Delay(5000)
        # проверка записи в журнале операций
        card.CheckOperJrn("Отменапривязкипрофиля", "frmInfDeaList", 'VCLObject("btnOperJrn")', 
                          "frmOperJournal", ["NAME"], 1, name_file)
        #Закрытие окна
        card.CloseWindow("frmInfDeaList")
    except Exception as error:
        # завершение формирование отчета
        card.AllureReportEnd(2, name_file, "failed", error)
        #---------
