from CardFramework import *

def ChangeCardInfo_AllDataSet():
    """ Изменение данных карты """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('travel_data')
    for row in data_list:
        try:
            if row['IDN_CARD'] and row['ITER_CODE'] == '1':
                name_file = f'{NCRD.GetRandomNumber()}_ChangeCardInfo.json'   
                ChangeCardInfo(row['IDN_CARD'], name_file)
            elif row['IDN_CARD'] is None and row['ITER_CODE'] == '1':
                name_file = f'{NCRD.GetRandomNumber()}_ChangeCardInfo.json'
                NCRD.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Изменение данных карты Travel", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')

            
def ChangeCardInfo(idn_card, name_file):
    NCRD = CardFramework() 
    # Создание главной иерархии json отчета
    new_path = NCRD.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    NCRD.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Изменение данных карты", f"Операция Изменение данных карты {idn_card}", NCRD.GetDateTimeMilli()]
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
        NCRD.FindNeedOperation("Изменение данных карты") 
        NCRD.ConfirmOperation("Изменение данных карты")
        ProjCode = NCRD.FindChildField("frmDFSimpleEngine", "Name", "Window('TExEdit', ' ', 4)")
        ProjCode.Keys('ALM2013411')
        ok_btn = NCRD.FindChildField("frmDFSimpleEngine", "Name", "VCLObject('btnOK')")
        ok_btn.Click()
        NCRD.CheckOperEndWindow()
        NCRD.WaitLoadWindow('NCrdList')
        oper_jrn = NCRD.FindChildField("NCrdList", "Name", "VCLObject('btnOperJrn')")
        oper_jrn.Click()
        status_crd = NCRD.GetGridDataFields("NCrdList", "NAME", "DOCNUM") # Получаем статус карты для дальнейшей проверки
        if status_crd[0].replace("\'", '') == 'Изменениеданныхкарты':
            # Отчетность
            NCRD.AllureReportTemplate(abs_path, name_file, "Изменение данных карты", "passed", {"message": f"Карта с идентификатором {status_crd[1]} данные изменены"},
                                         'VCLObject("frmOperJournal")', "Данные изменены", new_path, "passed", 1, 1, rm = True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Карта с идентификатором {status_crd[1]} данные изменены')
        else:
            # Отчетность
            NCRD.AllureReportTemplate(abs_path, name_file, "Изменение данных карты", "failed", {"message": f"Карта с идентификатором {status_crd[1]} данные не изменены"},
                                         'VCLObject("frmOperJournal")', "Нету изменении", new_path, "failed", 1, 1, rm = True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Карта с идентификатором {status_crd[1]} данные не изменены')
        Sys.Process("COLVIR").VCLObject("NCrdList").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        NCRD.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 

