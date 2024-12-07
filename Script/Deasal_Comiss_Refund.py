﻿from CardFramework import *

def DeasalComissRefund_AllDataSet():
    """ Возврат переплаченной комиссии по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('ndeacrd_data')
    for row in data_list:  
        try:
            if row['PRJ_CODE'] and row['DEASAL']:
                name_file = f'{Ndeacrd.GetRandomNumber()}_DeasalComissRefund.json'  
                DeasalComissRefund(row['CLI_ID'], row['PRJ_CODE'],name_file)
            elif row['PRJ_CODE'] is None and row['DEASAL'] is None:
                name_file = f'{Ndeacrd.GetRandomNumber()}_DeasalComissRefund.json'
                Ndeacrd.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Возврат переплаченной комиссии", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
            
def DeasalComissRefund(cli_code, prj_code, name_file):
    """ Возврат переплаченной комиссии """
    Ndeacrd = CardFramework()
    count = 1
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Возврат переплаченной комиссии", f"Операция возврата переплаченной комиссии проекта {prj_code}", Ndeacrd.GetDateTimeMilli()]
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
        Ndeacrd.FindNeedOperation("Возврат переплаченной комиссии") 
        Ndeacrd.ConfirmOperation("Возврат переплаченной комиссии")
        Ndeacrd.ErrorMessageHandler()
        Ndeacrd.CheckOperEndWindow()
        Delay(2000)
        status_doc = Ndeacrd.GetGridDataFields("frmaNDeaSalLst", "STAT_NAME", "CODE") # Получаем статус документа для дальнейшей проверки
        if status_doc[0].replace("\'", '') == 'Зарегистрирован':
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возврат переплаченной комиссии", "passed", {"message": f"Возврат переплаченной комиссии по проекту {status_doc[1]} выполнена успешно!"},
                                           'VCLObject("frmaNDeaSalLst")', "Комиссия возвращена", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Возврат переплаченной комиссии по проекту {status_doc[1]} выполнена успешно!')
            count += 1
        else:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возврат переплаченной комиссии", "failed", {"message": f"Ошибка при попытке возврата комиссии с {status_doc[1]}"},
                                           'VCLObject("frmaNDeaSalLst")', "Ошибка возврата", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Ошибка при попытке возврата комиссии с {status_doc[1]}')
            count += 1
        Sys.Process("COLVIR").VCLObject("frmaNDeaSalLst").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", count, 1, rm=True)
