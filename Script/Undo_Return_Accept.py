﻿from CardFramework import *

def UndoReturnAccept_AllDataSet():
    """ Отмена возвращения карты на акцепт по всему датасету """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:
        if row['ITER_CODE'] == '2':
            name_file = f'{NCRD.GetRandomNumber()}_UndoReturnAccept.json'   
            UndoReturnAccept(row['IDN_CARD'], name_file)
            
def UndoReturnAccept(idn_card, name_file):
    """ Отмена возвращения карты на акцепт """
    NCRD = CardFramework() 
    # Создание главной иерархии json отчета
    new_path = NCRD.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    NCRD.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Акцепт карты - Отменить возврат", f"Отменить возврат карты {idn_card}", NCRD.GetDateTimeMilli()]
    abs_path = NCRD.FindAbsPathFile(name_file) # Получение абсолютного пути файла
    NCRD.AddKeyValueJson(abs_path, key, value)
    def_dict = NCRD.GetDefaultDict(abs_path)
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
    NCRD.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", "Операции - СКС Договора"]
    NCRD.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    # Начало работы скрипта автотеста
    try:      
        NCRD.TaskInput('NCRD')
        NCRD.WaitLoadWindow('frmFilterParams')
        NCRD.SetFilter(CARDIDN=idn_card) # Берем номер идентификатора из бд, для поиска нашей карты
        NCRD.WaitLoadWindow('NCrdList')
        but_operations = Sys.Process("COLVIR").VCLObject("NCrdList").VCLObject("btnRunOperation") # Определение контекстного меню с опреациямии
        but_operations.Click()
        NCRD.FindNeedOperation("Отменить возврат") 
        NCRD.ConfirmOperation("Отменить возврат")
        NCRD.CheckOperEndWindow()
        NCRD.WaitLoadWindow('NCrdList')
        status_crd = NCRD.GetGridDataFields("NCrdList", "STAT_NAME", "CODE", "ACC_CODE", "CARDCODE") # Получаем статус карты для дальнейшей проверки
        if status_crd[0].replace("\'", '') == 'Отказановакцепте':
            # Отчетность
            NCRD.AllureReportTemplate(abs_path, name_file, "Отменить возврат", "passed", {"message": f"Карта с идентификатором {status_crd[1]} в состоянии {status_crd[0]}"},
                                         'VCLObject("NCrdList")', "Операция успешна", new_path, "passed", 1, 1)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Карта с идентификатором {status_crd[1]} в состоянии {status_crd[0]}')
        else:
            # Отчетность
            NCRD.AllureReportTemplate(abs_path, name_file, "Отменить возврат", "failed", {"message": f"Карта с идентификатором {status_crd[1]} в состоянии {status_crd[0]}"},
                                         'VCLObject("NCrdList")', "Ошибка операции", new_path, "failed", 1, 1, rm = True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Операция {status_crd[0]} не выполнена')
        Sys.Process("COLVIR").VCLObject("NCrdList").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        NCRD.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 
