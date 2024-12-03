from CardFramework import *

def CancelDeasalRegister_AllDataSet():
    """ Отмена регистрации зарплатного проекта по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('ndeacrd_data')
    for row in data_list: 
        try: 
            if row['PRJ_CODE'] and row['DEASAL']:
                name_file = f'{Ndeacrd.GetRandomNumber()}_CancelDeasalRegister.json'  
                CancelDeasalRegister(row['CLI_ID'], row['PRJ_CODE'],name_file)
            elif row['PRJ_CODE'] is None and row['DEASAL'] is None:
                name_file = f'{Ndeacrd.GetRandomNumber()}_CancelDeasalRegister.json'
                Ndeacrd.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Отмена регистрации зарплатного проекта", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
            
def CancelDeasalRegister(cli_code, prj_code, name_file):
    """ Отмена регистрации зарплатного проекта """
    Ndeacrd = CardFramework()
    count = 1 
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Отмена регистрации зарплатного проекта", f"Отмена регистрации зарплатного проекта {prj_code}", Ndeacrd.GetDateTimeMilli()]
    abs_path = Ndeacrd.FindAbsPathFile(name_file) # Получение абсолютного пути файла
    Ndeacrd.AddKeyValueJson(abs_path, key, value)
    def_dict = Ndeacrd.GetDefaultDict(abs_path)
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
    Ndeacrd.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", "Зарплатные договора"]
    Ndeacrd.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    # Начало работы скрипта автотеста
    try:
        Ndeacrd.TaskInput('DEASAL')
        Ndeacrd.WaitLoadWindow('frmFilterParams', time_await=3000)
        Ndeacrd.SetFilter(CLI_CODE=cli_code, PRJ_CODE=prj_code) # Вставляем номер документа из бд, для поиска нашего заведенного договора
        Delay(30000)
        Ndeacrd.WaitLoadWindow('frmaNDeaSalLst', time_await=30000)
        but_operations = Sys.Process("COLVIR").VCLObject("frmaNDeaSalLst").VCLObject("btnRunOperation") # Определение контекстного меню с опреациямии
        but_operations.Click()
        Ndeacrd.FindNeedOperation("Отмена регистрации") 
        Ndeacrd.ConfirmOperation("Отмена регистрации")
        Delay(2000)
        status_doc = Ndeacrd.GetGridDataFields("frmaNDeaSalLst", "STAT_NAME", "CODE") # Получаем статус документа для дальнейшей проверки
        if status_doc[0].replace("\'", '') == 'Введен':
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Отмена регистрации зарплатного проекта", "passed", {"message": f"Документ с номером {status_doc[1]} в состоянии {status_doc[0]}"},
                                           'VCLObject("frmaNDeaSalLst")', "Договор отменен", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            count += 1
            Log.Checkpoint(f'Документ с номером {status_doc[1]} в состоянии {status_doc[0]}')
        else:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Отмена регистрации зарплатного проекта", "failed", {"message": f"Документ с номером {status_doc[1]} в состоянии {status_doc[0]}"},
                                           'VCLObject("frmaNDeaSalLst")', "Договор не отменен", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            count += 1
            Log.Warning(f'Отмена регистрации документа не выполнена, документ в состоянии {status_doc[0]}')
        Sys.Process("COLVIR").VCLObject("frmaNDeaSalLst").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла ошибка по проекту {prj_code}"},
                                     'desktop', None, new_path, "failed", count, 1, rm=True)