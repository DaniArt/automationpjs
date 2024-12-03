from CardFramework import *

def UndoSendCardAccept_AllDataSet():
    """ Отмена отправки на акцептование карты клиента по всему датасету """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
        try:
            if row['IDN_CARD'] and row['DEPO_CODE'] == 'AA6':
                name_file = f'{NCRD.GetRandomNumber()}_UndoSendCardAccept.json'
                UndoSendCardAccept(row['IDN_CARD'],row['CLI_ID'],name_file)
            elif row['IDN_CARD'] is None and row['DEPO_CODE'] == 'AA6':
                name_file = f'{NCRD.GetRandomNumber()}_UndoSendCardAccept.json'
                NCRD.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Отмена отправки на акцептование карты", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
            
def UndoSendCardAccept(idn_card,cl_code,name_file):
    """ Отмена отправки на акцептование карты клиента """
    NCRD = CardFramework()
    # Создание главной иерархии json отчета
    new_path = NCRD.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    NCRD.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Отмена отправки на акцептование карты", f"Отмена отправки на акцептование карты {idn_card}", NCRD.GetDateTimeMilli()]
    abs_path = NCRD.FindAbsPathFile(name_file) # Получение абсолютного пути файла
    NCRD.AddKeyValueJson(abs_path, key, value)
    def_dict = NCRD.GetDefaultDict(abs_path)
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
    NCRD.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", "Продукт - КартаКарта"]
    NCRD.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    # Начало работы скрипта автотеста
    try:   
      NCRD.TaskInput('NCRD')
      NCRD.WaitLoadWindow('frmFilterParams')
      NCRD.SetFilter(CLI_code=cl_code,CARDIDN=idn_card) # Вставляем номер идентификатора из бд, для поиска нашей карты
      NCRD.WaitLoadWindow('NCrdList', time_await=3000)
      but_operations = Sys.Process("COLVIR").VCLObject("NCrdList").VCLObject("btnRunOperation") # Определение контекстного меню с опреациямии
      but_operations.Click()
      NCRD.FindNeedOperation("Отменить отправку") 
      NCRD.ConfirmOperation("Отменить отправку")
      NCRD.WaitLoadWindow('NCrdList', time_await=6000)
      OperJrn = Sys.Process("COLVIR").VCLObject("NCrdList").VCLObject("btnOperJrn") # Определение контекстного меню с опреациямии
      OperJrn.Click()    
      Delay(3000)
      NCRD.WaitLoadWindow('frmOperJournal', time_await=3000)
      status_crd = NCRD.GetGridDataFields("frmOperJournal", "NAME") # Получаем статус карты для дальнейшей проверки
      if status_crd[0].replace("\'", '') == 'Отменитьотправку':
        # Отчетность
        NCRD.AllureReportTemplate(abs_path, name_file, "Отмена отправки на акцептование карты клиента", "passed", {"message": f"Карта с идентификатором {idn_card} в состоянии {status_crd[0]}"},
                                     'VCLObject("frmOperJournal")', "Отправка на акцепт отменена", new_path, "passed", 1, 1, rm = True)
        # --------------------------------------------------------------------------------------------------------------------------
        Log.Checkpoint(f'Карта с идентификатором {idn_card} в состоянии {status_crd[0]}')
      else:
        # Отчетность
        NCRD.AllureReportTemplate(abs_path, name_file, "Отмена отправки на акцептование карты клиента", "failed", {"message": f"Операция отмены отправки не выполнена"},
                                     'VCLObject("frmOperJournal")', "Отмена отправки неуспешна", new_path, "failed", 1, 1, rm = True)
        # --------------------------------------------------------------------------------------------------------------------------
        Log.Warning(f'Операция отмены отправки не выполнена')
      Sys.Process("COLVIR").VCLObject("frmOperJournal").Close()
      Sys.Process("COLVIR").VCLObject("NCrdList").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        NCRD.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", count, 1, rm=True) 
