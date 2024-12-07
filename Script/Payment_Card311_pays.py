﻿from Sordpay import *


def CreatePaymentForCrd_AllDataSet():
  """ Создание и оплата (оплата проходит автоматом) платежных ордеров по всему датасету
  Данный автотест предназначен для документов типа: 214, 221 (счета в валюте), 310, 311, 314, 317 """
  PaydocDataset = Sordpay()
  PaydocDataset.LoginInColvir()
#  login_user, pass_user = PaydocDataset.GetLoginPass('SK_MANAGER')
#  PaydocDataset.LoginInColvir(login_user, pass_user)
  data_list = PaydocDataset.ReadDatasetFromDB('payorder_crd')
  for row in data_list:
    if row['STEP_CASE'] =='undo_pay_sordpay':
      PaydocDataset.StartDebugLog()
      get_doc_number = CreatePaymentForCrd(row['ORDER_TYPE_PAY'], row['OPERATION_CODE_PAY'], row['WND_NAME'], 
                                              row['PAYER_ACCOUNT'], row['CLIENT_IIN'], 
                                              row['RECIPIENT_ACCOUNT_PAY'],row['RECIPIENT_IIN'], row['DESKRIBE_PAY'], 
                                              row['KNP_PAY'], row['KOD'], row['KBE'], row['NO_COMMIS'], 
                                              row['FAST_PAY'], row['RECIPIENT_IIN_PAY'],row['VAL_CODE_ACC'],row['CLI_TYPE'],row['SIGNATURE'])
      row['DOC_NUMBER_PAY'] = get_doc_number                                          
      PaydocDataset.SaveDebugLog()    
      PaydocDataset.UpdateDatasetTableDB('payorder_crd', data_list)

def CreatePaymentForCrd(order_type, oper_code,main_wnd,payer_acc,client_IIN,recipient_acc,recipient_IIN,describe, 
                       KNP, KOD, KBE, no_commis, fast_pay, recipient_iin, val_code,cli_type,signature):
  doc_number = ''  
  Paydoc = Sordpay()
  name_scenario = 'Картотека2'
  name_case = 'CreatePaymentOrderUndoPaySordpay'
  summ_oper = Paydoc.BalanceACC(val_code,recipient_acc)
  if int(summ_oper)<= 10000:
    summ_oper = 20000
    Paydoc.NewCustomerPayAccount(payer_acc,int(summ_oper))
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
  payer_account.Keys(recipient_acc)
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
  recipient_account.Keys(payer_acc)
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
  #Sys.Process("COLVIR").Dialog("Подтверждение").VCLObject("Yes").Click()
  #Paydoc.WaitLoadWindow(main_wnd, time_await=20000)
  Paydoc.ErrorMessageHandler(dop_window='True')
  Paydoc.SetSMSCode()
  Paydoc.CheckOperEndWindow()
  result = Paydoc.GetGridDataFields("frmRDocList", "STAT_NAME", "CODE")    
  if result[0].replace("\'", '') == 'Созданплатеж':
    doc_number = result[1].replace("\'", '')
    Log.Checkpoint("Документ оплачен тип "+str(order_type)+ " по счету "+str(recipient_acc))
    log = 'Операция выполнена успешно, счет пополнен' 
    Paydoc.SaveAutologs(name_scenario,name_case,log)
  else:
    Log.Warning("Документ не оплачен" + str(recipient_acc))
    log = "Ошибка, документ не оплачен, данные клиента: счет " +str(recipient_acc)+ " иин: " +str(recipient_IIN)
    Paydoc.SaveAutologs(name_scenario,name_case,log)
  Sys.Process("COLVIR").VCLObject("frmRDocList").Close()
  return doc_number
 