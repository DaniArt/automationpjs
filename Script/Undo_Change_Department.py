﻿from CardFramework import *
 
def UndoChangeDepartment_AllDataSet():
    """ Отмена перевода в другое подразделение договора СКС для клиента по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:  
        if row['ITER_CODE'] == '1':
            name_file = f'{Ndeacrd.GetRandomNumber()}_UndoChangeDepartment.json'  
            UndoChangeDepartment(row['DOC_CODE'], row['CLI_ID'], row['ACC_CRD'], name_file)
            
def UndoChangeDepartment(DOC_CODE, cli_code, acc_code, name_file):
    """ Отмена перевода в другое подразделение договора СКС для клиента """
    Ndeacrd = CardFramework()
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Отмена перевода в другое подразделение", f"Операция отмены перевода в другое подразделение по договору {DOC_CODE}", Ndeacrd.GetDateTimeMilli()]
    abs_path = Ndeacrd.FindAbsPathFile(name_file) # Получение абсолютного пути файла
    Ndeacrd.AddKeyValueJson(abs_path, key, value)
    def_dict = Ndeacrd.GetDefaultDict(abs_path)
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
    Ndeacrd.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", "Операции - СКС Договора"]
    Ndeacrd.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    # Начало работы скрипта автотеста
    try:  
        Ndeacrd.TaskInput('NDEACRD')
        Ndeacrd.WaitLoadWindow('frmFilterParams')
        Ndeacrd.SetFilter(CODE=DOC_CODE) # Вставляем номер документа из бд, для поиска нашего заведенного договора
        Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=5000)
        but_operations = Sys.Process("COLVIR").VCLObject("DeaSCAList").VCLObject("btnRunOperation") # Определение контекстного меню с опреациямии
        but_operations.Click()
        Ndeacrd.FindNeedOperation("Отмена перевода в другое подр.") 
        Ndeacrd.ConfirmOperation("Отмена перевода в другое подр.")
        Ndeacrd.CheckOperEndWindow()
        Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=3000)
        opr_jrn = Ndeacrd.FindChildField("DeaSCAList", "Name", "VCLObject('btnOperJrn')")
        opr_jrn.Click()
        Ndeacrd.WaitLoadWindow('frmOperJournal', time_await=3000)
        status_oper = Ndeacrd.GetGridDataFields("frmOperJournal", "NAME")
        if status_oper[0].replace("\'", '') == 'Отменапереводавдругоеподр.':
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Перевод в другое подразделение", "passed", {"message": f"Выполнена Перевод в другое подразделение по договору {DOC_CODE}"},
                                           'VCLObject("frmOperJournal")', "Подразделение изменено", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Выполнен Перевод в другое подразделение по договору {DOC_CODE}')
        else:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Перевод в другое подразделение", "failed", {"message": f"Ошибка! Операция 'Перевод в другое подразделение' не выполнена"},
                                           'VCLObject("frmOperJournal")', "Подразделение не изменено", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning("Перевод в другое подразделение не выполнена")
        Sys.Process("COLVIR").VCLObject("frmOperJournal").Close()
        Sys.Process("COLVIR").VCLObject("DeaSCAList").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 