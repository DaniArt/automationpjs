from CardFramework import *

def CreateTSEDevice_AllDataSet():
    """ Создание устройства ТСП по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('ndeatse_table')
    for row in data_list:  
        try:
            if row['DEPO_CODE'] == 'AA6':
                name_file = f'{Ndeacrd.GetRandomNumber()}_CreateTSEDevice.json'  
                CreateTSEDevice(row['CLI_ID'], row['PRODUCT'], row['AMOUNT'], name_file)
            
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
            
def CreateTSEDevice(cli_id, product, amount, name_file):
    """ Создание устройства ТСП """
    Ndeacrd = CardFramework()
    count = 1
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Создание устройства ТСП", f"Проверка корректности создания устройства ТСП", Ndeacrd.GetDateTimeMilli()]
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
        Ndeacrd.TaskInput('NTSE')
        Delay(120000)
        Ndeacrd.WaitLoadWindow('frmTSETreeLst', time_await=6000)
        operation_create = Ndeacrd.FindChildField("frmTSETreeLst", "Name", "VCLObject('btnInsert')")
        operation_create.Click()
        Delay(5000)
        Ndeacrd.WaitLoadWindow('frmTSETreeDtl', time_await=6000)
        tsp = Ndeacrd.FindChildField("frmTSETreeDtl", "Name", "VCLObject('edCODE')")
        tsp.Keys(cli_id)
        tsp_name = Ndeacrd.FindChildField("frmTSETreeDtl", "Name", "VCLObject('edLONGNAME')")
        tsp_name.Keys('TestName')
        lng_name = Ndeacrd.FindChildField("frmTSETreeDtl", "Name", "VCLObject('edLONGNAMELAT')")
        lng_name.Keys('TestName')
        cli_code = Ndeacrd.FindChildField("frmTSETreeDtl", "Name", "VCLObject('edtOrgName')")
        cli_code.Keys(cli_id)
        LLPlayer.KeyDown(VK_RETURN, 500)
        LLPlayer.KeyUp(VK_RETURN, 500)
        save_btn = Ndeacrd.FindChildField("frmTSETreeDtl", "Name", "VCLObject('btnSave')")
        save_btn.Click()
        Delay(150000)
        Ndeacrd.CheckOperEndWindow()
        Delay(2000)
        Ndeacrd.WaitLoadWindow('frmTSETreeLst', time_await=3000)
        find_btn = Ndeacrd.FindChildField("frmTSETreeLst", "Name", "VCLObject('btnFind')")
        find_btn.Click()
        find_value = Ndeacrd.FindChildField("frmFindDlg", "Name", "VCLObject('edValue')")
        find_value.Click()
        find_btn.Keys(cli_id)
        ok_btn = Ndeacrd.FindChildField("frmFindDlg", "Name", "VCLObject('btnOK')")
        ok_btn.Click()
        go_to = Ndeacrd.FindChildField("frmTreeFndDialog", "Name", "VCLObject('btnOk')")
        go_to.Click()   
        Ndeacrd.WaitLoadWindow('frmTSETreeDtl', time_await=3000)
        status_doc = Ndeacrd.GetGridDataFields("frmTSETreeDtl", "CODE") # Получаем статус документа для дальнейшей проверки
        if status_doc[0].replace("\'", '') == cli_id:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Подвзяка устройства ТСП", "passed", {"message": f"Устройство {status_doc[0]} успешно создано!"},
                                           'VCLObject("frmTSETreeDtl")', "Устройство создано", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Устройство {status_doc[0]} успешно создано!')
            count += 1
        else:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Подвзяка устройства ТСП", "failed", {"message": f"Ошибка! Устройство для ЮЛ {cli_id} не было создано!"},
                                           'VCLObject("frmTSETreeDtl")', "Устройство не создано", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Ошибка! Устройство для ЮЛ {cli_id} не было создано!')
            count += 1
        Sys.Process("COLVIR").VCLObject("frmTSETreeDtl").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", count, 1, rm=True) 
