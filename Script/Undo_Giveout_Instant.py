﻿from CardFramework import *

def UndoGiveoutInstant_AllDataSet():
    """ Отвязка карты моментального выпуска к договору СКС по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
        try:
            if row['DOC_CODE'] and row['DEPO_CODE'] == 'AA6':
                name_file = f'{Ndeacrd.GetRandomNumber()}_UndoGiveoutInstant.json' 
                UndoGiveoutInstant(row['PRODUCT'],row['CLI_ID'],row['DOC_CODE'],row['REG_DATE'],name_file)
            elif row['DOC_CODE'] is None and row['DEPO_CODE'] == 'AA6':
              name_file = f'{Ndeacrd.GetRandomNumber()}_UndoGiveoutInstant.json'
              Ndeacrd.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Отмена выдачи карты моментального выпуска", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
             
def UndoGiveoutInstant(product,cl_code,doc_code,reg_date,name_file):
    """ Отвязка карты моментального выпуска к договору СКС """
    Ndeacrd = CardFramework()
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Отмена выдачи карты моментального выпуска", f"Отмена подвязки карты {product} от договора {doc_code}", Ndeacrd.GetDateTimeMilli()]
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
      Ndeacrd.WaitLoadWindow('frmFilterParams', time_await=6000)
      Ndeacrd.SetFilter(CLI_code=cl_code ,CODE=doc_code) # Вставляем номер документа из бд, для поиска нашего заведенного договора
      Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=6000)
      but_operations = Sys.Process("COLVIR").VCLObject("DeaSCAList").VCLObject("btnRunOperation") # Определение контекстного меню с опреациямии
      but_operations.Click()
      Ndeacrd.FindNeedOperation("Отмена выдачи карты мом.вып.") 
      Ndeacrd.ConfirmOperation("Отмена выдачи карты мом.вып.")
      Delay(2000)
      Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=6000)
      OperJrn = Sys.Process("COLVIR").VCLObject("DeaSCAList").VCLObject("btnOperJrn") # Определение контекстного меню с опреациямии
      OperJrn.Click()    
      Delay(3000)
      Ndeacrd.WaitLoadWindow('frmOperJournal', time_await=3000)
      form_data = Ndeacrd.GetGridDataFields("frmOperJournal", "NAME")
      if form_data[0].replace("\'", "") == 'Отменавыдачикартымом.вып.': # Проверка состояния документа
        # Отчетность
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Отмена выдачи карты моментального выпуска", "passed", {"message": f"Продукт с идентификатором {product} был отвязан"},
                                       'VCLObject("frmOperJournal")', "Карта отвязана", new_path, "passed", 1, 1, rm=True)
        # --------------------------------------------------------------------------------------------------------------------------
        Log.Checkpoint(f'Продукт с идентификатором {product} был отвязан')
      else:
        # Отчетность
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Отмена выдачи карты моментального выпуска", "failed", {"message": f"Операция по отвязке карты не выполнена"},
                                       'VCLObject("frmOperJournal")', "Карта не отвязана", new_path, "failed", 1, 1, rm=True)
        # --------------------------------------------------------------------------------------------------------------------------
        Log.Warning(f'Операция по отвязке карты не выполнена')
      Sys.Process("COLVIR").VCLObject("frmOperJournal").Close()
      Sys.Process("COLVIR").VCLObject("DeaSCAList").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 