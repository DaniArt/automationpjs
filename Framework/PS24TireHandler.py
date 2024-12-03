from ColvirFramework import *


class PS24TireHandler(CommonOperation):
    """ Класс работы с шиной процессинга
    ссылка на документацию библиотеки: https://suds-py3.readthedocs.io/en/latest/
    При указание в переменной среде адрес добавлять адрес шины с окончанием ?wsdl , во избежания ошибки 500
    """
    def CheckRequest(self,client,type_case = "1"):
        """Проверка запроса"""
        self.client = client
        self.type_case = type_case
        status_code1 = self.client.last_received().getChild("soap:Envelope").getChild("soap:Body").getChild("ns2:capRes").getChild("ns2:header").getChild("ns2:status").getText()
        if status_code1 == "1":
          if self.type_case == "1":
            Log.Checkpoint("HTTP запрос выполнен успешно!",str(self.client.last_sent()))
            Log.Checkpoint("Ответ на HTTP запрос: ",str(self.client.last_received()))
            return True
          if type_case == "0":
            Log.Warning("HTTP запрос выполнен успешно, однако ожидалась ошибка",str(self.client.last_sent()))
            return False
        elif status_code1 == "0":
          if self.type_case == "1":
            error_code = self.client.last_received().getChild("soap:Envelope").getChild("soap:Body").getChild("ns2:capRes").getChild("ns2:header").getChild("ns2:errCode").getText()
            error_text = self.client.last_received().getChild("soap:Envelope").getChild("soap:Body").getChild("ns2:capRes").getChild("ns2:header").getChild("ns2:errText")
            if error_text is not None:
              error_text = error_text.getText()
            Log.Message(str(self.client.last_sent()))
            Log.Warning("Ошибка при выполнении HTTP запроса, код ошибки: " + str(error_code) + ", текст ошибки: " + str(error_text))
            return False
          elif self.type_case == "0":  
            error_code = self.client.last_received().getChild("soap:Envelope").getChild("soap:Body").getChild("ns2:capRes").getChild("ns2:header").getChild("ns2:errCode").getText()
            error_text = self.client.last_received().getChild("soap:Envelope").getChild("soap:Body").getChild("ns2:capRes").getChild("ns2:header").getChild("ns2:errText")
            if error_text is not None:
              error_text = error_text.getText()
            Log.Message(str(self.client.last_sent()))
            Log.Checkpoint("Ожидаемая ошибка при выполнении HTTP запроса, код ошибки: " + str(error_code) + ", текст ошибки: " + str(error_text))
            return True        
                
    def GetMaxTrID(self):
        """Получение максимального id транзакции"""
        select = """
                 select Max(ID) from
                (select trn.ID, trn.EXTIME from APT_TRN @cap trn
                UNION ALL
                select lac.ID, lac.EXTIME from APT_LOGACC@cap lac
                )global where global.ID>'780000000'
                order by EXTIME desc 
                """
        queryResult = self.OracleHandlerDB(select)
        if queryResult is not None:
          return int(str(queryResult[0][0]))
      
    def FindPSAccId(self,acc):
        """Поиск ID счата в пс"""
        self.acc = acc
        select_acc_id = """
                        select tidn.ACC_ID
                        from
                          APT_ACC@cap tacc,
                          APR_ACC@cap racc,
                          APR_CUR@cap rcur,
                          APT_BAL@cap tbal,
                          APT_IDN@cap tidn,
                          APR_IDN@cap aidn,
                          APR_LOCK@cap rlock,
                          APR_LOCK@cap accidnlock
                        where 
                          tacc.acc_id=racc.ID(+)
                          and tacc.cur_id=rcur.ID(+)
                          and tacc.id=tbal.id(+)
                          and tidn.ACC_ID=tacc.ID
                          and tidn.IDN_ID=aidn.ID
                          and accidnlock.id = tidn.lckfl    
                          and rlock.id = tacc.lckfl
                          and tidn.CODE = '""" + self.acc + """'
                          """
        queryResult = self.OracleHandlerDB(select_acc_id)
        if queryResult is not None:
          return str(queryResult[0][0])
      
    def CheckCanseledHold(self,hold_ref, acc):
        """Проверка закрытие холда""" 
        self.hold_ref = hold_ref
        self.acc = acc
        acid = self.FindPSAccId(self.acc)
        date_operday = self.GetEnviron("DATE_OPERDAY")
        select = """
        select substr(to_char(tachld.opntime,'DD.MM.YY'),1,8)
        from 
        APT_ACC@cap tacc,
        APT_ACCHLD@cap tachld,
        APR_HLD@cap ahld
        where 
        tacc.id=tachld.id(+)
        and tachld.hld_id=ahld.id(+)
        and 66<>'0'
        and tacc.ID='""" + str(acid) + """'
        and tachld.CODE = '""" + str(self.hold_ref) + """'
        order by tachld.opntime DESC
        """
        queryResult = self.OracleHandlerDB(select)
        if queryResult is not None:
          if str(queryResult[0][0]) == date_operday:
            Log.Checkpoint("Холд успешно отменен " + acc)
          else:
            Log.Warning("Дата закрытия не совпадает с текущей " + acc)
        
    def CheckABISHold(self,acc,amount):
        """Проверка холда в колвир"""
        self.acc = acc
        self.amount = amount
        acid = self.FindPSAccId(self.acc)
        date_operday = self.GetEnviron("DATE_OPERDAY")
        select_hold_reference = """
        select tachld.CODE
        from 
        APT_ACC@cap tacc,
        APT_ACCHLD@cap tachld,
        APR_HLD@cap ahld
        where 
        tacc.id=tachld.id(+)
        and tachld.hld_id=ahld.id(+)
        and 66<>'0'
        and tacc.ID='""" + str(acid) + """'
        and amount = '""" + self.amount + """'
        and trunc(tachld.opntime) >= TO_DATE('""" + date_operday + """', 'DD.MM.YY')
        order by tachld.opntime DESC
        """
        queryResult = self.OracleHandlerDB(select_hold_reference)
        if queryResult is not None:
          query_hold_reference = str(queryResult[0][0])
          Log.Checkpoint("Холд успешно отобразился на счёте " + acc)
          return query_hold_reference
        else:
          Log.Warning("Холд по заданному счёту и сумме отсутствует " + acc)
      
    def CheckABISTransaction(self,id_transaction,expected_trn_status,schet,amount,trn_code):
        """Проверка корректно ли транзакция села в АБИС"""
        self.id_transaction = id_transaction
        self.expected_trn_status = expected_trn_status
        self.schet = schet
        self.amount = amount
        self.trn_code = trn_code
        Delay(15000)
        select = """
              select trn.ID, trn.STATUS, idn.CODE, trn.Amount, a.CODE, cnl.code
              from
              apr_cnl @cap cnl,
              APR_TRN @cap a,
              APT_TRN @cap trn,
              apt_idn @cap idn,
              APR_STATUSTRN @cap stat
              where trn.ACC_ID=idn.ACC_ID
              and trn.ID = '""" + self.id_transaction + """'
              and (trn.STATUS = '""" + self.expected_trn_status + """'or trn.STATUS = '1')
              and trn.STATUS=stat.CONSTCODE
              and trn.CNL_ID=CNL.ID
              and idn.CODE = '""" + self.schet + """'
              and trn.Amount = '""" + self.amount + """'
              and a.CODE = '""" + str(self.trn_code) + """'
              and cnl.code = 'TWO'
              and rownum = 1
          """
        queryResult = self.OracleHandlerDB(select)
        if queryResult is not None:
          query_dict = {"id":str(queryResult[0][0]),"trn_status":str(queryResult[0][1]), "acc":str(queryResult[0][2]), "amt":str(queryResult[0][3]), "code":str(queryResult[0][4]), "cnl_code":str(queryResult[0][5])}
          true_dict = {"id":str(self.id_transaction),"trn_status":str(self.expected_trn_status), "acc":str(self.schet), "amt":str(self.amount), "code":str(self.trn_code), "cnl_code":"TWO"}
          if queryResult is not None:
            diff_fields = self.CompareDicts(query_dict,true_dict)
            if diff_fields:
              Log.Warning("Не совпадает поля " + str(diff_fields) + " с ожидаемыми значениями")
            else:
              Log.Checkpoint("Транзакция обработана успешно! " + self.id_transaction)
          elif queryResult is None:
            Log.Warning("Транзакция не обработана в АБИС " + self.id_transaction)
        else:
          Log.Warning("Запрос вернул None, возможо ошибка в статусе транзакции")
       
"""Подстановка Header-ов по типу транзакции"""
class SetAttribFINAPlugin(MessagePlugin):
    def marshalled(self, context):
        """Установка атрибутов тега capReq"""
        body = context.envelope.getChild('Body')
        params = body[0]
        params.set('capType', 'FINA')
        params.set('version', '3.0')  
  
class SetAttribRVSLPlugin(MessagePlugin):  
    def marshalled(self, context):
      """Установка атрибутов тега capReq"""
      body = context.envelope.getChild('Body')
      params = body[0]
      params.set('capType', 'RVSL')
      params.set('version', '3.0')
        
        
class SetAttribRVPTPluginPartlyUndo(MessagePlugin):
    def marshalled(self, context):
      """Установка атрибутов тега capReq"""
      body = context.envelope.getChild('Body')
      params = body[0]
      params.set('capType', 'RVPT')
      params.set('version', '3.0')
        
        
class SetAttribERRMPlugin(MessagePlugin):
    def marshalled(self, context):
      """Установка атрибутов тега capReq"""
      body = context.envelope.getChild('Body')
      params = body[0]
      params.set('capType', 'ERRM')
      params.set('version', '3.0')
        
class SetAttribBALNPlugin(MessagePlugin):
    def marshalled(self, context):
      """Установка атрибутов тега capReq"""
      body = context.envelope.getChild('Body')
      params = body[0]
      params.set('capType', 'BALN')
      params.set('version', '3.0')