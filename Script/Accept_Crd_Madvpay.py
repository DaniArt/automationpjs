﻿from CardFramework import *

def AcceptCrdMadvpay_AllDataSet():
    """ Оприходывание карты через Madvpay по всему датасету """
    Madvpay = CardFramework()
    #login_user, pass_user = Madvpay.GetLoginPass('BOC_OFFICER')
    Madvpay.LoginInColvir()
    data_list = Madvpay.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:  
        try:
            if row['ACC_CRD'] and row['DEPO_CODE'] == 'AA6':
                name_file = f'{Madvpay.GetRandomNumber()}_AcceptCrdMadvpay.json'  
                AcceptCrdMadvpay(row['DOC_CODE'], row['CLI_ID'], row['ACC_CRD'], name_file)
            elif row['ACC_CRD'] is None and row['DEPO_CODE'] == 'AA6':
                name_file = f'{Madvpay.GetRandomNumber()}_AcceptCrdMadvpay.json'
                Madvpay.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Оприходывание карты", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
            
def AcceptCrdMadvpay(DOC_CODE,cli_code,acc_code,name_file):
    """ Оприходывание карты через Madvpay """
    Madvpay = CardFramework()
    # Создание главной иерархии json отчета
    new_path = Madvpay.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Madvpay.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Оприходывание карты", f"Оприходывание карты через Madvpay", Madvpay.GetDateTimeMilli()]
    abs_path = Madvpay.FindAbsPathFile(name_file) # Получение абсолютного пути файла
    Madvpay.AddKeyValueJson(abs_path, key, value)
    def_dict = Madvpay.GetDefaultDict(abs_path)
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
    Madvpay.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", "Операции - СКС Договора"]
    Madvpay.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    # Начало работы скрипта автотеста
    try:   
        Madvpay.TaskInput('MADVPAY')
        Madvpay.WaitLoadWindow('frmFilterParams')
        Madvpay.SetFilter(STATE_NAME='Передан') # Вставляем номер документа из бд, для поиска нашего заведенного договора
        Madvpay.WaitLoadWindow('AdvancePaymentList', time_await=5000)
        GridDefine = Sys.Process("COLVIR").VCLObject("AdvancePaymentList").VCLObject("pnlClient").WaitVCLObject("DBGrid", 3000)
        GridDefine.Click()
        MadvpayGrid = Madvpay.GetGridDataFields("AdvancePaymentList", "LONGNAME")
        if MadvpayGrid[0].replace("\'", '') == 'Передан':
            Madvpay.WaitLoadWindow('AdvancePaymentList', time_await=5000)
            but_operations = Madvpay.FindChildField("AdvancePaymentList", "Name", "VCLObject('btnRunOperation')")
            but_operations.Click()
            if Sys.Process("COLVIR").Popup("Контекст").WaitTextObject("Принять",4000).Exists:
                #if Madvpay.FindNeedOperation("Принять").Exists: 
                Madvpay.ConfirmOperation("Принять")
                Madvpay.CheckOperEndWindow()
                GridDefine.Click() # Вызов клика по полю для избегания краша теста 
                status_oper = Madvpay.GetGridDataFields("AdvancePaymentList", "LONGNAME") # Получаем статус карты для дальнейшей проверки
                if status_oper[0].replace("\'", '') == 'Исполнен':
                    # Отчетность
                    Madvpay.AllureReportTemplate(abs_path, name_file, "Оприходывание карты", "passed", {"message": f"Выполнена оприходывание карты в кладовой"},
                                                   'VCLObject("AdvancePaymentList")', "Карта передана", new_path, "passed", 1, 1, rm=True)
                    # --------------------------------------------------------------------------------------------------------------------------
                    Log.Checkpoint(f'Выполнена оприходывание карты в кладовой')
                else:
                    # Отчетность
                    Madvpay.AllureReportTemplate(abs_path, name_file, "Оприходывание карты", "failed", {"message": f"Ошибка! Операция оприходывания не выполнена"},
                                                   'VCLObject("AdvancePaymentList")', "Карта не передана", new_path, "failed", 1, 1, rm=True)
                    # --------------------------------------------------------------------------------------------------------------------------
                    Log.Warning("Ошибка! Операция оприходывания не выполнена")
                refresh_btn = Madvpay.FindChildField("AdvancePaymentList", "Name", "VCLObject('btnRefresh')")
                refresh_btn.Click() # Кнопка обновления
                MadvpayGrid = Madvpay.GetGridDataFields("AdvancePaymentList", "LONGNAME")
                i += 1 
            else:
                name_file = f'{Madvpay.GetRandomNumber()}_AcceptCrdMadvpay.json'
                Madvpay.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Оприходывание карты через Madvpay", 
                                                f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        else:
            # Если ни одна карта не была отправлена на оприходование, делаем отчет MadvpayGrid[0] == ''
            Madvpay.AllureReportTemplate(abs_path, name_file, "Отсутствие карт", "passed", {"message": "Карты в состоянии 'Передан' отсутствуют в кладовой"}, 
                                         'VCLObject("AdvancePaymentList")', 'Нету карт в кладовой', new_path, "passed", 1, 1, rm=True)
            Log.Message('Нету карт в кладовой')
                
        Sys.Process("COLVIR").VCLObject("AdvancePaymentList").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Madvpay.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 