from ColvirFramework import *
from AutorizationColvir import *

name_test_global = "" # глобальная переменная для хранения названия файла

# Блок с декораторами
def AutorithColvir(user_name: str):
    # декоратор для авторизация в Колвире
    def LoginInColvirDecor(f):    
        def wrapper(*args):
            if user_name.upper() == "COLVIR":
                LoginInColvir()
            else:
                login_user, pass_user = GetLoginPass(user_name)
                LoginInColvir(login_user, pass_user)
            f(*args)
        return wrapper
    return LoginInColvirDecor

def TestName(name: str, name_file: str):
    # декоратор с названием теста
    def TestNameDecor(f):    
        def wrapper(*args):
            CreateJsonFile(name_test=name_file)
            CreateNameTest(name, name_test_global)
            f(*args)
        return wrapper
    return TestNameDecor
    
def SubTestName(name: str):
    # декоратор с названием сабсьюта
    def SubSuiteDecor(f):    
        def wrapper(*args):
            AddSubSuite(sub_suite=name)
            f(*args)
        return wrapper
    return SubSuiteDecor
    
def Module(name: str):
    # декоратор с названием модуля
    def ModuleDecor(f):    
        def wrapper(*args, name_file = name_test_global):
            AddModuleName(module_name = name)
            try:
                f(*args, name_file = name_test_global)
            except Exception as error:
                AllureReportEnd(2, name_test_global, "failed", error)
        return wrapper
    return ModuleDecor


#--------------------
# Блок с методами для формирования отчета Allure        
#class AllureReport():
 #   """ Класс работы с отчетом Allure """
def CreateJsonFile(name_test: str, json_body=''):
    """Функция создает файл Json с названием, которое передается в функцию
    в функцию также можно передать тело json. Если ничего не передавать, то создастся пустое тело
    в ввиде словаря питона - {}"""
    colvir = CommonOperation()
    global name_test_global
    name_test_global = name_test
    allure_path = colvir.GetEnviron('NEW_PATH')
    file = f"{allure_path}{name_test}.json"
    if json_body == '':
        json_body = {}
    with open(f'{file}', 'w', encoding='utf-8') as file:
        file.write(f'{json_body}') #Передаваемые значение необходимо оборачивать строку, так как другие типы данных не поддерживаются при редак файла
        file.close
    Log.Event(f"Создан файл - {file}")
        
def CreateNameTest(name_test: str, name_file: str):
    # Функция добавляет название теста в отчет
    colvir = CreateJsonReport()
    key = ["name", "description", "start"]
    value = [name_test, name_test, GetDateTimeMilli()]
    abs_path = FindAbsPathFile(name_file)  # Получение абсолютного пути файла
    AddKeyValueJson(abs_path, key, value)
    
def AddSubSuite(sub_suite: str):
    # Функция добавляет название группы тестов в отчет
    key_labels_subsuite = ["name", "value"]
    value_labels_subsuite = ["subSuite", sub_suite]
    Log.Message(f"Глобальная переменная - {name_test_global}")
    abs_path = FindAbsPathFile(name_test_global)  # Получение абсолютного пути файла
    AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)
    
def AddModuleName(module_name: str):
    # Функция добавляет название модуля
    key_labels_suite = ["name", "value"]
    value_labels_suite = ["suite", module_name]
    abs_path = FindAbsPathFile(name_test_global)  # Получение абсолютного пути файла
    AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)

def FindAbsPathFile(file_name):
    """Функция, которая принимает название файла и возвращает его абсолютный путь
    В названии файла необходимо указывать тип расширения. В данном случае .json"""
    colvir = CommonOperation()
    user_name = getpass.getuser() #Получение логина пользователя, чтобы функция работала под разнымми пользователями
    allure_path = colvir.GetEnviron('NEW_PATH')
    allure_path = allure_path[:-1]
    if ".json" in file_name:
        file_name = f"{file_name}.json"
        new_name = file_name.replace(".json", "-result", 1)
        try:
            os.rename(f"{allure_path}/{file_name}", f'{allure_path}/{new_name}')
        except FileNotFoundError as error:
            Log.Event(f"Не найден файл {file_name}. Возможно он уже был переименован")
            Log.Event(error)
    else:
        file_name = f"{file_name}.json"
        new_name = f"{file_name[:-5]}-result.json"
        try:
            os.rename(f"{allure_path}/{file_name}", f'{allure_path}/{new_name}')
        except FileNotFoundError as error:
            Log.Event(f"Не найден файл {file_name}. Возможно он уже был переименован")
            Log.Event(error)
    full_path = os.path.join(allure_path, new_name)
    Log.Message(full_path)
    p = os.path.normpath(os.path.abspath(full_path)) #После того, как файл найден в переменную записывается его абсолютный путь
    Log.Message(p)
    return p.replace("\\", "/") #возвращается абс путь с изменненным слешем
    
def AddKeyValueJson(path_to_file, key, value):
    """Функция добавляет в файл json параметры ключ: значение
    #Функция принимает списки с ключами и значениями. Один список с ключами, второй список с значениями.
    #Порядок расположения ключей и значений должен совпадать для каждой пары"""
    required_key = ["attachments", "steps", "labels"] # Данные ключи будут добавляться всегда, с пустым словарем, если они не существуют в словаре
    required_value = [[], [], []]
    count = 0
    if type(key) == list and type(value) == list: # Передаваемый тип данных должен быть list
        for i in range(len(required_key)):
            if required_key[i] in key:
                count += 1
                Log.Warning(f'В функцию нельзя передавать ключ {required_key[i]}')
        if count > 0:
            Log.Error(f'В функцию передаются запрещенные ключи')
        else:
            key += required_key
            value += required_value
            with open(path_to_file, 'r+') as file:
                    data = json.load(file)
                    file.close
                    default_data = defaultdict(dict, data)
                    for i in range(len(key)):
                        if key[i] in ("steps", "attachments", "labels") and key[i] in default_data:
                            Log.Event(f'Ключ {key[i]} уже существует в словаре')
                        else:
                            default_data[key[i]] = value[i]
            with open(path_to_file, 'w') as file:
                file.write(json.dumps(dict(default_data)))
                file.close
    else:
        Log.Warning(f'Передаваемые данные не являются списком - {type(key)}, {type(value)}. Данные необходимо передавать в списке')
        
def AddNestedElements(path_to_file, path_to_key, key, value, need_list=True):
    """Функция принимает наименование элемента. Может принимать и дочерние элементы. Пример: element["step"]["step"]
    Принимает значение элемента. Если флаг list = True, то передаваемые значения словаря будут обернуты в список
    Если флаг list = False, то будет добавлен только словарь
    В данной реализации пока предусмотрена передача только словаря"""
    required_key = ["steps", "attachments", "labels"] # Данные ключи будут добавляться всегда, с пустым словарем, если они не существуют в словаре
    required_value = [[], [], []]
    count = 0
    with open(path_to_file, 'r+') as file: # Выгружаем данные из файла в переменную
        data = json.load(file)
        file.close
    for i in range(len(required_key)):
        if required_key[i] in key:
            count += 1
            Log.Warning(f'В функцию нельзя передавать ключ {required_key[i]}')
    if count > 0:
        Log.Error(f'В функцию передаются запрещенные ключи')
    else:
        if type(key) is list and type(value) is list: # Передаваемый тип данных должен быть list
            if isinstance(dp.get(data, path_to_key), (list, dict)):
                if isinstance(dp.get(data, path_to_key), list):
                    Log.Event(f'тип ключа - {type(dp.get(data, path_to_key))}')
                    key += required_key
                    value += required_value

                    new_dict = zip(key, value)
                    new_dict = dict(new_dict)
                    value_list = dp.get(data, path_to_key)
                    value_list.append(new_dict)
                    with open(path_to_file, 'w') as file:
                        file.write(json.dumps(data))
                        file.close
                if isinstance(dp.get(data, path_to_key), dict):
                    Log.Event(f'тип ключа - {type(dp.get(data, path_to_key))}')
                    new_dict = zip(key, value)
                    new_dict = dict(new_dict)
                    value_dict = dp.get(data, path_to_key)
                    value_dict.update(new_dict)
                    with open(path_to_file, 'w') as file:
                        file.write(json.dumps(data))
                        file.close
            else:
                Log.Warning(f'Значение ключа не является списком или словарем - {type(dp.get(data, path_to_key))}')
        else:
            Log.Warning(f'Передаваемые данные не являются списком - {type(key)}, {type(value)}. Данные необходимо передавать в списке')


def GetDateTimeMilli():
    """Получение времени"""
    milliseconds = int(round(time.time() * 1000))
    return milliseconds
    
def AllureReportTemplate(abs_path, name_file, name_step, status_step, message, pic_object, name_pic, new_path, status_test, step_id, substep_id, rm = False):
    """Шаблон для заполнения json файла с отчетом для Allure
    Если после отработки функции необходимо переместить файл, то при вызове функции указываем rm = True"""
    report = CreateJsonReport() 
    step_id -= 1
    if substep_id == 1:
        path_step = 'steps'
    else:
        path_step = 'steps' + (f'/{step_id}/steps' * (substep_id - 1))
    path_to_pic = (f'steps/{step_id}/' * substep_id) + 'attachments'
    stop_time = f'steps/{step_id}/' * substep_id
    stop_time = stop_time[:-1]
    key_steps = ["name", "status", "statusDetails", "start"]
    value_steps = [name_step, status_step, message, GetDateTimeMilli()]
    AddNestedElements(abs_path, path_step, key_steps, value_steps)
    # Сначала проверяется, передается ли значение desktop. Если да, то создается скрин всего рабочего стола
    # Необходимо в местах где нет конкретного названия объекта, которое необходимо передать для скриншота
    if pic_object == 'desktop':
        name_pic_step_1 = f'{report.GetRandomNumber()}.png'
        Sys.Desktop.Picture().SaveToFile(f'{new_path}{name_pic_step_1}')
        key_attach = ["name", "source", "type"]
        val_attach = [name_pic, name_pic_step_1, "image/png"]
        AddNestedElements(abs_path, path_to_pic, key_attach, val_attach)
    # Если значение desktop не передается, то выполняется проверка на not None и если значение есть, то создается скриншот
    # Передаваемого объекта
    # Если передавать название объекта, то ТС удет его скринить, если не передавать, то данный блок выполняться не будет
    elif pic_object is not None and name_pic is not None:
        get_pict = Sys.Process("COLVIR").Find("Name", pic_object)
        name_pic_step_1 = f'{report.GetRandomNumber()}.png'
        get_pict.Picture().SaveToFile(f'{new_path}{name_pic_step_1}')
        key_attach = ["name", "source", "type"]
        val_attach = [name_pic, name_pic_step_1, "image/png"]
        AddNestedElements(abs_path, path_to_pic, key_attach, val_attach)
    AddNestedElements(abs_path, stop_time, ["stop"], [GetDateTimeMilli()])
    AddKeyValueJson(abs_path, ["status", "stop"], [status_test, GetDateTimeMilli()])
    if rm == True:
        Log.Message("Перемещение не требуется по новой логике")

    
def AllureReportEnd(count: int, name_file: str, status: str, error: str = None):
    # метод обрабатывает непредвиденные ошибки и перемещает файл в allure-result
    colvir = CommonOperation() 
    abs = FindAbsPathFile(name_file) # Получение абсолютного пути файла
    new_path = colvir.GetEnviron('NEW_PATH') # путь для перемещения файла с отчетом
    if status == "failed":
        Log.Warning(f"Произошла ошибка при выполнении скрипта")
        Log.Warning(f"Текст ошибки - {error}")
        AllureReportTemplate(abs, name_file, f"Непредвиденная ошибка", status, {"message": f"Возникла ошибка. Текст ошибки - {error}"},
                                  "desktop", "Возникла ошибка", new_path, status, count, 1, rm=True)
    elif status == "passed":
        Log.Checkpoint(f"Тест завершен успешно")
        AllureReportTemplate(abs, name_file, f"Тест выполнен", status, {"message": f"Тест завершен успешно"},
                                  "desktop", "Завершен успешно", new_path, status, count, 1, rm=True)

