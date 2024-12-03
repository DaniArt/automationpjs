from CardFramework import *

def LinkInstantCardToCKC_AllDataSet():
    """ Подвязка карты моментального выпуска к договору СКС по всему датасету """
    Ndeacrd = CardFramework()
    Ndeacrd.LoginInColvir()
    data_list = Ndeacrd.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:
        if row['ITER_CODE'] == '1':
            name_file = f'{Ndeacrd.GetRandomNumber()}_LinkInstantCardToCKC.json' 
            form_data = LinkInstantCardToCKC(row['PRODUCT'], row['DOC_CODE'], row['REG_DATE'], name_file)
            row['IDN_CARD'] = form_data
            Ndeacrd.UpdateDatasetTableDB('ckcdoc_data', data_list)
             
def LinkInstantCardToCKC(product, doc_code, reg_date, name_file):
    """ Подвязка карты моментального выпуска к договору СКС """
    card_idn = ''
    Ndeacrd = CardFramework()
    # Создание главной иерархии json отчета
    new_path = Ndeacrd.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Ndeacrd.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Подвязка договора - Подвязка инстант карты к договору СКС", f"Подвязка карты {product} к договору {doc_code}", Ndeacrd.GetDateTimeMilli()]
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
        Ndeacrd.SetFilter(CODE=doc_code) # Вставляем номер документа из бд, для поиска нашего заведенного договора
        Ndeacrd.WaitLoadWindow('DeaSCAList', time_await=6000)
        but_operations = Sys.Process("COLVIR").VCLObject("DeaSCAList").VCLObject("btnRunOperation") # Определение контекстного меню с опреациямии
        but_operations.Click()
        Ndeacrd.FindNeedOperation("Выдача карты момент. выпуска") 
        Ndeacrd.ConfirmOperation("Выдача карты момент. выпуска")
        Delay(2000)
        Ndeacrd.ConfirmOperation("Выбрать карту из пула?")
        Sys.Process("COLVIR").VCLObject("frmDynamicDialog").VCLObject("DynamicBox").VCLObject("FLESSENTAI").Click()
        but_ok = Ndeacrd.FindChildField("frmDynamicDialog", "Name", "VCLObject('btnOK')")
        but_ok.Click()
        add_filter = Ndeacrd.FindChildField("frmaPoolCrdsRef", "Name", "VCLObject('ExSpeedButton1')")
        add_filter.Click()
        product_field = Ndeacrd.FindChildField("frmFilterParams", "Name", "VCLObject('DCL_CODE')")
        product_field.Keys(product) 
        dord_field = Ndeacrd.FindChildField("frmFilterParams", "Name", "VCLObject('DORD')")
        dord_field.Keys("^a")
        dord_field.Keys(reg_date)
        ok_btn = Ndeacrd.FindChildField("frmFilterParams", "Name", "VCLObject('btnOK')")
        ok_btn.Click()
        Ndeacrd.WaitLoadWindow('frmaPoolCrdsRef', time_await=6000)
        LLPlayer.KeyDown(VK_RETURN, 500) # Используем кнопку ENTER для выбора карты, т.к все карточки нами же свежесозданные и пустые 
        LLPlayer.KeyUp(VK_RETURN, 500)
        Ndeacrd.WaitLoadWindow('NCardDetail', time_await=10000)
        Delay(3000) # Функция ожидания истекает, и требуемое окно перезагружается при запуска, добавляем ожидание в ручную
        btn_idennfy = Ndeacrd.FindChildField("NCardDetail", "Name", "PageTab('Идентификация держателя')")
        btn_idennfy.Click()
        code_word = Ndeacrd.FindChildField("NCardDetail", "Name", "VCLObject('edPWD')")
        code_word.Click()
        Sys.Process("COLVIR").Dialog("Внимание").VCLObject("Yes").Click()
        Delay(3000) # Так же после предупреждения, требуется небольшое ожидание
        code_word.Click()
        code_word.Keys("123123") # Объязательное окно с кодовым словом
        btn_save = Ndeacrd.FindChildField("NCardDetail", "Name", "VCLObject('btnSave')")
        btn_save.Click()
        Ndeacrd.CheckOperEndWindow()
        btn_open = Ndeacrd.FindChildField("DeaSCAList", "Name", "VCLObject('btnBrowse')")
        btn_open.Click()
        btn_reclick = Ndeacrd.FindChildField("DeaSCADetail", "Name", "VCLObject('edDEP_CODE')")
        btn_reclick.Click() # Кликаем по окну с документом, для обнаружения
        form_data = Ndeacrd.GetGridDataFields("DeaSCADetail", "CARDIDN", "STATNAME", need_tab="qryCard")
        card_idn = form_data[0].replace("\'", '')
        if form_data[1].replace("\'", "") == 'Заявлениенавыпусквведено': # Проверка состояния документа
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Подвязка договора СКС для клиента", "passed", {"message": f"Карта с идентификатором {form_data[0]} в состоянии {form_data[1]}"},
                                           'VCLObject("DeaSCADetail")', "Договор подвязан", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Карта с идентификатором {form_data[0]} в состоянии {form_data[1]}')
        else:
            # Отчетность
            Ndeacrd.AllureReportTemplate(abs_path, name_file, "Подвязка договора СКС для клиента", "failed", {"message": f"Операция {form_data[1]} по карте {form_data[0]} не выполнена"},
                                           'VCLObject("DeaSCADetail")', "Договор не подвязан", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Операция {form_data[1]} по карте {form_data[0]} не выполнена')
        Sys.Process("COLVIR").VCLObject("DeaSCADetail").Close()
        Sys.Process("COLVIR").VCLObject("DeaSCAList").Close()
        return card_idn
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Ndeacrd.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", 2, 1, rm=True) 
