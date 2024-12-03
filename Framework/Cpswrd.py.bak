from ColvirFramework import *

  
class Cpswrd(CommonOperation, GenerateTestingData, CreateJsonReport):
    """ Класс работы с задачей CPSWRD """  
  
    def GetLoginARM(self, login):
        """ Получение АРМа логина через запрос к БД """
        self.login = login    
        select = """
          select c.USE_NAME
          from CV_USR2 c
          where c.CODE = '""" + self.login + """'
        """
        result = self.OracleHandlerDB(select)
        if result is not None:
          return result[0][0]
      
    def GetGrantsProfileUser(self, login_user):
        """ Получение назначенных профилей полномочий через запрос к БД,
        потому что наши редиски не привязывают некоторые профили к АРМ"""
        self.login_user = login_user    
        select = """
            select GR.LONGNAME
            from C_GRNROL GR, C_USRROL UR , c_usr u 
            where GR.ID=UR.ROL_ID  
              and exists (select 1 from DUAL where C_pkgAccess.fChkRolForAdm(0,GR.ID)=1)
              and u.id = ur.usr_id 
              and u.code = '"""+ self.login_user +"""'"""
        result = self.OracleHandlerDB(select)
        return result
    
    def GetLoginStatus(self, login):
        """ Получение статуса логина через запрос к БД, по признакам: архивный, заблокирован, администратор.
        1 - да, 0 - нет"""
        self.login = login
        state = False
        select = """select c.ARCFL,c.ARESTFL
                    from CV_USR2 c
                    where  GROUPFL=0 AND exists(select 1 from dual where C_pkgUsr.fChkAdm(C.ID)=1)
                    and CODE like '"""+ self.login +"""'"""
        result = self.OracleHandlerDB(select)
        if result is not None:
          for line in result:
            if int(line[0]) == 1 or int(line[1]) == 1:
              Log.Warning('На учетной записи '+ self.login +' стоит признак архива и\или запрета')
              state = True
          self.GetAccountStatusDB(self.login)
        return state
    
    def SetLoginUnlock(self, need_login):
        """ Снятие признаков архива и\или ареста, изменение даты окончание действия учетной записи """
        self.need_login = need_login    
        self.TaskInput('MUSERL') 
        self.SetFilter(CODE=self.need_login)
        self.WaitLoadWindow("frmUsrList")
        result = self.GetGridDataFields("frmUsrList", "CODE")
        if result[0].replace("\'", '') == self.need_login:
          btn_edit = self.FindChildField("frmUsrList", "Name", "VCLObject('btnEdit')")
          btn_edit.Click()
          self.WaitLoadWindow("frmUsrDetail")
          arhive_box = self.FindChildField("frmUsrDetail", "Name", "VCLObject('chkARCFL')")
          arest_box = self.FindChildField("frmUsrDetail", "Name", "VCLObject('chkARESTFL')")
          if arhive_box.State == 1:
            arhive_box.Click()
            Log.Checkpoint('С учетной записи '+ self.need_login +' снят признак архива')
          if arest_box.State == 1:
            arest_box.Click()
            Log.Checkpoint('С учетной записи '+ self.need_login +' снят признак запрета')
          btn_save = self.FindChildField("frmUsrDetail", "Name", "VCLObject('btnSave')")
          btn_save.Click()
        else:
          Log.Warning('Переданный логин '+ self.need_login +' не найден  в списке')
        Sys.Process("COLVIR").VCLObject("frmUsrList").Close()
    
    def GetAccountStatusDB(self, need_login):
        """ Получение статуса учетной записи в БД """
        self.need_login = need_login
        status = False
        select = """SELECT username, account_status FROM dba_users
                    WHERE USERNAME = UPPER('"""+ self.need_login +"""')
                 """
        result = self.OracleHandlerDB(select)
        if result is not None:
          for line in result:
            if line[1] != 'OPEN':
              Log.Warning('Учетная запись '+ self.need_login +' заблокирована на уровне базы данных')
              status = True
          if status:
            select_update = """ALTER USER """+ self.need_login +""" ACCOUNT UNLOCK """
            self.OracleHandlerDB(select_update, dml_query='True')
            Log.Checkpoint('Учетная запись '+ self.need_login +' успешно разблокирована на уровне базы данных')
      
    def UpdateUserPosition(self, need_login):
        """ Установка будущей даты в параметре (окончание действия) учетной записи в задаче CPSWRD в случае истечении;
        устранение сообщение возникающая при подтверждении пароля 'Не найдена позиция для пользователя *учетная запись'
        """
        self.need_login = need_login
        select = """ select s.usr_id, to_char(s.todate,'dd.mm.yyyy') as todate from C_USER c, C_STFUSR s
                      where c.code = '""" + self.need_login + """' and s.usr_id = c.id """    
        result = self.OracleHandlerDB(select)
        date_operday = self.GetEnviron("DATE_OPERDAY")
        to_date = aqConvert.DateTimeToFormatStr(date_operday, "%d.%m.%Y")
        for value in result:
          normal_date = aqConvert.DateTimeToFormatStr(str(value[1]), "%d.%m.%y")
          if aqConvert.StrToDate(normal_date) < aqConvert.StrToDate(to_date):
            new_to_date = self.GetPlusDailyDate(777, to_date)
            future_date = aqConvert.DateTimeToFormatStr(new_to_date, "%d.%m.%Y")
            result_update = """ begin update C_STFUSR c set c.todate = to_date('""" + str(future_date) + """','DD.MM.YYYY')
                                       where c.usr_id = """ + str(value[0]) + """; commit; end; """
            self.OracleHandlerDB(result_update, dml_query='True')
            Log.Event('Срок действие даты истечение позиции пользователя ' + str(self.need_login) + ' обновлен')
          else:
            Log.Event('Дата истечения позиции пользователя равна ' + str(normal_date) + ' обновление срока не требуется')

    def OutlookSendMail(self, address, message_subject, text, name_user='', password=''):
        """ Метод отправки письма пользователям на почту Outlook
        входные параметры: адрес(например: bcc.kz), тема письма, текст письма
        имя пользователя, пароль пользователя"""
        self.address = address
        self.message_subject = message_subject
        self.text = text
        self.name_user = name_user
        self.password = password
        stand, alias_bd = self.GetTestStandAliasDB()    
        begin = """ begin Z_MAIL_PKG.SET_MAILSERVER(c_pkgprm.fgetvalprm('Z_026_SMTP_IP_INSIDE'));
                            z_mail_pkg.send('""" + self.address + """',
                            '""" + self.message_subject + """',
                            '""" + self.text + ', ' + self.name_user + '  ' + self.password + '  ' + alias_bd + """',
                            'InfoQa-@bcc.kz');
                            commit; end; """
        self.OracleHandlerDB(begin, dml_query='True')
    
    def ChangePasswordDBUsers(self, agile_address, message_subject, text, relog_user_login, relog_new_password, package_name):
        """ Изменение паролей пользователям в девелопере"""
        self.agile_address = agile_address
        self.message_subject = message_subject
        self.text = text
        self.relog_user_login = relog_user_login
        self.relog_new_password = relog_new_password
        self.package_name = package_name    
        query = """ALTER USER """ + self.relog_user_login + """ IDENTIFIED BY """ + self.relog_new_password + """
        """
        self.OracleHandlerDB(query, dml_query='True')
        self.OutlookSendMail(agile_address, message_subject, text, relog_user_login, relog_new_password)
        Log.Checkpoint("Пользователю " + self.relog_user_login + " изменён пароль с помощью запроса в БД")
        # добавим привилегии на пакеты/процедуры/функции
        self.GrantProcedures(self.relog_user_login,self.package_name)
    
    def GrantProcedures(self, database_login, package_name):
        """ Предоставление пользователям привилегий на редактирование/дебаг/логирование пакетов/процедур/функций 
        в среде разработки pl/sql developer
        входные параметры: /database_login - наименование учетной записи;
        /package_name - наименование пакета/процедуры/функции;"""
        self.database_login = database_login
        self.package_name = package_name    
        if self.package_name:
          final_package = self.package_name.split(';')
          query = """ GRANT DEBUG CONNECT SESSION TO """ + self.database_login  + """ """
          self.OracleHandlerDB(query,dml_query='True')
          for final_package in zip(final_package):
            query = """ GRANT EXECUTE on """ + final_package[0]  + """ TO """ + self.database_login  + """ """
            self.OracleHandlerDB(query,dml_query='True')
            Log.Checkpoint('Пользователю ' + self.database_login  + ' добавлены привилегии на пакет/процедуру/функцию '
                                                                      + final_package[0])
        else:
          Log.Event('Отсутствует наименование пакетов/процедур/функций в csv.файле для предоставление привилегий пользователю ' + self.database_login)
        