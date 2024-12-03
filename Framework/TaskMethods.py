from ColvirFramework import *  
from FindMethods import *
from MathMethods import *
from GeneratingData import *
from DateMethods import *
from SQL import *
from CardFrameworks import *


class TaskMethods(CommonOperation, GenerateTestingData, CreateJsonReport):
    gen = Credits()
    date = Date()
    sql = Sql()
    gd = CardFrameworks()

    Math = MathMethods()
    Gen = Credits()

    def CheckOperJrn(self, status: str, parent_obj: str, child_obj: str, wait_obj: str, get_data: List[str], step: int,
                     name_file: str, oper_descr: str=None, date = None, type_parent_obj: str = "VCLObject", count_row: int = 0, rtn = False) -> List[str]:
        """ Метод проверяет выполнение операции в Журнале операций. Первым в списке параметров ЖО должен идти параметр со статусом операции.
            Только потом могут идти параметры, которые необходимо забрать"""
        self.status = status # статус операции в ЖО
        self.parent_obj = parent_obj # родительский объект для кнопки ЖО
        self.child_obj = child_obj # дочерний объект для кнопки ЖО
        self.wait_obj = wait_obj # имя объекта ЖО для ожидания загрузки окна
        self.get_data = get_data # список данных, которые необходимо получить из ctrl-shift-alt-l
        self.step = step # номер шага отчета аллюр
        self.name_file = name_file # имя файла отчета аллюр
        self.oper_descr = oper_descr # описание операции в фильтре
        self.type_parent_obj = type_parent_obj # тип родительского объекта. По умолчанию VCLObject
        self.count_row = count_row # число строки. Если нужная запись в журнале находится не на первой строке
        self.rtn = rtn # флаг для возврата значений. По умолчанию False. True вернет список со значениями свойств
        self.date = date # дата, по которой фильтруется ЖО. По умолчанию вводится текущая дата
        today_date = self.GetSysDateShort()
        list_fields = []
        abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
        new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
        self.ClickInputField(self.parent_obj, self.child_obj, type_parent_obj = self.type_parent_obj, need_tab = False)
        if Sys.Process("COLVIR").WaitVCLObject("frmFilterParams", 5000).Exists:
            self.ClickInputField("frmFilterParams", 'VCLObject("btnOK")', need_tab = False)
        self.WaitLoadWindow(self.wait_obj, 30000)
        if oper_descr:
            self.ClickInputField("frmOperJournal", "VCLObject('btnFilter')")
            if date == None:
                self.SetFilter(DOPER_FROM=today_date, NAMEOPERMOV=oper_descr)
                self.WaitLoadWindow("frmOperJournal", 3000)
            else:
                self.SetFilter(DOPER_FROM=date, NAMEOPERMOV=oper_descr)
            self.WaitLoadWindow('VCLObject("FilterDescription")', 3000)
        if self.count_row > 0:
            self.LLPKeys(VK_DOWN, self.count_row)
        for i in range(len(self.get_data)):
            field = self.GetDataFromObject(self.wait_obj, self.get_data[i])
            list_fields.append(field[0].replace("\'", ''))
        if self.rtn == True:
            return list_fields
            Log.Message(field)
            Log.Message(self.step)
        if self.status in field:
            Log.Checkpoint(f'В журнале есть запись в статусе {self.status}')
            # Отчетность ---------------------------------------------------------------------------------------------------------------
            self.AllureReportTemplate(abs, self.name_file, f"Проверка ЖО", "passed", {"message": f"'В журнале есть запись в статусе {self.status}"},
                                         f'VCLObject({self.wait_obj})', "Есть запись в ЖО", new_path, "passed", 1, self.step)
          # --------------------------------------------------------------------------------------------------------------------------
        else:
            Log.Warning(f'Нет записи в ЖО в статусе {self.status}')
           # Отчетность ---------------------------------------------------------------------------------------------------------------
            self.AllureReportTemplate(abs, self.name_file, f"Проверка ЖО", "failed", {"message": f"Нет записи в ЖО в статусе {self.status}"},
                                         f'VCLObject({self.wait_obj})', "Нет записи в ЖО", new_path, "failed", 1, self.step)
          # --------------------------------------------------------------------------------------------------------------------------
        # закрываем окно
        close = Sys.Process("COLVIR").VCLObject(self.wait_obj)
        close.Close()
        
        
    def InputTaskForCreateDoc(self, name_task: str, type_product: str, name_object: List[str]):
        # метод открывает необходимую задачу в Колвир, вводит и тип продукта и открывает форму документа для создания
        self.name_task = name_task # имя задачи
        self.type_product = type_product # тип продукта
        self.name_object = name_object # наименования объектов. Передается в списке
        
        self.TaskInput(self.name_task) # ввод задачи
        self.InputEmptyFilter() # нажатие на Пустой в фильтре
        self.WaitLoadWindow(name_object[0], time_await=40000)
        self.InputTemplateValue(name_object[0], type_product)
        self.WaitLoadWindow(name_object[2], time_await=40000)
        
    def SetFilterDict(self, dict_prm: Dict[str, str]):
        """ Метод принимает словарь. Ключ - это название объекта поля в фильтре.
        Значение - значение, которое передается в поле фильтра
        Для ключа btnOther, нажимается кнопка 'Еще', данный ключ может идти с пустым параметром
        Для ключа SET_RAT, проставляется галочка санкционирования (1 - санкционирование, 0 - отмена санкционирования)
        Для работы с чекбоксами передавать Поле='ClickX' - где Х - это статус чекбокса
        (1 отмечен, 0 не отмечен, 2 не учтен - выглядит как квадрат)
        """
        self.dict_prm = dict_prm    
        self.WaitLoadWindow("frmFilterParams")
        clear_btn = self.FindChildField("frmFilterParams", "Name", "VCLObject('btnClearFilter')")
        clear_btn.Click()
        get_task = self.FindChildField("AppLayer", "Name", "VCLObject('MainPanel')", "internal")
        dep_required = self.GetFilterFields(get_task.Text)
        if Sys.Process("COLVIR").VCLObject("frmFilterParams").VCLObject("pnlButtons").VCLObject("pnlRight").WaitVCLObject("btnOther", 6000).Enabled:
            Sys.Process("COLVIR").VCLObject("frmFilterParams").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOther").Click()
        dep_field_short = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('DEP')", 5, True, 100)
        dep_field = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('DEP_CODE')", 5, True, 100)
    
        for key, value in self.dict_prm.items():
            if str(value).startswith('Click'):
                checkbox_btn = self.FindChildField("frmFilterParams", "Name", f"VCLObject({key})")
                for _ in range(3): # так как статусов всего 3
                    if str(checkbox_btn.wState) == value[-1:]:
                        break
                    else:
                        checkbox_btn.Click()
            elif key == 'SET_RAT':
              sanction_checkbox = self.FindChildField("frmFilterParams", "Name", "VCLObject('SET_RAT')")
              if value == 1 and not sanction_checkbox.Checked:
                sanction_checkbox.Click()
              if value == 0 and sanction_checkbox.Checked:
                sanction_checkbox.Click()
            elif key == 'DEP' or key =='DEP_CODE':
              dep_field = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", f"VCLObject({key})", 5, True, 100)
              if dep_field.Exists:
                dep_field.Keys(value)
            elif isinstance(value, dict):
              for keys, vals in value.items():
                need_dict_field = self.FindChildField("frmFilterParams", "Name", f"VCLObject({keys})")
                need_dict_field.Keys(vals)
            else:
              need_field = self.FindChildField("frmFilterParams", "Name", f"VCLObject({key})")
              need_field.Keys(value)
        ok_button = self.FindChildField("frmFilterParams", "Name", "VCLObject('btnOK')")
        ok_button.Click()

        
    def FindDocument(self, name_task: str, name_object: List[str], fltr_prm: List[str]):
        # метод открывает необходимую задачу, параметры фильтра и проверяет статус документа
        self.name_task = name_task # задача
        self.name_object = name_object # список имен объектов
        self.fltr_prm = fltr_prm # параметры фильтра
        
        self.TaskInput(self.name_task) # ввод задачи
        
        self.WaitLoadWindow(name_object[0], time_await=40000)
        
    def inputData(self, parent_name: str, child_name: str, value, type_child_obj: str = 'vcl', need_tab: bool = False, clean = ''):
        # метод вводит значение в поле и нажимает TAB если необходимо
        self.parent_name = parent_name # родительский объект
        self.child_name = child_name # дочерний объект
        self.value = value # значение для ввода
        self.type_child_obj = type_child_obj # тип дочерного объекта. По умолчанию vcl. vcl = VCLObject, txt = TextObject
        self.need_tab = need_tab # TAB. Если True, то нажимается таб, по умолчанию  стоит False
        self.clean = clean # опциональный параметры, если необходимо сперва очистить поле
        if self.type_child_obj == 'vcl':
            if self.clean != "":
                self.ClearInputLine(self.parent_name, f"VCLObject({self.child_name})")
            input_value = self.FindChildField(self.parent_name, "Name", f"VCLObject({self.child_name})")
        else:
            if self.clean != "":
                self.ClearInputLine(self.parent_name, f"TextObject({self.child_name})")
            input_value = self.FindChildField(self.parent_name, "Name", f"TextObject({self.child_name})")
        input_value.Keys(self.value)
        
        if self.need_tab == True:
            self.LLPKeys(VK_TAB, 1)
            
    def ClickInputField(self, parent_name: str, child_name: str, type_parent_obj: str = "VCLObject", need_tab: bool = False):
        Find = FindMethods()
        # метод кликает по необходимому полю
        # и при необходимости нажимает таб
        self.parent_name = parent_name # родительский объект
        self.child_name = child_name # дочерний объект
        self.need_tab = need_tab # TAB. Если True, то нажимается таб, по умолчанию  стоит False
        self.type_parent_obj = type_parent_obj # тип родительского объекта. Например VCLObject
        input_value = Find.FindObject(self.type_parent_obj, self.parent_name, self.child_name)
        input_value.Click()       
        if self.need_tab == True:
            self.LLPKeys(VK_TAB, 1)
            
    def OpenTab(self, parent_name: str, child_name: str, type_obj: str = ''):
        # метод открывает объект с типом PageTab
        self.parent_name = parent_name # родительский объект
        self.child_name = child_name # дочерний объект, наименование таба
        self.type_obj = type_obj # тип объекта. По умолчанию пустая строка
        # если передать TextObject, то будет искать назване таба по тексту
        if self.type_obj == '':
            tab = self.FindChildField(self.parent_name, "Name", f"PageTab({self.child_name})")
        else:
            tab = self.FindChildField(self.parent_name, "Name", f"TextObject({self.child_name})")
        tab.Click()
        
    def OpenTClSpeedButton(self, parent_name: str, child_name: str):
        # метод открываем окно выбора значений
        # для полей, которые выдают ошибку при вводе значений
        self.parent_name = parent_name # родительский объект
        self.child_name = child_name # дочерний объект
        
        speed_button = self.FindChildField(self.parent_name, "Name", f"VCLObject({self.child_name})")
        speed_button.VCLObject("TClSpeedButton").Click()
        
    def SaveDoc(self, parent_name: str, wait_obj: str, type_parent_obj: str = "VCLObject"):
        # метод сохраняет документ
        self.parent_name = parent_name # родительский объект
        self.type_parent_obj = type_parent_obj # тип родительского объекта
        self.wait_obj = wait_obj # объект, который ожидается после сохранения
        if self.type_parent_obj == "VCLObject":
            self.ClickInputField(self.parent_name, 'VCLObject("btnSave")', need_tab = False)
        elif self.type_parent_obj == "Dialog":
            self.ClickInputField(self.parent_name, 'VCLObject("btnSave")', need_tab = False)
        self.WaitLoadWindow(self.wait_obj, time_await=40000)
        
    def CheckStatusDoc(self, status: str, parent_name: str, need_data: str,
                       type_check: str, name_file: str, step: int, type_obj: str = None):
        # метод проверяет статус документа через 4 клавиши
        self.status = status # ожидаемый статус документа
        self.parent_name = parent_name # родительский объект
        self.need_data = need_data # наименование статуса документа через 4 клавиши
        self.type_check = type_check # тип проверки. cre - для создания, find - для поиска, oper - после выполнения операции
        self.name_file = name_file # наименование файла для отчета
        self.step = step # номер шага для отчета
        self.type_obj = type_obj # тип объекта, если через 4 клавиши не определяет объекты
        # Если передать Text, то будет искать по тексту
        if self.type_obj != None:
            Log.Message("Поиск по тексту")
            check_status = self.GetGridDataFieldsText(self.parent_name, self.need_data)
        else:
            Log.Message("Поиск по объекту")
            check_status = self.GetGridDataFields(self.parent_name, self.need_data)
        abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
        new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
        if check_status[0].replace("\'","") == self.status:
            if type_check == 'cre':
                Log.Checkpoint(f'Создан документ в статусе {self.status}')
                # Отчетность ---------------------------------------------------------------------------------------------------------------
                self.AllureReportTemplate(abs, self.name_file, f"Создание документа", "passed", {"message": f"Создан документ со статусом {self.status}"},
                                               f'VCLObject({self.parent_name})', "Документ создан", new_path, "passed", 1, self.step)
                # --------------------------------------------------------------------------------------------------------------------------
                # закрываем окно
                close = Sys.Process("COLVIR").VCLObject(self.parent_name)
                close.Close()
            elif type_check == 'find':
                Log.Checkpoint(f'Найден документ в статусе {self.status}')
                # Отчетность ---------------------------------------------------------------------------------------------------------------
                self.AllureReportTemplate(abs, self.name_file, f"Поиск документа", "passed", {"message": f"Найден документ со статусом {self.status}"},
                                               f'VCLObject({self.parent_name})', "Документ найден", new_path, "passed", 1, self.step)
                # --------------------------------------------------------------------------------------------------------------------------
            elif type_check == 'oper':
                Log.Checkpoint(f'Выполнена операция')
                # Отчетность ---------------------------------------------------------------------------------------------------------------
                self.AllureReportTemplate(abs, self.name_file, f"Выполнение операции", "passed", {"message": f"Выполнена операция"},
                                               f'VCLObject({self.parent_name})', "Выполнена операция", new_path, "passed", 1, self.step)
                # --------------------------------------------------------------------------------------------------------------------------
        else:
            if type_check == 'cre':
                Log.Warning(f'Не создан документ в статусе {self.status}')
                # Отчетность ---------------------------------------------------------------------------------------------------------------
                self.AllureReportTemplate(abs, self.name_file, f"Создание документа", "failed", {"message": f"Не создан документ со статусом {self.status}"},
                                               f'VCLObject({self.parent_name})', "Документ не создан", new_path, "failed", 1, self.step)
                # --------------------------------------------------------------------------------------------------------------------------
                # закрываем окно
                close = Sys.Process("COLVIR").VCLObject(self.parent_name)
                close.Close()
            elif type_check == 'find':
                Log.Warning(f'Не найден документ в статусе {self.status}')
                # Отчетность ---------------------------------------------------------------------------------------------------------------
                self.AllureReportTemplate(abs, self.name_file, f"Поиск документа", "failed", {"message": f"Не найден документ со статусом {self.status}"},
                                               f'VCLObject({self.parent_name})', "Документ не найден", new_path, "failed", 1, self.step)
                # --------------------------------------------------------------------------------------------------------------------------
            elif type_check == 'oper':
                Log.Warning(f'Не выполнена операция')
                # Отчетность ---------------------------------------------------------------------------------------------------------------
                self.AllureReportTemplate(abs, self.name_file, f"Выполнение операции", "failed", {"message": f"Не выполнена операция"},
                                               f'VCLObject({self.parent_name})', "Не выполнена операция", new_path, "failed", 1, self.step)
                # --------------------------------------------------------------------------------------------------------------------------
        
    def AllureReportEnd(self, count: int, name_file: str, status: str, error: str = None):
        # метод обрабатывает непредвиденные ошибки и перемещает файл в allure-result
        self.count = count # уровень шага
        self.name_file = name_file # имя файла
        self.status = status # статус отчета
        self.error = error # текст ошибки, если скрипт падает на except
        
        abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
        new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
        if self.status == "failed":
            Log.Warning(f"Произошла ошибка при выполнении скрипта")
            Log.Warning(f"Текст ошибки - {self.error}")
            self.AllureReportTemplate(abs, self.name_file, f"Непредвиденная ошибка", self.status, {"message": f"Возникла ошибка. Текст ошибки - {self.error}"},
                                      "desktop", "Возникла ошибка", new_path, self.status, self.count, 1, rm=True)
        elif self.status == "passed":
            Log.Checkpoint(f"Тест завершен успешно")
            self.AllureReportTemplate(abs, self.name_file, f"Тест выполнен", self.status, {"message": f"Тест завершен успешно"},
                                      "desktop", "Завершен успешно", new_path, self.status, self.count, 1, rm=True)

    def PerformingOperation(self, name_oper: str, confirm_oper: str, parent_object: str, child_object: str):
      # метод для выполнения операции
      self.name_oper = name_oper # название операции
      self.confirm_oper = confirm_oper # подтверждение операции
      self.parent_object = parent_object # родительский объект
      self.child_object = child_object # дочерний объект
        
      btn_opr = self.FindChildField(self.parent_object, "Name", f"VCLObject({self.child_object})")
      btn_opr.Click()
      if Sys.Process("COLVIR").WaitPopup("Контекст", 80000).Exists:
          self.FindNeedOperation(self.name_oper)
      else:
          Log.Event("Попап с операциями не появился, нажимаем еще раз")
          btn_opr = self.FindChildField(self.parent_object, "Name", f"VCLObject({self.child_object})")
          btn_opr.Click()
          self.FindNeedOperation(self.name_oper)
      self.ConfirmOperation(self.confirm_oper)
        
    def FindDoc(self, name_task: str, dict_prm: Dict[str, str], wait_obj: str):
        # метод вводит задачу и указываем параметры в фильтре для поиска документа
        self.name_task = name_task # наименование задачи
        self.wait_obj = wait_obj # имя объекта для ожидания во время поиска
        self.dict_prm = dict_prm  
      
        self.TaskInput(self.name_task) # ввод задачи
        self.SetFilterDict(self.dict_prm)
        self.WaitLoadWindow(self.wait_obj, time_await=40000)
        
    def CloseWindow(self, parent_obj: str, type_parent_obj: str = "VCLObject"):
        # метод закрывает главное окно в Колвир
        self.parent_obj = parent_obj # имя окна для закрытия
        self.type_parent_obj = type_parent_obj # тип родительского объекта. По умолчанию VCLObject
        if self.type_parent_obj == "VCLObject":
            close_btn = Sys.Process("COLVIR").VCLObject(self.parent_obj)
        elif self.type_parent_obj == "TextObject":
            close_btn = Sys.Process("COLVIR").TextObject(self.parent_obj)
        elif self.type_parent_obj == "Dialog":
            close_btn = Sys.Process("COLVIR").Dialog(self.parent_obj)
        close_btn.Close()
        
    def SPPITest(self, dict_fields: Dict[int, str]):
        # метод заполняет SPPI тест
        # на вход подается словарь где в качестве ключа
        # выступают номера объектов Window. Например 24 в примере Window("TCSSEdit", "", 24)
        # в качестве значения передается "ДА" или "НЕТ"
        self.dict_fields = dict_fields
        self.WaitLoadWindow("frmDFSimpleEngine", time_await=40000)
        colvir = Sys.Process("COLVIR")
        panel = colvir.VCLObject("frmDFSimpleEngine").VCLObject("LayoutFrame")
        for key, value in self.dict_fields.items():
            panel.Window("TCSSEdit", "", key).Click(37, 7)
            colvir.Window("TPopupListbox", "", 1).ListItem(value).Click()
        self.ClickInputField("frmDFSimpleEngine", 'VCLObject("btnOK")', need_tab = False)
        
    def GetDataFromObject(self, parent_name_obj: str, code_grid: str, need_tab: str = None) -> str:
        # метод возвращает данные из объекта
        self.parent_name_obj = parent_name_obj # родительское имя объекта
        self.code_grid = code_grid # код значения из 4 клавиш
        self.need_tab = need_tab # необходимый таб для 4 клавиш
        data_field = self.GetGridDataFieldsText(self.parent_name_obj, self.code_grid, need_tab = self.need_tab)
        return data_field[0].replace("\'", '')
        
    def GetDataFromDoc(self, parent_name_obj_insert: str, doc_name_obj: str, field_obj: str, need_grid_tab: str = None, corect_data: str = '', 
                       name_tab: str = None, need_allure: bool = False, step: int = 1, name_file: str = '') -> str:
        # метод забирает данные из документа и возвращает в виде списка
        self.parent_name_obj_insert = parent_name_obj_insert # имя родительского объекта где кнопка просмотра документа
        self.doc_name_obj = doc_name_obj # объект окна из которого нужны данные
        self.field_obj = field_obj # список с объектами у которых будут браться значения данных
        self.name_tab = name_tab # имя вкладки, если данные находятся во вкладке
        self.need_grid_tab = need_grid_tab # код значения из 4 клавиш
        self.need_allure = need_allure # флаг необходимости отчета аллюр с проверкой значений
        self.step = step # шаг отчета аллюр
        self.corect_data = corect_data # список с элементами для сравнения, если необходим отчет. По умолчанию ''
        self.name_file = name_file # имя файла с отчетом аллюр
        self.ClickInputField(self.parent_name_obj_insert, 'VCLObject("btnBrowse")', need_tab = False)
        self.WaitLoadWindow(self.doc_name_obj, 40000)
        if self.name_tab != None:
            self.OpenTab(self.doc_name_obj, self.name_tab)
        Log.Message(self.field_obj)     
        data_field = self.GetDataFromObject(self.doc_name_obj, self.field_obj, need_tab = self.need_grid_tab)
        if self.need_allure == True:
            self.CheckCorrectData(data_field, self.corect_data, self.step, self.name_file, f'VCLObject({self.doc_name_obj})')
        self.CloseWindow(self.doc_name_obj)
        return data_field
        
    def CheckCorrectData(self, fact_data: str, correct_data: str, step: int, name_file: str, picture_obj: str = "desktop"):
        # метод сравнивает данные фактические с ожидаемыми
        # на вход принимаются строки
        self.fact_data = fact_data # фактические данные
        self.correct_data = correct_data # ожидаемые данные
        self.picture_obj = picture_obj # объект для скриншота для аллюр. По умолчанию desktop
        self.name_file = name_file # имя файла с отчетом аллюр
        self.step = step # # шаг отчета
        abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
        new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
        if self.fact_data == self.correct_data:
            Log.Checkpoint(f"Данные совпадают. Ожидаемые данные - {self.correct_data}. Фактические данные - {self.fact_data}")
            # Отчетность ---------------------------------------------------------------------------------------------------------------
            self.AllureReportTemplate(abs, self.name_file, f"Проверка корректности данных", "passed", {"message": f"Данные совпадают. Ожидаемые данные - {self.correct_data}. Фактические данные - {self.fact_data}"},
                                           self.picture_obj, "Корректно", new_path, "passed", 1, self.step)
            # --------------------------------------------------------------------------------------------------------------------------
        else:
            Log.Warning(f"Данные не совпадают. Ожидаемые данные - {self.correct_data}")
            # Отчетность ---------------------------------------------------------------------------------------------------------------
            self.AllureReportTemplate(abs, self.name_file, f"Проверка корректности данных", "failed", {"message": f"Данные не совпадают. Ожидаемые данные - {self.correct_data}. Фактические данные - {self.fact_data}"},
                                           self.picture_obj, "Не корректно", new_path, "failed", 1, self.step)
            # --------------------------------------------------------------------------------------------------------------------------
            
    def InputValuesGrdPositions(self, parent_obj: str, list_values: List[str]):
        # метод заполняет данные в окне GrdPositions
        self.parent_obj = parent_obj # имя родительского объекта
        self.list_values = list_values # список со значениями для заполнения
        first_object = self.FindChildField(self.parent_obj, "Name", f"VCLObject('GrdPositions')")
        first_object.Window("TDBGridInplaceEdit", "", 1).Click()
        for row in self.list_values:
            # сперва очищаем поле, оно может быть заполнено
            first_object.Keys("^a[Del]")
            self.inputData(self.parent_obj, "GrdPositions", row, need_tab = True)
        self.ClickInputField("Внимание", 'VCLObject("No")', type_parent_obj = "Dialog", need_tab = False)

    def WaitNonPermanentWindow(self, parent_name: str, time_wait: int):
        # метод ожидает окно, которое не постоянно
        # если окно вышло, то нажимает ОК
        # если нет, то ничего не делает
        self.parent_name = parent_name # имя родительского объекта
        self.time_wait = time_wait # время ожидания
        if Sys.Process("COLVIR").WaitVCLObject(self.parent_name, self.time_wait).Exists:
            self.ClickInputField(self.parent_name, 'VCLObject("btnOK")', need_tab = False)
            
    def OffOtpPassCheckbox(self):
        # метод ставить чекбокс Откл. ОТП пароля
        # если при выполнении операции выходит данное окно
        self.WaitLoadWindow("frmDynamicDialog", 30000)
        self.ClickInputField("frmDynamicDialog", 'VCLObject("OTP_FL")', need_tab = False)
        self.ClickInputField("frmDynamicDialog", 'VCLObject("btnOK")', need_tab = False)

    def SancFromJrnOper(self, parent_name: str, child_object: str, name_file: str, step_report: int, num_row: str = 0):
        # метод санкционирует операцию в журнале операций
        self.parent_name = parent_name
        self.child_object = child_object
        self.num_row = num_row
        self.name_file = name_file
        self.step_report = step_report
        self.ClickInputField(self.parent_name, self.child_object, need_tab = False)
        self.WaitLoadWindow("frmOperJournal", 30000)
        self.LLPKeys(VK_DOWN, self.num_row)
        self.ClickInputField("frmOperJournal", 'VCLObject("btnPost")', need_tab = False)
        self.CheckOperEndWindow()
        self.CheckSancFromJrnOper(self.name_file, self.step_report)

    def CheckSancFromJrnOper(self, name_file: str, step_report: int):
        # метод проверяет, что санкционирование выполнилось
        self.step_report = step_report
        self.name_file = name_file
        result = self.GetGridDataFields("frmOperJournal", "RATFL")
        abs = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
        new_path = self.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
        if result[0].replace("\'", '') == '0':
            Log.Checkpoint("Санкционирование выполнилось")
            # Отчетность ---------------------------------------------------------------------------------------------------------------
            self.AllureReportTemplate(abs, self.name_file, f"Санкционирование в ЖО", "passed", {"message": f"Выполнено санкционирование операции в ЖО"},
                                           'VCLObject("frmOperJournal")', "Санкционирование выполнилось", new_path, "passed", 1, self.step_report)
            # --------------------------------------------------------------------------------------------------------------------------
        else:
            Log.Warning("Санкционирование не выполнилось")
            # Отчетность ---------------------------------------------------------------------------------------------------------------
            self.AllureReportTemplate(abs, self.name_file, f"Санкционирование в ЖО", "failed", {"message": f"Не выполнено санкционирование операции в ЖО"},
                                           'VCLObject("frmOperJournal")', "Санкционирование не выполнилось", new_path, "failed", 1, self.step_report)
            # --------------------------------------------------------------------------------------------------------------------------
        self.CloseWindow("frmOperJournal")

    def GetDataFromWindow(self, parent_name: str, name_button: str, name_window: str,
                          find_obj, value_obj: List[str], fltr_prm: Dict[str, str] = {}) -> List:
        # метод получает данные из окна или проверяет значения в нем, через 4 клавиши
        self.parent_name = parent_name # имя родительского объекта
        self.name_button = name_button # имя кнопки окна для открытия
        self.name_window = name_window # имя объекта окна
        self.find_obj = find_obj # имя объекта из которого нужно получить данные
        self.value_obj = value_obj # значение из 4-х клавиш для возврата
        # можеть искать по объекту, по тексту
        # если передать int, то будет производиться нажатие клавиши вниз
        # какое число передается, столько раз и нажмет
        self.fltr_prm = fltr_prm # словарь с данными для фильтрации, если она есть
        # если фильтрации нет, то ничего не передавать
        list_value = []
        self.ClickInputField(self.parent_name, self.name_button, need_tab = False)
        if (Sys.Process("COLVIR").WaitVCLObject("frmFilterParams", 10000).Exists and
               self.fltr_prm is not None):
               # перенос строки
            self.SetFilterDict(self.fltr_prm)
        else:
            Log.Event("Окно с фильтром не существует")
        self.WaitLoadWindow(self.name_window, 30000)
        if type(self.find_obj) == str:
            self.ClickInputField(self.name_window, self.find_obj, need_tab = False)
        else:
            self.LLPKeys(VK_DOWN, range_numbers=self.find_obj)
        for elem in self.value_obj:
            result = self.GetDataFromObject(self.name_window, elem)
            list_value.append(result.replace("\'",""))
        self.CloseWindow(self.name_window)
        return list_value

    def GetDataControlSumm(self, parent_name: str, name_button: str, value_obj: List[str],
                           fltr_prm: Dict[str, str] = {}, count_row: int = None) -> List:
                           # перенос строки
        # метод забирает данные из документа в контроле сумм
        self.parent_name = parent_name # имя родительского объекта
        self.name_button = name_button # имя кнопки окна для открытия
        self.value_obj = value_obj # значение из 4-х клавиш для возврата
        self.fltr_prm = fltr_prm # словарь с данными для фильтрации
        self.count_row = count_row # строка в журнале. Если передать число
        # то будет произведено нажатие клавиши вниз = count_row
        self.ClickInputField(self.parent_name, self.name_button, need_tab = False)
        self.SetFilterDict(self.fltr_prm)
        self.WaitLoadWindow("frmDeaPaySelfList", 30000)
        result = self.GetDataFromWindow("frmDeaPaySelfList", 'VCLObject("btnBrowse")', "frmDeaPayDetail",
                                        0, self.value_obj)
                                        # перенос строки
        self.CloseWindow("frmDeaPaySelfList")
        return result

    def GetRefFromJrn(self, parent_name: str, name_button: str,
                      count_row: int = None) -> List:
                      # перенос строки
        # метод возвращает референс операции и тип санкции из ЖО
        self.parent_name = parent_name # имя родительского объекта
        self.name_button = name_button # имя кнопки окна для открытия
        self.count_row = count_row # строка в журнале. Если передать число
        # то будет произведено нажатие клавиши вниз = count_row
        self.ClickInputField(self.parent_name, self.name_button, need_tab = False)
        self.WaitLoadWindow("frmOperJournal", 30000)
        if self.count_row != None:
            self.LLPKeys(VK_DOWN, range_numbers=self.count_row)
        result = self.GetDataFromWindow("frmOperJournal", 'VCLObject("btnBrowse")', "frmOperJournalDtl",
                               0, ["REFER"])
        type_sanction = self.GetTypeSanctionSsafeord()
        result.append(type_sanction)
        self.CloseWindow("frmOperJournal")
        return result

    def CheckWindowEndOper(self):
        """Закрытие мерзкого окна 'операция выполнена' c дополнительной тех. задержкой
        (сделано в цикле из-за лагов окна приложения при долгом выполнении операции,
         что приводило к ошибке поиска необходимого окна)
        """
        if Sys.Process("COLVIR").WaitWindow("TMessageForm", "Colvir Banking System", -1, 180000).Exists:
            find_window = Sys.Process("COLVIR").Dialog("Colvir Banking System")
            find_window.Close()
            Delay(500) # тех задержка перед следующей операцией
            return True
        return False

    def FindOperationByLLP(self, llp_name: List, count: List):
        # метод поиска операции по тексту
        self.llp_name = llp_name # # список с наименованиями
        self.count = count # количество нажатий клавиши
        for i in range(len(self.llp_name)):
            self.LLPKeys(self.llp_name[i], range_numbers=self.count[i])
            self.LLPKeys(VK_RETURN, range_numbers=1)

    def PerformingOperationByLLP(self, llp_name: List, count: List, confirm_oper: str,
                                parent_object: str, child_object: str):
                                # перенос строки
        # метод производит поиск операции по тексту и выполняет ее
        self.llp_name = llp_name # список с наименованиями
        # передается несколько, если операция вложенная
        self.count = count # количество нажатий клавиш
        self.confirm_oper = confirm_oper # текст подтверждения
        self.parent_object = parent_object # наименование родительского объекта
        self.child_object = child_object # объект кнопки операции
        btn_opr = self.FindChildField(self.parent_object, "Name", f"VCLObject({self.child_object})")
        btn_opr.Click()
        if Sys.Process("COLVIR").WaitPopup("Контекст", 80000).Exists:
            self.FindOperationByLLP(self.llp_name, self.count)
        else:
            Log.Event("Попап с операциями не появился, нажимаем еще раз")
            btn_opr = self.FindChildField(self.parent_object, "Name", f"VCLObject({self.child_object})")
            btn_opr.Click()
            self.FindOperationByLLP(self.llp_name, self.count)
        self.ConfirmOperation(self.confirm_oper)

    def SetIndividRate(self, date_rate: str, value_rate: str):
        # метод устанавливает индивидуальную ставку
        self.date_rate = date_rate # дата ставки
        self.value_rate = value_rate # значение ставки
        self.WaitLoadWindow("frmPcnDialog", 30000)
        sysdate = self.GetSysDateShort()
        sysdate = f"{sysdate[:2]}.{sysdate[2:4]}.{sysdate[4:]}"
        if '.' not in self.date_rate:
            self.date_rate = f"{self.date_rate[:2]}.{self.date_rate[2:4]}.{self.date_rate[4:]}"
        Log.Event(sysdate)
        Log.Event(self.date_rate)
        btn_ins = Sys.Process("COLVIR").VCLObject("frmPcnDialog").VCLObject("btnInsert")
        btn_ins.Click()
        need_row = Sys.Process("COLVIR").VCLObject("frmPcnDialog").VCLObject("cxGrid").Window("TcxGridSite", "", 1).TextObject(sysdate)
        need_row.Click()
        input_data = Sys.Process("COLVIR").VCLObject("frmPcnDialog").VCLObject("cxGrid").Window("TcxGridSite", "", 1)
        input_data.Keys(self.date_rate)
        self.LLPKeys(VK_TAB, range_numbers=1)
        input_data.Keys(self.value_rate)
        self.LLPKeys(VK_TAB, range_numbers=8)
        input_data.Keys("Autotests")
        btn_ok = Sys.Process("COLVIR").VCLObject("frmPcnDialog").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK")
        btn_ok.Click()

    def ScrollWindow(self, parent_name: str, child_name: str, text_name: str):
        self.parent_name = parent_name # имя родительского объекта
        self.child_name = child_name # имя дочернего объекта
        self.text_name = text_name # имя текстового объекта для поиска скроллом
        VScrollBar = self.FindChildField(self.parent_name, "Name", self.child_name)
        Max = VScrollBar.VScroll.Max
        Min = VScrollBar.VScroll.Min
        while not self.FindChildField(self.parent_name, "Name", self.text_name).VisibleOnScreen:
            VScrollBar.Pos += (Min + 8)

    def ClearInputLine(self, parent_name: str, child_obj: str):
        # метод очищает строку ввода
        # необходим когда нужно заменить существующее значение в поле на новое
        self.parent_name = parent_name # имя родительского объекта
        self.child_obj = child_obj # дочерний объект
        self.FindChildField(self.parent_name, "Name", self.child_obj).DblClick()
        self.LLPKeys(VK_BACK, range_numbers=1)
        
    def ClickOperation(self, classname: str, oper_name: str, sub_oper_name: str=None, index: int=None):
        """ Выбор необходимой операции из списка операций.
        В метод передается:
        - classname - название окна (отличается в зависимости от выбранного Task), из которого выбирается операция 
        - oper_name (required) - название операции из основного выпадающего списка операций
        - sub_oper_name (optional) - название подоперации. Передается в случае, если операция делится на подоперации
        - index (optional) - индекс операции. Передается в случае, если есть несколько операций с одинаковым названием и нужно выбрать одну из них
        """
        self.classname = classname
        self.oper_name = oper_name
        self.sub_oper_name = sub_oper_name
        self.index = index
        wnd_confirmed = False
        try:
            opr_btn = self.FindChildField(self.classname, "Name", 'VCLObject("btnRunOperation")')
            self.WaitLoadWindow(self.classname, 20000)
            opr_btn.Click()
            # Ищем операцию oper_name в основном окне
            wnd = Sys.Process('COLVIR').Popup('Контекст')
            max_wait_time = 5000
            end_time = datetime.now() + timedelta(milliseconds=max_wait_time)
            while True:
                if self.index is not None:
                    item = wnd.FindChild("Name", f'TextObject("{self.oper_name}", {self.index})')
                else:
                    item = wnd.FindChild("Text", self.oper_name)
                if item.Exists:
                    item.Click()
                    break
                if not item.Exists and aqDateTime.Now() < end_time:
                    LLPlayer.KeyDown(VK_DOWN, 5000)
                    LLPlayer.KeyDown(VK_UP, 5000)
                else:
                    Log.Error(f"Операция '{self.oper_name}' не найдена.")
                    return False
            # Если sub_oper_name указан, ищем его в дополнительном окне
            if self.sub_oper_name:
                sub_wnd = Sys.Process("COLVIR").FindChild("Name", "Window('#32768', '', 1)", 5000)
                if not sub_wnd.Exists:
                    Log.Warning("Дополнительное окно не найдено.")
                    return False
                sub_item = sub_wnd.FindChild("Text", self.sub_oper_name)
                if not sub_item.Exists:
                    Log.Warning(f"Подоперация '{self.sub_oper_name}' не найдена.")
                    return False
                sub_item.Click()
                if Sys.Process("COLVIR").Dialog("Подтверждение").Exists:
                    self.ConfirmOperation(f'Выполнить операцию "{self.sub_oper_name}"')
                    wnd_confirmed = True
                    Log.Message(f"Подоперация '{self.sub_oper_name}' выбрана.")
            if not wnd_confirmed and Sys.Process("COLVIR").Dialog("Подтверждение").Exists:
                self.ConfirmOperation(f'Выполнить операцию "{self.oper_name}"')
                Log.Message(f"Операция '{self.oper_name}' выбрана.")
            return True
        except Exception as e:
            Log.Error(f"Ошибка при выборе операции: {str(e)}")
            return False
            
    def GetPayDateFromGraph(self, doc_num):
        ''' Метод получения даты платежа из графика платежей через процедуру '''
        self.doc_num = doc_num
        self.OracleFunctionExecute("Z_PKG_AUTO_TEST.AT_fGetPayDateFromGraph", str, self.doc_num)
