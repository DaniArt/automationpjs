from ColvirFramework import *
from TaskMethods import *
from TestVariables import *

  
class Operjrnrat(CommonOperation, CreateJsonReport):
    """ Класс работы с задачей Operjrnrat """
  
    def StandartSanctionOperation(self, input_login_type=None, account_num=None, name_scen=None, name_case=None, name_module=None, name_file=None, **need_filters):
        """ Простое санкционирование операций под необходимым пользователем 
        без определенного порядка санкций, т.е подряд (порядок должен быть уже определен заранее)
        Поля для заполнения фильтра передаются в виде словаря ПОЛЕ=значение (без кавычек если значение ключа это переменная)
        Если не передан логин, будет использован уже запущенный пользователь 
        """
        self.input_login_type = input_login_type
        self.need_filters = need_filters
        self.account_num = account_num
        self.name_scen = name_scen
        self.name_case = name_case
        self.name_module = name_module
        self.name_file = name_file
        list_status = False # меняется на True, если санкция проставлена успешно
        list_sanction = True # меняется на False, если необходима санкция еще одним исполнителем 
        # Создание главной иерархии json отчета
        name_file = f'{self.GetRandomNumber()}_{self.name_file}.json'
        user_name = self.GetUserName() #Получение логина пользователя, чтобы функция работала под разнымми пользователями
        new_path = self.GetEnviron('NEW_PATH')
        self.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
        key = ["name", "description", "start"]
        value = [f"Санкционирование операции {self.name_scen} по {self.name_case}", f"Санкционирование операции {self.name_scen}", self.GetDateTimeMilli()]
        abs_path = self.FindAbsPathFile(name_file) # Получение абсолютного пути файла
        self.AddKeyValueJson(abs_path, key, value)
        def_dict = self.GetDefaultDict(abs_path)
        key_labels_suite = ["name", "value"]
        value_labels_suite = ["suite", f"{self.name_module}"]
        self.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
        key_labels_subsuite = ["name", "value"]
        value_labels_subsuite = ["subSuite", f"Санкционирование операции {self.name_scen}"]
        self.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
        # ----------------------------------------------------------------------------------------------------------------------------
        # проверка на нулевой референс
        if 'REF_OPER' in self.need_filters and \
          (self.need_filters['REF_OPER'] == 0 or self.need_filters['REF_OPER'] == '0'):
          Log.Warning('На санкционирование передан референс 0, проверьте предыдущий тест')
          #log = 'Ошибка' 
          #self.SaveAutologs(self.name_scen,self.name_case,log)
          return list_status, list_sanction
        if self.input_login_type is not None:
          login_user, pass_user = self.GetLoginPass(self.input_login_type)
          self.LoginInColvir(login_user, pass_user)
        self.TaskInput('OPERJRNRAT')
        self.SetFilter(SET_RAT=1, btnOther='', fields=self.need_filters)
        self.WaitLoadWindow("frmOperJournal", time_await=30000)
        find_doc = self.GetGridDataFields("frmOperJournal", "NAMEOPRMOV") 
        if find_doc[0].replace("\'", ''):
          Log.Checkpoint(find_doc[0][:120])
          self.AllureReportTemplate(abs_path, name_file, "Поиск санкции", "passed", {"message": find_doc[0][:120]},
                                                                     'VCLObject("frmOperJournal")', "Санкция найдена", new_path, "passed", 1, 1)
          agree_but = Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnPost")
          agree_but.Click()
          if self.account_num is not None:
            self.LimitAccBlockHandler(self.account_num) # проверка лимитной группы
          if not self.ErrorMessageHandler(): # проверка на ошибку проставления санкции
            self.CheckOperEndWindow()
            list_status = True
          executors_but = Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnExecutors")
          executors_but.Click()
          self.WaitLoadWindow("frmExecutors")
          dict_res = self.DBGetSanctionInfo("frmExecutors")
          for key, value in dict_res.items():
            if value is None:
              Log.Event(key)
              list_sanction = False
            else:
              Log.Checkpoint(key + " исполнитель " + value)
          self.AllureReportTemplate(abs_path, name_file, "Одобрение санкции", "passed", {"message": f"{key} исполнитель {value}"},
                                                  'VCLObject("frmExecutors")', "Санкция одобрена", new_path, "passed", 1, 2, rm=True)

          Sys.Process("COLVIR").VCLObject("frmExecutors").Close()
        else:
          Log.Warning("Список cанкционирования пуст")
          self.AllureReportTemplate(abs_path, name_file, "Поиск санкции", "failed", {"message": 'Список cанкционирования пуст'},
                                    'VCLObject("frmOperJournal")', "Санкция не найдена", new_path, "failed", 1, 1, rm=True)
        Sys.Process("COLVIR").VCLObject("frmOperJournal").Close()
        return list_status, list_sanction
        
    def UndoStandartSanctionOperation(self, input_login_type=None, name_scen=None, name_case=None, name_module=None, name_file=None, **need_filters):
        """ Отмена санкционирования операций под необходимым пользователем 
        без определенного порядка санкций, т.е подряд (порядок должен быть уже определен заранее)
        Поля для заполнения фильтра передаются в виде словаря ПОЛЕ=значение (без кавычек если значение ключа это переменная)
        Если не передан логин, будет использован уже запущенный пользователь 
        """
        self.input_login_type = input_login_type
        self.need_filters = need_filters
        list_status = False # меняется на True, если санкция отменена успешно
        list_sanction = True # меняется на False, если необходимо отменить санкцию еще одним исполнителем 
        self.name_scen = name_scen
        self.name_case = name_case
        self.name_module = name_module
        self.name_file = name_file
        # Создание главной иерархии json отчета
        name_file = f'{self.GetRandomNumber()}_{self.name_file}.json'
        user_name = self.GetUserName() #Получение логина пользователя, чтобы функция работала под разнымми пользователями
        new_path = self.GetEnviron('NEW_PATH')
        self.CreateJsonFile(name_file) #Создание файла джейсон с пустым словарем в теле
        key = ["name", "description", "start"]
        value = [f"Санкционирование операции {self.name_scen} по {self.name_case}", f"Санкционирование операции {self.name_scen}", self.GetDateTimeMilli()]
        abs_path = self.FindAbsPathFile(name_file) # Получение абсолютного пути файла
        self.AddKeyValueJson(abs_path, key, value)
        def_dict = self.GetDefaultDict(abs_path)
        key_labels_suite = ["name", "value"]
        value_labels_suite = ["suite", f"{self.name_module}"]
        self.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
        key_labels_subsuite = ["name", "value"]
        value_labels_subsuite = ["subSuite", f"Санкционирование операции {self.name_scen}"]
        self.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
        # ----------------------------------------------------------------------------------------------------------------------------
        if self.input_login_type is not None:
          login_user, pass_user = self.GetLoginPass(self.input_login_type)
          self.LoginInColvir(login_user, pass_user)
        # проверка на нулевой референс
        if self.need_filters['REF_OPER'] == 0 or self.need_filters['REF_OPER'] == '0':
          Log.Warning('На санкционирование передан референс 0, проверьте предыдущий тест')
          #log = 'Ошибка' 
          #self.SaveAutologs(self.name_scen,self.name_case,log)
          return list_status, list_sanction
        self.TaskInput('OPERJRNRAT')
        self.SetFilter(SET_RAT=0, btnOther='', fields=self.need_filters)
        self.WaitLoadWindow("frmOperJournal", time_await=30000)
        find_doc = self.GetGridDataFields("frmOperJournal", "NAMEOPRMOV") 
        if find_doc[0].replace("\'", ''):
          Log.Checkpoint(find_doc[0][:120])
          self.AllureReportTemplate(abs_path, name_file, "Поиск санкции", "passed", {"message": find_doc[0][:120]},
                                            'VCLObject("frmOperJournal")', "Санкция найдена", new_path, "passed", 1, 1)
          but_undo_sanction = Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnRefuse")
          but_undo_sanction.Click()
          if Sys.Process("COLVIR").WaitWindow("TForm", "Отменить одобрение", -1, 2500).Exists:
            reason_undo = Sys.Process("COLVIR").Dialog("Отменить одобрение").Window("TEdit", "", 1)
            reason_undo.Keys("Отменяю полностью")
            but_ok_undo = Sys.Process("COLVIR").Dialog("Отменить одобрение").Button("OK")
            but_ok_undo.Click()
          if not self.ErrorMessageHandler(): # проверка на ошибку отмены санкции
            self.CheckOperEndWindow()
            list_status = True 
          executors_but = Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnExecutors")
          executors_but.Click()
          self.WaitLoadWindow("frmExecutors")
          dict_res = self.DBGetSanctionInfo("frmExecutors")
          list_wait = []
          list_desine = []
          for key, value in dict_res.items():
            if value is not None and key.startswith('Отказ'):
              Log.Checkpoint(key + " исполнитель " + value)
            if key.startswith('Ожидает'):
              list_wait.append(key)
            elif key.startswith('Отказ'):
              list_desine.append(key)
          if len(list_wait) != len(list_desine):
            list_sanction = False
          self.AllureReportTemplate(abs_path, name_file, "Одобрение санкции", "passed", {"message": f"{key} исполнитель {value}"},
                                                            'VCLObject("frmExecutors")', "Санкция одобрена", new_path, "passed", 1, 2, rm=True)
          Sys.Process("COLVIR").VCLObject("frmExecutors").Close()
        else:
          Log.Warning("Список cанкционирования пуст")
          self.AllureReportTemplate(abs_path, name_file, "Поиск санкции", "failed", {"message": 'Список cанкционирования пуст'},
                                          'VCLObject("frmOperJournal")', "Санкция не найдена", new_path, "failed", 1, 1, rm=True)
        Sys.Process("COLVIR").VCLObject("frmOperJournal").Close()
        return list_status, list_sanction
    
    def PrioritySanction(self, contract_number):
        """ Санкционирование операций согласно очередности выставления в журнале операции """
        self.contract_number = contract_number
        select = """ 
        select  opchr.code as CHACODE, t.sopr as SUMMA
        from t_operjrn t, T_OPRCHR_STD opchr, t_ord o
        where opchr.id = t.cha_id
        and t.rat_id is not null
        and t.ord_id = o.id
        and t.dep_id =  o.dep_id
        and o.code = '""" + self.contract_number + """'  
        order by t.njrn asc """
        result = self.OracleHandlerDB(select)
        dict_rec = {}
        for line in result:
          dict_rec[line[0]] = line[1]
        return dict_rec

    def SanctionRepeatedInput(self, order_type,doc_num,summ_oper,payer_acc,payer_iin,recipient_acc,
                              recipient_iin,bik_bank_recipient,KNP,KOD,KBE,KBK,input_login_type=None):
        """ Санкционирование повторным вводом расчетных документов"""
        self.input_login_type = input_login_type
        self.order_type = order_type
        self.doc_num = doc_num
        self.summ_oper = summ_oper
        self.payer_acc = payer_acc
        self.payer_iin = payer_iin
        self.recipient_acc = recipient_acc
        self.recipient_iin = recipient_iin
        self.bik_bank_recipient = bik_bank_recipient
        self.KNP = KNP
        self.KOD = KOD
        self.KBE = KBE
        self.KBK = KBK    
        if self.input_login_type is not None:
          login_user, pass_user = self.GetLoginPass(self.input_login_type)
          self.LoginInColvir(login_user, pass_user)      
        self.TaskInput('BRNPAYVRF')
        self.WaitLoadWindow("frmOrdPayVrfList")
        create_but = Sys.Process("COLVIR").VCLObject("frmOrdPayVrfList").VCLObject("btnSearch")
        create_but.Click()
        self.WaitLoadWindow("frmDynamicDialog")
        order_type_field = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("KSO_CODE")')
        order_type_field.Keys(self.order_type)
        doc_date = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("DORD")')
        doc_date.Keys(self.NormalDateMask())
        doc_date.Keys("[Tab]")
        execute_date = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("DVAL")')
        execute_date.Keys(self.NormalDateMask())
        execute_date.Keys("[Tab]")
        payer_account = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("CODE_ACL")')
        payer_account.Keys(self.payer_acc)
        summ_operation = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("AMOUNT")')
        summ_operation.Keys(self.summ_oper)
        payer_iin_field = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("RNN_CL")')
        payer_iin_field.Keys(self.payer_iin)
        bank_recipient = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("CODE_BCR")')
        bank_recipient.Keys(self.bik_bank_recipient)
        recipient_account = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("CODE_ACR")')
        recipient_account.Keys(self.recipient_acc)
        if KBK:
          KBK_field = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("KBK")')
          KBK_field.Keys(self.KBK)
        recipient_iin_field = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("RNN_CR")')
        recipient_iin_field.Keys(self.recipient_iin)
        KOD_field = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("CODE_OD")')
        KOD_field.Keys(self.KOD)
        KNP_field = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("KNP")')
        KNP_field.Keys(self.KNP)
        KBE_field = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("CODE_BE")')
        KBE_field.Keys(self.KBE)
        doc_number_field = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("CODE")')
        doc_number_field.Keys(self.doc_num)
        Log.Event("Поля основной формы заполнены")
        ok_button = self.FindChildField("frmDynamicDialog", "Name", 'VCLObject("btnOK")')
        ok_button.Click()
        # если не найден документ прерываемся
        if Sys.Process("COLVIR").WaitWindow("TMessageForm", "Информация", -1, 2500).Exists:
          Log.Warning("Документ номер "+ str(self.doc_num) +" с указанными реквизитами не найден")
          Sys.Process("COLVIR").Dialog("Информация").Close()
          Sys.Process("COLVIR").VCLObject("frmOrdPayVrfList").Close()
          return
        elif Sys.Process("COLVIR").WaitVCLObject("frmMailOrdDynDtl2", 25000).Exists:
          dict_fileds = {"Код операции":"edCodeSt","Номер документа":"edCode","Дата документа":"edDateFrom",
                      "Дата исполнения":"edDval","Счет плательщика":"edCodeAcl","ИИН плательщика":"edRnnCl", 
                      "ФИО плательщика":"edTxtPay","Сумма операции":"edSdok","Счет получателя":"edCodeAcr", 
                      "ИИН получателя":"edRnnCr","ФИО получателя":"edTxtBen","Назначение платежа":"edTxtDscr",
                      "КБК":"edCodeBc","КНП":"edKNP","КОД":"edCODE_OD","КБК":"edCODE_BE"}
          for key, value in dict_fileds.items():
            need_field = self.FindChildField("frmMailOrdDynDtl2", "Name", 'VCLObject('+ value +')')
            if not need_field.ReadOnly:
              Log.Warning("Поле " + key + " расчетного документа доступно к редактированию")
          button_save = Sys.Process("COLVIR").VCLObject("frmMailOrdDynDtl2").VCLObject("btnSave")
          button_save.Click()
          if not self.ErrorMessageHandler():
            self.WaitLoadWindow("frmDynamicDialog")
          Sys.Process("COLVIR").VCLObject("frmDynamicDialog").Close()
          Sys.Process("COLVIR").VCLObject("frmMailOrdDynDtl2").Close()
          jur_oper = Sys.Process("COLVIR").VCLObject("frmOrdPayVrfList").VCLObject("btnOperJrn")
          jur_oper.Click()
          self.WaitLoadWindow("frmOperJournal")
          user_exec = Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnExecutors")
          user_exec.Click()
          self.WaitLoadWindow("frmExecutors")
          dict_res = self.DBGetSanctionInfo("frmExecutors")
          for key, value in dict_res.items():
            if value is None:
              Log.Warning(key + " санкция не была проставлена")
            else:
              Log.Checkpoint(key + " получена " + value)
          Log.Checkpoint("Расчетный документ " + str(self.order_type) + " номер " + str(self.doc_num) + " успешно санкционирован повторным вводом")
          Sys.Process("COLVIR").VCLObject("frmExecutors").Close()
          Sys.Process("COLVIR").VCLObject("frmOperJournal").Close()       
        else:
          Log.Warning("Не найдено окно 'Платежное поручение клиента' или время ожидания окна истекло")
        Sys.Process("COLVIR").VCLObject("frmOrdPayVrfList").Close()
           
    def GetReferInfo(self, refer, set_rat, date_rat):
        """ Получение и возврат ID и NJRN записи из журнала операций по референсу операции, дате и 
        типу санкции. Тип санкции set_rat может быть в двух состояних: '1' - проставление санкции и '0' - 
        снятие санкции """
        self.refer = refer
        self.set_rat = set_rat
        self.date_rat = date_rat
        if self.set_rat == '1':
          rat_filter = """ and ROWNUM <= '20001' and j.REFER like '""" + str(self.refer) + """' ||'%' 
                          and j.DOPER = '""" + self.date_rat + """' and ('""" + self.set_rat + """'='1' and j.RAT_ID is not null and 
                          exists(select 1 from DUAL where C_PKGGRANT.fChkVrf (j.RAT_ID,C_vrf_Journal)=1
                          and C_PKGGRANT.fChkJrnVrf(j.ID,j.NJRN,10,j.BOP_ID,j.NOPER,j.TUS_ID) = 1)) 
                          order by NSDOK desc, EXECDT desc , NJRN desc """
        else:
          rat_filter = """ and ROWNUM <= '20001'  and j.REFER like '""" + str(self.refer) + """' ||'%' 
                           and j.DOPER = '""" + self.date_rat + """' and ('""" + self.set_rat + """'='0' and j.UNDOFL='0' and 
                           exists(select 1 from DUAL where C_PKGGRANT.fChkVrf(nvl(T_pkgDtlLst.fUndoRat(j.ID,j.NJRN),-1))=1 
                           and C_PKGGRANT.fChkJrnVrf(j.ID,j.NJRN,10,j.BOP_ID,j.NOPER,j.TUS_ID)=1)) 
                           order by NSDOK desc, EXECDT desc , NJRN desc """
        select = """  Select j.ID, j.NJRN,j.DEP_ID, j.ORD_ID,
            (select code from T_ORD t where j.DEP_ID = t.DEP_ID and j.ORD_ID = t.ID) as DOCNUM,
            j.BOP_ID, T_BOP_DSCR_STD.CODE as BP_CODE,j.DOPER,j.NOPER,s.NAME,j.UNDOFL, j.CANCELFL, 
            (select CODE from C_DEP_STD where C_DEP_STD.ID = j.DEP_ID) as DEP_CODE,
            opchr.CODE as CHA_CODE,j.CHA_ID,s.NAME as SC_NAME,
            TO_NUMBER((case when j.UNDOFL = '0' and nvl(j.CANCELFL,'0') = '0' then T_pkgDtlLst.GetJrnSum(j.ID, j.NJRN, '0') else null end)) as NSDOK,
            (select CODE from C_USR where ID = j.TUS_ID) as TUS_CODE, j.EXECDT,j.TRA_ID,
            substr(nvl(nvl(j.DSCR, nvl((select LONGNAME from T_OPRCHR_LNG where ID = opchr.ID and LNG_ID = P_Lng),opchr.LONGNAME)),s.NAME),1,250) as NAMEOPRMOV,
            (select CODE from T_VAL_STD where ID = j.VAL_ID) as VAL_CODE
            From 
            T_OPERJRN j,T_PROCESS,  T_SCEN s,T_BOP_DSCR_STD,T_OPRCHR_STD opchr
          Where 
            j.ID = T_PROCESS.ID and s.ID = j.BOP_ID and s.NORD = j.NOPER and j.BOP_ID = T_BOP_DSCR_STD.ID(+) and
            j.CHA_ID = opchr.ID(+) and exists (select 1 from T_SCEN_VRF where j.BOP_ID = ID and j.NOPER = NORD) """ + rat_filter
        result = self.OracleHandlerDB(select, need_zero='True')
        if result != '0':
          for line in result:
            return str(int(line[0])), str(int(line[1]))
        else:
          return 0, 0
      
    def CheckWaitSanction(self, id, njrn, undo_sanction=None):
        """ Получение списка записей санкционирования из вкладки 'Исполнители' по id и njrn из журнала операций и
        возврат первой строки с типом санкции в состоянии 'Ожидает санкции' (обрезая слова ожидает санции) """
        self.id = id.replace('"', '')
        self.njrn = njrn.replace('"', '')
        self.undo_sanction = undo_sanction
        select = """ select decode (ov.REFUSEFL, 1, 'Отказ ', '')||rd.NAME as NAME
            from T_OPERVRF ov, T_VRFDSC rd, C_USR
            where
            ov.ID = """ + self.id + """ and ov.NJRN = """ + self.njrn + """ and ov.RAT_ID = rd.ID 
            and ov.TUS_ID = C_USR.ID (+)
            union all
            select 'Ожидает '||rd.NAME as NAME
            from T_OPERJRN ov, T_VRFDSC rd, T_OPERVRF ovr
            where
            ov.ID = """ + self.id + """ and ov.NJRN = """ + self.njrn + """ and ov.RAT_ID = rd.ID and ovr.id(+) = ov.id 
            and ovr.njrn(+) = ov.njrn
            and ovr.refusefl(+) is null
            union all
            select 'Ожидает '||rd.NAME as NAME
            from T_OPERVRFNXT ov, T_VRFDSC rd
            where
            ov.ID = """ + self.id + """ and ov.NJRN = """ + self.njrn + """  and ov.RAT_ID = rd.ID
            """
        result = self.OracleHandlerDB(select)
        if result is not None:
          for line in result:
            if line[0].startswith('Санкция') and self.undo_sanction is not None:
              Log.Message(str(line[0][8:]))
              return line[0][8:]
            elif line[0].startswith('Ожидает') and self.undo_sanction is None:
              Log.Message(str(line[0][16:]))
              return line[0][16:]
        
    def GetListSanctionPaydoc(self):
        """ Возврат списка санкций и индекса логина санкционирующего в LoginPool для расчетных документов"""
        #типы санкций доступных начальнику РКК
        rkk_chief = ["Контроль платежей ЮЛ", "Контроль выплаты ГЦВП", "Контроль плат.ордеров","Контроль плат.ордеров", 
                    "Контроль мем.ордеров", "Пенсионные платежи", "Социальные платежи","Зарплатные платежи", 
                    "Зарплатные плат.внеш", "Платежи Банка", "Контроль ПП в инвал", "Операции по ПК",
                    "Платежи Банка УР", "Контроль плат.треб.пор", "налоговых платежей ФЛ", "Повторный ввод ПП", "доп_вал-й контрольPAY"]
        rkk_login_type = 'HEAD_RKK'
        #типы санкций доступных начальнику ДПФ
        dpf_chief = ["РКО (свыше 10 000 дол)", "Дебет счетов LIMIT", "Контроль целевого исп.", "контролера ПК",
                    "контролера WU", "Операции WU", "Операции по банкомату"]
        dpf_login_type = 'HEAD_OPERU'
        #типы санкций доступных валютному контроллеру
        valut_contr = ["валютного контроля", "Валютный контроль"]
        valut_login_type = 'VALUT_CONTR'
        #типы санкций по лимитной группе
        limit = ["Дебет счетов LIMIT", "Остаток 2203 больше 1860", "Остаток 2203 равен/меньше 1860"]
        limit_login_type = 'HEAD_CARD2'
        return rkk_chief, rkk_login_type, dpf_chief, dpf_login_type, valut_contr, valut_login_type, limit, limit_login_type
    
    def GetListSanctionCashdoc(self):
        """ Возврат списка санкций и индекса логина санкционирующего в LoginPool для кассовых документов"""
        #типы санкций доступных начальнику ОПЕРУ
        operu_chief = ["контролера", "Инд.условия", "Начальника ОПЕРУ", "Зачислить по документам", 
        "Контроль операций WU", "по расходным операциям ЗНР 6205/6286", "Контроль платежей ЮЛ", 
        "Контроль МП ЮЛ", "Дебет счетов LIMIT", "Контроль целевого исп.", 
        "контролера ПК", "контролера WU", "Операции WU", "Операции по банкомату", "без кода подтверждения"]
        operu_chief_login_type = 'HEAD_OPERU'
        #типы санкций доступных валютному контроллеру
        valut_contr =  ["валютного контроля"]
        valut_login_type = 'VALUT_CONTR'
        #типы санкций доступных СО контроллеру
        soprcontr = ["по актуальным доверн.", "на вн/б и меморанд.док", "Контроль комиссии ОПЕР", "до 1000 МРП","свыше 1000 МРП",
                      "контролера (нач.отдела", "Операции по ПК", "вал. контролера СО", "Открытие счетов",
                      "Контроль комиссии"]
        soprcontr_login_type = 'SK_OPERCONTR_DEP'
        return operu_chief, operu_chief_login_type, valut_contr, valut_login_type, soprcontr, soprcontr_login_type
    
    def DisconnectLimitAccount(self, contract_number):
        """ Снятие лимитов по счетам клиента, входной параметр - номер договора. Исполь-ся в Undo_Sanction_Acceptance_Deposit """
        self.contract_number = contract_number
        query = """ declare
        begin for rec in (select s.id, s.dep_id
                      from t_ord s
                     where s.code = '""" + self.contract_number + """') loop
        begin
            update t_lim v
               set v.todate = (trunc(sysdate)-1)
             where v.ord_id = rec.id
               and v.orddep_id = rec.dep_id;
            commit; end; end loop; end; """
        self.OracleHandlerDB(query, dml_query='True')
    
    def GetListSanctionInterPay(self):
      """ Возврат списка санкций и индекса логина санкционирующего в LoginPool для международных переводов"""
      #типы санкций доступных контролеру
      soprcontr = ["контролера", "Контроль комиссии ОПЕР", "вал. контролера СО", "Опер контроль на МП", 
      "Контроль ПП в инвал", "Контроль платежей ЮЛ", "Контроль МП ЮЛ", "РКО (свыше 10 000 дол)", "Операции по ПК", 
      "Контроль целевого исп.", "контролера ПК", "Платежи Банка УР", "по актуальным доверн.", "без кода подтверждения"]
      soprcontr_login_type = 'SOPRCONTR'
      #типы санкций доступных валютному контроллеру
      valut_contr =  ["валютного контроля", "Заявки на продажу вал.", "Валютный контроль", "Вал.контроль вход.пл.",
       "Контроль комиссии", "доп_валютного контроля"]
      valut_login_type = 'VALUT_CONTR'
      return soprcontr, soprcontr_login_type, valut_contr, valut_login_type
      