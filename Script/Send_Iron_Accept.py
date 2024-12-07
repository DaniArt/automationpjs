﻿from CardFramework import *

def SendIronAccept_AllDataSet():
    """ Отправка на акцептование карты клиента по всему датасету """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('iron_data')
    for row in data_list:
        try:
            if row['IDN_CARD'] and row['ITER_CODE'] == '1':
                name_file = f'{NCRD.GetRandomNumber()}_SendIronAccept.json'  
                form_data = SendIronAccept(row['CLI_ID'], name_file)
                row['ACC_CRD'] = form_data
                NCRD.UpdateDatasetTableDB('iron_data', data_list)
            elif row['IDN_CARD'] is None:
                name_file = f'{NCRD.GetRandomNumber()}_SendIronAccept.json'
                NCRD.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Отправка на акцептование карты, Iron карта", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
            
def SendIronAccept(cli_id, name_file):
    """ Отправка на акцептование карты клиента """
    acc_crd = ''
    NCRD = CardFramework()
    # Создание главной иерархии json отчета
    new_path = NCRD.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    NCRD.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Отправка на акцептование карты", f"Отправка на акцептование карты клиента {cli_id}", NCRD.GetDateTimeMilli()]
    abs_path = NCRD.FindAbsPathFile(name_file) # Получение абсолютного пути файла
    NCRD.AddKeyValueJson(abs_path, key, value)
    def_dict = NCRD.GetDefaultDict(abs_path)
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
    NCRD.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", "Продукт - Iron карта"]
    NCRD.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    # Начало работы скрипта автотеста
    try:   
        NCRD.TaskInput('NDEACRD')
        NCRD.WaitLoadWindow('frmFilterParams', time_await=5000)
        NCRD.SetFilter(CLI_CODE=cli_id) # Вставляем номер документа из бд, для поиска нашего заведенного договора
        NCRD.WaitLoadWindow('DeaSCAList', time_await=3000)
        browse_btn = NCRD.FindChildField("DeaSCAList", "Name", "VCLObject('btnBrowse')")
        browse_btn.Click()
        NCRD.WaitLoadWindow('DeaSCADetail', time_await=3000)
        CardOper = NCRD.FindChildField("DeaSCADetail", "Name", "VCLObject('btnCardOper')")
        CardOper.Click()
        NCRD.FindNeedOperation("Отправить на акцептование") 
        NCRD.ConfirmOperation("Отправить на акцептование")
        Sys.Process("COLVIR").VCLObject("frmDFSimpleEngine").VCLObject("LayoutFrame").CheckBox("Да").Click()
        epin_checkbox = NCRD.FindChildField("frmDFSimpleEngine", "Name", "CheckBox('Да.')")
        epin_checkbox.Click()
        btn_ok = NCRD.FindChildField("frmDFSimpleEngine", "Name", "VCLObject('btnOK')")
        btn_ok.Click()
        NCRD.ConfirmOperation("Изменить реквизиты расчетов по договору на счет карты по-умолчанию?")
        NCRD.ConfirmOperation("У договора СКС нет счетов. Счет будет создан автоматически, продолжить?")
        NCRD.CheckOperEndWindow()
        NCRD.WaitLoadWindow('frmaNewCrdAccAction', time_await=3000)
        ok_btn = NCRD.FindChildField("frmaNewCrdAccAction", "Name", "VCLObject('btnOK')")
        ok_btn.Click()
        NCRD.ConfirmOperation("Изменить реквизиты расчетов по договору на счет карты по-умолчанию?")
        if Sys.Process("COLVIR").WaitVCLObject("RptToPrintList", 10000).Exists:
            close_btn = NCRD.FindChildField("RptToPrintList", "Name", "VCLObject('btnClose')")
            close_btn.Click()
            NCRD.CheckOperEndWindow()
        else:
            Log.Event("Объект RptToPrintList не найден, продолжаем выполнение теста...")
        NCRD.WaitLoadWindow('DeaSCADetail', time_await=3000)
        status_crd = NCRD.GetGridDataFields("DeaSCADetail", "STATNAME", "CRD_CODE", "ACC_CODE", need_tab="qryCard") # Получаем статус карты для дальнейшей проверки
        acc_crd = status_crd[2].replace("\'", '')
        if status_crd[0].replace("\'", '') == 'Переданонаакцептование':
            # Отчетность
            NCRD.AllureReportTemplate(abs_path, name_file, "Отправка на акцептование карты клиента", "passed", {"message": f"Карта с идентификатором {status_crd[1]} в состоянии {status_crd[0]}"},
                                         'VCLObject("DeaSCADetail")', "Карта отправлена на акцептование", new_path, "passed", 1, 1, rm = True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Карта с идентификатором {status_crd[1]} в состоянии {status_crd[0]}')
        else:
            # Отчетность
            NCRD.AllureReportTemplate(abs_path, name_file, "Отправка на акцептование карты клиента", "failed", {"message": f"Операция передачи на акцепт не выполнена"},
                                         'VCLObject("DeaSCADetail")', "Карта не отправлена на акцепт", new_path, "failed", 1, 1, rm = True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Операция передачи на акцепт не выполнена')
        Sys.Process("COLVIR").VCLObject("DeaSCADetail").Close()
        return acc_crd
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        NCRD.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 
