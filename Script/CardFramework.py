from ColvirFramework import *
from TaskMethods import *
from SQL import Sql
from TestVariables import*
#from Cpswrd import *


class CardFramework(CommonOperation, GenerateTestingData, CreateJsonReport, Sql):   
  """ Данный класс осуществляет коректную работу SOAP операции и проверку результатов после выполнения запросов """         
      
  def SoapRequest(url,body='',headers = {'content-type': 'application/soap+xml; charset=UTF-8'},timeout=90,need_result = False,http_method = 'post',need_full_response = False):  # TODO: need_result убрать, использовать need_full_response
    """ Метод для отправки HTTP запроса через библиотеку requests на вход принимает url, тело запроса и HTTP заголовки.
    Если статус ответа 200(ОК) на выход отдает содержимое ответа сервера, в противном случае None
    Если парамет need_result = True, на выход будет передаваться код ответа и содержимое ответа
    Если парамет need_full_response = True, на выход будет передаваться response полностью
    """
    Sys.Keys('[Win]')
    Delay(200)
    Sys.Keys('[Win]')
    Log.Event(f'Попытка выполнить HTTP запрос url = {url}')
    Log.Event(f'headers = {headers}')
    Log.Event(f'body = {body}')
    try:
      if http_method == 'post':
        response = requests.post(url,data=body.encode('utf-8'),headers=headers,verify=False,timeout=timeout)
      elif http_method == 'patch':
        response = requests.patch(url,data=body.encode('utf-8'),headers=headers,verify=False,timeout=timeout)
      elif http_method == 'get':
        response = requests.get(url,headers=headers,verify=False,timeout=timeout)
      Sys.Keys('[Win]')
      Delay(200)
      Sys.Keys('[Win]')
      if need_full_response:
        Log.Event(f'HTTP запрос выполнен успешно. Получен ответ: {response.text}')
        return response
      elif response.status_code == requests.codes.ok:
        Log.Event(f'HTTP запрос выполнен успешно. Получен ответ: {response.text}')
        if need_result:
          return response.status_code, response.content
        return response.content
      else:
        Log.Warning(f'Ошибка HTTP запроса, HTTP Status = {response.status_code}')
        Log.Event(f'Получен ответ: {response.text}')
        if need_result:
          return response.status_code, response.text
        return None
    except Exception as err:
      Log.Warning(f'Ошибка HTTP запроса: {err.args}')
      if need_result:
        return 999, str(err.args)
      return None

  def GetXmlValue(self,xml_str,tag_name):
    """ Возвращает занчение элемента с тегом = tag_name.
    На вход принимает строку содержащую XML, и полный путь к тегу
    """
    self.xml_str = xml_str
    self.tag_name = tag_name
    try:
      tree = ET.ElementTree(ET.fromstring(self.xml_str))
      root = tree.getroot()
      child = root.find(self.tag_name)
      return child.text
    except:
      Log.Warning('Ошибка при получении XML значения')
      return None

  def DeaExists(**kwargs):
    """ Проверяет существование договора в БД Colvir
    Вх.парам: kwargs['Договор'] (str) - номер договора;
    Вых.парам: {'Результат операции': (str) - OK или Договор не найден}
    Вых.парам:(bool) - True если договор найден, иначе False
    """
    Log.Event(f"Выполнияем проверку на существование договора {kwargs.get('Договор')}")
    select = f"""select  case count(*) when 1 then 'OK' else 'Договор не найден' end
    from  T_ORD o, T_DEA d where o.DEP_ID = d.DEP_ID and o.ID = d.ID  and o.CODE = '{kwargs.get('Договор')}'"""
    result = self.OracleHandlerDB(select)
    if result is not None and result[0][0] == 'OK':
      Log.Checkpoint('Договор найден')
      return {'Результат операции': 'OK'}
    else:
      Log.Event('Договор не найден')
      return {'Результат операции': 'Договор не найден'}     
      
      
  def CheckAccBalance(self, acc_crd):
    """ Функция проверяет баланс текущего счета в БД Colvir """
    result = ''
    Log.Event(f"Выполнияем запрос на получение ID по счету {acc_crd}")
    select = f"""select c.acc_id from apt_idn@cap c where c.code = '{acc_crd}'""" # Достаем идентификатора аккаунта
    check_acc = self.SimpleQuery(select)
    select = f"""select n.balance from apt_trn@cap n where n.acc_id = '{check_acc}' ORDER BY n.EXTIME desc FETCH FIRST 1 ROWS ONLY""" # Получение баланса до пополнения
    result = self.SimpleQuery(select)
    if result is not None:
        Log.Checkpoint(f'Запрос успешен! Баланс карты: {result}')
    else:
        Log.Event(f'По счету {acc_crd}, баланс не доступен')
    return result
    
    
  def UpdateProcInterwal(self):
      """ Убираем интервал ожидаения по текущей транзакции внутри APTTRN"""
      run_trn = f"""begin delete from apt_acc_intwait@cap 
      where acc_id in (select acc_id from apt_trn@cap where status = '1'); 
      commit; end;"""
      self.OracleHandlerDB(run_trn, dml_query='True')
      
  def WhileTimeout(self, correct_data: str, fact_data: str, step: int, name_file: str, timeout=120):
      """Запуск цикла с таймером"""
      task = TaskMethods()
      start_time = time.time()
      # на вход принимаются строки
      self.correct_data = correct_data
      self.fact_data = fact_data
      self.step = step
      self.name_file = name_file # имя файла с отчетом аллюр
      abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
      new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
      # -------- 
      while (time.time() - start_time) < timeout:
          time.sleep(4)
          if correct_data in f'fact_data': 
              Log.Event(f'Текущий статус объекта в цикле: **{correct_data}**')
              break
          else:
              Log.Event(f'Работа цикла не закончена')
      task.CheckCorrectData(fact_data, correct_data, self.step, self.name_file, picture_obj = None)
      
      
      
  def GetProcFile(self, tran_id):
      proc_file = f"""select i.id 
                    from N_CRDIN i, N_CRDINDTL d, N_CRDINTRN n
                    where i.id = D.FILE_ID
                       and d.id = n.id
                       and n.trn_num = {tran_id}"""
                     
      file_id = Sql.SimpleQuery(proc_file) # Присваем в переменную
                     
      activate_file = f'begin update (select * from n_crdin where id = {file_id})set state = 1; Commit; end; '    
      self.OracleHandlerDB(activate_file, dml_query='True')          
      
  def AptCheckStatus(self, tran_id: int,  step: int, name_file: str, timeout=120):
      """Проверка статуса транзакции в APTTRN"""
      task = TaskMethods()
      start_time = time.time()
      # на вход принимаются строки
      correct_data = 'Выгружена в АБС, обработана'
      self.tran_id = tran_id
      self.step = step
      self.name_file = name_file # имя файла с отчетом аллюр
      abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
      new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
      # --------
      select = f"""select (select LONGNAME from APR_STATUSTRN@cap where CODE='CAP_STATUS' and CONSTVAL=to_char(trn.STATUS)
      and LNG_ID=AP_LNG.GetActive@cap) STATUSNAME from APT_TRN@CAP trn where trn.ID = '{tran_id}'"""  
      while (time.time() - start_time) < timeout:
          apttrn_status = self.SimpleQuery(select)
          time.sleep(4)
          # Проверка на None
          if apttrn_status is None:
              Log.Event(f'По транзакции: {tran_id}, статус не найден. Повторяем запрос...')
              continue
          if apttrn_status in correct_data: 
              Log.Event(f'Текущий статус транзакции: **{apttrn_status}**')
              break
          else:
              Log.Event(f'По транзакции: {tran_id}, идет обработка')
      task.CheckCorrectData(apttrn_status, correct_data, self.step, self.name_file, picture_obj = None) # Формирует отчет по статусу транзакции
      
  def ExtCheckStatus(self, tran_id: int, acc_crd: str, step: int, name_file: str, timeout=120):
      """Проверка статуса транзакции в EXTTRN"""
      task = TaskMethods()
      start_time = time.time()
      # на вход принимаются строки
      correct_data = 'обработана'
      self.tran_id = tran_id
      self.step = step
      self.acc_crd = acc_crd # Номер карты
      self.name_file = name_file # имя файла с отчетом аллюр
      abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
      new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
      # --------
      selectproc = f"""select proc_id from G_CAPTmpExtTrn t where  OBJ_CODE = '{acc_crd}' and id = '{tran_id}'"""
      proc_data = self.SimpleQuery(selectproc)
      #-------
      select = f"""select decode(t.STATUS,0,'не обработана',1,'обработана',2,'ошибка обработки') as STATUS_NAME
      from G_CAPTmpExtTrn t where t.OBJ_CODE = '{self.acc_crd}' and t.id = '{self.tran_id}'"""
      while (time.time() - start_time) < timeout:
          exttrn_status = self.SimpleQuery(select)
          time.sleep(4)
          try:
              # Проверка на None
              if exttrn_status is None:
                  Log.Event(f'По транзакции: {tran_id}, статус не найден. Повторяем запрос...')
                  continue
                  
              if exttrn_status in 'Выгружена в EXTTRN обработана':
                  Log.Event(f'Текущий статус транзакции: **{exttrn_status}**')
                  break
              else:
                  Log.Event(f'По транзакции: {tran_id}, идет обработка')
          except Exception:
              Log.Message('Запрос не вернул ответ')   
      task.CheckCorrectData(exttrn_status, correct_data, self.step, self.name_file, picture_obj = None) # Формирует отчет по статусу транзакции         

      
  def CalculateCommis(self, before_bln: float, amount: float, acc_crd: str, commission_rate: float, operation_type: str, step: int, name_file: str, tran_id: int, cms_sum: int, picture_obj = None):
      ''' Метод расчета комиссии по платежу '''
      calc_result = ''
      self.before_bln = before_bln # Баланс до
      self.amount = amount # Сумма транзакции
      self.acc_crd = acc_crd # Счет карты
      self.tran_id = tran_id # id транзакции
      self.cms_sum = cms_sum # Доп комиссия
      self.commission_rate = commission_rate # Процент комиссии
      self.operation_type = operation_type # Тип операции: outc - вычитание, inc - сложение
      # -- Для алюра
      self.step = step # Шаги
      self.name_file = name_file # имя файла с отчетом аллюр
      abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
      new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
      self.picture_obj = picture_obj # объект для скриншота для аллюр. По умолчанию desktop
      # Присвоение символа для отчета
      if self.operation_type == 'outc':
          sym = '-'
      elif self.operation_type == 'inc':
          sym = '+'
      else:
          Log.Event('Ошибочный тип операции')
      # -- Расчет в случае наличия комиссии
      balance_now = self.CheckAccBalance(self.acc_crd)
      if self.commission_rate is not None:
          if self.operation_type == 'outc':
              commission = 0
              commission = self.amount * self.commission_rate
              calc_result = (self.before_bln - self.amount) - (commission + cms_sum)
          elif self.operation_type == 'inc':
              commission = 0
              commission = self.amount * self.commission_rate
              calc_result = (self.before_bln + self.amount) - (commission + cms_sum)
          else:
              Log.Event("Неверный тип операции")
      else:
        Log.Event('Нету комиссии') 
      difference = balance_now - calc_result     
      if calc_result == balance_now:
          Log.Checkpoint(f"Данные совпадают. Ожидаемые данные - {calc_result}. Фактические данные - {balance_now}")
          # Отчетность ---------------------------------------------------------------------------------------------------------------
          self.AllureReportTemplate(abs, self.name_file, f"Проверка корректности транзакции", "passed", {"message": f"Данные совпадают. Ожидаемые данные - {calc_result}. Фактические данные - {balance_now}. Счет - {self.acc_crd}"},
                                         self.picture_obj, "Корректно", new_path, "passed", 1, self.step)
          # --------------------------------------------------------------------------------------------------------------------------
          self.AllureReportTemplate(abs, self.name_file, f"Проверка расчета транзакции", "passed", {"message": f"({self.before_bln}(баланс до) {sym} {amount}(сумма) - ({commission}(Комиссия) + {cms_sum} Доп комиссия) = {balance_now}(текущий баланс). ID Транзакции: {self.tran_id}"},
                                         self.picture_obj, "Корректно", new_path, "passed", 1, self.step + 1)
          # --------------------------------------------------------------------------------------------------------------------------
      elif self.commission_rate is None:
          # -------------------------- Если нету комиссии --------------------------------------------
          self.AllureReportTemplate(abs, self.name_file, f"Комиссия отсутствует", "passed", {"message": f"Расчет прошел без учета комиссии. Счет - {self.acc_crd}"},
                                 self.picture_obj, "Корректно", new_path, "passed", 1, self.step)
          # --------------------------------------------------------------------------------------------------------------------------
      else:
          Log.Warning(f"Данные не совпадают. Ожидаемые данные - {calc_result}. Фактические данные - {balance_now}")
          # Отчетность ---------------------------------------------------------------------------------------------------------------
          self.AllureReportTemplate(abs, self.name_file, f"Проверка корректности транзакции", "failed", {"message": f"Данные не совпадают. Ожидаемые данные - {calc_result}. Фактические данные - {balance_now}, Разница {difference}. Счет - {self.acc_crd}"},
                                         self.picture_obj, "Не корректно", new_path, "failed", 1, self.step)
          # --------------------------------------------------------------------------------------------------------------------------
          self.AllureReportTemplate(abs, self.name_file, f"Проверка расчета транзакции", "failed", {"message": f"{self.before_bln}(баланс до) {sym} {amount}(сумма) - ({commission}(Комиссия) + {cms_sum} Доп комиссия) = {balance_now}(текущий баланс). ID Транзакции: {self.tran_id}"},
                                         self.picture_obj, "Не корректно", new_path, "failed", 1, self.step + 1)
          # --------------------------------------------------------------------------------------------------------------------------
      return calc_result
      
  def CalculateBonus(self, before_bln: float, amount: float, acc_crd: str, bonus_rate: float, operation_type: str, step: int, name_file: str, tran_id: int, picture_obj = None):
      ''' Метод расчета бонуса по платежу '''
      bon_result = ''
      self.before_bln = before_bln # Баланс до
      self.amount = amount # Сумма транзакции
      self.acc_crd = acc_crd # Счет карты
      self.bonus_rate = bonus_rate # Процент комиссии
      self.tran_id = tran_id # id транзакции
      self.operation_type = operation_type # Тип операции: outc - вычитание, inc - сложение
      # -- Для алюра
      self.step = step # Шаги
      self.name_file = name_file # имя файла с отчетом аллюр
      abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
      new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
      self.picture_obj = picture_obj # объект для скриншота для аллюр. По умолчанию desktop
      # -- Расчет в случае наличия бонуса
      balance_now = self.CheckAccBalance(self.acc_crd)
      # Проверка наличия бонуса
      bon_take = f"select bonus_amount from bcm_user.bcm_bonus@cap where trn_id = {tran_id}" 
      bon_amount = Sql.SimpleQuery(bon_take)
      if self.bonus_rate is not None:
          bonus = 0
          bonus = self.amount * self.bonus_rate
      else:
        Log.Event('Нету бонуса')
      if bon_amount == bonus:
          Log.Checkpoint(f"Данные совпадают. Ожидаемые данные - {bon_result}. Фактические данные - {balance_now}")
          # Отчетность ---------------------------------------------------------------------------------------------------------------
          self.AllureReportTemplate(abs, self.name_file, f"Проверка корректности транзакции", "passed", {"message": f"Данные совпадают. Ожидаемые данные - {bonus}. Фактические данные - {bon_amount}. Счет - {self.acc_crd}"},
                                         self.picture_obj, "Корректно", new_path, "passed", 1, self.step)
      else:
          Log.Checkpoint(f"Данные совпадают. Ожидаемые данные - {bon_result}. Фактические данные - {balance_now}")
          # Отчетность ---------------------------------------------------------------------------------------------------------------
          self.AllureReportTemplate(abs, self.name_file, f"Проверка корректности транзакции", "failed", {"message": f"Данные не совпадают. Ожидаемые данные - {bon_result}. Фактические данные - {balance_now}, Разница {difference}. Счет - {self.acc_crd}"},
                                         self.picture_obj, "Не корректно", new_path, "failed", 1, self.step)
      return bon_result

  def CalculateTransaction(self, before_bln: float, amount: float, acc_crd: str, operation_type: str, step: int, name_file: str, tran_id: int, picture_obj = None):
      ''' Метод расчета транзакции '''
      calc_result = ''
      self.before_bln = before_bln # Баланс до
      self.amount = amount # Сумма транзакции
      self.acc_crd = acc_crd # Счет карты
      self.tran_id = tran_id # id транзакции
      self.operation_type = operation_type # Тип операции: outc - вычитание, inc - сложение
      # -- Для алюра
      self.step = step # Шаги
      self.name_file = name_file # имя файла с отчетом аллюр
      abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
      new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
      self.picture_obj = picture_obj # объект для скриншота для аллюр. По умолчанию desktop
      # Присвоение символа для отчета
      if self.operation_type == 'outc':
          sym = '-'
      elif self.operation_type == 'inc':
          sym = '+'
      else:
          Log.Event('Ошибочный тип операции')
      # -- Расчет в случае наличия комиссии
      balance_now = self.CheckAccBalance(self.acc_crd)
      if self.operation_type == 'outc':
          calc_result = self.before_bln - self.amount
      elif self.operation_type == 'inc':
          calc_result = self.before_bln + self.amount
      else:
          Log.Event("Неверный тип операции")    
      difference = balance_now - calc_result
      if calc_result == balance_now:
          Log.Checkpoint(f"Данные совпадают. Ожидаемые данные - {calc_result}. Фактические данные - {balance_now}")
          # Отчетность ---------------------------------------------------------------------------------------------------------------
          self.AllureReportTemplate(abs, self.name_file, f"Проверка корректности транзакции", "passed", {"message": f"Данные совпадают. Ожидаемые данные - {calc_result}. Фактические данные - {balance_now}. Счет - {self.acc_crd}"},
                                         self.picture_obj, "Корректно", new_path, "passed", 1, self.step)
          # --------------------------------------------------------------------------------------------------------------------------
          self.AllureReportTemplate(abs, self.name_file, f"Проверка расчета транзакции", "passed", {"message": f"({self.before_bln}(баланс до) {sym} {amount}(сумма) = {balance_now}(текущий баланс) (Без учета комиссии). ID Транзакции: {self.tran_id}"},
                                         self.picture_obj, "Корректно", new_path, "passed", 1, self.step + 1)
          # --------------------------------------------------------------------------------------------------------------------------
      else:
          Log.Checkpoint(f"Данные совпадают. Ожидаемые данные - {calc_result}. Фактические данные - {balance_now}")
          # Отчетность ---------------------------------------------------------------------------------------------------------------
          self.AllureReportTemplate(abs, self.name_file, f"Проверка корректности транзакции", "failed", {"message": f"Данные не совпадают. Ожидаемые данные - {calc_result}. Фактические данные - {balance_now}, Разница {difference}. Счет - {self.acc_crd}"},
                                         self.picture_obj, "Не корректно", new_path, "failed", 1, self.step)
          # --------------------------------------------------------------------------------------------------------------------------
          self.AllureReportTemplate(abs, self.name_file, f"Проверка расчета транзакции", "failed", {"message": f"{self.before_bln}(баланс до) {sym} {amount}(сумма)= {balance_now}(текущий баланс) (Без учета комиссии). ID Транзакции: {self.tran_id}"},
                                         self.picture_obj, "Не корректно", new_path, "failed", 1, self.step + 1)
          # --------------------------------------------------------------------------------------------------------------------------
      return calc_result          
                
  def CheckCorrectTransaction(self, commis: float, bon: float, cms_sum: int, before_bln: float, amount: float, acc_crd: str, operation_type: str, step: int, name_file: str, tran_id: int, picture_obj = None):
      # метод проводит проверку расчета транзакции сравнивает данные фактические с ожидаемыми
      # на вход принимаются строки
      CheckCacl = ''
      self.commis = commis # Процент комиссии если есть
      self.bon = bon # Процент бонуса
      self.before_bln = before_bln # Баланс до
      self.amount = amount # Сумма транзакции
      self.acc_crd = acc_crd # Счет карты
      self.tran_id = tran_id # id транзакции
      self.operation_type = operation_type
      self.cms_sum = cms_sum # Доп комиссия
      self.picture_obj = picture_obj # объект для скриншота для аллюр. По умолчанию desktop
      self.step = step # Шаги
      self.name_file = name_file # имя файла с отчетом аллюр
      abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
      new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
      balance_now = self.CheckAccBalance(self.acc_crd)
      # Расчет в случае наличия Комиссии указаной во входных данных 
      if self.commis is not None and self.bon is not None:
          CheckCacl = self.CalculateCommis(self.before_bln, self.amount, self.acc_crd, self.commis, self.operation_type, self.step, self.name_file, self.tran_id, cms_sum, self.picture_obj)
      # Расчет в случае наличия бонуса указаной во входных данных 
      elif self.commis is None and self.bon is not None:  
          CheckCacl = self.CalculateBonus(self.before_bln, self.amount, self.acc_crd, self.bon, self.operation_type, self.step, self.name_file, self.tran_id, self.picture_obj)
      # Расчет в случае отсутсвия бонуса и комиссии
      elif self.commis is None and self.bon is None:
          CheckCacl = self.CalculateTransaction(self.before_bln, self.amount, self.acc_crd, self.operation_type, self.step, self.name_file, self.tran_id, self.picture_obj)
      else:
          Log.Event('Метод не отработал, из за ошибочных параметров')
      return CheckCacl
        
      
  def generate_reference(self):
    # Генерирует униккальный референс для соап запросов
    random_number = random.randint(0, 9999)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"TEST{random_number}_{timestamp}"
    reference = generate_reference()
    Log.Message(reference)
              
    
  def OpenNewCardMclienBoks(self,code_inn,res,type_doc,cli_role,type_cl,name,surName,nameCom,sex,full_name,name_dep,birthday,dateReg):
      """ Создание карточек клиента Физ лицо, Юр лицо, ИП"""
      date_operday = self.GetEnviron("DATE_OPERDAY")
      to_date = aqConvert.DateTimeToFormatStr(date_operday, "%d.%m.%y")
      to_co_date = aqConvert.DateTimeToFormatStr(date_operday, "%Y-%m-%d")
      self.code_inn = code_inn
      self.type_cl = type_cl
      self.type_doc = type_doc
      self.sex = sex
      self.full_name = full_name
      self.name_dep = name_dep
      self.birthday = birthday
      self.dateReg = dateReg
      date_from_before = self.GetPlusDailyDate(-30)
      date_from = aqConvert.DateTimeToFormatStr(date_from_before, "%d.%m.%Y")
      date_to_after = self.GetPlusDailyDate(3569)
      date_to = aqConvert.DateTimeToFormatStr(date_to_after, "%d.%m.%Y")
      num_phone = self.GeneratePhoneNumber()
      self.cli_role = cli_role
      num_pass = self.GeneratePassNum()
      self.name = name
      self.surName = surName
      self.nameCom = nameCom
      id_main = self.GetIdRecord()
      self.res = res
      sysdate = self.GetSysDate()
      sysdate_frmdt = f'{sysdate[0:2]}-{sysdate[2:4]}-{sysdate[4:]}'
      if self.type_cl == 'FL' or self.type_cl == 'PBOYUL':
          selectDelete = f"""BEGIN
                          DELETE FROM TESTINGIINFLBOKS
                          where IIN = '{self.code_inn}'; commit; END;"""
          self.OracleHandlerDB(selectDelete, dml_query=True)
      elif self.type_cl == 'JUR' or self.type_cl == 'PBOYULS':
          selectDelete = f"""BEGIN
                          DELETE FROM TESTINGIINJURBOKS
                          where IIN = '{self.code_inn}'; commit; END;"""
          self.OracleHandlerDB(selectDelete, dml_query=True)
      if self.res == '1':
          grCountry = 'Гражданин РК'
          codeCountry = '398'
          nameCountry = 'КАЗАХСТАН'
          res_country = 'KZ'
          nation_code = '005'
          if self.sex == 'M':
              nation = 'КАЗАХ'
          else:
              nation = 'КАЗАШКА'
          codeNatioan = '1'
      elif self.res == '0':
          grCountry = 'Иностранный гражданин'
          codeCountry= '643'
          nameCountry = 'РОССИЯ'
          res_country = 'RU'
          nation_code = '001'
          if self.sex == 'M':
              nation = 'РУССКИЙ'
          else:
              nation = 'РУССКАЯ'
          codeNatioan = '2'
      if self.type_cl == 'FL':
          selectUpDateNK = f"""
                     BEGIN insert into g_iin(RNN, IIN, JURFL, RESIDFL, CONSTFL, INDIVIDFL, NAME, FIO, LASTREGEND, REASONDEREG, NOTARY_LAWYER, INACTIVE, TAXDEP_ID, CORRECTDT)
                     values('', '{self.code_inn}', '0', '{self.res}', '1', '0', '{self.full_name}', '{self.full_name}', '', '', '', '0', '5238', ''); commit; END;
                     """
          self.OracleHandlerDB(selectUpDateNK, dml_query='True')
          codeCli = self.OracleCallProcedure("CreateClientCard", f'{self.code_inn}', f'{self.type_doc}', f'{date_from}', f'{date_to}',
                                               f'{num_phone}', f'{self.cli_role}', f'{num_pass}', f'{self.type_cl}', f'{self.res}', f'{self.sex}', f'{res_country}',
                                               f'{full_name}', f'{name_dep}', f'{self.birthday}', return_value = True, num_out = ['1'])
      elif self.type_cl == 'PBOYUL':
          selectUpDateNK = f"""
                     BEGIN insert into g_iin (RNN, IIN, JURFL, RESIDFL, CONSTFL, INDIVIDFL, NAME, FIO, LASTREGEND, REASONDEREG, NOTARY_LAWYER, INACTIVE, TAXDEP_ID, CORRECTDT)
                     values('', '{self.code_inn}', '0', '{self.res}', '1', '0', '', '{self.full_name}', '', '', '', '0', '5238', ''); commit; END;
                     """
          self.OracleHandlerDB(selectUpDateNK, dml_query='True')
          # создание уникального id записи gbdl
          select_max_gbdl_id = f"""SELECT MAX(ID) FROM Z_077_MCA_GBDL_DATA_RESPONCE"""
          get_max_id = self.OracleHandlerDB(select_max_gbdl_id)
          id_gbdl = int(get_max_id[0][0]) + 1
          Log.Message(id_gbdl)
          # добавляем запись в stat_egov
          # здесь находятс данные о типе оквэд и тд
          insert_stat_egov = f"""
                              BEGIN insert into z_077_StatEgovLog(IBIN,  ILANG, XRES,  CALLDATE,  RES, TYPE,  STATUS,  BINIIN,  CLIN,  REGISTERDATE,  OKEDCODE,  OKEDNAME,  SECONDOKEDS, KRPCODE, KRPNAME, KRPBFCODE, KRPBFNAME, KATOCODE,  KATOID,  KATOADDRESS, FIO, IP)
                                    values('{self.code_inn}','RU','', '{sysdate}', '1', 'Ok',  'true',  '{self.code_inn}',  'ИП {self.surName} {self.name[0]}.',  '01.01.2020',  '46213', 'Оптовая торговля масличными культурами', '', '105', 'Малые предприятия (<= 5)',  '105', 'Малые предприятия (<= 5)',  '751210000', '268025',  'Г.АЛМАТЫ, АЛАТАУСКИЙ РАЙОН, Микрорайон Карасу, улица Центральная, дом 1', '{self.full_name}',  'true'); commit; END;
                              """
          self.OracleHandlerDB(insert_stat_egov, dml_query='True')
          # добавляем запись в таблицу с GBDL данными
          # чтобы не запускался ГБДЛ-сервис, так как на тестовых стендах он не работает
          # и сгенерированных данных там нет
          insert_mca_gbdl = f"""            
                            BEGIN insert into Z_077_MCA_GBDL_DATA_RESPONCE (IIN, XMLMSG, MSGID, MSGCODE, MSGRESOINSEDATE, CLIIIN, CLISURNAME, CLINAME, CLIPATRONYMIC, CLIBIRTHDATE, CLIDEATHDATE, CLIGENDERCODE, CLINATIONALCODE, CLINATIONAL, CLIСITIZENSHIPCODE, CLIСITIZENSHIP, CLILIFESTATUSCODE, CLILIFESTATUS, CLIBPCOUNTRYCODE, CLIBPCOUNTRY, CLIREGSTATUSCODE, CLIREGCOUNTRYCODE, CLIREGCOUNTRY, CLIREGDDISTRICTCODE, CLIREGDISTRICT, CLIREGDREGIONCODE, CLIREGREGION, CLIREGCITY, CLIREGSTREET, CLIREGBUILDING, CLIREGCORPUS, CLIREGFLAT, DOCTYPE, DOCTYPECODE, DOCNUMBER, DOCSERIES, DOCBEGINDATE, DOCENDDATE, DOCISSUEORG, DOCSTATUS, DOCCODE, CLICAPABLESTATUS, CLIMISSINGSTATUS, CLIMISSINGENDDATE, CLIEXCLUDEREASON, CLIDISAPPEAR, CLIADDSTATUSCODE, CLIADDCOUNTRYCODE, CLIADDCOUNTRY, CLIADDDDISTRICTCODE, CLIADDDISTRICT, CLIADDDREGIONCODE, CLIADDREGION, CLIADDCITY, CLIADDSTREET, CLIADDBUILDING, CLIADDCORPUS, CLIADDFLAT, RESPONSERESULT, RESPONSEDATE, ID, CLILATSURNAME, CLILATNAME, TOKEN, PUBLICKEY, XMLKDP, XMLGOVGBD, CLIREGFULLADDR)
                                  values ('{self.code_inn}', '', '', 'SCSS001', '{sysdate}', '{self.code_inn}', '{self.surName}', '{self.name}', '', '{self.birthday}', null, '{self.sex}', '{nation_code}', '{nation}', '{codeCountry}', '{res_country}', '0', 'Нормальный', '{codeCountry}', '{res_country}', '1', '{codeCountry}', '{res_country}', '1907', 'АЛМАТИНСКАЯ', '1907211', 'ИЛИЙСКИЙ РАЙОН', 'Казциковский, Казцик', 'УЛИЦА В.Г.Гиль', '45', null, '2', null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, '{sysdate}', {id_gbdl}, '', '', null, null, null, null, null); commit; END;
                            """
          self.OracleHandlerDB(insert_mca_gbdl, dml_query='True')
          # перед тем, как создать карточку ИП необходимо создать карточку физ лица
          # так как без нее карточка ИП не откроется или откроется с грубыми ошибками
          cli_code_fl = self.OracleCallProcedure("CreateClientCard", f'{self.code_inn}', f'{self.type_doc}', f'{date_from}', f'{date_to}',
                                       f'{num_phone}', f'{self.cli_role}', f'{num_pass}', 'FL', f'{self.res}', f'{self.sex}', f'{res_country}',
                                       f'{full_name}', f'{name_dep}', f'{self.birthday}', return_value = True, num_out = ['1'])
          Log.Message(cli_code_fl[0][1])
          # теперь создаем саму карточку ИП
          codeCli = self.OracleCallProcedure("CreateClientCard", f'{self.code_inn}', f'{self.type_doc}', f'{date_from}', f'{date_to}',
                                               f'{num_phone}', f'{self.cli_role}', f'{num_pass}', 'PBOYUL', f'{self.res}', f'{self.sex}', f'{res_country}',
                                               f'{full_name}', f'{name_dep}', f'{self.birthday}', return_value = True, num_out = ['1'])
          Log.Message(codeCli[0][1])
      elif self.type_cl == 'JUR':
          select_iin_db_fl = f"""
                        select iin, name, surname, middlename, resident, birthday, sex from TESTINGIINFLBOKS
                        where resident = '{self.res}' and rownum = 1
                        """

          slct_cnt_iin = f"""
                          select COUNT(IIN) FROM TESTINGIINFLBOKS
                          """
          cnt_iin = self.OracleHandlerDB(slct_cnt_iin)
          for i in range(cnt_iin[0][0]):
              iin_db_fl = self.OracleHandlerDB(select_iin_db_fl)
              dlt_iin = f"""begin delete from TESTINGIINFLBOKS where IIN = '{iin_db_fl[0][0]}'; commit; end;"""
              if iin_db_fl[0][3] == '0':
                  sexFL = 'M'
              elif iin_db_fl[0][3] == '1':
                  sexFL = iin_db_fl[0][5]
              Log.Message(iin_db_fl[0][0])
              Log.Message(self.code_inn)
              Log.Message(code_inn)
              # проверяем, что данного IIN нет в бд налогоплательщиков G_IIN
              slct_g_iin = f""" select count(IIN) from g_iin where IIN = '{select_iin_db_fl[0][0]}'"""
              result_g_iin = self.OracleHandlerDB(slct_g_iin)
              if result_g_iin[0][0] == 0:
                  Log.Event(f"ИИН {select_iin_db_fl[0][0]} не найден в БД налогоплательщиков G_IIN")
                  # проверяем, есть ли ИИН в бд банка g_cli
                  slct_g_cli = f"""select count(taxcode) from g_cli g, g_clihst gh
                                   where g.id = gh.id and g.dep_id = gh.dep_id and trunc(sysdate) between gh.FROMDATE and gh.TODATE
                                         and TAXCODE = '{select_iin_db_fl[0][0]}'   
                                """
                  result_g_cli = self.OracleHandlerDB(slct_g_cli)
                  if result_g_cli[0][0] == 0:
                      Log.Event(f"ИИН {select_iin_db_fl[0][0]} не найден в БД банка G_CLI")
                      # инсертим данные в бд налогоплательщиков G_IIN
                      Log.Event(f"Производим Insert данных в бд налогоплательщиков в G_IIN")
                      selectUpDateNKFL = f"""
                                          BEGIN insert into g_iin (RNN, IIN, JURFL, RESIDFL, CONSTFL, INDIVIDFL, NAME, FIO, LASTREGEND, REASONDEREG, NOTARY_LAWYER, INACTIVE, TAXDEP_ID, CORRECTDT)
                                          values('', '{iin_db_fl[0][0]}', '0', '{iin_db_fl[0][4]}', '1', '0', '{iin_db_fl[0][2]} {iin_db_fl[0][1]} {iin_db_fl[0][3]}', '{iin_db_fl[0][2]} {iin_db_fl[0][1]} {iin_db_fl[0][3]}', '', '', '', '0', '5238', ''); commit; END;
                                          """
                      self.OracleHandlerDB(selectUpDateNKFL, dml_query='True')
                      result_fl = self.OracleCallProcedure("CreateClientCard", f'{iin_db_fl[0][0]}', f'{self.type_doc}', f'{date_from}', f'{date_to}',
                                                           f'{num_phone}', f'{self.cli_role}', f'{num_pass}', 'FL', f'{iin_db_fl[0][4]}', f'{iin_db_fl[0][6]}', f'{res_country}',
                                                           f'{iin_db_fl[0][2]} {iin_db_fl[0][1]} {iin_db_fl[0][3]}', f'{name_dep}', f'{iin_db_fl[0][5]}', return_value = True, num_out = ['1'])
                      self.OracleHandlerDB(dlt_iin, dml_query=True)
                      break
                  else:
                      Log.Event(f"ИИН {select_iin_db_fl[0][0]} существует в БД банка G_CLI. Производится выбор другого ИИН")
                      self.OracleHandlerDB(dlt_iin, dml_query=True)
              else:
                  Log.Event(f"ИИН {select_iin_db_fl[0][0]} существует в БД налогоплательщиков G_IIN. Производится выбор другого ИИН")
                  self.OracleHandlerDB(dlt_iin, dml_query=True)
              if i == cnt_iin[0][0]:
                  Log.Warning(f"В датасете TESTINGIINFLBOKS нет подходящего ИИН физ лица")
          slct_cnt_iin_j = f"""
                          select COUNT(IIN) FROM TESTINGIINJURBOKS
                          """
          cnt_iin_j = self.OracleHandlerDB(slct_cnt_iin_j)
          for i in range(cnt_iin_j[0][0]):
              dlt_iin_j = f"""BEGIN DELETE FROM TESTINGIINJURBOKS where IIN = '{self.code_inn}'; commit; END;"""
              slct_g_iin_j = f""" select count(IIN) from g_iin where IIN = '{self.code_inn}'"""
              slct_iin_jur = f"""SELECT COUNT(IIN) FROM TESTINGIINJURBOKS WHERE IIN = '{self.code_inn}'"""
              result_g_iin_j = self.OracleHandlerDB(slct_g_iin_j)
              if result_g_iin_j[0][0] == 0:
                  Log.Event(f"ИИН {select_iin_db_fl[0][0]} не найден в БД налогоплательщиков G_IIN")
                  # проверяем, есть ли ИИН в бд банка g_cli
                  slct_g_cli_j = f"""select count(taxcode) from g_cli g, g_clihst gh
                                   where g.id = gh.id and g.dep_id = gh.dep_id and trunc(sysdate) between gh.FROMDATE and gh.TODATE
                                         and TAXCODE = '{self.code_inn}'   
                                """
                  result_g_cli_j = self.OracleHandlerDB(slct_g_cli_j)
                  if result_g_cli_j[0][0] == 0:
                      Log.Event(f"ИИН {self.code_inn} не найден в БД банка G_CLI")
                      selectUpDateNK = f"""
                          BEGIN insert into g_iin(RNN, IIN, JURFL, RESIDFL, CONSTFL, INDIVIDFL, NAME, FIO, LASTREGEND, REASONDEREG, NOTARY_LAWYER, INACTIVE, TAXDEP_ID, CORRECTDT)
                          values('{self.code_inn}', '{self.code_inn}', '1', '{self.res}', '0', '0', '{self.nameCom}', '{self.nameCom}', '', '', '', '0', '5238', ''); commit; END;
                          """
                      self.OracleHandlerDB(selectUpDateNK, dml_query=True)
                      select_iin_main = f"""
                          begin insert into z_077_ent_gbdul_main(id_gbdul_main, BIN, REQUESTDATE, XML_DATA, REGSTATUSCODE, REGSTATUSNAME, REGDEPARTCODE, REGDEPARTNAME, REGDATE, REGLASTDATE, FULLNAMERU, FULLNAMEKZ, FULLNAMELAT, SHORTNAMERU, SHORTNAMEKZ, SHORTNAMELAT, ORGFORMCODE, ORGFORMNAME, FORMOFLAWCODE, FORMOFLAWNAME, EPRISETYPECODE, EPRISETYPENAME, TAXORGSTATUS, CREATIONMETHODCODE, CREATIONMETHODNAME, PROPERTYTYPECODE, PROPERTYTYPENAME, TYPICALCHARACTER, COMMERCEORG, ENTERPRISESUBJECT, AFFILIATED, INTERNATIONAL, FOREIGNINVEST, ONECITIZENSHIP, BRANCHESEXISTS, ACTIVITYOKEDCODE, ACTIVITYOKEDNAME, ADDRESSZIPCODE, ADDRESSKATO, ADDRESSDISTRICT, ADDRESSREGION, ADDRESSCITY, ADDRESSSTREET, ADDRESSBUILDING, FOUNDRESCOUNT, FOUNDERSCOUNTFL, FOUNDERSCOUNTUL, ORGSIZECODE, ORGSIZENAME, STATCOMOKEDCODE, STATCOMOKEDNAME, ACTIVITYATTRCODE, ACTIVITYATTRNAME)
                          values ({id_main}, '{self.code_inn}', '{self.GetSysDate()}', '', null, null, null, null, null, null, null, null, null, null, null, null, null, null, '20', null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, '050000', '751210000', null, null, null, 'улица Центральная', '1', null, null, null, null, null, null, null, null, null); commit; end;
                          """
                      self.OracleHandlerDB(select_iin_main, dml_query=True)
                      select_iin_leaders = f"""
                          begin insert into z_077_ent_gbdul_leaders(ID_GBDUL_MAIN, ORG_BIN, COUNTRYCODE, COUNTRYNAME, CITIZENCOUNTRYCODE, CITIZENCOUNTRYNAME, NATIOANLITYCODE, NATIONALITYNAME, IIN, SURNAME, NAME, MIDDLENAME)     
                          values({id_main}, '{self.code_inn}', '{codeCountry}', '{nameCountry}', '{codeCountry}', '{nameCountry}', '{codeNatioan}', '{grCountry}', '{iin_db_fl[0][0]}', '{iin_db_fl[0][2]}', '{iin_db_fl[0][1]}', ''); commit; end;
                          """
                      self.OracleHandlerDB(select_iin_leaders, dml_query=True)
                      select_iin_founders = f"""  
                          begin insert into z_077_ent_gbdul_founders(ID_GBDUL_MAIN, ORGBIN, FOUNDERCOUNTRYCODE, FOUNDERSCOUNTRYNAME, FOUNDERSNATIONCODE, FOUNDERSNATIONNAME, FOUNDERSCITIZENCODE, FOUNDERSCITIZENNAME, FOUNDERSIIN, FOUNDERSSURNAME, FOUNDERSNAME, FOUNDERSMIDDLENAME, FOUNDERSREGNUMBER, FOUNDERSREGDATE, FOUNDERSORGFULLNAMERU, FOUNDERSORGFULLNAMEKZ)     
                          values({id_main}, '{self.code_inn}', '{codeCountry}', '{nameCountry}', '{codeNatioan}', '{grCountry}', '{codeCountry}', '{nameCountry}', '{iin_db_fl[0][0]}', '{iin_db_fl[0][2]}', '{iin_db_fl[0][1]}', '', '', '', '', ''); commit; end;
                          """
                      self.OracleHandlerDB(select_iin_founders, dml_query=True)
                      select_iin_StatEgovLog = f""" 
                          BEGIN insert into z_077_StatEgovLog(IBIN,  ILANG, XRES,  CALLDATE,  RES, TYPE,  STATUS,  BINIIN,  CLIN,  REGISTERDATE,  OKEDCODE,  OKEDNAME,  SECONDOKEDS, KRPCODE, KRPNAME, KRPBFCODE, KRPBFNAME, KATOCODE,  KATOID,  KATOADDRESS, FIO, IP)
                          values('{self.code_inn}','RU','', '{self.GetSysDate()}', '{self.res}', 'Ok',  'true',  '{self.code_inn}',  '{self.nameCom}',  '{to_co_date}',  '46213', 'Оптовая торговля масличными культурами', '', '105', 'Малые предприятия (<= 5)',  '105', 'Малые предприятия (<= 5)',  '751210000', '268025',  'Г.АЛМАТЫ, АЛАТАУСКИЙ РАЙОН, Микрорайон Карасу, улица Центральная, дом 1', '{iin_db_fl[0][2]} {iin_db_fl[0][1]}',  'false'); COMMIT; END;
                          """
                      self.OracleHandlerDB(select_iin_StatEgovLog, dml_query=True)
                      codeCli = self.OracleCallProcedure("CreateClientCard", f'{self.code_inn}', f'{self.type_doc}', f'{date_from}', f'{date_to}',
                                                                   f'{num_phone}', f'{self.cli_role}', f'{num_pass}', f'{self.type_cl}', f'{self.res}', f'{self.sex}', f'{res_country}',
                                                                   f'{self.nameCom}', f'{name_dep}', f'{self.dateReg}', return_value = True, num_out = ['1'])
                      self.OracleHandlerDB(dlt_iin_j, dml_query=True)
                      # создаем документ с образцами подписей/печатей в досье карточки клиента
                      sign_sample = self.OracleCallProcedure("Z_PKG_AUTO_TEST.pCreDocDosCli", f'{codeCli[0][1].strip()}', '696', None, 'Образец подписи физического лица/печати юридического лица',
                                                                                                     '01.01.18', '34877685', '0', '1', None, 'Не знаем', 'Для автотестов',
                                                                                                     '0', None, '1', None, '.jpg', '0', return_value = True, num_out = ['3'])
                      Log.Message(sign_sample[0][1])
                      # проверяем, что ИИН удалился
                      check_dlt_iin = self.OracleHandlerDB(slct_iin_jur)
                      if check_dlt_iin[0][0] == 0:
                          Log.Event(f"ИИН {self.code_inn} удален из g_iin")
                      else:
                          Log.Warning(f"ИИН {self.code_inn} не удален из g_iin")
                      break
                  else:
                      Log.Event(f"ИИН {self.code_inn} существует в БД банка G_CLI. Производится выбор другого ИИН")
                      self.OracleHandlerDB(dlt_iin_j, dml_query=True)
                      # проверяем, что ИИН удалился
                      check_dlt_iin = self.OracleHandlerDB(slct_iin_jur)
                      if check_dlt_iin[0][0] == 0:
                          Log.Event(f"ИИН {self.code_inn} удален из g_iin")
                      else:
                          Log.Warning(f"ИИН {self.code_inn} не удален из g_iin")
              else:
                  Log.Event(f"ИИН {self.code_inn} существует в БД налогоплательщика G_IIN Производится выбор другого ИИН")
                  self.OracleHandlerDB(dlt_iin_j, dml_query=True)
                  # проверяем, что ИИН удалился
                  check_dlt_iin = self.OracleHandlerDB(slct_iin_jur)
                  if check_dlt_iin[0][0] == 0:
                      Log.Event(f"ИИН {self.code_inn} удален из g_iin")
                  else:
                      Log.Warning(f"ИИН {self.code_inn} не удален из g_iin")
              if i == cnt_iin_j[0][0]:
                  Log.Warning(f"В датасете TESTINGIINJURBOKS нет подходящего ИИН юр лица")
      return codeCli[0][1]