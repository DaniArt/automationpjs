﻿from CardFramework import *

def ChangeBlockReason_AllDataSet():
    """ Изменить причину блокировки карты по всему датасету """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:
        if row['ITER_CODE'] == '1':
            name_file = f'{NCRD.GetRandomNumber()}_ChangeBlockReason.json'   
            ChangeBlockReason(row['IDN_CARD'], name_file)

            
def ChangeBlockReason(idn_card, name_file):
    """ Изменить причину блокировки карты клиента """
    NCRD = CardFramework() 
    # Создание главной иерархии json отчета
    new_path = NCRD.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    NCRD.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Изменить причину блокировки карты", f"Изменить причину блокировки карты {idn_card}", NCRD.GetDateTimeMilli()]
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
        but_operations = NCRD.FindChildField("NCrdList", "Name", "VCLObject('btnRunOperation')")
        but_operations.Click()
        NCRD.FindNeedOperation("Изменить причину блокировки") 
        NCRD.ConfirmOperation("Изменить причину блокировки")
        reason = NCRD.FindChildField("frmDynamicDialog", "Name", "VCLObject('REASON')")
        reason.Keys('41')
        describe = NCRD.FindChildField("frmDynamicDialog", "Name", "VCLObject('REASON_DSCR')")
        describe.Keys('TEST')
        blockway = NCRD.FindChildField("frmDynamicDialog", "Name", "VCLObject('VERIFY_TYPE')")
        blockway.Keys('3')
        btn_ok = NCRD.FindChildField("frmDynamicDialog", "Name", "VCLObject('btnOK')")
        btn_ok.Click()
        NCRD.CheckOperEndWindow()
        NCRD.WaitLoadWindow('NCrdList')
        status_crd = NCRD.GetGridDataFields("NCrdList", "BLOCKREASON", "CODE") # Получаем статус карты для дальнейшей проверки
        if status_crd[0].replace("\'", '') == '41':
            # Отчетность
            NCRD.AllureReportTemplate(abs_path, name_file, "Изменить причину блокировки", "passed", {"message": f"Карта с идентификатором {status_crd[1]} изменена причина блокировки"},
                                         'VCLObject("NCrdList")', "Причина изменена", new_path, "passed", 1, 1, rm = True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Карта с идентификатором {status_crd[1]} изменена причина блокировки')
        else:
            # Отчетность
            NCRD.AllureReportTemplate(abs_path, name_file, "Изменить причину блокировки", "failed", {"message": f"Карта с идентификатором {status_crd[1]} операция не выполнена"},
                                         'VCLObject("NCrdList")', "Ошибка операции", new_path, "failed", 1, 1, rm = True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Карта с идентификатором {status_crd[1]} операция не выполнена')
        Sys.Process("COLVIR").VCLObject("NCrdList").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        NCRD.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 
