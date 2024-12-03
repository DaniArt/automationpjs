from Sordpay import *
                                                                                                  
                                                                                                  
def CreatePaymentOrderSpending_AllDataSet():
    """ Создание и оплата (оплата проходит автоматом) платежных ордеров по всему датасету
    Данный автотест предназначен для документов типа: 214, 221 (счета в валюте), 310, 311, 314, 317 """
    PaydocDataset = Sordpay()
    PaydocDataset.LoginInColvir()
    data_list = PaydocDataset.ReadDatasetFromDB('sordpay_crd')
    for row in data_list:
        try:
            if row['STEP_CASE'] =='pm_jur':
                name_file = f'{PaydocDataset.GetRandomNumber()}_CreatePaymentOrderSpending.json'
                get_doc_number = CreatePaymentOrderSpending(row['ORDER_TYPE_PAY'], row['OPERATION_CODE_PAY'], row['WND_NAME'], 
                                                        row['PAYER_ACCOUNT'], row['CLIENT_IIN'], 
                                                        row['RECIPIENT_ACCOUNT_PAY'],row['RECIPIENT_IIN'], row['DESKRIBE_PAY'], 
                                                        row['KNP_PAY'], row['KOD'], row['KBE'], row['NO_COMMIS'], 
                                                        row['FAST_PAY'], row['RECIPIENT_IIN_PAY'],row['VAL_CODE_ACC'],
                                                        row['CLI_TYPE'],row['SIGNATURE'],name_file)
                row['DOC_NUMBER_PAY'] = get_doc_number                                           
                PaydocDataset.UpdateDatasetTableDB('sordpay_crd', data_list)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
            
                                                                                                  
def CreatePaymentOrderSpending(order_type, oper_code,main_wnd,payer_acc,client_IIN,recipient_acc,recipient_IIN,describe, KNP, KOD, KBE, no_commis, fast_pay, recipient_iin, val_code,cli_type,signature,name_file):
    Paydoc = Sordpay()
    Paydoc.CashInSoap(recipient_acc,'100000',val_code)
    # Создание главной иерархии json отчета
    new_path = Paydoc.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Paydoc.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Создание документа в задаче Sordpay {order_type}", f"Создание документа пополнения для проверки отмены пополнения через задачу Sordpay", Paydoc.GetDateTimeMilli()]
    abs_path = Paydoc.FindAbsPathFile(name_file) # Получение абсолютного пути файла
    Paydoc.AddKeyValueJson(abs_path, key, value)
    def_dict = Paydoc.GetDefaultDict(abs_path)
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
    Paydoc.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", "Продукт - КартаКарта"]
    Paydoc.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    # Начало работы скрипта автотеста  
    sum_full = Paydoc.BalanceACC(val_code,recipient_acc)
    summ_oper = int(sum_full)/2
    try:
        Paydoc.TaskInput('SORDPAY')
        Paydoc.InputEmptyFilter()
        Paydoc.WaitLoadWindow('frmRDocList', time_await=20000)
        Paydoc.InputTemplateValue("frmRDocList", order_type)
        Paydoc.WaitLoadWindow(main_wnd, time_await=20000)
        operation_field = Paydoc.FindChildField(main_wnd, "Name", 'VCLObject("edCodeSt")')
        operation_field.DblClick()
        operation_field.Keys(oper_code)
        operation_field.Keys("[Tab]")
        gen_doc_num = Paydoc.FindChildField(main_wnd, "Name", "VCLObject('edCode')", "internal")
        Paydoc.DocNumGenValidator('Номер документа', gen_doc_num)
        date_doc = Paydoc.FindChildField(main_wnd, "Name", "VCLObject('edDateFrom')", "internal")
        Paydoc.FieldValueValidator('Дата документа', date_doc, 'date')
        date_exec = Paydoc.FindChildField(main_wnd, "Name", "VCLObject('edDval')", "internal")
        Paydoc.FieldValueValidator('Дата исполнения', date_exec, 'date')
        payer_account = Paydoc.FindChildField(main_wnd, "Name", 'VCLObject("edCodeAcl")')
        payer_account.Keys(payer_acc) 
        payer_account.Keys("[Tab]")
        iin_client = Paydoc.FindChildField(main_wnd, "Name", "VCLObject('edRnnCl')", "internal")
        iin_client.Click()
        Paydoc.CheckWarningPayerAccount() # обработка проблем со счетом
        Paydoc.FieldValueValidator('ИИН клиента', iin_client, 'number', recipient_IIN)
        full_name_client = Paydoc.FindChildField(main_wnd, "Name", "VCLObject('edTxtPay')", "internal")
        full_name_client.Click()
        Paydoc.FieldValueValidator('Наименование клиента', full_name_client, 'text', 'Красавчик')
        summ_operation = Paydoc.FindChildField(main_wnd, "Name", 'VCLObject("edSdok")')
        summ_operation.Keys(int(summ_oper))
        summ_operation.Keys("[Tab]")
        Paydoc.CheckWarningPayerAccount()
        recipient_account = Paydoc.FindChildField(main_wnd, "Name", 'VCLObject("edCodeAcr")')
        recipient_account.Keys(recipient_acc) 
        recipient_account.Keys("[Tab]")
        Paydoc.CheckWarningPayerAccount() # обработка проблем со счетом
        iin_recip = Paydoc.FindChildField(main_wnd, "Name", "VCLObject('edRnnCr')", "internal")
        iin_recip.Click()
        Paydoc.CheckWarningPayerAccount()
        Paydoc.FieldValueValidator('ИИН получателя', iin_recip, 'number', client_IIN, log_type='Event')
        Paydoc.CheckWarningPayerAccount()
        full_name_recip = Paydoc.FindChildField(main_wnd, "Name", "VCLObject('edTxtBen')", "internal")
        full_name_recip.Click()
        Paydoc.FieldValueValidator('Наименование получателя', full_name_recip, 'text', 'АО "ForteBank"', log_type='Event')
        text_descript = Paydoc.FindChildField(main_wnd, "Name", 'VCLObject("edTxtDscr")')
        text_descript.Keys(describe)
        text_descript.Keys("[Tab]")
        Sys.Process("COLVIR").VCLObject("frmMailOrdDynDtl2").VCLObject("pnlClient").VCLObject("pnlSupport").VCLObject("pnlBottom").VCLObject("tabDetail").PageTab("???").Click()
        KNP_field = Paydoc.FindChildField(main_wnd, "Name", 'VCLObject("edKNP")')
        KNP_field.Keys(KNP)
        KOD_field = Paydoc.FindChildField(main_wnd, "Name", 'VCLObject("edCODE_OD")')
        KOD_field.Keys(KOD)
        KBE_field = Paydoc.FindChildField(main_wnd, "Name", 'VCLObject("edCODE_BE")')
        KBE_field.Keys(KOD)
        KBE_field.Keys("[Tab]")
        if cli_type != 'FL': 
            Sys.Process("COLVIR").VCLObject(main_wnd).VCLObject("pnlClient").VCLObject("pnlSupport").VCLObject("pnlBottom").VCLObject("tabDetail").PageTab("Подписи").Click()   
        text_signature = Paydoc.FindChildField(main_wnd, "Name", 'VCLObject("edTxtHead")')
        text_signature.Keys(signature)
        if no_commis:
            no_commis_box = Paydoc.FindChildField(main_wnd, "Name", 'VCLObject("chkManComisFl")')
            no_commis_box.Click()
        Log.Event("Все обязательные поля успешно заполнены")
        Paydoc.AllureReportTemplate(abs_path, name_file, "Проверка заполнения обязательных полей в Платежном Требование", "passed", {"message": f"Все обязательные поля заполнены тип документа {order_type}"},
                      'VCLObject("frmMailOrdDynDtl2")', "Проверка обязательных полей", new_path, "passed", 1, 1)
        save_but = Sys.Process("COLVIR").VCLObject(main_wnd).VCLObject("btnSave")
        save_but.Click()
        Paydoc.CheckWarningPayerAccount()
        Paydoc.CheckWarningPayerAccount()
        # окно ввода СМС кода
        Sys.Process("COLVIR").VCLObject("frmMailOrdDynDtl2").TitleBar(0).Button("Закрыть").Click()
        #проверка ПМ
        operations_but = Sys.Process("COLVIR").VCLObject("frmRDocList").VCLObject("btnRunOperation")
        operations_but.Click()
        if not Sys.Process("COLVIR").WaitVCLObject("Контекст", 3000).Exists:
            operations_but.Click()
        Paydoc.FindNeedOperation("Оплатить")
        Paydoc.ConfirmOperation("Оплатить")
        Paydoc.ErrorMessageHandler(recursive='True', negativ_case='True')
        Paydoc.ClickNeedButConfirmWindow('Yes')
        Paydoc.ErrorMessageHandler(dop_window='True')
        Paydoc.CheckOperEndWindow()
        result = Paydoc.GetGridDataFields("frmRDocList", "STAT_NAME", "CODE")    
        if result[0].replace("\'", '') == 'Созданплатеж':
            doc_number = result[1].replace("\'", '')
            Log.Checkpoint("Документ оплачен тип"+str(order_type)+ "по счету"+str(payer_acc))
            Paydoc.AllureReportTemplate(abs_path, name_file, "Проверка оплаты документа", "passed", {"message": f"Документ успешно оплачен  счет платильщика {payer_acc}, тип документа {order_type}"},
                 'VCLObject("frmRDocList")', "Проверка оплаты", new_path, "passed", 1, 2, rm=True)
        else:
            Log.Warning("Документ не оплачен" + str(payer_acc))
            Paydoc.AllureReportTemplate(abs_path, name_file, "Проверка оплаты документа", "failed", {"message": f"Документ не оплачен счет платильщика {payer_acc}, тип документа {order_type}"},
                    'VCLObject("frmRDocList")', "Проверка оплаты", new_path, "failed", 1, 2, rm=True)
        Sys.Process("COLVIR").VCLObject("frmRDocList").Close()
        return doc_number
    except Exception as error:
        Log.Warning(f"Текст ошибки - {error}")
        # Отчетность ---------------------------------------------------------------------------------------------------------------
        Paydoc.AllureReportTemplate(abs_path, name_file, f"Непредвиденная ошибка", "failed", {"message": f"Возникла ошибка. Текст ошибки - {error}"},
                                     "desktop", "Возникла ошибка", new_path, "failed", 1, 2, rm=True) 