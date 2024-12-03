from CardFramework import *
from TaskMethods import *

def CheckPoolCnt_AllDataSet():
    """ Создание заявки на неэмбоссированные карты по всему датасету  """
    Card = CardFramework()
    Card.LoginInColvir()
    data_list = Card.ReadDatasetFromDB('ckcdoc_data')
    for row in data_list:
        if row['ITER_CODE'] == '2':
            name_file = f'{Card.GetRandomNumber()}_CheckPoolCnt.json'   
            form_data = CheckPoolCnt(row['DEPO_CODE'],row['PRODUCT'],row['VAL_CODE'], row['AMOUNT'], name_file)

def CheckPoolCnt(depo_code,product,val_code,amount,name_file):
    Card = TaskMethods()
    try:
        # создание отчета allure
        Card.CreateAllureReport("Colvir. БОКС/ПС", "Операции - СКС Договора", "Проверка ограничения выпуска карт на подразделение CNT при выпуске пула", name_file)
        #---------   
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
        giveout_depo.Keys("CNT")
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
        if status_cards[0].replace("\'", '') == '1': # Проверка статуса заявки, где 1 - обработан, 0 - не обработан
            # Отчетность
            Card.AllureReportTemplate(abs_path, name_file, "Создание заявки на неэмбоссированные карточки", "passed", {"message": f"Заявка успешно обработана по продукту. Данные: Код продукта {status_cards[1]}"},
                                           'VCLObject("frmCrdReqLst")', "Карты созданы!", new_path, "passed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Checkpoint(f'Заявка успешно обработана по продукту {status_cards[1]}')
        else:
            # Отчетность
            Card.AllureReportTemplate(abs_path, name_file, "Создание заявки на неэмбоссированные карточки", "failed", {"message": f"Операция обработки по продукту неэмбоссированных карт не выполнена, код продукта{product}"},
                                           'VCLObject("frmCrdReqLst")', "Ошибка создания", new_path, "failed", 1, 1, rm=True)
            # --------------------------------------------------------------------------------------------------------------------------
            Log.Warning(f'Операция обработки по продукту неэмбоссированных карт {status_cards[1]} не выполнена.')
        Sys.Process("COLVIR").VCLObject("frmCrdReqLst").Close()
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        Card.AllureReportTemplate(abs_path, name_file, "Возникла ожидаемая ошибка", "passed", {"message": f"Возникла ожидаемая ошибка"},
                                     'desktop', None, new_path, "passed", 2, 1, rm=True) 
