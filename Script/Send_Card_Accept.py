from CardFramework import *

def SendCardAccept_AllDataSet():
    """ Отправка на акцептование карты клиента по всему датасету """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
        try:
            if row['IDN_CARD'] and row['DEPO_CODE'] == 'AA6':
                name_file = f'{NCRD.GetRandomNumber()}_SendCardAccept.json'  
                form_data = SendCardAccept(row['IDN_CARD'],row['CLI_ID'],name_file)
                row['ACC_CRD'] = form_data
                NCRD.UpdateDatasetTableDB('crdreq_data', data_list)
            elif row['IDN_CARD'] is None and row['DEPO_CODE'] == 'AA6':
                name_file = f'{NCRD.GetRandomNumber()}_SendCardAccept.json'
                NCRD.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Отправка на акцептование карты", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
            
def SendCardAccept(idn_card,cl_code,name_file):
    """ Отправка на акцептование карты клиента """
    acc_crd = ''
    count = 1
    NCRD = CardFramework()
    # Создание главной иерархии json отчета
    new_path = NCRD.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    NCRD.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Отправка на акцептование карты", f"Отправка на акцептование карты {idn_card}", NCRD.GetDateTimeMilli()]
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
      NCRD.WaitLoadWindow('NCrdList')
      but_operations = Sys.Process("COLVIR").VCLObject("NCrdList").VCLObject("btnRunOperation") # Определение контекстного меню с опреациямии
      but_operations.Click()
      NCRD.FindNeedOperation("Отправить на акцептование") 
      NCRD.ConfirmOperation("Отправить на акцептование")
      Delay(1000)
      Sys.Process("COLVIR").VCLObject("frmDFSimpleEngine").VCLObject("LayoutFrame").CheckBox("Да").Click()
      Delay(1000)
      epin_checkbox = NCRD.FindChildField("frmDFSimpleEngine", "Name", "CheckBox('Да.')")
      epin_checkbox.Click()
      Delay(1000)
      btn_ok = NCRD.FindChildField("frmDFSimpleEngine", "Name", "VCLObject('btnOK')")
      btn_ok.Click()
      NCRD.ConfirmOperation("Изменить реквизиты расчетов по договору на счет карты по-умолчанию?")
      NCRD.ConfirmOperation("У договора СКС нет счетов. Счет будет создан автоматически, продолжить?")
      NCRD.WaitLoadWindow('NCrdList')
      status_crd = NCRD.GetGridDataFields("NCrdList", "STAT_NAME", "CODE", "ACC_CODE") # Получаем статус карты для дальнейшей проверки
      acc_crd = status_crd[2].replace("\'", '')
      if status_crd[0].replace("\'", '') == 'Переданонаакцептование':
        # Отчетность
        NCRD.AllureReportTemplate(abs_path, name_file, "Отправка на акцептование карты клиента", "passed", {"message": f"Карта с идентификатором {status_crd[1]} в состоянии {status_crd[0]}"},
                                     'VCLObject("NCrdList")', "Карта отправлена на акцептование", new_path, "passed", 1, 1, rm = True)
        # --------------------------------------------------------------------------------------------------------------------------
        Log.Checkpoint(f'Карта с идентификатором {status_crd[1]} в состоянии {status_crd[0]}')
        count += 1
      else:
        # Отчетность
        NCRD.AllureReportTemplate(abs_path, name_file, "Отправка на акцептование карты клиента", "failed", {"message": f"Операция {status_crd[0]} не выполнена"},
                                     'VCLObject("NCrdList")', "Карта не отправлена на акцепт", new_path, "failed", 1, 1, rm = True)
        # --------------------------------------------------------------------------------------------------------------------------
        Log.Warning(f'Операция {status_crd[0]} не выполнена')
        count += 1
      Sys.Process("COLVIR").VCLObject("NCrdList").Close()
      return acc_crd
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        NCRD.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", count, 1, rm=True) 