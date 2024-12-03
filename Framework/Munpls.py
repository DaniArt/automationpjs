from ColvirFramework import *


class Munpls(CommonOperation):
    """ Класс работы с задачей MUNPLS """

    def PaymentOrderValidator(self, wndname, nalog=''):
        """Валидатор полей платежного или кассового ордера по исполненным документам в коммуналке"""
        self.wndname = wndname
        self.nalog = nalog
        self.WaitLoadWindow(self.wndname)
        if self.wndname == "frmContFPayCardDet":
          describe = self.FindChildField(self.wndname, "Name", 'VCLObject("mmTXT_DSCR")')
        else:
          describe = self.FindChildField(self.wndname, "Name", 'VCLObject("edTxtDscr")')
        self.FieldValueValidator('Назначение платежа', describe, 'text')
        self.CheckValuesKNP(self.wndname)
        # только для платежных ордеров
        if self.nalog:
          nalog_tab = self.FindChildField(self.wndname, "Name", 'PageTab("Налоги")')
          nalog_tab.Click()
          KBK_field = self.FindChildField(self.wndname, "Name", 'VCLObject("edCodeBc")')
          if re.findall('(\d+)', KBK_field.Child(0).Text):  # ищем есть ли цифры в поле
            Log.Event("Автозаполнение поля 'КБК' отработало успешно")
          else:
            Log.Warning("Значение поля 'КБК' пусто")
        Log.Checkpoint("Поля документа с назначением " + describe.Text[:140] + "... валидированы")
        Sys.Process("COLVIR").VCLObject(self.wndname).Close()
      
    def PayOrderListCheck(self, wndname, nalog=''):
        """ Проверка списка платежек или кассовых ордеров по коммунальным платежам """
        self.wndname = wndname
        self.nalog = nalog
        if self.wndname == "frmContFPayCardDet":
          btn_pay_ord = Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnOrd")
          # если открывается список платежей, а не сам ордер, проверка в цикле
          if Sys.Process("COLVIR").WaitVCLObject("frmPayOrdLstJRN", 1600).Exists:
            for index in range(2): # зашита проверка 2 документов в списке
              if index > 0:
                Sys.Desktop.KeyDown(VK_DOWN)
                Sys.Desktop.KeyUp(VK_DOWN)
              btn_ok_picker = self.FindChildField("frmPayOrdLstJRN", "Name", 'VCLObject("btnOK")')
              btn_ok_picker.Click()
              self.PaymentOrderValidator(self.wndname, self.nalog)
              if index == 0:
                btn_pay_ord.Click()
              Delay(800)
          else:
            self.PaymentOrderValidator(self.wndname, self.nalog)        
        elif self.wndname == "frmCashOrdDynDtl2":
          btn_cash_order = Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnCashOrd")
          # если открывается список платежей, а не сам ордер, проверка в цикле
          if Sys.Process("COLVIR").WaitVCLObject("frmCashOrdLstJRN", 1600).Exists:
            for index in range(2): # зашита проверка 2 документов в списке
              if index > 0:
                Sys.Desktop.KeyDown(VK_DOWN)
                Sys.Desktop.KeyUp(VK_DOWN)
              btn_ok_picker = self.FindChildField("frmCashOrdLstJRN", "Name", 'VCLObject("btnOK")')
              btn_ok_picker.Click()
              self.PaymentOrderValidator(self.wndname, self.nalog)
              if index == 0:
                btn_cash_order.Click()
              Delay(800)
          else:
            self.PaymentOrderValidator(self.wndname, self.nalog)
        
    def LoadMTReversal(self, ben_acc, name_ben_acc, iin_ben, bank_ben, payer_acc, payer_acc_name, iin_payer,
                      paydoc_num, paydoc_date, paydoc_refer, summ_doc, pay_identy, fam_detail, name_detail,
                      surname_detail, date_detail, iin_detail, period_paydoc):                    
        """Формирование МТ ошибки коммунального платежа и имитация получения его из внешней системы для сторно 
        """
        self.ben_acc = ben_acc
        self.name_ben_acc = name_ben_acc
        self.iin_ben = iin_ben
        self.bank_ben = bank_ben
        self.payer_acc = payer_acc
        self.payer_acc_name = payer_acc_name
        self.iin_payer = iin_payer
        self.paydoc_num = paydoc_num
        self.paydoc_date = paydoc_date
        self.paydoc_refer = paydoc_refer
        self.summ_doc = summ_doc
        self.pay_identy = pay_identy
        self.fam_detail = fam_detail
        self.name_detail = name_detail
        self.surname_detail = surname_detail
        self.date_detail = date_detail
        self.iin_detail = iin_detail
        self.period_paydoc = period_paydoc    
        mask_refer = 'GCVP-00' + str(self.DocNumberGenerator('big_value'))
        select = """declare iErr number; cCRLF varchar2(2) := CHR(13) || CHR(10); cSUB char(1) := CHR(26); 
                    ErrMsg varchar2(500);
                    begin  
                    t_log.clean; 
                    c_pkgIe.pFromMt(iErr, 
                    'MSGID=33039863;MSGTYPE=102;SENDER=SCLEAR00000;'||cSUB|| 
                    '{1:F01K059470000000010066410}'||cCRLF||
                    '{2:O1021806071505SCLEAR00000000000000001806071506U}'||cCRLF||
                    '{4:'||cCRLF||
                    ':20:""" + mask_refer + """'||cCRLF||
                    ':50:/D/""" + self.ben_acc + """'||cCRLF||
                    '/NAME/""" + self.name_ben_acc + """'||cCRLF||
                    '/IDN/""" + self.iin_ben + """'||cCRLF||
                    '/CHIEF/Сабыржанов С.С.'||cCRLF||
                    '/MAINBK/Жакупова Г.Т.'||cCRLF||
                    '/IRS/1'||cCRLF||
                    '/SECO/1'||cCRLF||
                    ':52B:""" + self.bank_ben + """'||cCRLF||
                    ':57B:ALFAKZKA'||cCRLF||
                    ':59:""" + self.payer_acc + """'||cCRLF||
                    '/NAME/""" + self.payer_acc_name + """'||cCRLF||
                    '/IDN/""" + self.iin_payer + """'||cCRLF||
                    '/IRS/1'||cCRLF||
                    '/SECO/9'||cCRLF||
                    ':70:'||cCRLF||
                    '/NUM/32229659'||cCRLF||
                    '/DATE/180607'||cCRLF||
                    '/SEND/07'||cCRLF||
                    '/VO/01'||cCRLF||
                    '/KNP/021'||cCRLF||
                    '/PSO/01'||cCRLF||
                    '/PRT/01'||cCRLF||
                    '/ASSIGN/Возврат ошибочных элементов платежа № """ + self.paydoc_num + """ от """ + self.paydoc_date + """ '||cCRLF||
                    'референс """ + self.paydoc_refer + """ на сумму """ + self.summ_doc + """. Ошибка на 1 чел. на сумму """ + self.summ_doc + """'||cCRLF||
                    ':21:1'||cCRLF||
                    ':32B:KZT""" + self.summ_doc + """'||cCRLF||
                    ':70:'||cCRLF||
                    '/OPV/""" + self.pay_identy + """'||cCRLF||
                    '/FM/""" + self.fam_detail + """'||cCRLF||
                    '/NM/""" + self.name_detail + """'||cCRLF||
                    '/FT/""" + self.surname_detail + """'||cCRLF||
                    '/DT/""" + DateTimeToFormatStr(self.date_detail, '%Y%m%d') + """'||cCRLF||
                    '/IDN/""" + self.iin_detail + """'||cCRLF||
                    '/PERIOD/""" + DateTimeToFormatStr(self.period_paydoc, '%m%Y') + """'||cCRLF||
                    '/ASSIGN/[ИИН] не соответствует указанным Ф.И.О.'||cCRLF||
                    ':32A:""" + DateTimeToFormatStr(self.paydoc_date, '%y%m%d') + """KZT""" + self.summ_doc + """'||cCRLF||
                    '-}'||cCRLF);
                    DBMS_OUTPUT.PUT_LINE(to_chaR(IeRR)); if IeRR <> 0 then select c_pkgIe.READ_ERRMSG(ROWNUM) into ErrMsg 
                    from DUMMY 
                    where ROWNUM <= c_pkgIe.ERRMSG_COUNT; DBMS_OUTPUT.PUT_LINE(substr(ErrMsg, 1, 250)); 
                    DBMS_OUTPUT.PUT_LINE(substr(ErrMsg, 250)); end if; T_LOG.print; end;"""    
        Log.Message(select)
        self.OracleHandlerDB(select, dml_query='True')
        return mask_refer
    
    
    def GetFIOByIIN(self, bin_iin):
        """ Получение ФИО клиента по ИИН из таблицы G_IIN """
        self.bin_iin = bin_iin
        select = """select FIO from g_iin
                    where iin = '""" + self.bin_iin + """'"""
        result = self.OracleHandlerDB(select)
        if result is not None:
          return result[0][0]
      
    def PayFieldsValidator(self, wndname_pay):
        """ Проверка сохранения полей во вкладке 'Дополнительно' после сохранения платежа """
        self.wndname_pay = wndname_pay    
        docs_type = self.FindChildField(self.wndname_pay, "Name", 'VCLObject("edPassType")', "internal")
        docs_number = self.FindChildField(self.wndname_pay, "Name", 'VCLObject("edPassNum")', "internal")
        docs_organization = self.FindChildField(self.wndname_pay, "Name", 'VCLObject("edPassOrg")', "internal")
        docs_date = self.FindChildField(self.wndname_pay, "Name", 'VCLObject("edPassDate")', "internal")
        cli_famil = self.FindChildField(self.wndname_pay, "Name", 'VCLObject("edPName1")', "internal")
        cli_name = self.FindChildField(self.wndname_pay, "Name", 'VCLObject("edPName2")', "internal")
        cli_surname = self.FindChildField(self.wndname_pay, "Name", 'VCLObject("edPName3")', "internal")
        cli_adress_type = self.FindChildField(self.wndname_pay, "Name", 'VCLObject("edAdrTyp")', "internal")
        cli_full_adress = self.FindChildField(self.wndname_pay, "Name", 'VCLObject("memAddress")')
        cli_resident = self.FindChildField(self.wndname_pay, "Name", 'VCLObject("edRegCode")', "internal")
        self.FieldValueValidator('Тип документа', docs_type, 'text')
        self.FieldValueValidator('Номер документа', docs_number, 'number')
        self.FieldValueValidator('Кем выдан', docs_organization, 'text')
        self.FieldValueValidator('Дата выдачи', docs_date, 'number')
        self.FieldValueValidator('Фамилия плательщика', cli_famil, 'text')
        self.FieldValueValidator('Имя плательщика', cli_name, 'text')
        self.FieldValueValidator('Отчество плательщика', cli_surname, 'text')
        self.FieldValueValidator('Тип адреса', cli_adress_type, 'text')
        self.FieldValueValidator('Полный адрес', cli_full_adress, 'text')
        self.FieldValueValidator('Страна резиденства', cli_resident, 'text')