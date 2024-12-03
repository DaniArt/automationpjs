import ColvirFramework


class Sql():
  CommonOperation = ColvirFramework.CommonOperation()
  
  @staticmethod
  def SimpleQuery(select):
    """Выполняет простой SQL запрос, который обязательно должен вернуть единственный результат
    Вх.парам: select (str) - SQL запрос
    Вых.парам: (any) Первое значние из первой строки или None"""
    query_result = Sql.CommonOperation.OracleHandlerDB(select)
    try:
        return query_result[0][0]
    except Exception:
        return None
      
      


  @staticmethod
  def SimpleLineQuery(select,col = 0):
    """Выполняет простой SQL запрос, который обязательно должен вернуть хотя-бы одну строку
    Вх.парам: select (str) - SQL запрос
    col (int) - количестов возвращаемых столбцов. 0 - вернет все столбцы
    Вых.парам: (list) Первая строка или []"""
    query_result = Sql.CommonOperation.OracleHandlerDB(select)
    if query_result is not None:
      if col > 0:
        return query_result[0][:col]
      else:
        return query_result[0]
    else:
      return [None]*col
      
  @staticmethod
  def SimpleLineQuery(select,col = 0):
    """Выполняет простой SQL запрос, который обязательно должен вернуть хотя-бы одну строку
    Вх.парам: select (str) - SQL запрос
    col (int) - количестов возвращаемых столбцов. 0 - вернет все столбцы
    Вых.парам: (list) Первая строка или []"""
    query_result = Sql.CommonOperation.OracleHandlerDB(select)
    if query_result is not None:
      if col > 0:
        return query_result[0][:col]
      else:
        return query_result[0]
    else:
      return [None]*col
      
  @staticmethod
  def GetDeaIdDepId(dea_number):
    """Возвращает id и dep_id договора по номеру договра"""
    select = f"""select  to_char(d.ID),  to_char(d.DEP_ID) from  T_ORD o, T_DEA d  where o.DEP_ID = d.DEP_ID and o.ID = d.ID
    and exists (select 1 from DUAL where c_pkgGrant.fChkUsrOrd_2(d.DEP_ID,d.ID,3)=1)  and o.CODE = '{dea_number}'"""
    return Sql.SimpleLineQuery(select,2)

  @staticmethod
  def GetAccOrdIdDepId(acc):
    """Возвращает ord_id, dep_id и id счета по номеру счета"""
    select = f"""SELECT to_char(ORD_ID), to_char(DEP_ID), to_char(ID) FROM G_ACCBLN WHERE CODE = '{acc}'"""
    return Sql.SimpleLineQuery(select,3)

  @staticmethod
  def GetDeaAcc(dea_id_or_dea_num,dea_dep_id=None):
    """Возвращает счет 2204 по id, dep_id  или по номеру договора"""
    if dea_dep_id is None:
      dea_id_or_dea_num,dea_dep_id = Sql.GetDeaIdDepId(dea_id_or_dea_num)
    if dea_id_or_dea_num is not None and dea_dep_id is not None:
      select = f"""select distinct p.code_acc from t_arldea o, t_deapayatr p where p.dep_id = o.dep_id
      and p.id = o.ord_id and p.nord = o.pay_nord and o.dep_id = '{dea_dep_id}' and o.ord_id =  '{dea_id_or_dea_num}'"""
      return Sql.SimpleQuery(select)
    else:
      return None
      
  @staticmethod    
  def StartCapJob():
    job = f'''begin bcm_user.bcm_pkg_job.pStartCapJob@cap; end;'''
    Sql.CommonOperation.OracleHandlerDB(job, dml_query='True') 
    
  @staticmethod   
  def set_cat(cli_id, cli_cat1, cli_cat2):
    """Возвращает счет 2204 по id, dep_id  или по номеру договора"""
    set_category = f"""
    declare
      l_clicode varchar(2000 char) := '{cli_id}'; --код клиента
      l_cat_id1 number := {cli_cat1}; --категори¤ 1
      l_cat_id2 number := {cli_cat2}; --категори¤ 2

      l_nNumErr number;
      l_cErrMsg varchar2(2000 char);

    begin
      delete from bcm_user.bcm_clicat_hst
       where trunc(sysdate) between fromdate and todate
         and (dep_id, id) in (select cli_dep_id, cli_id
                                from bcm_user.bcm_cliprm
                               where type_ref = 'CODE'
                                 and cvalue = l_clicode);

      commit;

      --”станавливаем категории на мес¤ц
      bcm_user.bcm_pkg_cat.pSaveBonusClass(pClicode  => l_clicode,
                                           pCatId_1  => l_cat_id1,
                                           pCatId_2  => l_cat_id2,
                                           pOperType => 'ACTIVATE',
                                           p_nNumErr => l_nNumErr,
                                           p_cErrMsg => l_cErrMsg);
      commit;

      dbms_output.put_line(l_nNumErr || ' - ' || l_cErrMsg);
    end;
    """
    Sql.CommonOperation.OracleHandlerDB(set_category, dml_query='True')