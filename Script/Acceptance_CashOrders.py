﻿from Sordcash import *
                                      
                                      
def AcceptanceCashOrdersCheckUndoPay():
  """ Прием по приходным кассовым ордерам в иностранной и нац валюте по всему датасету """
  CashdocDataset = Sordcash()
  login_user, pass_user = CashdocDataset.GetLoginPass('KASSIR')
  CashdocDataset.LoginInColvir(login_user, pass_user)
  data_list = CashdocDataset.ReadDatasetFromDB('sordcash_crd')
  for row in data_list:
      try:
          if row['STEP_CASE'] == 'deb-payment' and row['TEST_RUN'] == '0': 
              name_file = f'{CashdocDataset.GetRandomNumber()}_CreatePaymentOrderSpending.json'  
              AcceptanceCashOrder(row['ORDER_TYPE'], row['PAYER_ACCOUNT'],row['DOC_NUMBER'], row['SUMM_OPERATION'],name_file)
      except Exception as e:
            Log.Event('Возникла ошибка идем дальше')
                                      
def AcceptanceCashOrder(order_type,payer_acc, doc_num, summ_oper,name_file):  
  
  try:   
      Cashdoc = Sordcash()
      Cashdoc.CashInSoap(payer_acc,'100000','KZT')
      new_path = Cashdoc.GetEnviron('NEW_PATH')
      name_pict = name_file.replace("json", "png")
      Cashdoc.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
      key = ["name", "description", "start"]
      value = ["Прием денег через кассу", "Пополнения счета через кассу", Cashdoc.GetDateTimeMilli()]
      abs_path = Cashdoc.FindAbsPathFile(name_file) # Получение абсолютного пути файла
      Cashdoc.AddKeyValueJson(abs_path, key, value)
      def_dict = Cashdoc.GetDefaultDict(abs_path)
      key_labels_suite = ["name", "value"]
      value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
      Cashdoc.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
      key_labels_subsuite = ["name", "value"]
      value_labels_subsuite = ["subSuite", "Продукт - КартаКарта"]
      Cashdoc.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
      get_bal_value = Cashdoc.GetMadvpayCashboxBal()
      """ @content: Запустить задачу 'SORDCASH'  """
      """ @expected: Появится окно 'Фильтр' """
      from_date = Cashdoc.NormalDateMask()
      to_date = from_date
      Cashdoc.TaskInput('SORDCASH')
      """ @content: Заполнить необходимые поля в фильтре для того, чтобы найти необходимый документ """
      """ @expected: Появится окно 'Кассовые документы' с необходимым документом """
      Cashdoc.SetFilter(EDDATEFROM=from_date, EDDATETO=to_date, 
                        AMOUNT_FROM=summ_oper, AMOUNT_TO=summ_oper, btnOther='',
                        CODE=doc_num, KSO_CODE=order_type)
      Cashdoc.WaitLoadWindow("frmOrdCashList",time_await=20000)
      """ @content: В окне 'Кассовые документы' выбрать необходимый документ в состоянии 'Зарегистрирован'
                    и выполнить 'Операции' -> 'Прием денег' """
      find_pay = Cashdoc.GetGridDataFields("frmOrdCashList", "LONGNAME")
      if find_pay[0].replace("\'", '') == 'Зарегистрирован':
        but_operations = Sys.Process("COLVIR").VCLObject("frmOrdCashList").VCLObject("btnRunOperation")
        but_operations.Click()
        if not Sys.Process("COLVIR").WaitVCLObject("Контекст", 3000).Exists:
          but_operations.Click()
        Cashdoc.FindNeedOperation("Прием денег")
        Cashdoc.ConfirmOperation("Прием денег")
        if not Cashdoc.ErrorMessageHandler(dop_window='True'):
          Log.Message('Проверка док')
        if Sys.Process("COLVIR").WaitVCLObject("frmDynamicDialog", 6000).Exists:
          btn_ok_summ = Cashdoc.FindChildField("frmDynamicDialog", "Name", "VCLObject('btnOK')")
          btn_ok_summ.Click()
        if not Cashdoc.ErrorMessageHandler():
          """ @expected: Появляется окно 'Сформированные отчеты' с кассовым ордером """
          Cashdoc.WaitReportPrintList()
          """ @content: В окне 'Сформированные отчеты' нажать на кнопку 'Печать' """
          Cashdoc.CheckOperEndWindow()
          result = Cashdoc.GetGridDataFields("frmOrdCashList", "LONGNAME", "OPR_CODE", "CODE", "PROC_ID")
          if result[0].replace("\'", '') == 'Исполнен':
            """ @expected: Проверить текст сформированного кассового ордера на корректность заполнения полей.
                           В окне 'Кассовые документы' появится документ в состоянии 'Исполнен'
                           Баланс ценностей в кассе должен измениться на сумму документа.
                           В 'Журнале операций' появляется фин проводка """
            Log.Checkpoint("Успешно выполнена операция 'Прием денег' по документу тип:" + str(order_type))
            Cashdoc.AllureReportTemplate(abs_path, name_file, "Проверка Приема денег", "passed", {"message": f"Проверка Приема денег {payer_acc}"},
                            'VCLObject("frmOrdCashList")', "Прием денег", new_path, "passed", 1, 1, rm=True)
            Cashdoc.GetCommisPay(result[3])
            jur_oper = Sys.Process("COLVIR").VCLObject("frmOrdCashList").VCLObject("btnOperJrn")
            jur_oper.Click()
            Cashdoc.WaitLoadWindow("frmOperJournal",time_await=20000)
            list = Cashdoc.GetGridDataFields("frmOperJournal","TRA_ID","ID","NJRN")
            Cashdoc.StaticSelectFinancialTransation(list[1],list[2],list[0])  
            Sys.Process("COLVIR").VCLObject("frmOperJournal").Close()
            Cashdoc.GetMadvpayCashboxBal(get_bal_value)
          else:
            Log.Warning("Не найден документ в состоянии 'Исполнен', тип:" + str(order_type))
            Cashdoc.AllureReportTemplate(abs_path, name_file, "Проверка Приема денег", "failed", {"message": f"Проверка Приема денег {payer_acc}"},
                                'VCLObject("frmOrdCashList")', "Проверка Приема денег", new_path, "failed", 1, 1, rm=True)
      else:
        Log.Warning("Документ с состоянии 'Зарегистрирован' не найден, тип:" + str(order_type))
      Sys.Process("COLVIR").VCLObject("frmOrdCashList").Close()
  except Exception as error:
        Log.Warning(f"Текст ошибки - {error}")
        # Отчетность ---------------------------------------------------------------------------------------------------------------
        Cashdoc.AllureReportTemplate(abs_path, name_file, f"Непредвиденная ошибка", "failed", {"message": f"Возникла ошибка. Текст ошибки - {error}"},
                                     "desktop", "Возникла ошибка", new_path, "failed", 1, 2, rm=True)