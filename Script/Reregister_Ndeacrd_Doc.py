﻿from CardFramework import *

def ReregisterNdeacrdDoc_AllDataSet():
    """ Перерегистрация документа СКС для клиента по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:  
      try:
          if row['DOC_CODE']:
            name_file = f'{Ndeacrd.GetRandomNumber()}_RegisterNdeacrdCKC.json'  
            form_data = ReregisterNdeacrdDoc(row['DOC_CODE'],name_file)
            row['ACC_CRD'] = form_data
            Ndeacrd.UpdateDatasetTableDB('ckcdoc_data', data_list)
          elif row['DOC_CODE'] is None:
                name_file = f'{Ndeacrd.GetRandomNumber()}_ReregisterNdeacrdDoc.json'
                Ndeacrd.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Регистрация договора СКС", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
      except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
            
def ReregisterNdeacrdDoc(DOC_CODE,name_file):
    """ Перерегистрация документа СКС для клиента """
    form_data  = ''
    Ndeacrd = CardFramework()
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Перерегистрация договора СКС", "Перерегистрация договора СКС для клиента", Ndeacrd.GetDateTimeMilli()]
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
        Ndeacrd.WaitLoadWindow('DeaSCAList')
        but_operations = Sys.Process("COLVIR").VCLObject("DeaSCAList").VCLObject("btnRunOperation") # Определение контекстного меню с опреациямии
        but_operations.Click()
        Ndeacrd.FindNeedOperation("Регистрация") 
        Ndeacrd.ConfirmOperation("Регистрация")
        Delay(2000)
        Ndeacrd.ConfirmOperation("У договора СКС нет счетов. Счет будет создан автоматически, продолжить?")
        Ndeacrd.CheckOperEndWindow()
        Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=3000)
        click_name = Ndeacrd.FindChildField("DeaSCAList", "Name", "TextObject('Зарегистрирован')")
        click_name.Click() # Сделано это, для того что бы избежать пустого окна при вызове формы с 4 кнопки
        status_doc = Ndeacrd.GetGridDataFields("DeaSCAList", "STATNAME", "DCL_CODENAME", "CODE") # Получаем статус документа для дальнейшей проверки
        if status_doc[0].replace("\'", '') == 'Зарегистрирован':
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Регистрация договора СКС для клиента", "passed", {"message": f"Документ с номером {status_doc[2]} в состоянии {status_doc[0]}"},
                                           'VCLObject("DeaSCAList")', "Договор зарегистрирован", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Документ с номером {status_doc[2]} в состоянии {status_doc[0]}')
        else:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Регистрация договора СКС для клиента", "failed", {"message": f"Документ с номером {status_doc[2]} в состоянии {status_doc[0]}"},
                                           'VCLObject("DeaSCAList")', "Договор не зарегистрирован", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Операция регистрации документа не выполнена, документ в состоянии {status_doc[0]}')       
        browse_btn = Ndeacrd.FindChildField("DeaSCAList", "Name", "VCLObject('btnBrowse')")
        browse_btn.Click()
        Ndeacrd.WaitLoadWindow('DeaSCADetail', time_await=3000)
        click_window = Ndeacrd.FindChildField("DeaSCADetail", "Name", "VCLObject('pnlObject')") # Захват окна
        click_window.Click()
        GridDea = Ndeacrd.GetGridDataFields("DeaSCADetail", "CLI_ACC_CODE", need_tab='MainQuery')# Получаем статус документа для дальнейшей проверки
        form_data = GridDea[0].replace("\'", '')
        Sys.Process("COLVIR").VCLObject("DeaSCAList").Close()
        return form_data
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 