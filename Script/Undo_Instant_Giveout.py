﻿from CardFramework import *

def UndoInstantGiveout_AllDataSet():
    """ Отмена выдачи карты моментального выпуска в договоре СКС по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:
        if row['ITER_CODE'] == '1':
            name_file = f'{Ndeacrd.GetRandomNumber()}_UndoInstantGiveout.json' 
            UndoInstantGiveout(row['PRODUCT'], row['DOC_CODE'], row['REG_DATE'], name_file)
             
def UndoInstantGiveout(product, doc_code, reg_date, name_file):
    """ Отмена выдачи карты моментального выпуска в договоре СКС """
    Ndeacrd = CardFramework()
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Отмена выпуска карты", f"Отмена подвязки карты {product} к договору {doc_code}", Ndeacrd.GetDateTimeMilli()]
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
        Ndeacrd.SetFilter(CODE=doc_code) # Вставляем номер документа из бд, для поиска нашего заведенного договора
        Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=6000)
        but_operations = Sys.Process("COLVIR").VCLObject("DeaSCAList").VCLObject("btnRunOperation") # Определение контекстного меню с опреациямии
        but_operations.Click()
        Ndeacrd.FindNeedOperation("Отмена выдачи карты мом.вып.") 
        Ndeacrd.ConfirmOperation("Отмена выдачи карты мом.вып.")
        Ndeacrd.CheckOperEndWindow()
        Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=3000)
        opr_jrn = Ndeacrd.FindChildField("DeaSCAList", "Name", "VCLObject('btnOperJrn')")
        opr_jrn.Click()
        Ndeacrd.WaitLoadWindow('frmOperJournal', time_await=3000)
        status_oper = Ndeacrd.GetGridDataFields("frmOperJournal", "NAME")
        if status_oper[0].replace("\'", '') == 'Отменавыдачикартымом.вып.':
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Отмена выдачи карты момент.выпуска", "passed", {"message": f"Выполнена отмена выдачи инстант карты по договору {DOC_CODE}"},
                                           'VCLObject("frmOperJournal")', "Операция выполнена", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Выполнена операция отмены выдачи карты моментального выпуска по договору {DOC_CODE}')
        else:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Отмена выдачи карты момент.выпуска", "failed", {"message": f"Ошибка! Операция 'Отмена выпуска инстант карты' не выполнена"},
                                           'VCLObject("frmOperJournal")', "Операция не выполнена", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning("Ошибка! Операция отмены выдачи карты моментального выпуска не выполнена")
        Sys.Process("COLVIR").VCLObject("frmOperJournal").Close()
        Sys.Process("COLVIR").VCLObject("DeaSCAList").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 