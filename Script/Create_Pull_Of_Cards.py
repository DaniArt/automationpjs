from CardFramework import *

def RequestToOpenCrd_AllDataSet():
    """ Создание заявки на неэмбоссированные карты по всему датасету  """
    Card = CardFramework()
    Card.LoginInColvir()
    data_list = Card.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
      try:
          if row['DEPO_CODE'] == 'AA6':
              name_file = f'{Card.GetRandomNumber()}_RequestToOpenCrd.json'   
              form_data = RequestToOpenCrd(row['DEPO_CODE'],row['PRODUCT'],row['VAL_CODE'], row['AMOUNT'], name_file)
              row['REG_DATE'] = form_data
              Card.UpdateDatasetTableDB('crdreq_data', data_list)
      except Exception as e:
          Log.Event('Возникла ошибка идем дальше')

def RequestToOpenCrd(depo_code,product,val_code,amount,name_file):
    """ Создание заявки на неэмбоссированные карты """
    Card = CardFramework()
    result = ''
    count = 1
    # Создание главной иерархии json отчета
    new_path = Card.GetEnviron('NEW_PATH')
    name_pict = name_file.replace("json", "png")  
    Card.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
    key = ["name", "description", "start"]
    value = ["Создание заявки - Создание заявки на неэмбоссированные карты", f"Операция создания пластика по продукту {product}", Card.GetDateTimeMilli()]
    abs_path = Card.FindAbsPathFile(name_file) # Получение абсолютного пути файла
    Card.AddKeyValueJson(abs_path, key, value)
    def_dict = Card.GetDefaultDict(abs_path)
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", "Colvir. Модуль - БОКС/ПС"]
    Card.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", "Продукт - КартаКарта"]
    Card.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    #Начало работы скрипта
    try:
      Card.TaskInput('CRDREQ')
      Card.InputEmptyFilter()
      Card.WaitLoadWindow('frmCrdReqLst')
      # Далее идет операция создания заявки на неэбосс.карт и заполнение формы 
      operation_create = Card.FindChildField("frmCrdReqLst", "Name", "VCLObject('btnInsert')")
      operation_create.Click()
      Card.WaitLoadWindow('frmCRDREQDTL')
      application_depo = Card.FindChildField("frmCRDREQDTL", "Name", "VCLObject('edDEP_CODE')")
      application_depo.Keys("^a")
      application_depo.Keys(depo_code)
      product_code = Card.FindChildField("frmCRDREQDTL", "Name", "VCLObject('edDCL_CODE')")
      product_code.Keys(product)
      val_name = Card.FindChildField("frmCRDREQDTL", "Name", "VCLObject('edVAL_CODE')")
      val_name.Keys(val_code)
      amount_crd = Card.FindChildField("frmCRDREQDTL", "Name", "VCLObject('edDCNT')")
      amount_crd.Keys(amount)
      giveout_depo = Card.FindChildField("frmCRDREQDTL", "Name", "VCLObject('edDEP_CODE_DELIV')")
      giveout_depo.Keys("^a")
      giveout_depo.Keys(depo_code)
      LLPlayer.KeyDown(VK_TAB, 500)
      LLPlayer.KeyUp(VK_TAB, 500) 
      btn_save = Card.FindChildField("frmCRDREQDTL", "Name", "VCLObject('btnSave')")
      btn_save.Click()
      Card.WaitLoadWindow('frmCrdReqLst')
      btn_send = Card.FindChildField("frmCrdReqLst", "Name", "VCLObject('btnSend')")
      btn_send.Click()
      Card.ClickNeedButConfirmWindow('YES')
      Card.WaitLoadWindow('frmCrdReqLst')
      status_cards = Card.GetGridDataFields("frmCrdReqLst", "STATE", "DCL_NAME", "DORD")
      result = status_cards[2].replace("\'", '').replace(".", '') # Убираем кавычки и точки, для последующего успешного ввода даты
      if status_cards[0].replace("\'", '') == '1': # Проверка статуса заявки, где 1 - обработан, 0 - не обработан
          # Отчетность
          Card.AllureReportTemplate(abs_path, name_file, "Создание заявки на неэмбоссированные карточки", "passed", {"message": f"Заявка успешно обработана по продукту. Данные: Код продукта {status_cards[1]}"},
                                         'VCLObject("frmCrdReqLst")', "Карты созданы!", new_path, "passed", 1, 1, rm=True)
          # --------------------------------------------------------------------------------------------------------------------------
          Log.Checkpoint(f'Заявка успешно обработана по продукту {status_cards[1]}')
          count += 1
      else:
          # Отчетность
          Card.AllureReportTemplate(abs_path, name_file, "Создание заявки на неэмбоссированные карточки", "failed", {"message": f"Операция обработки по продукту неэмбоссированных карт не выполнена, код продукта{product}"},
                                         'VCLObject("frmCrdReqLst")', "Ошибка создания", new_path, "failed", 1, 1, rm=True)
          # --------------------------------------------------------------------------------------------------------------------------
          Log.Warning(f'Операция обработки по продукту неэмбоссированных карт {status_cards[1]} не выполнена.')
          count += 1
      Sys.Process("COLVIR").VCLObject("frmCrdReqLst").Close()
      return result
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Card.AllureReportTemplate(abs_path, name_file, "Возникла непредвиденная ошибка", "failed", {"message": f"Возникла непредвиденная ошибка"},
                                     'desktop', None, new_path, "failed", count, 1, rm=True) 