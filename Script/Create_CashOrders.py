﻿from Sordcash import *
                                                         
                                                         
def CreateRecieptCashOrderCheckUndoPay():
    """ Создание и регистрация приходных кассовых ордеров, в иностранной и нац валюте для проверки отмены пополнения при наличии ПТП"""
    CashdocDataset = Sordcash()
    login_user, pass_user = CashdocDataset.GetLoginPass('KASSIR')
    CashdocDataset.LoginInColvir(login_user, pass_user)
    data_list = CashdocDataset.ReadDatasetFromDB('sordcash_crd')
    for row in data_list:
        try:
            if row['STEP_CASE'] == 'deb-payment' and row['TEST_RUN'] == '0': 
                name_file = f'{CashdocDataset.GetRandomNumber()}_CreatePaymentOrderSpending.json'  
                result_tuple = CreateRecieptCashOrder(row['ORDER_TYPE'], row['OPERATION_CODE'], row['PAYER_ACCOUNT'], 
                                                       row['SUMM_OPERATION'], row['DESCRIBE'], row['KNP'], row['KOD'], row['KBE'], row['KBK'],
                                                       row['NO_COMMIS'], row['CASHBOX_SYMBOL'], row['BIN_IIN_PAYER'],  
                                                       row['DEL_FLAG'], row['KGD_FLAG'], row['RESIDENT'], row['COUNTRY'], name_file)
                get_doc_number, get_dep_kassa, get_ref_sanction, get_type_sanction = result_tuple
                row['DOC_NUMBER'] = get_doc_number
                row['DEP_KASSA'] = get_dep_kassa
                row['REF_SANCTION'] = get_ref_sanction
                row['TYPE_SANCTION'] = get_type_sanction
                CashdocDataset.UpdateDatasetTableDB('sordcash_crd', data_list)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
                                                         
def CreateRecieptCashOrder(order_type, oper_code, payer_acc, summ_oper, describe, KNP, KOD, KBE, KBK, no_commis, 
                          cashbox_symbol, bin_iin_pay, del_kgd_flag, kgd_flag, resident_key, country_code,name_file):
 try:                           
     doc_number = ''
     dep_kassa = ''
     ref_sanction = ''
     type_sanction = ''
     Cashdoc = Sordcash()
     new_path = Cashdoc.GetEnviron('NEW_PATH')
     name_pict = name_file.replace("json", "png")
     Cashdoc.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
     key = ["name", "description", "start"]
     value = ["Создание документа пополнения через кассу", "Создание документа пополнения для проверки отмены пополнения счета через кассу", Cashdoc.GetDateTimeMilli()]
     abs_path = Cashdoc.FindAbsPathFile(name_file) # Получение абсолютного пути файла
     Cashdoc.AddKeyValueJson(abs_path, key, value)
     def_dict = Cashdoc.GetDefaultDict(abs_path)
     key_labels_suite = ["name", "value"]
     value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
     Cashdoc.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
     key_labels_subsuite = ["name", "value"]
     value_labels_subsuite = ["subSuite", "Продукт - КартаКарта"]
     Cashdoc.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
     Cashdoc.TaskInput('SORDCASH')
     Cashdoc.InputEmptyFilter()
     Cashdoc.WaitLoadWindow('frmOrdCashList', time_await=20000)
     Cashdoc.InputTemplateValue("frmOrdCashList", order_type)
     Cashdoc.WaitLoadWindow("frmCashOrdDynDtl2", time_await=20000)
     operation_field = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edCodeSt')")
     operation_field.DblClick()
     operation_field.Keys(oper_code)
     operation_field.Keys("[Tab]")
     gen_doc = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edCode')", "internal")
     Cashdoc.DocNumGenValidator('Номер документа', gen_doc)
     payer_account = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edCodeAcl')")
     payer_account.Keys(payer_acc)
     payer_account.Keys("[Tab]")
     iin_client = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edRnn')", "internal")
     iin_client.Click()
     # обработка отсутсвия полномочий на счета
     if Cashdoc.WarningMessageHandler():
       Sys.Process("COLVIR").VCLObject("frmOrdCashList").Close()
       return (doc_number, dep_kassa, ref_sanction, type_sanction)
     Cashdoc.FieldValueValidator('ИИН клиента', iin_client, 'number', '000000000000')
     full_name_client = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edCliName')")
     Cashdoc.FieldValueValidator('Наименование клиента', full_name_client, 'text', 'Красавчик')
     summ_operation = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edAmount')")
     summ_operation.Keys(summ_oper)
     summ_operation.Keys("[Tab]")
     describe_field = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edTxtDscr')")
     describe_field.Keys(describe)
     describe_field.Keys("[Tab]")
     KNP_tab = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "PageTab('КНП')")
     KNP_tab.Click()
     KNP_field = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edKNP')")
     KNP_field.Keys(KNP)
     KOD_field = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edCODE_OD')")
     KOD_field.Keys(KOD)
     KBE_field = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edCODE_BE')")
     KBE_field.Keys(KBE)
     info_tab = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "PageTab('Информация')")
     info_tab.Click()
     payer_name = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edTxtPay')")
     payer_name.Click()
     payer_name.Keys("[F2]")
     if Sys.Process("COLVIR").WaitVCLObject("frmCliPrsRefer3", 3000).Exists:
       but_ok_name = Cashdoc.FindChildField("frmCliPrsRefer3", "Name", "VCLObject('btnOK')")
       but_ok_name.Click()
       payer_name.Keys("[Tab]")
     else:
       Log.Warning("Не найдено окно 'Подписи должностных лиц'")
     addit_tab = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "PageTab('Дополнительно')")
     addit_tab.Click()
     bin_iin_payer = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('edRnn')")
     bin_iin_payer.Keys(bin_iin_pay)
     if no_commis:
       no_commis = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('chkARCFL')")
       no_commis.Click()
     Log.Event("Все обязательные поля успешно заполнены")
     Cashdoc.AllureReportTemplate(abs_path, name_file, "Проверка заполнения обязательных полей в Платежном Требование", "passed", {"message": f"Все обязательные поля заполнены тип документа {order_type}"},
                                                                           'VCLObject("frmCashOrdDynDtl2")', "Проверка обязательных полей", new_path, "passed", 1, 1)
     save_btn = Cashdoc.FindChildField("frmCashOrdDynDtl2", "Name", "VCLObject('btnSave')")
     save_btn.Click()
     if not Cashdoc.ErrorMessageHandler(time_await=2000) and Sys.Process("COLVIR").WaitVCLObject("frmCsrJrnDtl", 3000).Exists:
       Cashdoc.WaitLoadWindow('frmCsrJrnDtl', time_await=20000)
       cashbox_symbol_field = Cashdoc.FindChildField("frmCsrJrnDtl", "Name", "VCLObject('edKSCode')")
       cashbox_symbol_field.Keys(cashbox_symbol)
       save_but_symbol = Cashdoc.FindChildField("frmCsrJrnDtl", "Name", "VCLObject('btnSave')")
       save_but_symbol.Click()
       if not Cashdoc.ErrorMessageHandler(time_await=2000, recursive='True'):
         Cashdoc.WaitLoadWindow('frmCashOrdDynDtl2', time_await=20000)
         Sys.Process("COLVIR").VCLObject("frmCashOrdDynDtl2").Close()
       result = Cashdoc.GetGridDataFields("frmOrdCashList", "LONGNAME", "OPR_CODE", "CODE", "DORD")
       if result[0].replace("\'", '') == 'Введен' and not kgd_flag:
         new_date_order = result[3].replace("\'", '')
         date_statusbar = Cashdoc.OperDayValue()
         if new_date_order != date_statusbar:
           Cashdoc.SetNeedOperday(Cashdoc.NormalDateMask(new_date_order))
         operation_btn = Sys.Process("COLVIR").VCLObject("frmOrdCashList").VCLObject("btnRunOperation")
         operation_btn.Click()
         Cashdoc.FindNeedOperation("Регистрация")
         Cashdoc.ConfirmOperation("Регистрация")
         Cashdoc.LimitAccBlockHandler(payer_acc)
         Cashdoc.ClickNeedButConfirmWindow('Yes')
         if not Cashdoc.ErrorMessageHandler(dop_window='True',recursive='True'):
           Cashdoc.CheckOperEndWindow()       
     new_status = Cashdoc.GetGridDataFields("frmOrdCashList", "LONGNAME", "OPR_CODE", "CODE", "DEP_ID", "")
     doc_number = new_status[2].replace("\'", '')
     if new_status[0].replace("\'", '') == 'Зарегистрирован':
       Log.Checkpoint("Документ тип: " + str(order_type) + ", номер " + str(doc_number) + " успешно зарегистрирован ")
       Cashdoc.AllureReportTemplate(abs_path, name_file, "Проверка создания и регистрация кассового документа", "passed", {"message": f"Проверка создания и регистрация кассового документа счет платильщика {payer_acc}"},
                                                         'VCLObject("frmOrdCashList")', "Проверка создания и регистрация", new_path, "passed", 1, 1, rm=True)
       jur_oper = Sys.Process("COLVIR").VCLObject("frmOrdCashList").VCLObject("btnOperJrn")
       jur_oper.Click()
       Cashdoc.WaitLoadWindow('frmOperJournal', time_await=20000)
       list_result = Cashdoc.GetGridDataFields("frmOperJournal", "TRA_ID", "ORD_ID", "DEP_ID","ID","NJRN")
       get_refers = Cashdoc.GetNeedSanctionLines(list_result[1], list_result[2])
       save_refers = list(get_refers)
       # проверка, что по операции есть записи требующие санкции
       if int(save_refers[0][0]) != 0:
         ref_sanction = str(save_refers)
         type_sanction = Cashdoc.GetTypeSanction()
       result = Cashdoc.GetGridDataFields("frmOperJournal","TUS_CODE")
       dep_kassa = Cashdoc.GetNeedNunberKass(result[0])    
       Sys.Process("COLVIR").VCLObject("frmOperJournal").Close()
     else:
       Log.Warning("Документ не зарегистрирован, тип " + order_type  + ", номер " + str(doc_number))
       doc_number = ''
       Cashdoc.AllureReportTemplate(abs_path, name_file, "Проверка создания и регистрация кассового документа", "failed", {"message": f"Проверка создания и регистрация кассового документа счет платильщика {payer_acc}"},
                                                        'VCLObject("frmOrdCashList")', "Проверка создания документа", new_path, "failed", 1, 2, rm=True)
     Sys.Process("COLVIR").VCLObject("frmOrdCashList").Close()
     return doc_number, dep_kassa, ref_sanction, type_sanction
 except Exception as error:
        Log.Warning(f"Текст ошибки - {error}")
        # Отчетность ---------------------------------------------------------------------------------------------------------------
        Cashdoc.AllureReportTemplate(abs_path, name_file, f"Непредвиденная ошибка", "failed", {"message": f"Возникла ошибка. Текст ошибки - {error}"},
                                     "desktop", "Возникла ошибка", new_path, "failed", 1, 2, rm=True)