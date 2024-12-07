from ColvirFramework import *
from TaskMethods import *
from SQL import Sql
from TestVariables import*


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


    def CalculateCommis(self, before_bln: float, amount: float, acc_crd: str, commission_rate: float, operation_type: str, step: int, name_file: str, tran_id: int, picture_obj = None):
        ''' Метод расчета комиссии по платежу '''
        calc_result = ''
        self.before_bln = before_bln # Баланс до
        self.amount = amount # Сумма транзакции
        self.acc_crd = acc_crd # Счет карты
        self.tran_id = tran_id # id транзакции
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
                calc_result = (self.before_bln - self.amount) - commission
            elif self.operation_type == 'inc':
                commission = 0
                commission = self.amount * self.commission_rate
                calc_result = (self.before_bln + self.amount) - commission
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
            self.AllureReportTemplate(abs, self.name_file, f"Проверка расчета транзакции", "passed", {"message": f"({self.before_bln}(баланс до) {sym} {amount}(сумма) - {commission}(Комиссия) = {balance_now}(текущий баланс). ID Транзакции: {self.tran_id}"},
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
            self.AllureReportTemplate(abs, self.name_file, f"Проверка расчета транзакции", "failed", {"message": f"{self.before_bln}(баланс до) {sym} {amount}(сумма) - {commission}(Комиссия)) = {balance_now}(текущий баланс). ID Транзакции: {self.tran_id}"},
                                           self.picture_obj, "Не корректно", new_path, "failed", 1, self.step + 1)
            # --------------------------------------------------------------------------------------------------------------------------
        return calc_result

    def CalculateBonus(selsf, before_bln: float, amount: float, acc_crd: str, bonus_rate: float, operation_type: str, step: int, name_file: str, tran_id: int, picture_obj = None):
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
        # Присвоение символа для отчета
        if self.operation_type == 'outc':
            sym = '-'
        elif self.operation_type == 'inc':
            sym = '+'
        else:
            Log.Event('Ошибочный тип операции')
        # -- Расчет в случае наличия комиссии
        balance_now = self.CheckAccBalance(self.acc_crd)
        if self.bonus_rate is not None:
            if self.operation_type == 'outc':
                bonus = 0
                bonus = self.amount * self.bonus_rate
                bon_result = (self.before_bln - self.amount) + bonus
            elif self.operation_type == 'inc':
                bonus = 0
                bonus = self.amount * self.bonus_rate
                bon_result = (self.before_bln + self.amount) + bonus
            else:
                Log.Event("Неверный тип операции")
        else:
          Log.Event('Нету комиссии')
        difference = balance_now - bon_result
        if bon_result == balance_now:
            Log.Checkpoint(f"Данные совпадают. Ожидаемые данные - {bon_result}. Фактические данные - {balance_now}")
            # Отчетность ---------------------------------------------------------------------------------------------------------------
            self.AllureReportTemplate(abs, self.name_file, f"Проверка корректности транзакции", "passed", {"message": f"Данные совпадают. Ожидаемые данные - {bon_result}. Фактические данные - {balance_now}. Счет - {self.acc_crd}"},
                                           self.picture_obj, "Корректно", new_path, "passed", 1, self.step)
            # --------------------------------------------------------------------------------------------------------------------------
            self.AllureReportTemplate(abs, self.name_file, f"Проверка расчета транзакции", "passed", {"message": f"({self.before_bln}(баланс до) {sym} {amount}(сумма)) + {bonus}(Бонус) = {balance_now}(текущий баланс). ID Транзакции: {self.tran_id}"},
                                           self.picture_obj, "Корректно", new_path, "passed", 1, self.step + 1)
            # --------------------------------------------------------------------------------------------------------------------------
        elif self.commission_rate is None:
            # -------------------------- Если нету комиссии --------------------------------------------
            self.AllureReportTemplate(abs, self.name_file, f"Комиссия отсутствует", "passed", {"message": f"Расчет прошел без учета комиссии. Счет - {self.acc_crd}"},
                                   self.picture_obj, "Корректно", new_path, "passed", 1, self.step)
            # --------------------------------------------------------------------------------------------------------------------------
        else:
            Log.Checkpoint(f"Данные совпадают. Ожидаемые данные - {bon_result}. Фактические данные - {balance_now}")
            # Отчетность ---------------------------------------------------------------------------------------------------------------
            self.AllureReportTemplate(abs, self.name_file, f"Проверка корректности транзакции", "failed", {"message": f"Данные не совпадают. Ожидаемые данные - {bon_result}. Фактические данные - {balance_now}, Разница {difference}. Счет - {self.acc_crd}"},
                                           self.picture_obj, "Не корректно", new_path, "failed", 1, self.step)
            # --------------------------------------------------------------------------------------------------------------------------
            self.AllureReportTemplate(abs, self.name_file, f"Проверка расчета транзакции", "failed", {"message": f"{self.before_bln}(баланс до) {sym} {amount}(сумма)) + {bonus}(Бонус) = {balance_now}(текущий баланс). ID Транзакции: {self.tran_id}"},
                                           self.picture_obj, "Не корректно", new_path, "failed", 1, self.step + 1)
            # --------------------------------------------------------------------------------------------------------------------------
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

    def CheckCorrectTransaction(self, commis: float, bon: float, before_bln: float, amount: float, acc_crd: str, operation_type: str, step: int, name_file: str, tran_id: int, picture_obj = None):
        # метод проводит проверку расчета транзакции сравнивает данные фактические с ожидаемыми
        # на вход принимаются строки
        self.commis = commis # Процент комиссии если есть
        self.bon = bon # Процент бонуса
        self.before_bln = before_bln # Баланс до
        self.amount = amount # Сумма транзакции
        self.acc_crd = acc_crd # Счет карты
        self.tran_id = tran_id # id транзакции
        self.operation_type = operation_type
        self.picture_obj = picture_obj # объект для скриншота для аллюр. По умолчанию desktop
        self.step = step # Шаги
        self.name_file = name_file # имя файла с отчетом аллюр
        abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
        new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
        balance_now = self.CheckAccBalance(self.acc_crd)
        # Расчет в случае наличия Комиссии указаной во входных данных
        if self.commis is not None and self.bon is None:
            CheckCacl = self.CalculateCommis(self.before_bln, self.amount, self.acc_crd, self.comiss, self.operation_type, self.step, self.name_file, self.tran_id, self.picture_obj)
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

