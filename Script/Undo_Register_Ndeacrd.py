from CardFramework import *

def UndoRegisterNdeacrd_AllDataSet():
    """ Отмена регистрации документа СКС для клиента по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:  
        if row['ITER_CODE'] == '1':
            name_file = f'{Ndeacrd.GetRandomNumber()}_UndoRegisterNdeacrd.json'  
            UndoRegisterNdeacrd(row['DOC_CODE'],name_file)
            
def UndoRegisterNdeacrd(DOC_CODE,name_file):
    """ Отмена регистрации документа СКС для клиента """
    Ndeacrd = CardFramework()
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Отмена регистрации договора СКС", "Отмена регистрации договора СКС для клиента", Ndeacrd.GetDateTimeMilli()]
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
        Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=3000)
        but_operations = Sys.Process("COLVIR").VCLObject("DeaSCAList").VCLObject("btnRunOperation") # Определение контекстного меню с опреациямии
        but_operations.Click()
        Ndeacrd.FindNeedOperation("Отмена регистрации") 
        Ndeacrd.ConfirmOperation("Отмена регистрации")
        Delay(2000)
        Ndeacrd.ConfirmOperation("При отмене регистрации будут удалены порожденные договоры РКО. Продолжить выполнение операции?")
        Delay(6000)
        Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=3000)
        status_doc = Ndeacrd.GetGridDataFields("DeaSCAList", "STATNAME", "DCL_CODENAME", "CODE") # Получаем статус документа для дальнейшей проверки
        if status_doc[0].replace("\'", '') == 'Введен':
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Отмена регистрация договора СКС для клиента", "passed", {"message": f"Документ с номером {status_doc[2]} в состоянии {status_doc[0]}"},
                                           'VCLObject("DeaSCAList")', "Договор зарегистрирован", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Документ с номером {status_doc[2]} в состоянии {status_doc[0]}')
        else:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Отмена регистрация договора СКС для клиента", "failed", {"message": f"Документ с номером {status_doc[2]} в состоянии {status_doc[0]}"},
                                           'VCLObject("DeaSCAList")', "Договор не зарегистрирован", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Операция отмены регистрации документа не выполнена, документ в состоянии {status_doc[0]}')
        Sys.Process("COLVIR").VCLObject("DeaSCAList").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 
