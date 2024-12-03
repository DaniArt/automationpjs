from CardFramework import *

def UndoTransferPS_AllDataSet():
    """ Прекратить обслуживание карты клиента в ПС по всему датасету """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:
        if row['ITER_CODE'] == '1':
            name_file = f'{NCRD.GetRandomNumber()}_UndoTransferPS.json'   
            UndoTransferPS(row['IDN_CARD'], name_file)

            
def UndoTransferPS(idn_card, name_file):
    """ Прекратить обслуживание карты клиента в ПС """
    NCRD = CardFramework() 
    # Создание главной иерархии json отчета
    new_path = NCRD.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    NCRD.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Блокировка пластиковой карты", f"Блокировка пластиковой карты {idn_card}", NCRD.GetDateTimeMilli()]
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
        NCRD.FindNeedOperation("Прекратить обслуживание в ПС") 
        NCRD.ConfirmOperation("Прекратить обслуживание в ПС")
        NCRD.CheckOperEndWindow()
        NCRD.WaitLoadWindow('NCrdList')
        oper_jrn = NCRD.FindChildField("NCrdList", "Name", "VCLObject('btnOperJrn')")
        oper_jrn.Click()
        status_crd = NCRD.GetGridDataFields("NCrdList", "NAME", "DOCNUM") # Получаем статус карты для дальнейшей проверки
        if status_crd[0].replace("\'", '') == 'ПрекратитьобслуживаниевПС':
            # Отчетность
            NCRD.AllureReportTemplate(abs_path, name_file, "Прекратить обслуживание в ПС", "passed", {"message": f"Карта с идентификатором {status_crd[1]} прекращена обслуживание в ПС"},
                                         'VCLObject("frmOperJournal")', "Переведена в ПС", new_path, "passed", 1, 1, rm = True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Карта с идентификатором {status_crd[1]} прекращена обслуживание в ПС')
        else:
            # Отчетность
            NCRD.AllureReportTemplate(abs_path, name_file, "Прекратить обслуживание в ПС", "failed", {"message": f"Карта с идентификатором {status_crd[1]} не прекращена в ПС"},
                                         'VCLObject("frmOperJournal")', "Не переведена", new_path, "failed", 1, 1, rm = True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Карта с идентификатором {status_crd[1]} не прекращена в ПС')
        Sys.Process("COLVIR").VCLObject("NCrdList").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        NCRD.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 

