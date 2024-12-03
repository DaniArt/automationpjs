from CardFramework import *

def RegisterTSEDogovor_AllDataSet():
    """ Создание карточки ТСП по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('ndeatse_table')
    for row in data_list:  
       try:
           if row['DEPO_CODE'] == 'AA6':
              name_file = f'{Ndeacrd.GetRandomNumber()}_RegisterTSEDogovor.json'  
              RegisterTSEDogovor(row['CLI_ID'], name_file)
       except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
            
def RegisterTSEDogovor(cli_id, name_file):
    """ Создание карточки ТСП """
    Ndeacrd = CardFramework()
    count = 1
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Создание карточки ТСП", f"Проверка корректности создания карточки ТСП", Ndeacrd.GetDateTimeMilli()]
    abs_path = Ndeacrd.FindAbsPathFile(name_file) # Получение абсолютного пути файла
    Ndeacrd.AddKeyValueJson(abs_path, key, value)
    def_dict = Ndeacrd.GetDefaultDict(abs_path)
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
    Ndeacrd.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", "Продукт - Корпоративные карты"]
    Ndeacrd.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    # Начало работы скрипта автотеста
    try:
        Ndeacrd.TaskInput('NDEATSE')
        Ndeacrd.WaitLoadWindow('frmFilterParams', time_await=3000)
        Ndeacrd.SetFilter(CLI_CODE=cli_id) 
        Ndeacrd.WaitLoadWindow('frmDeaTSELst', time_await=3000)
        Ndeacrd.FindNeedOperation("Отправить сообщение в ПЦ") 
        Ndeacrd.ConfirmOperation("Отправить сообщение в ПЦ")
        Ndeacrd.CheckOperEndWindow()  
        Ndeacrd.WaitLoadWindow('frmDeaTSELst', time_await=3000)
        Delay(2000)
        status_doc = Ndeacrd.GetGridDataFields("frmDeaTSELst", "STAT_NAME", "CODE") # Получаем статус документа для дальнейшей проверки
        if status_doc[0].replace("\'", '') == 'Зарегистрирован в ПЦ':
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Регистрация договора ТСП", "passed", {"message": f"Документ с номером {status_doc[1]} в состоянии {status_doc[0]}"},
                                           'VCLObject("frmDeaTSELst")', "Договор зарегистрирован", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Документ с номером {status_doc[1]} в состоянии {status_doc[0]}')
            count += 1
        else:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Регистрация договора ТСП", "failed", {"message": f"Документ с номером {status_doc[1]} в состоянии {status_doc[0]}"},
                                           'VCLObject("frmDeaTSELst")', "Договор не зарегистрирован", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Операция регистрации документа не выполнена, документ в состоянии {status_doc[0]}')
            count += 1
        Sys.Process("COLVIR").VCLObject("frmDeaTSELst").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", count, 1, rm=True) 
