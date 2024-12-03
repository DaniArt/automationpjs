from CardFramework import *

def CreateDeasalDog_AllDataSet():
    """ Создание зарплатного договора по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('ndeacrd_data')
    for row in data_list:
      try:
        if row['CLI_ID'] and row['DEASAL']:
            name_file = f'{Ndeacrd.GetRandomNumber()}_CreateDeasalDog.json'   
            form_data = CreateDeasalDog(row['DEPO_CODE'],row['VAL_CODE'],
                                       row['CLI_ID'],row['TRF_DOG'], 
                                       row['CKC_CODE'],row['DEASAL'], name_file)
            row['PRJ_CODE'] = form_data
            Ndeacrd.UpdateDatasetTableDB('ndeacrd_data', data_list)
        elif row['IDN_CARD'] is None and row['DEASAL'] is None:
            name_file = f'{Ndeacrd.GetRandomNumber()}_CreateDeasalDog.json'
            Ndeacrd.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Создание договора DEASAL", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
      except Exception as e:
          Log.Event('Возникла ошибка идем дальше')

def CreateDeasalDog(depo_code,val_code,cli_id,tarif_code,ckc_code, deasal, name_file):
    """ Создание зарплатного договора """
    result = ''
    count = 1
    Ndeacrd = CardFramework()
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Создание договора DEASAL", "Создание зарплатного договора", Ndeacrd.GetDateTimeMilli()]
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
        Ndeacrd.InputEmptyFilter()
        Ndeacrd.WaitLoadWindow('frmaNDeaSalLst')
        operation_create = Ndeacrd.FindChildField("frmaNDeaSalLst", "Name", "VCLObject('btnInsert')")
        operation_create.Click()
        doc_code = Ndeacrd.FindChildField("frmVarDtlDialog", "Name", "VCLObject('edtKeyValue')")
        doc_code.Keys(deasal)  
        LLPlayer.KeyDown(VK_RETURN, 500)
        LLPlayer.KeyUp(VK_RETURN, 500) #Отжатие кнопки ENTER, тут мы подтверждаем окно с выбором документа
        cli_code2 = Ndeacrd.FindChildField("frmaNDeaSalDtl", "Name", "VCLObject('edVAL_CODE')")
        cli_code2.Keys(val_code)
        cur_code = Ndeacrd.FindChildField("frmaNDeaSalDtl", "Name", "VCLObject('edOrgName')")
        cur_code.Keys(cli_id)
        trf_code = Ndeacrd.FindChildField("frmaNDeaSalDtl", "Name", "VCLObject('edName')")
        trf_code.Keys('TOO TEST')
        depo_code2 = Ndeacrd.FindChildField("frmaNDeaSalDtl", "Name", "VCLObject('edSRV_DEP_CODE')")
        depo_code2.Keys(depo_code)
        depo_code3 = Ndeacrd.FindChildField("frmaNDeaSalDtl", "Name", "VCLObject('edSELL_DEP_CODE')")
        depo_code3.Keys(depo_code)
        LLPlayer.KeyDown(VK_TAB, 500)
        btn_save = Ndeacrd.FindChildField("frmaNDeaSalDtl", "Name", "VCLObject('btnSave')")
        btn_save.Click()
        Ndeacrd.WaitLoadWindow('frmaNDeaSalLst')
        status_doc = Ndeacrd.GetGridDataFields("frmaNDeaSalLst", "STAT_NAME", "CODE")
        result = status_doc[1].replace("\'", '')
        if status_doc[0].replace("\'", '') == 'Введен':
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Создание договора СКС для клиента", "passed", {"message": f"Документ с номером {status_doc[1]} в состоянии {status_doc[0]}"},
                                           'VCLObject("frmaNDeaSalLst")', "Договор создан", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Документ с номером {status_doc[1]} в состоянии {status_doc[0]}')
            count += 1
        else:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Создание договора СКС для клиента", "failed", {"message": f"Документ с номером {status_doc[1]} в состоянии {status_doc[0]}"},
                                           'VCLObject("frmaNDeaSalLst")', "Договор создан", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning("Операция создания документа не выполнена")
            count += 1
        Sys.Process("COLVIR").VCLObject("frmaNDeaSalLst").Close()
        return result
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", count, 1, rm=True) 
