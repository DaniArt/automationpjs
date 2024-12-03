from CardFramework import *
from TaskMethods import *

def ChangeOutcomeLimit_AllDataSet():
    """ Изменение расходного лимита """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('travel_data')
    for row in data_list:
        try:
          if row['IDN_CARD'] and row['ITER_CODE'] == '1':
              name_file = f'{NCRD.GetRandomNumber()}_ChangeOutcomeLimit.json'   
              ChangeOutcomeLimit(row['IDN_CARD'], name_file)
          elif row['IDN_CARD'] is None:
                name_file = f'{NCRD.GetRandomNumber()}_ChangeOutcomeLimit.json'
                NCRD.CreateAllureReport("Colvir. Модуль - БОКС/ПС", f"Изменение расходного лимита карты Travel", 
                                                  f"{TestVariables().get_var('_dcmnt_nt_fnd')}", name_file)
        except Exception as e:
            Log.Event('Возникла ошибка идем дальше')

            
def ChangeOutcomeLimit(idn_card, name_file):
    NCRD = TaskMethods()
    try: 
        # создание отчета allure
        NCRD.CreateAllureReport("Colvir. Модуль - БОКС/ПС", "Продукт - Travel карта", f"Изменить расходный лимит {idn_card}", name_file)
        #---------        
        NCRD.TaskInput('NCRD')
        NCRD.WaitLoadWindow('frmFilterParams')
        NCRD.SetFilter(CARDIDN=idn_card) # Берем номер идентификатора из бд, для поиска нашей карты
        NCRD.WaitLoadWindow('NCrdList')
        but_operations = NCRD.FindChildField("NCrdList", "Name", "VCLObject('btnRunOperation')")
        but_operations.Click()
        NCRD.FindNeedOperation("Изменение расходного лимита") 
        NCRD.ConfirmOperation("Изменение расходного лимита")
        chk_box = NCRD.FindChildField("frmDFSimpleEngine", "Name", "CheckBox('Сменить лимит на индивид.')")
        chk_box.Click()
        ok_btn = NCRD.FindChildField("frmDFSimpleEngine", "Name", "VCLObject('btnOK')")
        ok_btn.Click()
        NCRD.WaitLoadWindow('frmCrdLimLst')
        for _ in range(50):
            type_limit = NCRD.GetGridDataFields("frmCrdLimLst", "LIMTYPE_NAME", "PER_CODE", need_tab = 'qryRef') # Получаем статус карты для дальнейшей проверки
            if type_limit[0].replace("\'", '') == 'ЛимитнаснятиеАТМвнутристраны':
                lim_choose = NCRD.FindChildField("frmCrdLimLst", "Name", "TextObject('Лимит на снятие АТМ внутри страны')")
                lim_choose.Click()
                edit_btn = NCRD.FindChildField("frmCrdLimLst", "Name", "VCLObject('btnEdit')")
                edit_btn.Click()
                break
                
            else: 
                LLPlayer.KeyDown(VK_DOWN, 300) # нажатие стрелки вниз 1 раз
                LLPlayer.KeyUp(VK_DOWN, 300)
        NCRD.WaitLoadWindow('frmDFSimpleEngine')    
        sum_value = NCRD.FindChildField("frmDFSimpleEngine", "Name", 'Window("TExMoneyEdit", " ", 1)')
        sum_value.keys('200')
        chk_box2 = NCRD.FindChildField("frmDFSimpleEngine", "Name", "CheckBox('До конца текущего дня')")
        chk_box2.Click()
        btn_ok = NCRD.FindChildField("frmDFSimpleEngine", "Name", "VCLObject('btnOK')")
        btn_ok.Click()
        NCRD.CheckOperEndWindow()
        NCRD.WaitLoadWindow('NCrdList')
        # проверка записи в журнале операций
        NCRD.CheckOperJrn("Изменениерасходноголимита", "NCrdList", 'VCLObject("btnOperJrn")', "frmOperJournal", ["NAME"], 1, name_file)
        #---------
        # завершение формирование отчета
        NCRD.AllureReportEnd(2, name_file, "passed")
        # закрытие главного окна
        NCRD.CloseWindow("NCrdList")
        #------------------------
    except Exception as error:
        Log.Warning(f"Error: {error}")
        # Дополнительные действия по обработке ошибки
        # завершение формирование отчета
        NCRD.AllureReportEnd(3, name_file, "failed", error)
        #---------

