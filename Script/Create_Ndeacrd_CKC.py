from CardFramework import *

def CreateNdeacrdCKC_AllDataSet():
    """ Создание документа СКС для клиента по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:
      try:
          if row['ITER_CODE'] == '1':
            name_file = f'{Ndeacrd.GetRandomNumber()}_CreateNdeacrdCKC.json'   
            form_data = CreateNdeacrdCKC(row['DEPO_CODE'],row['VAL_CODE'],
                                       row['CLI_ID'],row['TARIF_CODE'], 
                                       row['TRF_DOG'],name_file)
            row['DOC_CODE'] = form_data
            Ndeacrd.UpdateDatasetTableDB('ckcdoc_data', data_list)
      except Exception as e:
          Log.Event('Возникла ошибка идем дальше')

def CreateNdeacrdCKC(depo_code,val_code,cli_id,tarif_code,ckc_code,name_file):
    """ Создание договора СКС для клиента """
    form_data = ''
    Ndeacrd = CardFramework()
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Создание договора СКС", "Создание договора СКС для клиента", Ndeacrd.GetDateTimeMilli()]
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
        Ndeacrd.InputEmptyFilter()
        Ndeacrd.WaitLoadWindow('DeaSCAList')
        operation_create = Ndeacrd.FindChildField("DeaSCAList", "Name", "VCLObject('btnInsert')")
        operation_create.Click()
        doc_code = Ndeacrd.FindChildField("frmVarDtlDialog", "Name", "VCLObject('edtKeyValue')")
        doc_code.Keys(ckc_code)  
        LLPlayer.KeyDown(VK_RETURN, 500)
        LLPlayer.KeyUp(VK_RETURN, 500) #Отжатие кнопки ENTER, тут мы подтверждаем окно с выбором документа
        depo_name = Ndeacrd.FindChildField("DeaSCADetail", "Name", "VCLObject('edDEP_CODE')")
        depo_name.Keys("^a")
        depo_name.Keys(depo_code)
        cli_code2 = Ndeacrd.FindChildField("DeaSCADetail", "Name", "VCLObject('edCLI_CODE')")
        cli_code2.Keys(cli_id)
        cur_code = Ndeacrd.FindChildField("DeaSCADetail", "Name", "VCLObject('edVAL_CODE')")
        cur_code.Keys(val_code)
        trf_code = Ndeacrd.FindChildField("DeaSCADetail", "Name", "VCLObject('edTRF_CODE')")
        trf_code.Keys(tarif_code)
        depo_field = Ndeacrd.FindChildField("DeaSCADetail", "Name", "PageTab('Подразделения')")
        depo_field.Click() 
        depo_code2 = Ndeacrd.FindChildField("DeaSCADetail", "Name", "VCLObject('edSRV_DEP_CODE')")
        depo_code2.Keys(depo_code)
        depo_code3 = Ndeacrd.FindChildField("DeaSCADetail", "Name", "VCLObject('edSELL_DEP_CODE')")
        depo_code3.Keys(depo_code)
        LLPlayer.KeyDown(VK_TAB, 500)
        btn_save = Ndeacrd.FindChildField("DeaSCADetail", "Name", "VCLObject('btnSave')")
        btn_save.Click()
        Ndeacrd.WaitLoadWindow('DeaSCAAccDtl')
        Sys.Process("COLVIR").VCLObject("DeaSCAAccDtl").Close()
        Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=3000)
        click_name = Ndeacrd.FindChildField("DeaSCAList", "Name", "TextObject('Введен')")
        click_name.Click() # Сделано это, для того что бы избежать пустого окна при вызове формы с 4 кнопки
        status_doc = Ndeacrd.GetGridDataFields("DeaSCAList", "STATNAME", "DCL_CODENAME", "CODE")
        form_data = status_doc[2].replace("\'", '')
        if status_doc[0].replace("\'", '') == 'Введен':
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Создание договора СКС для клиента", "passed", {"message": f"Документ с номером {status_doc[2]} в состоянии {status_doc[0]}"},
                                           'VCLObject("DeaSCAList")', "Договор создан", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Документ с номером {status_doc[2]} в состоянии {status_doc[0]}')
        else:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Создание договора СКС для клиента", "failed", {"message": f"Документ с номером {status_doc[2]} в состоянии {status_doc[0]}"},
                                           'VCLObject("DeaSCAList")', "Договор создан", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning("Операция создания документа не выполнена")
        Sys.Process("COLVIR").VCLObject("DeaSCAList").Close()
        return form_data
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 
