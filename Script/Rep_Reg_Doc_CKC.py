from CardFramework import *

def RepRegDocCKC_AllDataSet():
    """Повторная регистрация документа СКС для клиента по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('crdreq_data')
    for row in data_list:  
        try:
            if row['DOC_CODE'] and row['DEPO_CODE'] == 'AA6':
                name_file = f'{Ndeacrd.GetRandomNumber()}_RepRegDocCKC.json'  
                RegistrDocCKC(row['DOC_CODE'],name_file)
            elif row['DOC_CODE'] is None and row['DEPO_CODE'] == 'AA6':
              name_file = f'{Ndeacrd.GetRandomNumber()}_RepRegDocCKC.json'
              Ndeacrd.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Повторная регистрация договора СКС для клиента", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
            
def RegistrDocCKC(DOC_CODE,name_file):
    """ Регистрация документа СКС для клиента """
    Ndeacrd = CardFramework()
    count = 1
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Повторная регистрация договора СКС для клиента", f"Повторная регистрация договора {DOC_CODE} СКС", Ndeacrd.GetDateTimeMilli()]
    abs_path = Ndeacrd.FindAbsPathFile(name_file) # Получение абсолютного пути файла
    Ndeacrd.AddKeyValueJson(abs_path, key, value)
    def_dict = Ndeacrd.GetDefaultDict(abs_path)
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
    Ndeacrd.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", "Продукт - КартаКарта"]
    Ndeacrd.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    # Начало работы скрипта автотеста
    try:
      Ndeacrd.TaskInput('NDEACRD')
      Ndeacrd.WaitLoadWindow('frmFilterParams')
      Ndeacrd.SetFilter(CODE=DOC_CODE) # Вставляем номер документа из бд, для поиска нашего заведенного договора
      Ndeacrd.WaitLoadWindow('DeaSCAList')
      but_operations = Sys.Process("COLVIR").VCLObject("DeaSCAList").VCLObject("btnRunOperation") # Определение контекстного меню с опреациямии
      but_operations.Click()
      Ndeacrd.FindNeedOperation("Регистрация") 
      Ndeacrd.ConfirmOperation("Регистрация")
      Delay(2000)
      Ndeacrd.ConfirmOperation("У договора СКС нет счетов. Счет будет создан автоматически, продолжить?")
      Delay(2000)
      Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=3000)
      status_doc = Ndeacrd.GetGridDataFields("DeaSCAList", "STATNAME", "DCL_CODENAME", "CODE") # Получаем статус документа для дальнейшей проверки
      if status_doc[0].replace("\'", '') == 'Зарегистрирован':
        # Отчетность
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Повторная регистрация договора СКС для клиента", "passed", {"message": f"Документ с номером {status_doc[2]} в состоянии {status_doc[0]}"},
                                       'VCLObject("DeaSCAList")', "Договор зарегистрирован", new_path, "passed", 1, 1, rm=True)
        # --------------------------------------------------------------------------------------------------------------------------
        Log.Checkpoint(f'Документ с номером {status_doc[2]} в состоянии {status_doc[0]}')
        count += 1
      else:
        # Отчетность
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Повторная регистрация договора СКС для клиента", "failed", {"message": f"Документ с номером {status_doc[2]} в состоянии {status_doc[0]}"},
                                       'VCLObject("DeaSCAList")', "Договор не зарегистрирован", new_path, "failed", 1, 1, rm=True)
        # --------------------------------------------------------------------------------------------------------------------------
        Log.Warning(f'Операция регистрации документа не выполнена, документ в состоянии {status_doc[0]}')
        count += 1
      Sys.Process("COLVIR").VCLObject("DeaSCAList").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", count, 1, rm=True) 
