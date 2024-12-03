from ColvirFramework import *

def LoginInColvir(user_login='', user_password='', alias_bd='', stand=''):
    """ Логин в колвир по параметрам с принудительным перезапуском приложения
    Если передан флаг даты опердня, то приложение при входе сменит опердень на переданный
    """
    config = Config()
    common = CommonOperation()
    # если не заданы параметры для входа, то брать их админские из конфига
    if not user_login and not user_password:
      user_login, user_password = config.GetLoginPassAdm()
    if not alias_bd and not stand:
      stand, alias_bd = config.GetTestStandAliasDB()
    config.KillProcessApp('COLVIR.exe')  # проверка на запущенные копии колвира и завершение запущенных
    # если задано значение переменной среды, то добавляет и использует новое тестовое приложение, добавленное при инициализации
    if common.GetEnviron("CLIENT_FOLDER") != 'None':
      client_folder_name = config.GetClientFolderName()
      full_path_app = ProjectSuite.Path + client_folder_name + '\\colvir.exe'
      test_app_index = TestedApps.Add(full_path_app)
      TestedApps.Items[test_app_index].Run()
    else:
      TestedApps.Items[stand].Run()
    if common.WaitLoadWindow("frmLoginDlg", negativ_case=True):
      Log.Event("Вышло окно входа, не требующее настроек")
    # Проверки на наличие окна ошибки и окна входа, если вход был задан через сервер безопасности
    elif Sys.Process("COLVIR").WaitWindow("TMessageForm", "Ошибка", -1, 500).Exists or\
      Sys.Process("COLVIR").WaitVCLObject("CSSAuthPwdDialog", 500).Exists:
      Log.Event("Требуются настройки логина")
      common.LLPKeys(VK_ESCAPE)
      #если задан вход через сервер безопасности (логику всего метода надо будет обновить немного)
      main_menu = Sys.Process("COLVIR").VCLObject("frmCssAppl").MenuBar("Приложение").MenuItem("Исполнитель")
      main_menu.Click()
      main_menu_item = Sys.Process("COLVIR").Popup("Исполнитель").MenuItem("Настройки...")
      main_menu_item.Click()
      page_interface = common.FindChildField("frmAppPrmDialog", "Name", 'PageTab("Интерфейс")')
      page_interface.Click()
      alias_bd_checkbox = common.FindChildField("frmAppPrmDialog", "Name", 'VCLObject("cbAlias")')
      if alias_bd_checkbox.State == 0:
        alias_bd_checkbox.Click()
      page_security = common.FindChildField("frmAppPrmDialog", "Name", 'PageTab("Безопасность")')
      page_security.Click()
      conn_server_checkbox = common.FindChildField("frmAppPrmDialog", "Name", 'VCLObject("chbUseConnectionServer")')
      if conn_server_checkbox.State == 1:
        conn_server_checkbox.Click()
      conn_sec_server_checkbox = common.FindChildField("frmAppPrmDialog", "Name", 'VCLObject("chbUseSecurityServer")')
      if conn_sec_server_checkbox.State == 1:
        conn_sec_server_checkbox.Click()
      settings_btn_ok = common.FindChildField("frmAppPrmDialog", "Name", 'VCLObject("btnOK")')
      settings_btn_ok.Click()
      login_btn = Sys.Process("COLVIR").VCLObject("frmCssAppl").VCLObject("btnLogin")
      login_btn.Click()
      common.WaitLoadWindow("frmLoginDlg")
    login_window = Sys.Process("COLVIR").VCLObject("frmLoginDlg")
    login_field = login_window.VCLObject("pnlClient").VCLObject("edtName")
    login_field.Keys(user_login)
    passwd_field = login_window.VCLObject("pnlClient").VCLObject("edtPassword")
    passwd_field.Keys(user_password)
    alias_field = login_window.VCLObject("pnlAlias").VCLObject("cbALIAS")
    alias_field.Keys(alias_bd)
    ok_login = login_window.VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK")
    ok_login.Click()
    # перехват ошибки при входе в систему
    if common.ErrorMessageHandler():
      Log.Error('Произошла ошибка при входе в Colvir')
    common.WarningMessageHandler('no_log')  #Закрытие различных окон 'предупреждений' при входе в колвир
    common.ClickNeedButConfirmWindow('No', time_await=1800) # доп проверка на нераспечатанные отчеты
    common.WaitLoadWindow("frmCssAppl")
    # проверка не передана ли дата опердня
    Log.Event("Удачно авторизовались в колвире")

def GetLoginPass(login_type, list_logins=None):
    """ Метод получения номера строки учетной записи в LoginPool, установленной в переменной среде LOGIN_INDEX_LIST
    либо получение учетной записи по указанному типу в виде логин;пароль
    входной параметр - тип учетной записи
    возвращает логин и пароль (если указан индекс, то логин и пароль из LoginPool)
    формат заполнения переменной среды LOGIN_INDEX_LIST
    Тип списка: тип учетки=индекс/логин;пароль, тип учетки=индекс/логин;пароль
    Пример: FL:DEPOSITOFFICER=34,KASSIR=AS_KASSAN;qweqwe123
    """
    config = Config()
    common = CommonOperation()
    dict_index = {}
    login_numbers_value = None
    get_login_user = ''
    get_pass_user = ''
    get_variable = config.GetEnviron('LOGIN_INDEX_LIST')
    normal_list = get_variable.replace(' ', '').split(':')
    list_log_pas = normal_list[1].replace(' ', '').split(',')
    list_log_pas = [item.split('=') for item in list_log_pas]
    dict_index = dict(list_log_pas) # преобразуем в словарь
    for key, value in dict_index.items():
      if key == login_type:
        login_numbers_value = value
    if list_logins is not None and login_numbers_value is not None:
      return login_numbers_value
    elif list_logins is not None and login_numbers_value is None:
      Log.Event('Отсутствует список учетных записей ' + str(login_type) + ' в переменной среде LOGIN_INDEX_LIST')
      return login_numbers_value
    if login_numbers_value is None:
      Log.Warning('Отсутствует тип учетной записи ' + str(login_type) + ' в переменной среде LOGIN_INDEX_LIST')
      get_login_user = None
      get_pass_user = None
    elif login_numbers_value.isdigit(): # проверяем на наличие цифр
      get_login_user, get_pass_user = common.GetLoginPassByIndex(login_numbers_value)
    else:
      log_pas = login_numbers_value.replace(' ', '').split(';')
      get_login_user = log_pas[0]
      get_pass_user = log_pas[1]
    return get_login_user, get_pass_user
    
def GetLoginPassAdm():
    """ Получение логина и пароля админа (colvir) из конфига """
    get_login_adm = ConfigHandler(3)
    get_pass_adm = ConfigHandler(4)
    return get_login_adm, get_pass_adm
    
def GetTestStandAliasDB():
    """ Получение тестового стенда и алиаса БД из конфига """
    get_test_stand = ConfigHandler(0)
    get_alias = ConfigHandler(1)
    return get_test_stand, get_alias

def ConfigHandler(need_column):
    """ Обработка config.csv датасета для получения необходимого значения по номеру столбца """
    row = config.GetEnviron("CONFIG_COLVIR")
    return row.split(',')[need_column]
   
        
        