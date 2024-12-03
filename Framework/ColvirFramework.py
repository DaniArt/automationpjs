from datetime import datetime
from datetime import date
from datetime import timedelta
from random import choice
from random import randint
from string import digits
from string import ascii_letters
from os import system
from os import chdir
from os import path
from os import environ
import time
from time import perf_counter
from subprocess import check_output
from subprocess import call
import re
import csv
import shutil
import sys
import xml.etree.ElementTree as ET
import telnetlib
import socket
# необходим установленный Python 3.6.0 - 3.6.4 32-bit с библиотеками, которые импортируются ниже
sys.path.insert(0, aqEnvironment.GetEnvironmentVariable('PYTHON')) # расположение Python на локальной машине
import requests
import cx_Oracle
import json
import smtplib
from email.mime import multipart
from email.mime import text
from email import encoders
from email.mime import base
import os
import PIL
from PIL import Image
import urllib3
from suds import null
from suds.client import Client
from suds.plugin import MessagePlugin
from colorama import init, Fore
from typing import List
from typing import Dict
#import allure
#import pytest

from enum import Enum
import glob
import getpass
from collections import defaultdict
import dpath.util as dp
import time
import calendar
import random
#from faker import Faker


class Config:
    """ Класс парсинга конфига приложения colvir для тестов """


    def GetLoginPassAdm(self):
        """ Получение логина и пароля админа (colvir) из конфига """
        get_login_adm = self.ConfigHandler(3)
        get_pass_adm = self.ConfigHandler(4)
        return get_login_adm, get_pass_adm

    def GetTestStandAliasDB(self):
        """ Получение тестового стенда и алиаса БД из конфига """
        get_test_stand = self.ConfigHandler(0)
        get_alias = self.ConfigHandler(1)
        return get_test_stand, get_alias

    def GetClientFolderName(self):
        """ Получение имени папки с клиентской частью из конфига """
        get_stand_folder = self.ConfigHandler(5)
        return get_stand_folder

    def GetConnString(self):
        """ Получение строки подключения к БД из конфига """
        get_conn_str = self.ConfigHandler(2)
        get_alias_db = self.ConfigHandler(1)
        connect_info = get_conn_str.split(':')
        return connect_info[0], connect_info[1], get_alias_db

    def GetDatasetFolder(self, need_folder=''):
        """ Получение директории с датасетами для тестов и обработчиков """
        self.need_folder = need_folder
        if self.need_folder:
          return ProjectSuite.Path + 'Datasets\\' + self.need_folder + '\\'
        else:
          return ProjectSuite.Path + 'Datasets\\'

    def CheckUploadFileDatset(self, filename):
        """ Проверка, существует ли в корне проекта при сборке, файл с аналогичным именем """
        self.filename = filename
        if path.isfile(ProjectSuite.Path + self.filename):
          Log.Message("Был подложен файл датасета " + self.filename)
          return True
        else:
          return False

    def DatasetReader(self, dataset_folder, dataset_name, env_type=None):
        """ Зачитывание датасета в список построчно,
        возвращает список со списками строк (каждая строка в отдельном списке),
        параметр env_type указывается для проектов, где есть разделение по типам клиентов
        """
        self.dataset_folder = dataset_folder
        self.dataset_name = dataset_name
        self.env_type = env_type
        dataset_list = []

        if self.env_type is not None:
          self.dataset_name = self.dataset_name + self.GetEnviron(self.env_type) +'.csv'
        if self.CheckUploadFileDatset(self.dataset_name):
          get_folder = ProjectSuite.Path
        else:
          get_folder = self.GetDatasetFolder(self.dataset_folder)
        try:
          with open(get_folder + self.dataset_name, newline='', encoding='utf-8') as dataset:
            reader = csv.reader(dataset)
            for current_row in reader:
              dataset_list.append(current_row)
        except Exception as err:
          Log.Error('Не найден файл конфигурации или датасета ' + str(err))
        return dataset_list

    def DatasetWriter(self, dataset_folder, dataset_name, data_list, env_type=None):
        """ Запись данных в датасет построчно,
        параметр env_type указывается для проектов, где есть разделение по типам клиентов
        """
        self.dataset_folder = dataset_folder
        self.dataset_name = dataset_name
        self.data_list = data_list
        self.env_type = env_type

        if self.env_type is not None:
          self.dataset_name = self.dataset_name + self.GetEnviron(self.env_type) +'.csv'
        if self.CheckUploadFileDatset(self.dataset_name):
          get_folder = ProjectSuite.Path
        else:
          get_folder = self.GetDatasetFolder(self.dataset_folder)
        with open(get_folder + self.dataset_name, 'w', newline='', encoding='utf-8') as save_dataset:
          writer = csv.writer(save_dataset, delimiter=',')
          for rows in self.data_list:
            writer.writerow(rows)

    def DatasetReaderToOrderedDict(self, dataset_folder, dataset_name, env_type=None):
        """ Зачитывание датасета в список построчно,
        возвращает список с упорядоченными словарями (каждый словарь в отдельном списке),
        параметр env_type указывается для проектов, где есть разделение по типам клиентов
        """
        self.dataset_folder = dataset_folder
        self.dataset_name = dataset_name
        self.env_type = env_type
        dataset_dict = []
        if self.env_type is not None:
          self.dataset_name = self.dataset_name + self.GetEnviron(self.env_type) +'.csv'
        if self.CheckUploadFileDatset(self.dataset_name):
          get_folder = ProjectSuite.Path
        else:
          get_folder = self.GetDatasetFolder(self.dataset_folder)
        with open(get_folder + self.dataset_name, newline='', encoding='utf-8') as dataset:
          reader = csv.DictReader(dataset)
          reader = list(reader)
          for current_row in reader:
            dataset_dict.append(current_row)
        return dataset_dict

    def DatasetWriterFromOrderedDict(self, dataset_folder, dataset_name, data_dict, env_type=None):
        """ Запись данных в датасет построчно из списка словарей,
        параметр env_type указывается для проектов, где есть разделение по типам клиентов
        """
        self.dataset_folder = dataset_folder
        self.dataset_name = dataset_name
        self.data_dict = data_dict
        self.env_type = env_type
        if self.env_type is not None:
          self.dataset_name = self.dataset_name + self.GetEnviron(self.env_type) +'.csv'
        if self.CheckUploadFileDatset(self.dataset_name):
          get_folder = ProjectSuite.Path
        else:
          get_folder = self.GetDatasetFolder(self.dataset_folder)
        with open(get_folder + self.dataset_name, 'w', newline='', encoding='utf-8') as save_dataset:
          fieldnames=list((self.data_dict[0]).keys())
          writer = csv.DictWriter(save_dataset, delimiter=',',fieldnames=fieldnames)
          writer.writeheader()
          for rows in self.data_dict:
            writer.writerow(rows)

    def GetCAPConnectInfo(self):
        """ Возвращает данные для подключения к БД CAP"""
        login_cap = self.ConfigHandler(7)
        password_cap = self.ConfigHandler(8)
        alias_db_cap = self.ConfigHandler(6)
        get_stand, get_alias = self.GetTestStandAliasDB()
        return login_cap, password_cap, alias_db_cap, get_alias

    def ConfigHandler(self, need_column):
        """ Обработка config.csv датасета для получения необходимого значения по номеру столбца """
        self.need_column = need_column
        row = self.GetEnviron("CONFIG_COLVIR")
        return row.split(',')[self.need_column]


class ColvirState(Config):
    """ Класс подготовки основного состояния системы для работы тестов """


    def LoginInColvir(self, user_login='', user_password='', alias_bd='', stand=''):
        """ Логин в колвир по параметрам с принудительным перезапуском приложения
        Если передан флаг даты опердня, то приложение при входе сменит опердень на переданный
        """
        self.user_login = user_login
        self.user_password = user_password
        self.alias_bd = alias_bd
        self.stand = stand
        # если не заданы параметры для входа, то брать их админские из конфига
        if not self.user_login and not self.user_password:
          self.user_login, self.user_password = self.GetLoginPassAdm()
        if not self.alias_bd and not self.stand:
          self.stand, self.alias_bd = self.GetTestStandAliasDB()
        self.KillProcessApp('COLVIR.exe')  # проверка на запущенные копии колвира и завершение запущенных
        # если задано значение переменной среды, то добавляет и использует новое тестовое приложение, добавленное при инициализации
        if self.GetEnviron("CLIENT_FOLDER") != 'None':
          client_folder_name = self.GetClientFolderName()
          full_path_app = ProjectSuite.Path + client_folder_name + '\\colvir.exe'
          test_app_index = TestedApps.Add(full_path_app)
          TestedApps.Items[test_app_index].Run()
        else:
          TestedApps.Items[self.stand].Run()
        if self.WaitLoadWindow("frmLoginDlg", negativ_case=True):
          Log.Event("Вышло окно входа, не требующее настроек")
        # Проверки на наличие окна ошибки и окна входа, если вход был задан через сервер безопасности
        elif Sys.Process("COLVIR").WaitWindow("TMessageForm", "Ошибка", -1, 500).Exists or\
          Sys.Process("COLVIR").WaitVCLObject("CSSAuthPwdDialog", 500).Exists:
          Log.Event("Требуются настройки логина")
          self.LLPKeys(VK_ESCAPE)
          #если задан вход через сервер безопасности (логику всего метода надо будет обновить немного)
          main_menu = Sys.Process("COLVIR").VCLObject("frmCssAppl").MenuBar("Приложение").MenuItem("Исполнитель")
          main_menu.Click()
          main_menu_item = Sys.Process("COLVIR").Popup("Исполнитель").MenuItem("Настройки...")
          main_menu_item.Click()
          page_interface = self.FindChildField("frmAppPrmDialog", "Name", 'PageTab("Интерфейс")')
          page_interface.Click()
          alias_bd_checkbox = self.FindChildField("frmAppPrmDialog", "Name", 'VCLObject("cbAlias")')
          if alias_bd_checkbox.State == 0:
            alias_bd_checkbox.Click()
          page_security = self.FindChildField("frmAppPrmDialog", "Name", 'PageTab("Безопасность")')
          page_security.Click()
          conn_server_checkbox = self.FindChildField("frmAppPrmDialog", "Name", 'VCLObject("chbUseConnectionServer")')
          if conn_server_checkbox.State == 1:
            conn_server_checkbox.Click()
          conn_sec_server_checkbox = self.FindChildField("frmAppPrmDialog", "Name", 'VCLObject("chbUseSecurityServer")')
          if conn_sec_server_checkbox.State == 1:
            conn_sec_server_checkbox.Click()
          settings_btn_ok = self.FindChildField("frmAppPrmDialog", "Name", 'VCLObject("btnOK")')
          settings_btn_ok.Click()
          login_btn = Sys.Process("COLVIR").VCLObject("frmCssAppl").VCLObject("btnLogin")
          login_btn.Click()
          self.WaitLoadWindow("frmLoginDlg")
        login_window = Sys.Process("COLVIR").VCLObject("frmLoginDlg")
        login_field = login_window.VCLObject("pnlClient").VCLObject("edtName")
        login_field.Keys(self.user_login)
        passwd_field = login_window.VCLObject("pnlClient").VCLObject("edtPassword")
        passwd_field.Keys(self.user_password)
        alias_field = login_window.VCLObject("pnlAlias").VCLObject("cbALIAS")
        alias_field.Keys(self.alias_bd)
        ok_login = login_window.VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK")
        ok_login.Click()
        # перехват ошибки при входе в систему
        if self.ErrorMessageHandler():
          Log.Error('Произошла ошибка при входе в Colvir')
        self.WarningMessageHandler('no_log')  #Закрытие различных окон 'предупреждений' при входе в колвир
        if Sys.Process("COLVIR").WaitDialog("Подтверждение",3000).Exists:
          Sys.Process("COLVIR").Dialog("Подтверждение").VCLObject("No").Click()
        self.ClickNeedButConfirmWindow('No', time_await=1800) # доп проверка на нераспечатанные отчеты
        self.WaitLoadWindow("frmCssAppl")
        # проверка не передана ли дата опердня
        Log.Event("Удачно авторизовались в колвире")

    def KillProcessApp(self, name_app):
        """ Проверка на запущенные копии приложения через диспетчер задач
         и принудительное завершение всех запущенных процессов """
        self.name_app = name_app
        tasks = check_output('tasklist').splitlines()
        for task in tasks:
          list_process = task.decode("cp1251").split()
          if self.name_app in list_process:
            system("taskkill /im " + self.name_app + " /F")
        Delay(2000)  # даем выгрузиться из памяти

    def WaitingKillProcessApp(self, name_app):
        """ Метод получает название процесса и ждет пока он не появится в списке процессов Windows
            После того, как он появится происходит закрытие данного процесса
            Данный метод необходим для операций при которых выгружается из Колвира на рабочий стол
            какой-либо документ на печать, а выполнение операции происходит только после закрытия документа"""
        self.name_app = name_app
        # запускаем цикл, который будет проверять появился ли нужный процесс в списке
        while True:
            tasks = check_output('tasklist').splitlines()
            for task in tasks:
                list_process = task.decode("cp1251").split()
            if self.name_app in list_process:
                system("taskkill /im " + self.name_app + " /F")
                break
        Delay(2000)  # даем выгрузиться из памяти

    def OperDayValue(self):
        ''' В данной функции открывается окно с оперднем. Из него берется дата опердня. Окно закрывается '''
        Sys.Process("COLVIR").VCLObject("AppLayer").VCLObject("MainPanel").DblClick(1714, 16)
        od_value = Sys.Process("COLVIR").VCLObject("frmOprDayDialog").VCLObject("edOperDay").Window("TClMaskEdit", "__.__.__", 1).Value
        Sys.Process("COLVIR").VCLObject("frmOprDayDialog").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnCancel").Click()
        return od_value

    def SetNeedOperday(self, operday_date):
        """ Установка необходимого опердня для теста
        На вход необходимо подавать дату формата %d.%m.%y
        Сначала идет сравнение на совпадение переданной даты с установленным оперднем,
        если они совпадают, то опердень не будет проставлятся
        """
        self.operday_date = operday_date
        win_sys_date = Sys.Process("COLVIR").VCLObject("AppLayer").VCLObject("MainPanel").DblClick(1730, 16)
        date_statusbar = Sys.Process("COLVIR").VCLObject("frmOprDayDialog").VCLObject("edOperDay").Window("TClMaskEdit", "__.__.__", 1).Value
        Sys.Process("COLVIR").VCLObject("frmOprDayDialog").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnCancel").Click()
        if self.operday_date == date_statusbar.strip():
          Log.Event("Необходимая дата опердня уже установлена в колвире")
          return
        win_sys_date = Sys.Process("COLVIR").VCLObject("AppLayer").VCLObject("MainPanel").DblClick(1730, 16)
        self.WaitLoadWindow("frmOprDayDialog")
        need_day = Sys.Process("COLVIR").VCLObject("frmOprDayDialog").VCLObject("edOperDay")
        need_day.Keys(self.NormalDateMask(self.operday_date))
        ok_operday_window = Sys.Process("COLVIR").VCLObject("frmOprDayDialog").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK")
        ok_operday_window.Click()
        # если нужный день не является рабочим прибавляем дни до следующего рабочего дня
        self.WarningMessageHandler('no_log')
        Delay(1200)
        if Sys.Process("COLVIR").WaitVCLObject("frmOprDayDialog", 1200).Exists and \
          Sys.Process("COLVIR").WaitVCLObject("frmOprDayDialog", 1200).Enabled:
          daily_date = self.GetPlusDailyDate(1, self.operday_date)
          Log.Event("Будет определен и выставлен следующий рабочий день")
          need_day.Keys('[Home]')
          need_day.Keys(self.NormalDateMask(daily_date))
          ok_operday_window.Click()
        if Sys.Process("COLVIR").WaitWindow("TMessageForm", "Внимание", -1, 1200).Exists:
          txt_mess = Sys.Process("COLVIR").Dialog("Внимание").VCLObject("Message").Caption
          if txt_mess.startswith('Не открыт'):
            Log.Event(str(txt_mess))
          Sys.Process("COLVIR").Dialog("Внимание").VCLObject("Yes").Click()
          ok_operday_window.Click()
        self.WarningMessageHandler('no_log')

    def ReturnActualOperdayClient(self):
        """ Установка опердня в клиентской части колвира согласно переменной среды DATE_OPERDAY"""
        current_date = self.GetEnviron("DATE_OPERDAY")
        win_sys_date = Sys.Process("COLVIR").VCLObject("AppLayer").VCLObject("MainPanel").DblClick(1714, 16)
        date_statusbar = Sys.Process("COLVIR").VCLObject("frmOprDayDialog").VCLObject("edOperDay").Window("TClMaskEdit", "__.__.__", 1).Value
        Sys.Process("COLVIR").VCLObject("frmOprDayDialog").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnCancel").Click()
        if current_date != date_statusbar:
          self.SetNeedOperday(current_date)

    def WindowUser(self):
        """Открытие окна пользователя"""
        try:
            # закрыть окно диагностики если зависло
            if Sys.Process("COLVIR").WaitVCLObject("frmDebugView", 1200).Exists:
                Sys.Process("COLVIR").VCLObject("frmDebugView").Close()
            menu_user = Sys.Process("COLVIR").VCLObject("AppLayer").VCLObject("MainPanel")
            menu_user.Click(1373, 20)
            for _ in range(7):
              LLPlayer.KeyDown(VK_UP, 500) # нажатие стрелки вверх 1 раз
              LLPlayer.KeyUp(VK_UP, 500)
            LLPlayer.KeyDown(VK_RETURN, 500) # Нажатие Enter
            Log.Event("Окно отрыто 'Юзер' ")
        except:
            Log.Warning("Неудалось открыть окно 'Юзер'")

    def StartDebugLog(self):
        """ Включение отладки в колвире уровень 'Подробная' с предварительной очисткой """
        try:
          # закрыть окно диагностики если зависло
          if Sys.Process("COLVIR").WaitVCLObject("frmDebugView", 1200).Exists:
            Sys.Process("COLVIR").VCLObject("frmDebugView").Close()
          menu_debug = Sys.Process("COLVIR").VCLObject("AppLayer").VCLObject("MainPanel")
          menu_debug.Click(1373, 20)
          # Очистка отладки
          for _ in range(5):
            LLPlayer.KeyDown(VK_UP, 3) # нажатие стрелки вверх 4 раза
            LLPlayer.KeyUp(VK_UP, 3)
            LLPlayer.KeyDown(VK_RIGHT, 3) # нажатие стрелки вправо
            LLPlayer.KeyUp(VK_RIGHT, 3)
            if Sys.Process("COLVIR").WaitMenuItem("Отладка", 200).Exists:
                LLPlayer.KeyDown(VK_DOWN, 3) # нажатие стрелки вниз
                LLPlayer.KeyUp(VK_DOWN, 3)
                LLPlayer.KeyDown(VK_RETURN, 3) # нажатие enter на очистке отладки
                LLPlayer.KeyUp(VK_RETURN, 3)
            else:
                LLPlayer.KeyDown(VK_LEFT, 3) # нажатие стрелки влево
                LLPlayer.KeyUp(VK_LEFT, 3)
          # Проставление отладки "Подробная"
          menu_debug.Click(1373, 20)
          for _ in range(5):
              LLPlayer.KeyDown(VK_UP, 3) # нажатие стрелки вверх 4 раза
              LLPlayer.KeyUp(VK_UP, 3)
              LLPlayer.KeyDown(VK_RIGHT, 3) # нажатие стрелки вправо
              LLPlayer.KeyUp(VK_RIGHT, 3)
              if Sys.Process("COLVIR").WaitMenuItem("Отладка", 200).Exists:
                  LLPlayer.KeyDown(VK_RIGHT, 3) # нажатие стрелки вниз
                  LLPlayer.KeyUp(VK_RIGHT, 3)
                  LLPlayer.KeyDown(VK_RETURN, 3) # нажатие enter на очистке отладки
                  LLPlayer.KeyUp(VK_RETURN, 3)
              else:
                  LLPlayer.KeyDown(VK_LEFT, 3) # нажатие стрелки влево
                  LLPlayer.KeyUp(VK_LEFT, 3)
          Log.Event("Отладка на уровень 'Подробная' включена")
        except:
          Log.Warning("Не удалось включить отладку")

    def SaveDebugLog(self):
        """ Сохранение в лог записанной отладки через буфер обмена"""
        try:
          menu_debug = Sys.Process("COLVIR").VCLObject("AppLayer").VCLObject("MainPanel")
          menu_debug.Click(1373, 20)
          for _ in range(5):
              LLPlayer.KeyDown(VK_UP, 3) # нажатие стрелки вверх 4 раза
              LLPlayer.KeyUp(VK_UP, 3)
              LLPlayer.KeyDown(VK_RIGHT, 3) # нажатие стрелки вправо
              LLPlayer.KeyUp(VK_RIGHT, 3)
              if Sys.Process("COLVIR").WaitMenuItem("Отладка", 200).Exists:
                  LLPlayer.KeyDown(VK_DOWN, 3)
                  LLPlayer.KeyUp(VK_DOWN, 3)
                  LLPlayer.KeyDown(VK_DOWN, 3)
                  LLPlayer.KeyUp(VK_DOWN, 3)
                  LLPlayer.KeyDown(VK_RETURN, 3)
                  LLPlayer.KeyUp(VK_RETURN, 3)
              else:
                  LLPlayer.KeyDown(VK_LEFT, 3) # нажатие стрелки влево
                  LLPlayer.KeyUp(VK_LEFT, 3)
          if self.WarningMessageHandler('no_log'):
            Log.Event("Отладка пуста")
            return
          self.WaitLoadWindow("frmDebugView")
          text_log = self.FindChildField("frmDebugView", "Name", "VCLObject('DebugText')")
          text_log.Click(40,40)
          # копируем отладку в буфер обмена, чтобы отразить в лог
          text_log.Keys("^a")
          text_log.Keys("^c")
          Log.AppendFolder("Отладка")
          Log.Message(Sys.Clipboard)
          Log.PushLogFolder(-1)
          self.DebugLogAnalyst(Sys.Clipboard)
          Sys.Process("COLVIR").VCLObject("frmDebugView").Close()
        except:
          Log.Warning("Не удалось сохранить записанную отладку")

    def DebugLogAnalyst(self, log_txt):
        """ Анализ и обработка специальных строк из лога отладки """
        self.log_txt = log_txt
        log_oper_list = []
        for rows in self.log_txt.splitlines():
          if rows.startswith('Диагностика выполнения'):
            Log.Message("OPERATION: " + str(rows))
            log_oper_list.append(rows)
        self.SaveLogWithDebug(log_oper_list)

    def SaveLogWithDebug(self, log_info):
        """ Сохранение в файл обработанного списка лога отладки """
        self.log_info = log_info
        old_log_data = []
        # проверка есть ли файл с логом
        Log.Message(str(self.log_info))
        if not path.isfile(ProjectSuite.Path + 'debug_log.csv'):
          with open(ProjectSuite.Path + 'debug_log.csv', 'w', newline='', encoding='utf-8') as save_log:
            writer = csv.writer(save_log, delimiter=',')
            writer.writerow(self.log_info)
          Log.Message('Обработанный лог отладки успешно создан и сохранен, адрес ' + ProjectSuite.Path + 'debug_log.csv')
        else:
          with open(ProjectSuite.Path + 'debug_log.csv', newline='', encoding='utf-8') as log_data:
            reader = csv.reader(log_data)
            for current_row in reader:
              old_log_data.append(current_row)
          old_log_data.append(self.log_info)
          Log.Message(str(old_log_data))
          with open(ProjectSuite.Path + 'debug_log.csv', 'w', newline='', encoding='utf-8') as save_log:
            writer = csv.writer(save_log, delimiter=',')
            for rows in old_log_data:
              writer.writerow(rows)
          Log.Message('Обработанный лог отладки успешно дополнен и сохранен, адрес ' + ProjectSuite.Path + 'debug_log.csv')

class CommonOperation(ColvirState):
    """ Класс одинаковых и однотипных операций по всем модулям """

    def GetEnviron(self, variable):
        """ Обработчик переменной среды, возвращает результат установленных значений в переменной
        в виде строки, входной параметр - имя переменной среды.
        """
        self.variable = variable
        get_variable = aqEnvironment.GetEnvironmentVariable(self.variable)
        if self.variable == 'DATE_OPERDAY' and len(get_variable) != 8:
          # Если DATE_OPERDAY не задан - устанвоит текущий день.
          get_variable = aqConvert.DateTimeToFormatStr(aqDateTime.Today(),'%d.%m.%y')
        elif not get_variable:
          get_variable = None
          Log.Error("Переменная среда с именем " + str(self.variable) + " не существует")
        return get_variable

    def SetEnviron(self, name_environ, value):
        """ Установка значения переменной среды, на вход подается имя переменной среды
        и значение, которое нужно установить
        """
        self.name_environ = name_environ
        self.value = value
        result_command = call(['setx',self.name_environ,self.value],shell=True)
        if result_command != 0:
          Log.Warning("Ошибка выполнения команды setx для установки переменной среды, код "+ str(result_command))
        else:
          Log.Event('Значение переменной среды '+ self.name_environ +' успешно установлено '+ str(self.value))

    def GetLoginPassByIndex(self, need_index):
        """ Получение логина и пароля из логинпула для входа в приложение"""
        self.need_index = need_index
        data_list = self.ReadDatasetFromDB('loginpool')
        for row in data_list:
          if row['INDEX_LOGIN'] is not None and (int(row['INDEX_LOGIN']) == int(self.need_index)):
            pass_index_key = self.PassColumnLoginPool()
            return row['TEST_LOGIN'], row[pass_index_key]

    def PassColumnLoginPool(self):
        """ Получение столбца с паролем в зависимости от стенда """
        stand, alias = self.GetTestStandAliasDB()
        if alias.lower() in ['cbs3yes.world','cbs3bt','cbs3test','cbs3tp','cbs3YES','cbs3yes']:
          index_col = 'PASSWORD_3YES'
        elif alias.lower() == 'cbs3bt':
          index_col = 'PASSWORD_3BT'
        elif alias.lower() == 'cbs3test':
          index_col = 'PASSWORD_3test'
        elif alias.lower() == 'cbs3pp':
          index_col = 'PASSWORD_3PP'
        elif alias.lower() == 'cbs3tp':
          index_col = 'PASSWORD_3TEST'
        elif alias.lower() in ['cbstemp','cbs3t4','cbs3t5']:
          index_col = 'PASSWORD_TEMP'
        elif alias.lower() in ['cbs3c','cbs3m','cbs3k', 'cbs3w', 'cbs3y']:
          index_col = 'PASSWORD_3c'
        else:
          Log.Error('Не настроен столбец для стенда в методе по получению пароля '+ alias.lower())
        return index_col

    def SelectLoginDep(self, login_user):
        """ Получение номера подразделения логина через запрос к БД"""
        self.login_user = login_user
        if self.login_user is None:
          self.login_user = 'COLVIR'
        select = """
           select c.CODE, c.DEP_CODE
            from CV_USR2 c
            where GROUPFL=0 AND exists(select 1 from dual where C_pkgUsr.fChkAdm(C.ID)=1)
            and CODE = '""" + self.login_user + """'
        """
        result = self.OracleHandlerDB(select)
        need_dep = ''
        for line in result:
          login_dep = line[1][:3] # возвращаем первые 3 цифры подразделения для обрезки подфилиалов
        if str(login_dep) == '100':
          need_dep = '0000'
        elif login_dep:
          need_dep = self.SelectHeadDep(login_dep)
        return need_dep

    def SelectHeadDep(self, code_dep):
        """ Определение по первым 3 цифрам головного управления филиала, для проставления в фильтр поле 'подразделение' """
        self.code_dep = code_dep
        select = """
          select t.CODE
            ,SUBSTR(t.CODE||'. '||t.LONGNAME,0,255) as NAME
            from CV_DEP t
            where
            t.code like '%""" + self.code_dep + """%' and t.NLEVEL = 2
        """
        result = self.OracleHandlerDB(select)
        return result[0][0]

    def GetLoginPass(self, login_type, list_logins=None):
        """ Метод получения номера строки учетной записи в LoginPool, установленной в переменной среде LOGIN_INDEX_LIST
        либо получение учетной записи по указанному типу в виде логин;пароль
        входной параметр - тип учетной записи
        возвращает логин и пароль (если указан индекс, то логин и пароль из LoginPool)
        формат заполнения переменной среды LOGIN_INDEX_LIST
        Тип списка: тип учетки=индекс/логин;пароль, тип учетки=индекс/логин;пароль
        Пример: FL:DEPOSITOFFICER=34,KASSIR=AS_KASSAN;qweqwe123
        """
        self.login_type = login_type
        self.list_logins = list_logins
        dict_index = {}
        login_numbers_value = None
        get_login_user = ''
        get_pass_user = ''
        get_variable = self.GetEnviron('LOGIN_INDEX_LIST')
        normal_list = get_variable.replace(' ', '').split(':')
        list_log_pas = normal_list[1].replace(' ', '').split(',')
        list_log_pas = [item.split('=') for item in list_log_pas]
        dict_index = dict(list_log_pas) # преобразуем в словарь
        for key, value in dict_index.items():
          if key == self.login_type:
            login_numbers_value = value
        if self.list_logins is not None and login_numbers_value is not None:
          return login_numbers_value
        elif self.list_logins is not None and login_numbers_value is None:
          Log.Event('Отсутствует список учетных записей ' + str(self.login_type) + ' в переменной среде LOGIN_INDEX_LIST')
          return login_numbers_value
        if login_numbers_value is None:
          Log.Warning('Отсутствует тип учетной записи ' + str(self.login_type) + ' в переменной среде LOGIN_INDEX_LIST')
          get_login_user = None
          get_pass_user = None
        elif login_numbers_value.isdigit(): # проверяем на наличие цифр
          get_login_user, get_pass_user = self.GetLoginPassByIndex(login_numbers_value)
        else:
          log_pas = login_numbers_value.replace(' ', '').split(';')
          get_login_user = log_pas[0]
          get_pass_user = log_pas[1]
        return get_login_user, get_pass_user

    def TaskInput(self, code_task):
        """ Очистка поля и ввод необходимой задачи """
        self.code_task = code_task
        if (Sys.Process("COLVIR").WaitVCLObject("AppLayer", 1200).Exists):
          task_field = self.FindChildField("AppLayer", "Name", 'VCLObject"MainPanel"', "internal")
          task_field.Keys("^a")  #выделение поля для исключения в нем старых значений
          task_field.Keys(self.code_task)
          task_field.Keys("[Enter]")
        else:
          Log.Error("Ошибка ввода задачи, не найдено окно для ввода задачи")

    def WaitLoadWindow(self, window_name, time_await=3000, flag=None, negativ_case=None):
        """ Ожидание появления и доступности окна (с техническим запасом Delay).
        Если не передается флаг, то функция рекурсивно вызывает себя (для особо дерганных окон colvir)
        """
        self.window_name = window_name
        self.time_await = time_await
        self.flag = flag
        if Sys.Process("COLVIR").WaitVCLObject(self.window_name, self.time_await).Exists and \
        Sys.Process("COLVIR").VCLObject(self.window_name).WaitProperty("Enabled", True, self.time_await):
          Delay(3300)
          if self.flag is None:
            return self.WaitLoadWindow(self.window_name, self.time_await, 'flag')
          status = True
          if negativ_case is not None:
            Log.Warning("Появилось окно "+ self.window_name)
        else:
          if negativ_case is None:
            Log.Warning("Время ожидания окна "+ self.window_name +" истекло")
          status = False
        return status

    def NormalDateMask(self, need_date=None, not_mask=None, nls_date=None):
        """ Приведение даты к нужному формату без знаков для полей с маской """
        self.need_date = need_date
        self.not_mask = not_mask
        self.nls_date = nls_date
        if self.need_date is None:
          #получаем опердень со статусбара если не передана дата
          self.need_date = self.OperDayValue()
        if self.not_mask is not None:
          normal_date = normal_date = self.need_date.strip()
        elif self.nls_date is not None:
          self.need_date = aqConvert.StrToDate(self.need_date)
          normal_date = aqConvert.DateTimeToFormatStr(self.need_date, "%Y-%m-%d")
        else:
          normal_date = normal_date = self.need_date.strip().replace('.', '').replace(':', '')
        return normal_date

    def GetGridDataFieldsApt(self, wndname, *columns, need_tab=None,need_all_dict = None):
        """ Получение данных из Fields по выделенному документу,
        с произвольным количеством полей, для гридов
        ключ need_tab позволяет получать данные из необходимой вкладки
        ключ need_all_dict позволяет получить словарь сразу со всеми значениями, очищенный от кавычек и с пробелами между словами
        """
        self.wndname = wndname
        self.columns = columns
        self.need_tab = need_tab
        self.need_all_dict = need_all_dict
        result_list = []
        try:
          need_window = Sys.Process("COLVIR").VCLObject(self.wndname)
          need_window.Keys("!^~l")  #shift+ctrl+alt+l открываем секретное окно
          query_form = Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").ListItem("Все запросы формы")
          query_form.DblClick()
          Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel1").VCLObject("lbQueries").ListItem("MainQuery").Click()
          if self.need_tab is not None:
            need_query_tab = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel1").VCLObject("lbQueries").ListItem(self.need_tab)
            need_query_tab.Click()
          grid_sql = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel2").VCLObject("reSQL").wText
          result_fields = grid_sql[grid_sql.find('Fields'):]
          #очищаем от заголовка "Fields:" и убираем пробелы
          result_fields = result_fields[result_fields.find(':')+2:]
          if self.need_all_dict is not None:
            list_temp = result_fields.splitlines()
            list_fields = [v.split('=', 1) for v in list_temp[1:]]
            result_list = {}
            for field in list_fields:
              result_list[field[0].strip()] = field[1].strip().replace('\'','')
          else:
            result_fields = result_fields.replace(' ', '')
            list_temp = result_fields.splitlines()
            #разбиваем на списки параметр-значение внутри одного большого списка
            list_fields = [v.split('=', 1) for v in list_temp[1:]]
            for column in self.columns:
              for item in list_fields:
                if item[0] == column or column == 'all_fields':
                  result_list.append(item[1])
          Sys.Process("COLVIR").VCLObject("frmQrysFormList").Close()
          Sys.Process("COLVIR").VCLObject("frmQueryDlg").Close()
        except Exception as error:
          Log.Error("Не удалось получить данные из гридов, через специальное окно запросов формы " + str(error.args))
        return result_list

    def GetGridDataFields(self, wndname, *columns, need_tab=None,need_all_dict = None):
        """ Получение данных из Fields по выделенному документу,
        с произвольным количеством полей, для гридов
        ключ need_tab позволяет получать данные из необходимой вкладки
        ключ need_all_dict позволяет получить словарь сразу со всеми значениями, очищенный от кавычек и с пробелами между словами
        """
        self.wndname = wndname
        self.columns = columns
        self.need_tab = need_tab
        self.need_all_dict = need_all_dict
        result_list = []
        try:
          need_window = Sys.Process("COLVIR").VCLObject(self.wndname)
          need_window.Keys("!^~l")  #shift+ctrl+alt+l открываем секретное окно
          Delay(1000)
          query_form = Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").ListItem("Все запросы формы")
          query_form.DblClick()
          if self.need_tab is not None:
            need_query_tab = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel1").VCLObject("lbQueries").ListItem(self.need_tab)
            need_query_tab.Click()
          grid_sql = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel2").VCLObject("reSQL").wText
          result_fields = grid_sql[grid_sql.find('Fields'):]
          #очищаем от заголовка "Fields:" и убираем пробелы
          result_fields = result_fields[result_fields.find(':')+2:]
          if self.need_all_dict is not None:
            list_temp = result_fields.splitlines()
            list_fields = [v.split('=', 1) for v in list_temp[1:]]
            result_list = {}
            for field in list_fields:
              result_list[field[0].strip()] = field[1].strip().replace('\'','')
          else:
            result_fields = result_fields.replace(' ', '')
            list_temp = result_fields.splitlines()
            #разбиваем на списки параметр-значение внутри одного большого списка
            list_fields = [v.split('=', 1) for v in list_temp[1:]]
            for column in self.columns:
              for item in list_fields:
                if item[0] == column or column == 'all_fields':
                  result_list.append(item[1])
          Sys.Process("COLVIR").VCLObject("frmQrysFormList").Close()
          Sys.Process("COLVIR").VCLObject("frmQueryDlg").Close()
        except Exception as error:
          Log.Error("Не удалось получить данные из гридов, через специальное окно запросов формы " + str(error.args))
        return result_list
    
    def GetGridDataFieldsText(self, wndname, *columns, need_tab=None,need_all_dict = None):
        """ Получение данных из Fields по выделенному документу,
        с произвольным количеством полей, для гридов
        ключ need_tab позволяет получать данные из необходимой вкладки
        ключ need_all_dict позволяет получить словарь сразу со всеми значениями, очищенный от кавычек и с пробелами между словами
        """
        self.wndname = wndname
        self.columns = columns
        self.need_tab = need_tab
        self.need_all_dict = need_all_dict
        result_list = []
        try:
          need_window = Sys.Process("COLVIR").VCLObject(self.wndname)
          need_window.Keys("!^~l")  #shift+ctrl+alt+l открываем секретное окно
          Delay(3000)
          if Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").WaitTextObject("Все запросы формы", 5000).Exists:
              query_form = Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").TextObject("Все запросы формы")
          elif Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").WaitListItem("Все запросы формы", 3000).Exists:
              query_form = Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").ListItem("Все запросы формы")
          else:
              query_form = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel1").VCLObject("lbQueries").ListItem(self.need_tab)
          query_form.DblClick()
          if self.need_tab is not None:
              if Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel1").VCLObject("lbQueries").WaitListItem(self.need_tab, 3000).Exists:
                  need_query_tab = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel1").VCLObject("lbQueries").ListItem(self.need_tab)
              else:
                  need_query_tab = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel1").VCLObject("lbQueries").TextObject(self.need_tab)
              need_query_tab.Click()
          grid_sql = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel2").VCLObject("reSQL").wText
          result_fields = grid_sql[grid_sql.find('Fields'):]
          #очищаем от заголовка "Fields:" и убираем пробелы
          result_fields = result_fields[result_fields.find(':')+2:]
          if self.need_all_dict is not None:
            list_temp = result_fields.splitlines()
            list_fields = [v.split('=', 1) for v in list_temp[1:]]
            result_list = {}
            for field in list_fields:
              result_list[field[0].strip()] = field[1].strip().replace('\'','')
          else:
            result_fields = result_fields.replace(' ', '')
            list_temp = result_fields.splitlines()
            #разбиваем на списки параметр-значение внутри одного большого списка
            list_fields = [v.split('=', 1) for v in list_temp[1:]]
            for column in self.columns:
              for item in list_fields:
                if item[0] == column or column == 'all_fields':
                  result_list.append(item[1])
          Sys.Process("COLVIR").VCLObject("frmQrysFormList").Close()
          Sys.Process("COLVIR").VCLObject("frmQueryDlg").Close()
        except Exception as error:
          Log.Error("Не удалось получить данные из гридов, через специальное окно запросов формы " + str(error.args))
        return result_list

    def GetTreeDataFields(self, wndname, *columns):
        """ Получение данных из Fields по выделенному документу,
         с произвольным количеством полей, для деревьев """
        self.wndname = wndname
        self.columns = columns
        result_list = []
        try:
          need_window = Sys.Process("COLVIR").VCLObject(self.wndname)
          need_window.Keys("!^~l")  #shift+ctrl+alt+l открываем секретное окно
          query_form = Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").ListItem("Все запросы формы")
          query_form.DblClick()
          need_tree = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel1").VCLObject("lbQueries").ListItem("qryTree")
          need_tree.Click()
          grid_sql = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel2").VCLObject("reSQL").wText
          result_fields = grid_sql[grid_sql.find('Fields'):]
          #очищаем от заголовка "Fields:" и убираем пробелы
          result_fields = result_fields[result_fields.find(':')+2:].replace(' ', '')
          list_temp = result_fields.splitlines()
          #разбиваем на списки параметр-значение внутри одного большого списка
          list_fields = [v.split('=', 1) for v in list_temp]
          for column in self.columns:
            for i in list_fields:
              if i[0] == column:
                 result_list.append(i[1])
          Sys.Process("COLVIR").VCLObject("frmQrysFormList").Close()
          Sys.Process("COLVIR").VCLObject("frmQueryDlg").Close()
        except:
          Log.Error("Не удалось получить данные из древа, через специальное окно запросов формы")
        return result_list

    def GetGridQueryParams(self, wndname, *columns, need_tab=None):
        """ Получение данных из Query Parameters при создании и изменении единичных документов,
        с произвольным количеством полей, для гридов
        ключ need_tab позволяет получать данные из необходимой вкладки
        """
        self.wndname = wndname
        self.columns = columns
        self.need_tab = need_tab
        result_list = []
        try:
          need_window = Sys.Process("COLVIR").VCLObject(self.wndname)
          need_window.Keys("!^~l")  #shift+ctrl+alt+l открываем секретное окно
          query_form = Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").ListItem("Все запросы формы")
          query_form.DblClick()
          if self.need_tab is not None:
            need_query_tab = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel1").VCLObject("lbQueries").ListItem(self.need_tab)
            need_query_tab.Click()
          grid_sql = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel2").VCLObject("reSQL").wText
          result_params = grid_sql[grid_sql.find('Parameters'):grid_sql.find('Fields')]
          #очищаем от заголовка "Parameters:" и убираем пробелы
          result_params = result_params[result_params.find(':')+2:].replace(' ', '')
          list_temp = result_params.splitlines()
          #разбиваем на списки параметр-значение внутри одного большого списка
          list_params = [v.split('=', 1) for v in list_temp]
          for column in self.columns:
            for i in list_params:
              if i[0] == column:
                result_list.append(i[1])
          Sys.Process("COLVIR").VCLObject("frmQrysFormList").Close()
          Sys.Process("COLVIR").VCLObject("frmQueryDlg").Close()
        except:
          Log.Error("Не удалось получить данные раздела Parameters из гридов, через специальное окно запросов формы")
        return result_list

    def StaticSelectFinancialTransation(self, id_operation='', number_oper='', tra_id='', full_info=''):
        """ Получение фин проводок из журнала операций по проведенной операции через запрос в БД.
        Вывод сразу в лог по каждой транзакции, также возвращает список масок счетов по всем транзакциям.
        Если есть TRA_ID при формировании проводок, то рекомендуется передавать все 3 параметра: ID, NJRN, TRA_ID.
        По ключу full_info возвращает полный ответ БД со всеми данными по транзакциям для обработки в тестах.
        Данные передаваемые из гридов не нужно очищать от кавычек.
        """
        self.id_operation = id_operation
        self.number_oper = number_oper
        self.tra_id = tra_id
        self.full_info = full_info
        # фикс обратной
        if not self.tra_id:
          self.tra_id = "''"
        elif not self.id_operation and not self.number_oper:
          self.id_operation = "''"
          self.number_oper = "''"
        date_statusbar = self.OperDayValue() # Берется значение даты опердня
        to_date = aqConvert.DateTimeToFormatStr(date_statusbar, "%d.%m.%Y")
        select = """ select * from (select ll.code as PS, ag1.CODE as acc,
                  (select CODE from T_VAL_STD where ID = d.VAL_ID) as VAL_CODE, d.*,
                  GL_Anl.fAccAnlValue(ag1.DEP_ID, ag1.ID, 'DEPARTMENT') as dep
                  from t_trndtl d, g_accbln ag1, g_accblnhst gg, ledacc ll
                  where d.id in (select tra_id from t_operjrn
                  where id in (select child_id from t_procinh
                  where parent_ID = """+ str(self.id_operation) +"""
                  and NJRN = """+ str(self.number_oper) +"""
                  and tra_id is not null))
                  and d.dep_id = ag1.dep_id and d.acc_id = ag1.id
                  and ag1.id = gg.id and ag1.dep_id = gg.dep_id
                  and '""" + str(to_date) + """' between gg.fromdate and gg.todate
                  and gg.cha_id = ll.id) d
                  union all
                  select * from
                  (select ll.code, l.code as acc,
                  (select CODE from T_VAL_STD where ID = d.VAL_ID) as VAL_CODE, d.*,
                  GL_Anl.fAccAnlValue(l.DEP_ID, l.ID, 'DEPARTMENT') as dep
                    from t_trndtl d, g_accbln l, g_accblnhst gg, ledacc ll
                    where d.id = """+ str(self.tra_id) +"""
                   and d.dep_id = l.dep_id and d.acc_id = l.id
                   and l.id = gg.id and l.dep_id = gg.dep_id
                   and '""" + str(to_date) + """' between gg.fromdate and gg.todate
                   and gg.cha_id = ll.id) q """
        result = self.OracleHandlerDB(select)
        account_list = []
        full_info_list = []
        if result:
          for line in result:
            account_list.append(line[0])
            full_info_list.append(line)
            if str(line[5]) == '0':
              Log.Checkpoint("Кредит "+str(line[0])+" "+line[1]+" "+str(line[11])+" "+line[2])
            else:
              Log.Checkpoint("Дебет "+str(line[0])+" "+line[1]+" "+str(line[11])+" "+line[2])
        if self.full_info:
          return full_info_list
        Log.Message('Сформированые счета ' + str(account_list) + ' в результате выполнение операции')
        return account_list

    def ValRateTransation(self, id_operation, number_oper, sum_pay, sum_pay_rate):
        """ Получение фин проводок из журнала операций по проведенной операции через запрос в БД.
        Вывод сразу в лог по каждой транзакции, также возвращает список масок счетов по всем транзакциям.
        Сверка конвертации.
        Данные передаваемые из гридов не нужно очищать от кавычек.
        sum_pay сумма до конвертации.
        sum_pay_rate сумма после конвертации.
        """
        self.id_operation = id_operation
        self.number_oper = number_oper
        self.sum_pay = sum_pay
        self.sum_pay_rate = sum_pay_rate
        # фикс обратной
        if not self.id_operation and not self.number_oper:
          self.id_operation = "''"
          self.number_oper = "''"
        date_statusbar = self.OperDayValue() # Берется значение даты опердня
        to_date = aqConvert.DateTimeToFormatStr(date_statusbar, "%d.%m.%Y")
        select = """ select * from (select ll.code as PS, ag1.CODE as acc,
                    (select CODE from T_VAL_STD where ID = d.VAL_ID) as VAL_CODE, d.*,
                     GL_Anl.fAccAnlValue(ag1.DEP_ID, ag1.ID, 'DEPARTMENT') as dep
                     from t_trndtl d, g_accbln ag1, g_accblnhst gg, ledacc ll
                     where d.id in (select tra_id from t_operjrn
                     where id in (select child_id from t_procinh
                     where parent_ID = """+ str(self.id_operation) +"""
                     and NJRN = """+ str(self.number_oper) +"""
                     and tra_id is not null))
                     and d.dep_id = ag1.dep_id and d.acc_id = ag1.id
                     and ag1.id = gg.id and ag1.dep_id = gg.dep_id
                     and '""" + str(to_date) + """' between gg.fromdate and gg.todate
                     and gg.cha_id = ll.id) d
                     union all
                     select * from
                    (select ll.code, l.code as acc,
                    (select CODE from T_VAL_STD where ID = d.VAL_ID) as VAL_CODE, d.*,
                     GL_Anl.fAccAnlValue(l.DEP_ID, l.ID, 'DEPARTMENT') as dep
                     from t_trndtl d, g_accbln l, g_accblnhst gg, ledacc ll
                     where d.id = ''
                     and d.dep_id = l.dep_id and d.acc_id = l.id
                     and l.id = gg.id and l.dep_id = gg.dep_id
                     and '""" + str(to_date) + """' between gg.fromdate and gg.todate
                     and gg.cha_id = ll.id) q """

        result = self.OracleHandlerDB(select)
        full_info_list = []
        if result:
          for line in result:
            full_info_list.append(line)
            if str(line[5]) == '0':
              Log.Checkpoint("Кредит "+str(line[0])+" "+line[1]+" "+str(line[11])+" "+line[2])
            else:
              Log.Checkpoint("Дебет "+str(line[0])+" "+line[1]+" "+str(line[11])+" "+line[2])

    def DBGetSanctionInfo(self, wndname):
        """ Запрос к БД из окна 'Исполнители' на получение списка санкций по проведенной операции """
        self.wndname = wndname
        need_window = Sys.Process("COLVIR").VCLObject(self.wndname)
        need_window.Keys("!^~l")  #shift+ctrl+alt+l открываем секретное окно
        query_form = Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").ListItem("Все запросы формы")
        query_form.DblClick()
        self.WaitLoadWindow('frmQrysFormList')
        grid_sql = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel2").VCLObject("reSQL").wText
        grid_sql = re.sub(r'--.*\n',' ', grid_sql) #чистим от однострочных комментов
        #режем на 3 части
        bd_query = grid_sql[:grid_sql.find('Query')] # Часть с запросом к БД
        bd_query = bd_query.replace('order by 1, 2', 'order by MAGIC desc') #заменяем сортировку
        queryparams = grid_sql[grid_sql.find('Query'):grid_sql.find('Fields')] #Часть с параметрами
        #убираем первые 2 строки и сразу заменяем пробелы
        queryparams = queryparams[queryparams.find(':')+2:].replace(' ', '')
        listtemp = queryparams.splitlines() #помещаем строки в список
        #бьем строки по "=" и помещаем каждую в список параметров
        listparams = [v.split('=', 1) for v in listtemp]
        for i in listparams:
          if i != ['']: #отбрасываем пустые списки
            v = ':' + i[0] #берем имя переменной с двоеточием
            bd_query = bd_query.replace(v, i[1]) #заменяем имя на значение
        Sys.Process("COLVIR").VCLObject("frmQrysFormList").Close()
        Sys.Process("COLVIR").VCLObject("frmQueryDlg").Close()
        result = self.OracleHandlerDB(bd_query)
        result_dict = {}
        for line in result:
          result_dict[line[2]] = line[4]
        return result_dict
    
    def DBGetSanctionInfoSsafeord(self, wndname):
        """ Запрос к БД из окна 'Исполнители' на получение списка санкций по проведенной операции """
        self.wndname = wndname
        need_window = Sys.Process("COLVIR").VCLObject(self.wndname)
        need_window.Keys("!^~l")  #shift+ctrl+alt+l открываем секретное окно
        query_form = Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").TextObject("Все запросы формы")
        query_form.DblClick()
        self.WaitLoadWindow('frmQrysFormList')
        grid_sql = Sys.Process("COLVIR").VCLObject("frmQrysFormList").VCLObject("Panel2").VCLObject("reSQL").wText
        grid_sql = re.sub(r'--.*\n',' ', grid_sql) #чистим от однострочных комментов
        #режем на 3 части
        bd_query = grid_sql[:grid_sql.find('Query')] # Часть с запросом к БД
        bd_query = bd_query.replace('order by 1, 2', 'order by MAGIC desc') #заменяем сортировку
        queryparams = grid_sql[grid_sql.find('Query'):grid_sql.find('Fields')] #Часть с параметрами
        #убираем первые 2 строки и сразу заменяем пробелы
        queryparams = queryparams[queryparams.find(':')+2:].replace(' ', '')
        listtemp = queryparams.splitlines() #помещаем строки в список
        #бьем строки по "=" и помещаем каждую в список параметров
        listparams = [v.split('=', 1) for v in listtemp]
        for i in listparams:
          if i != ['']: #отбрасываем пустые списки
            v = ':' + i[0] #берем имя переменной с двоеточием
            bd_query = bd_query.replace(v, i[1]) #заменяем имя на значение
        Sys.Process("COLVIR").VCLObject("frmQrysFormList").Close()
        Sys.Process("COLVIR").VCLObject("frmQueryDlg").Close()
        result = self.OracleHandlerDB(bd_query)
        result_dict = {}
        for line in result:
          result_dict[line[2]] = line[4]
        return result_dict

    def GetNeedSanctionLines(self, ord_id, dep_id):
        """ Получение несанкционированных операций в журнале операций по порядку,
        с помощью ord_id и dep_id из журнала операций через запрос к БД
        """
        self.ord_id = ord_id.replace("\'", '').strip()
        self.dep_id = dep_id.replace("\'", '').strip()
        select = """
                 select nvl(t.refer,'0') as REFER
                 from (select """ + self.ord_id + """ ord_id, """ + self.dep_id + """ dep_id from dual)d
                 left join t_operjrn t
                 on t.ord_id = d.ord_id
                 and t.dep_id = d.dep_id
                 and t.rat_id is not null
                 order by t.njrn asc
                 """
        result = self.OracleHandlerDB(select)
        return result

    def GetNumberKassNumberDep(self, login):
        """Получение номер кассы и номер депортамента кассира из таблицы LoginPoll"""
        self.login = login
        select = """
                 select c.dep_number, c.kassa_number from LoginPool c
                 WHERE c.test_login = '"""+self.login+"""'
                       and rownum = 1
                 """
        result = self.OracleHandlerDB(select)
        return result

    def GetNeedNunberKass(self, tus_code):
        """Получение подразделения кассы"""
        self.tus_code = tus_code
        select = """
                 select c.dep_code from CV_USR2 c
                 WHERE c.code = """+self.tus_code+"""
                 """
        result = self.OracleHandlerDB(select)
        return result

    def CheckSummPM(self):
        """Проверка ПМ в БД"""
        select = """
                 select a.value from Q_LIM_RATE a
                 where RATETYPE = 'COL' 
                 """
        result = self.OracleHandlerDB(select)
        return result

    def CheckSummPMPS(self):
        """Проверка ПМ ПС в БД"""
        select = """
                 select value from  APR_CFG_VAL  @cap b, APR_CFG  @cap a
                 where a.ID = b.ID_CFG
                   and a.PARAM = 'LV_SUM' 
                 """
        result = self.OracleHandlerDB(select)
        return result

    def ExPM(self):
        """Запрос ПМ из своей таблицы"""
        select = """
                 select PM from PM
                 """
        result = self.OracleHandlerDB(select)
        PM = result[0][0]
        return PM

    def GetRateExchange(self,val_code):
        """Запрос курса валют на дату установленую в системной переменной"""
        date_operday = self.GetEnviron("DATE_OPERDAY")
        self.val_code = val_code
        select = """
                 select kr.VAL_CODE from TV_VALRAT kr
                 where kr.VAL_CODE = '"""+self.val_code+"""'
                   and kr.VRA_NAME = 'Учетный курс BCC'
                   and kr.FROMDATE ='"""+date_operday+"""' 
                """
        result = self.OracleHandlerDB(select)
        return result

    def PMAccountCheck(self, payer_acc):
        """ Получение количества использованного ПМ по счету карточки клиента """
        self.payer_acc = payer_acc
        select = """ 
                 select ab.amount from APT_CHKBAL @cap  ab, APT_IDN @cap ai 
                 where ab.id = ai.acc_id 
                   and ai.code = '"""+self.payer_acc+"""'
                 """
        result_balance_PM = self.OracleHandlerDB(select)
        if result_balance_PM != None:
          result = result_balance_PM[0][0]
        elif result_balance_PM == None:
          result = 0
        return result

    def GetIdAcc(self, payer_acc):
        """Получение ID счета"""
        self.payer_acc = payer_acc
        select = """
                 select c.id from G_ACCBLN c  
                 where c.code = '"""+self.payer_acc+"""'
                 """
        result =  self.OracleHandlerDB(select)
        move_result = result[0][0]
        return move_result

    def CheckMoveACCBal(self, payer_account, acc_recipient):
        """Движение по счету"""
        date_operday = self.GetEnviron("DATE_OPERDAY")
        self.payer_account = payer_account
        self.acc_recipient = acc_recipient
        select = """
                 select *  from 
                           (select g.sdok FROM P_ORD g
                             where g.dval =  '"""+date_operday+"""' 
                               and g.code_acl = '"""+self.payer_account+"""' 
                               and g.code_acr = '"""+self.acc_recipient+"""'
                               ORDER BY EXT_ID desc) 
                           where rownum = 1
                 """
        result = self.OracleHandlerDB(select)
        if result != None:
          move_result = result[0][0]
        elif result == None:
          move_result = 0
        return move_result

    def CheckUndoPay(self, sanction_pay):
        """Проверка отмены платежа"""
        date_operday = self.GetEnviron("DATE_OPERDAY")
        self.sanction_pay = sanction_pay
        if self.sanction_pay != None:
          tuple_ref = tuple(map(str, re.findall(r'[A-Z]+'+'[0-9]+', self.sanction_pay)))
          for item in tuple_ref:
            select = """ 
                 select undofl from T_OPERJRN 
                 where doper = '"""+date_operday+"""'
                 and refer = '"""+item+"""'
                 and undofl = '1'
                 and cancelfl = '0'
                 """
            result_pay = self.OracleHandlerDB(select)
            result = result_pay[0][0]
        else:
          Log.Message('Референс отсутствует в таблице')
          result = '10'
        return result

    def CheckMoveACC(self, sum_muve, payer_account, acc_recipient):
        """Проверка движения по счету по сумме"""
        date_operday = self.GetEnviron("DATE_OPERDAY")
        self.sum_muve = sum_muve
        self.payer_account = payer_account
        self.acc_recipient = acc_recipient
        select = """
                 select g.sdok  from P_ORD g 
                 where g.dval = '"""+date_operday+"""' 
                   and g.sdok ='"""+self.sum_muve+"""'
                   and g.code_acl = '"""+self.payer_account+"""' 
                   and g.code_acr = '"""+self.acc_recipient+"""'
                 """
        result = self.OracleHandlerDB(select)
        return result

    def SaveDocNamberColdeal(self,contract_number,client_code):
        """Сохранение номера договора инкассации для работы с инкассацией"""
        self.contract_number = contract_number
        self.client_code = client_code
        select = """
                 begin update Clients_Collection al
                 set al.doc_number_cont= '"""+self.contract_number+"""'  
                 WHERE al.client_code='"""+self.client_code+"""';
                 commit;end;
                 """
        result = self.OracleHandlerDB(select, dml_query=True)

    def SaveOTPPassword(self, set_otp, otp_id, otp_nord, name_otp):
        """Отключение проверки ОТР пароля"""
        self.set_otp = set_otp
        self.otp_id = otp_id
        self.otp_nord = otp_nord
        self.name_otp = name_otp
        self.OracleHandlerDB('alter trigger T_SCEN_BLK_STD_MODIFY disable',dml_query='True')
        select = """
                 begin
                 UPDATE T_SCEN_BLK
                 set exec_cond = '"""+self.set_otp+"""' 
                 where id = '"""+self.otp_id+"""' and nord = '"""+self.otp_nord+"""' and name = '"""+self.name_otp+"""';
                 commit;
                 end;
                 """
        result = self.OracleHandlerDB(select, dml_query=True)
        self.OracleHandlerDB('alter trigger T_SCEN_BLK_STD_MODIFY enable',dml_query='True')

    def BalanceACC(self,val_code ,acc_num):
        """Проверка остатка по счету"""
        self.val_code = val_code
        self.acc_num = acc_num
        select = """
                 select l.code as MASK,a.code as ACC_NUM,
           abs(t_pkgaccbal.faccbal(a.dep_id, a.id, trunc(sysdate),0,ag.val_id,0,0)) as COLVIR_BAL,
           abs(T_PkgAccBal.fFulNatVal(a.dep_id,a.id,trunc(sysdate),0,ag.VAL_ID,0,0)) as EQUAL_BAL,
           (SELECT case P_CUSTCODE
              when '026' then
              substr(TO_MONEY(G_PKGCAP.fBAL(A1.DEP_ID,A1.ID,P_OPERDAY,T_VAL.ID) -
              G_PKGCAP.fBAL(A1.DEP_ID, A1.ID,trunc(sysdate),T_VAL.ID,1,null,null,1),0,MULTIPLIER + 2),1,27)
              else substr(TO_MONEY(G_PKGCAP.fBAL(A1.DEP_ID,A1.ID,trunc(sysdate),T_VAL.ID),0,MULTIPLIER + 2),1,27)
              end
              from T_VAL, T_ACC AA, G_ACCBLN A1
              where T_VAL.ID = nvl(AA.VAL_ID, P_NATVAL)
              and A.ID = AA.ID and A.DEP_ID = AA.DEP_ID
               and A1.code = a.code) PS_BAL,
           tg.code as GROUP_ACC, gg.code, nvl(gl_anl.faccanlvalue(a.dep_id, a.id, 'VALUTA'),'"""+self.val_code+"""') as VAL_CODE,
           substr(l.code, 1, 4) as ACODE, a.id, a.dep_id, Z_PKG_AUTO_TEST.f_get_dcl_code(a.code) as product_code
           from g_clihst g, g_cli gg, g_accbln a, g_accblnhst ag, ledacc l, t_accgrp tg
           where g.id = gg.id
           and g.dep_id = gg.dep_id and trunc(sysdate) between g.fromdate and g.todate
           and g.id = ag.cli_id and g.dep_id = ag.clidep_id and trunc(sysdate) between ag.fromdate and ag.todate
           and a.id = ag.id and a.dep_id = ag.dep_id and a.cha_id = l.id and tg.dep_id = ag.dep_id
           and tg.id = ag.aut_id and a.code = '"""+self.acc_num+"""'
                 """
        result = self.OracleHandlerDB(select)
        balance_acc = result[0][2]
        return balance_acc

    def CheckPMClient(self, id_payer):
        """Проверка холдов по клиенту"""
        self.id_payer = id_payer
        select = """
                 select o.balance from APT_BAL @cap o , APR_BALTYPE @cap t 
                 where o.baltype_id = t.id and 
                 o.baltype_id = '1' and
                 o.id =  '"""+self.id_payer+"""'
                 """
        result = self.OracleHandlerDB(select)
        return result

    def GetTypeSanction(self):
        """ Получение списка логинов из окна 'Исполнители' для получения
        порядка санкционирования записи в журнале операций
        """
        list_sanction = ''
        if Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnExecutors").Enabled:
          user_exec = Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnExecutors")
          user_exec.Click()
          self.WaitLoadWindow("frmExecutors")
          dict_res = self.DBGetSanctionInfo("frmExecutors")
          for key, value in dict_res.items():
            if value is None:
              Log.Checkpoint(key)
              list_sanction = list_sanction + key[16:] + ';'
          Sys.Process("COLVIR").VCLObject("frmExecutors").Close()
        else:
          Log.Warning('Кнопка для перехода к окну "Исполнители" недоступна')
        return list_sanction
    
    def GetTypeSanctionSsafeord(self):
        """ Получение списка логинов из окна 'Исполнители' для получения
        порядка санкционирования записи в журнале операций
        """
        list_sanction = ''
        if Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnExecutors").Enabled:
          user_exec = Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnExecutors")
          user_exec.Click()
          self.WaitLoadWindow("frmExecutors")
          dict_res = self.DBGetSanctionInfoSsafeord("frmExecutors")
          for key, value in dict_res.items():
            if value is None:
              Log.Checkpoint(key)
              list_sanction = list_sanction + key[16:] + ';'
          Sys.Process("COLVIR").VCLObject("frmExecutors").Close()
        else:
          Log.Warning('Кнопка для перехода к окну "Исполнители" недоступна')
        return list_sanction

    def ConfirmOperation(self, check_message, time_await=2000, log_warning=None):
        """ Проверка выбранного пункта меню по окну 'Подтверждение'.
        Возвращает False если выбран не верный пункт меню или окно 'Подтверждение' не появилось
        """
        self.check_message = check_message
        self.time_await = time_await
        self.log_warning = log_warning
        state = False
        if Sys.Process("COLVIR").WaitWindow("TMessageForm", "Подтверждение", -1, self.time_await).Exists:
          confirm_caption = Sys.Process("COLVIR").Dialog("Подтверждение").VCLObject("Message").Caption
          if self.check_message in confirm_caption:
            yes_confirm= Sys.Process("COLVIR").Dialog("Подтверждение").VCLObject("Yes")
            yes_confirm.Click()
            Delay(500)
            state = True
          else:
            Log.Error("Ожидался текст пункта меню "+ str(check_message) +" ,а получен "+ str(confirm_caption))
        elif self.log_warning is not None:
          Log.Warning("Окно 'Подтверждение' с текстом "+ self.check_message +" не появилось")
        else:
          Log.Event("Окно 'Подтверждение' с текстом "+ self.check_message +" не появилось")
        return state

    def ClickNeedButConfirmWindow(self, need_button, time_await=5000):
        """ Нажатие необходимой кнопки в окне 'Подтверждение'
        Возвращает False если окно 'Подтверждение' не появилось
        """
        self.need_button = need_button
        self.time_await = time_await
        if Sys.Process("COLVIR").WaitWindow("TMessageForm", "Подтверждение", -1, self.time_await).Exists:
          click_need_button = Sys.Process("COLVIR").Dialog("Подтверждение").VCLObject(self.need_button)
          click_need_button.Click()
          Delay(500)
          state = True
        else:
          Log.Event("Окно 'Подтверждение' не появилось")
          state = False
        return state

    def InputTemplateValue(self, wndname, template_value):
        """ Нажатие кнопки создания документа и ввод необходимого шаблона """
        self.wndname = wndname
        self.template_value = template_value
        create_button = Sys.Process("COLVIR").VCLObject(self.wndname).VCLObject("btnInsert")
        if create_button.Enabled:
          create_button.Click()
          self.WaitLoadWindow("frmVarDtlDialog")
          template_window = Sys.Process("COLVIR").VCLObject("frmVarDtlDialog")
          num_field = template_window.VCLObject("edtKeyValue")
          num_field.Keys(self.template_value)
          ok_template = template_window.VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK")
          ok_template.Click()
        else:
          Log.Error("Кнопка создания документа недоступна")

    def InputEmptyFilter(self):
        """ Очистка и выбор пустого фильтра (для создания документов) """
        self.WaitLoadWindow("frmFilterParams")
        filter_window = Sys.Process("COLVIR").VCLObject("frmFilterParams")
        clean_filter = filter_window.VCLObject("btnClearFilter")
        clean_filter.Click()
        empty_filter = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('btnInsert')", 5, True, 100)
        if empty_filter.Exists and empty_filter.Visible:
          empty_filter.Click()
          return True
        else:
          Log.Event("У фильтра отсутствует кнопка 'Пустой'")
          return False

    def AdmUsr(self, test_login):
        """Установка признака админа пользователю"""
        self.test_login = test_login
        clear_btn = Sys.Process("COLVIR").VCLObject("frmFilterParams").VCLObject("btnClearFilter")
        clear_btn.Click()
        Delay(500)
        usr_login = Sys.Process("COLVIR").VCLObject("frmFilterParams").VCLObject("pnlClient").VCLObject("CODE")
        usr_login.Keys(self.test_login)
        Delay(500)
        Sys.Process("COLVIR").VCLObject("frmFilterParams").VCLObject("sbDown").Click()
        Delay(500)
        Sys.Process("COLVIR").VCLObject("frmFilterParams").VCLObject("pnlClient").VCLObject("ARCFL").DblClick()
        Delay(500)
        Sys.Process("COLVIR").VCLObject("frmFilterParams").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK").Click()

    def SetFilterCommis(self, **fields):
        """ Ввод данных в фильтр (необходимые поля передаются как Name=значение без кавычек)
        Очистка фильтра перед вводом и кнопка ОК после жмутся для всех по-умолчанию
        Для ключа btnOther, нажимается кнопка 'Еще', данный ключ может идти с пустым параметром
        Для ключа SET_RAT, проставляется галочка санкционирования (1 - санкционирование, 0 - отмена санкционирования)
        На вход может быть подан и словарь, он будет обработан как обычные Поле=значение
        Для работы с чекбоксами передавать Поле='ClickX' - где Х - это статус чекбокса
        (1 отмечен, 0 не отмечен, 2 не учтен - выглядит как квадрат)
        """
        self.fields = fields
        self.WaitLoadWindow("frmFilterParams")
        clear_btn = self.FindChildField("frmFilterParams", "Name", "VCLObject('btnClearFilter')")
        clear_btn.Click()
        get_task = self.FindChildField("AppLayer", "Name", "VCLObject('MainPanel')", "internal")
        dep_required = self.GetFilterFields(get_task.Text)
        dep_field_short = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('DEP')", 5, True, 100)
        dep_field = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('DEP_CODE')", 5, True, 100)
        if dep_field_short.Exists and dep_required:
          dep_field_short.Keys('CNT')
        if dep_field.Exists and dep_required:
          dep_field.Keys('CNT')
        for key, value in self.fields.items():
          if str(value).startswith('Click'):
            checkbox_btn = self.FindChildField("frmFilterParams", "Name", "VCLObject('"+ key +"')")
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
            dep_field = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('"+ key +"')", 5, True, 100)
            if dep_field.Exists:
              dep_field.Keys(value)
          elif isinstance(value, dict):
            for keys, vals in value.items():
              need_dict_field = self.FindChildField("frmFilterParams", "Name", "VCLObject('"+ keys +"')")
              need_dict_field.Keys(vals)
          else:
            need_field = self.FindChildField("frmFilterParams", "Name", "VCLObject('"+ key +"')")
            need_field.Keys(value)
        ok_button = self.FindChildField("frmFilterParams", "Name", "VCLObject('btnOK')")
        ok_button.Click()

    def SetFilterKass(self, **fields):
        """ Ввод данных в фильтр (необходимые поля передаются как Name=значение без кавычек)
        Очистка фильтра перед вводом и кнопка ОК после жмутся для всех по-умолчанию
        Для ключа btnOther, нажимается кнопка 'Еще', данный ключ может идти с пустым параметром
        Для ключа SET_RAT, проставляется галочка санкционирования (1 - санкционирование, 0 - отмена санкционирования)
        На вход может быть подан и словарь, он будет обработан как обычные Поле=значение
        Для работы с чекбоксами передавать Поле='ClickX' - где Х - это статус чекбокса
        (1 отмечен, 0 не отмечен, 2 не учтен - выглядит как квадрат)
        """
        self.fields = fields
        self.WaitLoadWindow("frmFilterParams")
        clear_btn = self.FindChildField("frmFilterParams", "Name", "VCLObject('btnClearFilter')")
        clear_btn.Click()
        get_task = self.FindChildField("AppLayer", "Name", "VCLObject('MainPanel')", "internal")
        dep_required = self.GetFilterFields(get_task.Text)
        dep_field_short = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('DEP')", 5, True, 100)
        dep_field = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('DEP_CODE')", 5, True, 100)
        if dep_field_short.Exists and dep_required:
          dep_field_short.Keys('CNT')
        if dep_field.Exists and dep_required:
          dep_field.Keys('CNT')
        for key, value in self.fields.items():
          if str(value).startswith('Click'):
            checkbox_btn = self.FindChildField("frmFilterParams", "Name", "VCLObject('"+ key +"')")
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
            dep_field = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('"+ key +"')", 5, True, 100)
            if dep_field.Exists:
              dep_field.Keys(value)
          elif isinstance(value, dict):
            for keys, vals in value.items():
              need_dict_field = self.FindChildField("frmFilterParams", "Name", "VCLObject('"+ keys +"')")
              need_dict_field.Keys(vals)
          else:
            need_field = self.FindChildField("frmFilterParams", "Name", "VCLObject('"+ key +"')")
            need_field.Keys(value)
        ok_button = self.FindChildField("frmFilterParams", "Name", "VCLObject('btnOK')")
        ok_button.Click()

    def SetFilter(self, **fields):
        """Ввод данных в фильтр (необходимые поля передаются как Name=значение без кавычек)
        Очистка фильтра перед вводом и кнопка ОК после жмутся для всех по-умолчанию
        Для ключа btnOther, нажимается кнопка 'Еще', данный ключ может идти с пустым параметром
        Для ключа SET_RAT, проставляется галочка санкционирования (1 - санкционирование, 0 - отмена санкционирования)
        На вход может быть подан и словарь, он будет обработан как обычные Поле=значение
        Для работы с чекбоксами передавать Поле='ClickX' - где Х - это статус чекбокса
        (1 отмечен, 0 не отмечен, 2 не учтен - выглядит как квадрат)
        """
        self.fields = fields
        self.WaitLoadWindow("frmFilterParams")
        clear_btn = self.FindChildField("frmFilterParams", "Name", "VCLObject('btnClearFilter')")
        clear_btn.Click()
        get_task = self.FindChildField("AppLayer", "Name", "VCLObject('MainPanel')", "internal")
        dep_required = self.GetFilterFields(get_task.Text)
        if Sys.Process("COLVIR").VCLObject("frmFilterParams").VCLObject("pnlButtons").VCLObject("pnlRight").WaitVCLObject("btnOther", 6000).Enabled:
            Sys.Process("COLVIR").VCLObject("frmFilterParams").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOther").Click()
        dep_field_short = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('DEP')", 5, True, 100)
        dep_field = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('DEP_CODE')", 5, True, 100)
        for key, value in self.fields.items():
          if str(value).startswith('Click'):
            checkbox_btn = self.FindChildField("frmFilterParams", "Name", "VCLObject('"+ key +"')")
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
            dep_field = Sys.Process("COLVIR").VCLObject("frmFilterParams").FindChildEx("Name", "VCLObject('"+ key +"')", 5, True, 100)
            if dep_field.Exists:
              dep_field.Keys(value)
          elif isinstance(value, dict):
            for keys, vals in value.items():
              need_dict_field = self.FindChildField("frmFilterParams", "Name", "VCLObject('"+ keys +"')")
              need_dict_field.Keys(vals)
          else:
            need_field = self.FindChildField("frmFilterParams", "Name", "VCLObject('"+ key +"')")
            need_field.Keys(value)
        Delay(3000)
        ok_button = self.FindChildField("frmFilterParams", "Name", "VCLObject('btnOK')")
        ok_button.Click()

    def GetFilterFields(self, name_task):
        """ Получение обязательных полей фильтра по названию задачи """
        self.name_task = name_task
        list_task = ('RECALC','SCASHVIEW','MEXCRAT','GETCOMMIS','SORDCASH','SORDPAY','MPAYCHK',
                      'OPERJRNRAT','CLIEXCREQ','REQPAY','FRCVPAY','FSNDPAY','MPAYINCHK', 'SPAYVIEW')
        if self.name_task in list_task:
          check_dep_field = True
        else:
          check_dep_field = False
        return check_dep_field

    def CheckOperEndWindow(self):
        """Закрытие мерзкого окна 'операция выполнена' c дополнительной тех. задержкой
        (сделано в цикле из-за лагов окна приложения при долгом выполнении операции,
         что приводило к ошибке поиска необходимого окна)
        """
        for _ in range(12):
            if Sys.Process("COLVIR").WaitWindow("TMessageForm", "Colvir Banking System", -1, 1800).Exists:
              find_window = Sys.Process("COLVIR").WaitDialog("Colvir Banking System", 60000)
              if find_window.Exists:
                  find_window.Close()
            Delay(500) # тех задержка перед следующей операцией
            return True
        Log.Message("Лишняя проверка мерзкого окна либо произошла непредвиденная ошибка и необходимое окно зависло","", pmNormal,"null",Sys.Desktop)
        return False

    def ListItemOper(self):
        """Работа с окном главного меню"""
        central_menu = Sys.Process("COLVIR").Popup("Контекст")
        text_items = []
        for i in range (0, central_menu.ChildCount):
            wndChild = central_menu.Child(i)
            item = wndChild.Name
            if "MenuItem" in str(item) or "Separator" in str(item):
              continue
            elif "TextObject" in str(item):
              text_items.append(str(item)[11:-1])
        return text_items

    def FindNeedOperation(self, operation_name, window=None, oper_btn=None):
        """Поиск и нажатие на необходимую операцию в цикле после нажатия на кнопку 'Операции'
        или необходимый пункт меню, с помощью статусбара (название выделенной операции берет из статусбара
        в нижнем левом окне). При недоступности операции или ее отсутствии в списке меню сделает скриншот и
        выведет Warning в лог (скрин корректно снимается только для меню из кнопки 'Операции')
        """
        items_oper = Sys.Process("COLVIR").Popup("Контекст")
        text_items = []
        for i in range (0, items_oper.ChildCount):
          wndChild = items_oper.Child(i)
          item = wndChild.Name
          if "MenuItem" in str(item) or "Separator" in str(item):
            continue
          elif "TextObject" in str(item):
            text_items.append(str(item)[12:-2])
        self.operation_name = operation_name
        self.window = window
        self.oper_btn = oper_btn
        menu_items_count, menu_items_list = self.GetMenuItemsCount(self.window, self.oper_btn)
        text_items_reverse = text_items[::-1]
        for i in range(len(text_items)):
          LLPlayer.KeyDown(VK_DOWN, 3) # нажатие стрелки вниз
          LLPlayer.KeyUp(VK_DOWN, 3)
          finder = items_oper.TextObject(text_items_reverse[i]).Text
          if finder == self.operation_name and menu_items_list.MenuItem(i).Enabled:
            LLPlayer.KeyDown(VK_RETURN, 3) # нажатие Enter если нашли нужную операцию и она доступна
            LLPlayer.KeyUp(VK_RETURN, 3)
            return True
          elif finder == self.operation_name and not menu_items_list.MenuItem(i).Enabled:
            Log.Warning("Операция '"+ self.operation_name +"' недоступна","",pmNormal,"null",Sys.Desktop.ActiveWindow())
            return False

    def CheckOperNotInList(self, operation_name, window=None, oper_btn=None):
        """Проверка что операций нет в писке после нажатия на кнопку 'Операции'
        или необходимый пункт меню, с помощью статусбара (название выделенной операции берет из статусбара
        в нижнем левом окне). Недоступность операции в списке расценивается как положительный результат проверки
        (скрин корректно снимается только для меню из кнопки 'Операции')
         """
        self.operation_name = operation_name
        self.window = window
        self.oper_btn = oper_btn
        state = False
        menu_items_count, menu_items_list = self.GetMenuItemsCount(self.window, self.oper_btn)
        status_bar = Sys.Process("COLVIR").VCLObject("frmCssMenu").VCLObject("StatusBar")
        for i in range(menu_items_count):
          LLPlayer.KeyDown(VK_DOWN, 3) # нажатие стрелки вниз
          LLPlayer.KeyUp(VK_DOWN, 3)
          finder = status_bar.wText[0]
          if finder == self.operation_name and menu_items_list.MenuItem(i).Enabled:
            Log.Warning("Операция '"+ self.operation_name +"' доступна и активна","",pmNormal,"null",Sys.Desktop.ActiveWindow())
            break
          elif finder == self.operation_name and not menu_items_list.MenuItem(i).Enabled:
            Log.Checkpoint("Операция '"+ self.operation_name +"' недоступна","",pmNormal,"null",Sys.Desktop.ActiveWindow())
            state = True
            break
        else:
          Log.Checkpoint("Операция '"+ self.operation_name +"' отсутствует в списке операций","", pmNormal,"null",Sys.Desktop.ActiveWindow())
          state = True
        self.LLPKeys(VK_ESCAPE)
        return state

    def GetMenuItemsCount(self, window, oper_btn, recurcive=True):
        """Подсчет пунктов меню исключая разделители,
        дополнительно возвращает сам объект списка, чтобы не искать повторно """
        self.window = window
        self.oper_btn = oper_btn
        self.recurcive = recurcive
        if self.window is not None and self.oper_btn is not None:
          oper_button = self.FindChildField(self.window, "Name", 'VCLObject("'+self.oper_btn+'")')
          oper_button.Click()
          Delay(1500)
        need_object = self.FindWindowColvir('', None, name_property="WndClass", value_property="#32768")
        real_menu_items = []
        if need_object is not None:
          for childs in range(need_object.ChildCount):
            if not need_object.Child(childs).Name.startswith('Separator'):
              real_menu_items.append(need_object.Child(childs))
          return len(real_menu_items), need_object
        elif need_object is None and (self.window is not None and self.oper_btn is not None and self.recurcive):
          self.GetMenuItemsCount(self.window, self.oper_btn, recurcive=False)
        else:
          return 0, need_object

    def DocNumGenValidator(self, field_name, need_field):
        """Проверка генератора номера документа (проверка автозаполнения и возможность изменения)"""
        self.need_field = need_field
        self.field_name = field_name
        get_num_field = self.need_field.Value
        if re.findall('(\d+)', get_num_field):  # ищем есть ли цифры в поле
          Log.Event("Сгенерированный номер документа: " + get_num_field)
          changed_number = self.DocNumberGenerator() + get_num_field[3:]
          self.need_field.Keys("[Home]")   #переносим каретку в начало строки
          self.need_field.Keys(changed_number)
          get_changed_number = self.need_field.Value
          if get_num_field == get_changed_number:
            Log.Warning("Не удалось изменить номер документа")
          else:
            Log.Event("Измененный номер документа: " + get_changed_number)
        else:
          Log.Event("Значение поля '" + self.field_name + "' пусто (будет заполнено автоматически)")
          self.need_field.Keys("[Home]")
          self.need_field.Keys('999999')

    def DocNumberGenerator(self, big_value=None, start_value=None, end_value=None):
        """Простая генерация номера документа"""
        self.big_value = big_value
        self.start_value = start_value
        self.end_value = end_value
        if self.start_value is not None and self.end_value is not None:
            return str(randint(self.start_value, self.end_value))
        elif self.big_value is not None:
            return str(randint(100000000, 999999999))
        else:
            return str(randint(100, 999))

    def GetMadvpayCashboxBal(self, bal_after_oper=None):
        """Получение баланса ценностей в кассе из других задач, до или после исполнения операций"""
        self.bal_after_oper = bal_after_oper
        self.TaskInput('MADVPAY')
        self.InputEmptyFilter()
        self.WaitLoadWindow("AdvancePaymentList", time_await=20000)
        get_bal_value = None
        if self.bal_after_oper is None:
          get_bal_value = self.ShowBalanceBefore()
        else:
          get_bal_value = self.ShowBalanceAfter(self.bal_after_oper)
        Sys.Process("COLVIR").VCLObject("AdvancePaymentList").Close()
        return get_bal_value

    def ShowBalanceBefore(self):
        """Получение и вывод в лог данных по ценностям в кассе до проведения операций"""
        balance_but = Sys.Process("COLVIR").VCLObject("AdvancePaymentList").VCLObject("btnRestMon")
        balance_but.Click()
        self.WaitLoadWindow("frmCshMonFrm", time_await=20000)
        balance_params = self.GetGridQueryParams("frmCshMonFrm", "CSH_ID", "TUS_ID")
        date_statusbar = self.GetEnviron("DATE_OPERDAY")
        bal_value_before = self.GetValueBalans(balance_params[0], balance_params[1], date_statusbar)
        for key, value in bal_value_before.items():
          if value:
            Log.Event(key + " баланс:" + value)
        Sys.Process("COLVIR").VCLObject("frmCshMonFrm").Close()
        return bal_value_before

    def ShowBalanceAfter(self, balance_val_before):
        """ Сравнение и вывод в лог валюты, которая изменилась после проведения операций"""
        self.balance_val_before = balance_val_before
        balance_but = Sys.Process("COLVIR").VCLObject("AdvancePaymentList").VCLObject("btnRestMon")
        balance_but.Click()
        self.WaitLoadWindow("frmCshMonFrm")
        balance_params = self.GetGridQueryParams("frmCshMonFrm", "CSH_ID", "TUS_ID")
        date_statusbar = self.GetEnviron("DATE_OPERDAY")
        get_bal_value_after = self.GetValueBalans(balance_params[0], balance_params[1], date_statusbar)
        counter_val = 0
        for i in self.balance_val_before:
          if self.balance_val_before[i] != get_bal_value_after[i]:
            Log.Checkpoint(i + " баланс изменился " + get_bal_value_after[i])
            counter_val += 1
        if counter_val == 0:
          Log.Warning("Баланс кассы не изменился")
        Sys.Process("COLVIR").VCLObject("frmCshMonFrm").Close()
        return counter_val

    def GetValueBalans(self, cashbox_id, tus_id, date_statusbar):
        """ Получение баланса кассы по всем валютам через запрос к бд """
        self.cashbox_id = cashbox_id
        self.tus_id = tus_id
        self.date_statusbar = date_statusbar
        select = """ select
            substr(c_PkgVal.fGetIsoCode(m.VAL_ID)||' ('||m.CODE||')',1,27) as VAL_STR, m.LONGNAME,
            to_money(decode(aa.activfl,1,T_PKGACCBAL.FADDPLN(a.dep_id,a.id,'""" + self.date_statusbar+ """',
            0,nvl(m.val_id, p_natval)))) as CNT
          from T_ACC aa, ANLACC a, ANLACC_DET d, ANLACC_DET d1, M_MONDSC m,
          (select ID, CODE, DEP_ID from M_CSHDSC) C
          where a.DEP_ID = d.DEP_ID and a.ID = d.ID
            and a.CHA_ID = (select ID from T_ANCHART where code ='CS_CASH')
            and d.SIGN_ID = T_ASGN.fCode2Id('M_CSH')
            and a.DEP_ID = d1.DEP_ID and a.ID = d1.ID and d1.SIGN_ID = T_ASGN.fCode2Id('M_MONDSC')
            and m.ID = d1.PK1
            and aa.DEP_ID = a.DEP_ID and aa.ID = a.ID
            and c.ID = d.PK1
            and ((""" + self.cashbox_id + """ is null and a.DEP_ID = P_IDDEP2) or
            (c.id = """ + self.cashbox_id + """ and a.DEP_ID = c.DEP_ID))
            and (""" + self.tus_id + """ is null or c.ID = any(select CSH_ID
            from M_CSHUSR where ID = """ + self.tus_id + """))
            and m.CASHFL = '1'
            order by d.PK1 """
        result = self.OracleHandlerDB(select)
        result_dict = {}
        for line in result:
          result_dict[line[1]] = line[2]
        return result_dict

    def ErrorMessageHandler(self, dop_window=None, negativ_case=None, time_await=2200, recursive='True',
                          need_text_error=None, allure=False, abs_path=None, name_file=None, name_step=None,
                          new_path=None, step=None, substep=None):
        """ Обработчик сообщений об ошибках со сбором диагностики из окна с ошибкой
        Параметр dop_window нужен если может появиться окно 'Обнаруженные ошибки' со списком перед основным окном
        Параметр negativ_case флаг ожидаемой ошибки, при которой будет выводится в лог event, а не warning
        Параметр need_text_error позволяет получить текст ошибки на выходе функции"""
        self.dop_window = dop_window
        self.negativ_case = negativ_case
        self.time_await = time_await
        self.recursive = recursive
        self.need_text_error = need_text_error
        # Переменные для формирования отчет Аллюр, в случае возникновения шибки
        self.allure = allure # Если передать True, то логи будут перемещаться в Аллюр
        self.step = step # шаг теста
        self.substep = substep # подшаг теста
        self.abs_path = abs_path # абсолютный путь
        self.name_step = name_step # наименование шага
        self.new_path = new_path # путь до папки allure-results
        self.name_file = name_file # название файла json с отчетом
        text_error = None
        if self.dop_window is not None and Sys.Process("COLVIR").WaitVCLObject("frmDynLstRefer", self.time_await).Exists:
          button_ok = self.FindChildField("frmDynLstRefer", "Name", "VCLObject('btnOK')")
          button_ok.Click()
        if Sys.Process("COLVIR").WaitWindow("#32770", "Произошла ошибка", -1, self.time_await).Exists:
          error_window = Sys.Process("COLVIR").Window("#32770", "Произошла ошибка", 1)
          text_error = str(error_window.Window("SysTabControl32", "", 1).Dialog("DIALOG").Window("Edit", "", 1).Text)
          if self.negativ_case is None:
            Log.Warning("Получено сообщение об ошибке:  " + text_error,"", pmNormal,"null",Sys.Desktop)
            if self.allure == True:
                self.AllureReportTemplate(self.abs_path, self.name_file, self.name_step, "failed", {"message": "Получено сообщение об ошибке:  " + text_error},
                                                    'desktop', "Непредвиденная ошибка", self.new_path, "failed", self.step, self.substep, rm=True)
          else:
            Log.Event("Получено ожидаемое сообщение об ошибке:  " + text_error,"", pmNormal,"null",Sys.Desktop)
          # собираем диагностику ошибки
          diagnostic_tab = error_window.Window("SysTabControl32", "", 1).PageTab("Диагностика")
          diagnostic_tab.Click()
          text_diag_err = error_window.Window("SysTabControl32", "", 1).Dialog("Dialog").Window("RichEdit20W", "", 1).Text
          Log.AppendFolder("Текст диагностики ошибки:")
          Log.Message(str(text_diag_err)) # отладочный лог готового запроса
          Log.PushLogFolder(-1)
          close_but_err = error_window.Button("Закрыть")
          close_but_err.Click()
          result = True
        elif self.recursive is not None:
          return self.ErrorMessageHandler(self.dop_window, self.negativ_case, self.time_await, recursive=None, need_text_error = self.need_text_error)
        else:
          result = False
        if self.need_text_error is not None:
          return text_error
        else:
          return result

    def WarningMessageHandler(self, negativ_case='', time_await=2200, dialog='Colvir Banking System', uia_dialog='Colvir_Banking_System'):
        """ Обработчик предупреждающих сообщений если передан ключ negativ_case,
        в лог выводится Event, а не Warning"""
        self.negativ_case = negativ_case
        self.time_await = time_await
        self.dialog = dialog
        self.uia_dialog = uia_dialog
        flag_mess = ''
        if Sys.Process("COLVIR").WaitWindow("#32770", self.dialog, -1, self.time_await).Exists:
          try:
            text_warning = Sys.Process("COLVIR").Dialog(self.dialog).UIAObject(self.uia_dialog).Child(7).Name
            flag_mess = 1
          except:
            flag_mess = 0
          state = True
          Sys.Process("COLVIR").Dialog(self.dialog).Close()
        else:
          state = False
        if flag_mess == 1 and not self.negativ_case:
          Log.Warning("Получено предупреждающее сообщение: " + str(text_warning.replace('Text', '').replace('UIAObject', '').replace('\\', '')),"", pmNormal,"null",Sys.Desktop)
        elif flag_mess == 1 and self.negativ_case:
          Log.Event("Получено предупреждающее сообщение: " + str(text_warning.replace('Text', '').replace('UIAObject', '').replace('\\', '')),"", pmNormal,"null",Sys.Desktop)
        elif flag_mess == 0 and not self.negativ_case:
          Log.Warning("Получено предупреждающее сообщение, которое не удалось обработать","", pmNormal,"null",Sys.Desktop)
        elif flag_mess == 0 and self.negativ_case:
          Log.Event("Получено предупреждающее сообщение, которое не удалось обработать","", pmNormal,"null",Sys.Desktop)
        return state

    def CatalogErrorMessageHandler(self, negativ_case='', time_await=2200):
        """ Обработчик сообщений об ошибках при заполнении справочника если передан ключ negativ_case,
        в лог выводится Event, а не Warning"""
        self.negativ_case = negativ_case
        self.time_await = time_await
        flag_mess = ''
        if Sys.Process("COLVIR").WaitWindow("TMessageForm", "Ошибка", -1, self.time_await).Exists:
          try:
            text_warning = Sys.Process("COLVIR").Dialog("Ошибка").VCLObject("Message").Caption
            flag_mess = 1
          except:
            flag_mess = 0
          state = True
          Sys.Process("COLVIR").Dialog("Ошибка").Close()
        else:
          state = False
        if flag_mess == 1 and not self.negativ_case:
          Log.Warning("Получено сообщение об ошибке: " + str(text_warning),"", pmNormal,"null",Sys.Desktop)
        elif flag_mess == 1 and self.negativ_case:
          Log.Event("Получено сообщение об ошибке: " + str(text_warning),"", pmNormal,"null",Sys.Desktop)
        elif flag_mess == 0 and not self.negativ_case:
          Log.Warning("Получено сообщение об ошибке, которое не удалось обработать","", pmNormal,"null",Sys.Desktop)
        elif flag_mess == 0 and self.negativ_case:
          Log.Event("Получено сообщение об ошибке, которое не удалось обработать","", pmNormal,"null",Sys.Desktop)
        return state

    def FindChildField(self, wndname_parent, name_property, name_field, internal='', log_event=None):
        """ Поиск необходимого поля по property и значению, и возврат его как объекта
        Для полей списков доп флаг internal для получения внутреннего значения поля
        name_property и name_field можно передавать в виде списка, если необходимо одновременно несколько свойств
        """
        self.wndname_parent = wndname_parent
        self.name_field = name_field
        self.name_property = name_property
        self.internal = internal
        parent_window = Sys.Process("COLVIR").VCLObject(self.wndname_parent)
        need_object = parent_window.FindChild(self.name_property, self.name_field, 15)
        if need_object.Exists and self.internal:
          internal_val = need_object.Child(0)
          Log.Message("Найденное поле " + str(internal_val.FullName))
          Log.Message("Значение поля " + str(internal_val.Value))
          return internal_val
        elif need_object.Exists:
          Log.Message("Найденное поле " + str(need_object.FullName))
          return need_object
        elif log_event is not None:
          Log.Event("Искомый объект " + str(self.name_field) + " не найден")
          return None
        else:
          Log.Warning("Искомый объект " + str(self.name_field) + " не найден")
          return None

    def FindWindowColvir(self, find_last_window, *prev_wnd, name_property='', value_property='', event_log=None):
        """ Поиск необходимого окна внутри colvir по по property и значению, и возврат его как объекта.
        По ключу find_last_window будет производиться поиск верхнего доступного окна (Enabled = True) для работы с ним
        """
        self.value_property = value_property
        self.name_property = name_property
        self.find_last_window = find_last_window
        self.prev_wnd = prev_wnd
        if not self.find_last_window:
          need_object = Sys.Process("COLVIR").FindChild(self.name_property, self.value_property, 1)
          if need_object.Exists:
            return need_object
          elif event_log is not None:
            Log.Event("Искомое окно " + self.value_property + " не найдено")
            return None
          else:
            Log.Warning("Искомое окно " + self.value_property + " не найдено")
            return None
        else:
          property = ["ObjectType", "Name", "Enabled", "Visible"]
          values = ["VCLObject", "regexp:VCLObject.*", True, True]
          need_list_object = Sys.Process("COLVIR").FindAllChildren(property, values)
          expect_list = ('Выбор режима','Colvir Banking System','Банковская система COLVIR: GO_ COLVIR  (COLVIR/COLVIR-1000)')
          if self.prev_wnd and self.prev_wnd[0] is not None:
            expect_list = expect_list + self.prev_wnd[0]
          for child_object in need_list_object:
            if child_object.WndCaption is not None and child_object.WndCaption not in expect_list:
              Log.Message("Найденное окно " + str(child_object.FullName))
              Log.Message("Найденное окно " + str(child_object.WndCaption))
              return child_object
          else:
            Log.Event("Не найдено новое окно по заданным условиям доступности")
            return None

    def SaveWithWarnings(self, window_name):
        """ Сохранение документа с перехватом и закрытием уведомлений
        о несоответсвии значения списку, корректные значения списков выбираются по принципу -
        открыть список -> выбрать первое значение -> закрыть список
        """
        self.window_name = window_name
        save_btn = self.FindChildField(self.window_name, "Name", 'VCLObject("btnSave")')
        save_btn.Click()
        try_counter = 0 # количество попыток, чтобы не ушел в вечный цикл
        state = False
        while self.WarningMessageHandler('no_log'):
          self.CatalogErrorMessageHandler('no_log', time_await=1000)
          if try_counter >= 3:
            Log.Warning("Количество попыток сохранения превысило допустимое количество")
            state = True
            return state
          need_window = self.FindWindowColvir('', None, name_property="ObjectIdentifier", value_property=self.window_name)
          if need_window is None:
            break
          need_window.Keys("^a")
          need_window.Keys("[BS]")
          need_window.Keys("[F2]")
          need_last_window = None
          if not need_window.Enabled:
            if Sys.Process("COLVIR").WaitVCLObject("frmFilterParams", 1500).Exists:
              self.SetFilter()
            need_last_window = self.FindWindowColvir('last_window', None)
            if need_last_window is not None and need_last_window.ObjectIdentifier != self.window_name: # если новое окно не то же, что и переданное
              btn_ok_list = self.FindChildField(need_last_window.ObjectIdentifier, "Name", 'VCLObject("btnOK")', log_event="Event")
              if btn_ok_list is not None and btn_ok_list.Enabled: # проверка на пустой список
                btn_ok_list.Click()
              else:
                Log.Warning("Список значений пуст, либо выбранное значение неактивно","", pmNormal,"null",Sys.Desktop)
                need_last_window.Close()
                state = True
                return state
          else:
            rand_str = self.DocNumberGenerator()
            need_window.Keys(" TEST_"+ rand_str) # пробел в начале строки здесь очень важен, чтобы ввод подхватился активным окном
          save_btn.Click()
          if Sys.Process("COLVIR").WaitVCLObject("ErrMessageForm", 1500).Exists: # специфическое окно ошибки
            Sys.Process("COLVIR").VCLObject("ErrMessageForm").Close()
          try_counter += 1
        return state

    def FieldValueValidator(self,field_name, need_field, type_field, test_str='',  **log_type):
        """ Валидатор автозаполнения значений полей на форме (date, number, text)"""
        self.need_field = need_field
        self.field_name = field_name
        self.type_field = type_field
        self.test_str = test_str
        self.log_type = log_type
        if self.type_field == 'date':
          # получаем опердень со статусбара
          system_date = self.SystemDateValue()
          date_statusbar = aqConvert.DateTimeToFormatStr(system_date, "%d.%m.%y")
          if self.need_field.Value == date_statusbar: # сравниваем с датой на статусбаре
            Log.Event("Значение поля '" + self.field_name + "' совпадает с датой опердня")
          else:
            self.ValueValidatorLogs(self.log_type, self.field_name)
            self.need_field.Keys("[Home]")
            if self.test_str:
              Log.Event("Значение поля '" + self.field_name + "' будет заполнено автоматически тестовой строкой")
              self.need_field.Keys(self.NormalDateMask(self.test_str))
            else:
              Log.Event("Значение поля '" + self.field_name + "' будет заполнено автоматически датой опердня")
              self.need_field.Keys(self.NormalDateMask(date_statusbar))
        elif self.type_field == 'number':
          get_num_field = self.need_field.Value
          if re.findall('(\d+)', get_num_field):  # ищем есть ли цифры в поле
            Log.Event("Автозаполнение поля '"+ self.field_name +"' отработало успешно, значение "+ str(self.need_field.Value))
          else:
            self.ValueValidatorLogs(self.log_type, self.field_name)
            if self.test_str:
              Log.Event("Значение поля '" + self.field_name + "' будет заполнено автоматически")
              self.need_field.Keys("[Home]")
              self.need_field.Keys(self.test_str)
        elif self.type_field == 'text':
          get_text_str = self.need_field.Value
          if re.findall('(\w+)', get_text_str):  # ищем есть ли буквы и слова в поле
            Log.Event("Автозаполнение поля '" + self.field_name + "' отработало успешно, значение "+ str(self.need_field.Value))
          else:
            self.ValueValidatorLogs(self.log_type, self.field_name)
            if self.test_str:
              Log.Event("Значение поля '" + self.field_name + "' будет заполнено автоматически")
              self.need_field.Keys("[Home]")
              self.need_field.Keys(self.test_str)
        else:
          Log.Warning("Неверное значение ключа для валидатора либо данный ключ отсутствует в обработчике")

    def ValueValidatorLogs(self, type_log, field_name):
        """ Выбор вывода лога Warning или Event в зависиости от заданного ключа type_log """
        self.field_name = field_name
        self.type_log = type_log
        if self.type_log:
          Log.Event("Значение поля '" + self.field_name + "' пусто")
        else:
          Log.Event("Значение поля '" + self.field_name + "' пусто")

    def FieldValueComparator(self, field_name, need_field, control_value, check_property='Value'):
        """ Сравниватель значений поля с контрольным значением """
        self.field_name = field_name
        self.need_field = need_field
        self.control_value = control_value
        self.check_property = check_property
        if self.check_property == 'Value':
          fieldval = self.need_field.Value.strip()
        if fieldval == self.control_value:
          Log.Event("Значение поля "+ str(self.field_name) +" совпадает с контрольным и равно "+ str(fieldval))
        else:
          Log.Warning("Значение поля "+ str(self.field_name) +" не совпадает с контрольным и равно "+ str(fieldval) +
                      " а должно быть "+ str(self.control_value))

    def GeneratePeriodContribution(self):
        """ Генерация периода отчисления из текущей даты """
        now = datetime.now()
        str_now = datetime.strftime(now, "%m%Y")
        return str_now

    def CheckValuesKNP(self, wndname):
        """ Проверка автозаполнения полей во вкладке КНП с хитрым доступом к значению полей """
        self.wndname = wndname
        dict_knp = {}
        KNP_tab = self.FindChildField(self.wndname, "Name", 'PageTab("КНП")')
        KNP_tab.Click()
        KNP_field = self.FindChildField(self.wndname, "Name", 'VCLObject("edKNP")')
        dict_knp['КНП'] = KNP_field.Child(0).Text
        KOD_field = self.FindChildField(self.wndname, "Name", 'VCLObject("edCODE_OD")')
        dict_knp['КОд'] = KOD_field.Child(0).Text
        KBE_field = self.FindChildField(self.wndname, "Name", 'VCLObject("edCODE_BE")')
        dict_knp['КБе'] = KBE_field.Child(0).Text
        for key, value in dict_knp.items():
          if value:
            Log.Event(key + " = " + value)
          else:
            Log.Warning("Поле " + key + " пусто! ")

    def GetCleanAcc(self, dep_acc, val_acc='KZT', mask_acc='2204%', acc_in_ps='1', need_ost_acc='3000',
                    kolvo_acc='1', group_acc='', no_need_acc=''):
        """ Получение из бд счетов без арестов, блокировок и картотеки
        Входные параметры:
        dep_acc - подразделение счета, val_acc - код валюты счета
        mask_acc - маска счета(2204% фл, 2203% юр), acc_in_ps - обслуживается в ПС(0 или 1),
        need_ost_acc - остаток на счете, kolvo_acc - количество счетов,
        group_acc - группа обслуживания счета,
        no_need_acc - счета, которые необходимо исключить(по номеру счета)"""
        self.val_acc = val_acc
        self.dep_acc = dep_acc
        self.mask_acc = mask_acc
        self.acc_in_ps = acc_in_ps
        self.need_ost_acc = need_ost_acc
        self.kolvo_acc = kolvo_acc
        self.group_acc = group_acc
        self.no_need_acc = no_need_acc
        if self.group_acc:
          join_group_acc = """ and tg.code = '""" + self.group_acc + """' """
        else:
          join_group_acc = ''
        if self.no_need_acc:
          need_block_acc =  "and a.code <>'" + self.no_need_acc + "'"
        else:
          need_block_acc = ''
        select = """
            select distinct a.code as num_acc, l.code as mask_acc, d.code as dep_account, tg.code as group_acc
          from g_accbln a
          join g_accblnhst ah
            on ah.id = a.id
           and ah.dep_id = a.dep_id and ah.arcfl = 0
           left join G_LOCK ga
            on a.DEP_ID = ga.DEP_ID
           and a.ID = ga.ACC_ID
           left join g_locktype gt
            on ga.locktype = gt.id
           AND trunc(sysdate) BETWEEN ga.fromdate AND NVL(ga.todate, p_maxdate)
           AND gt.code NOT IN ('БС','БНПА','БП','БА','БН','БСПО','ББ','БИН','LOCK','LOCK_P','LOCK_S')
           join APT_ACC@CAP tt
            on tt.id = G_pkgCAP.fGetAccIDNInCap(a.dep_id, a.id)
          join APR_LOCK@CAP rr
            on rr.id = tt.lckfl
           AND rr.name <> 'Locked'
          join (select * from T_VAL_STD where code =  '""" + self.val_acc + """') t2
            on ah.val_id = t2.id
          join g_clihst t5
            on ah.cli_id = t5.id
           and ah.clidep_id = t5.dep_id
          join c_dep d
            on a.dep_id = d.id
           and d.code = '""" + self.dep_acc + """'
          join ledacc_std l
            on l.id = ah.cha_id
          join t_accgrp tg
             on tg.dep_id = ah.dep_id
             and tg.id = ah.aut_id
           """ + join_group_acc + """
        where trunc(sysdate) between ah.fromdate and ah.todate
           and trunc(sysdate) between t5.fromdate and t5.todate
           and not exists (select * from S_CRD2 cd where cd.acc_id = a.id)
           and l.code LIKE '""" + self.mask_acc + """'
           and ah.nondebfl = 0
           and a.capfl = """ + self.acc_in_ps + """
           and 0 - T_PkgAccBal.fAccBal(a.dep_id,a.id,trunc(sysdate),0,ah.VAL_ID,0,0) >= """ + self.need_ost_acc + """
           """ + need_block_acc + """
           and rownum <= """ + self.kolvo_acc + """
        """
        empty_result = []
        result = self.OracleHandlerDB(select)
        if result is not None:
          return result
        else:
          return empty_result

    def GetAccountInfo(self, acc_number, need_dict=None):
        """ Получение информации по номеру счета:
        MASK - Маска счета, ACC_NUM - номер счета, COLVIR_BAL - баланс в АБИС,
        EQUAL_BAL - баланс АБИС в KZT, K2 - картотека2 на счете (1 есть, 0 нет),
        AREST - аресты на счете (1 есть, 0 нет), BLOCK - блокировки на счете (1 есть, 0 нет),
        INKASSO - инкассовые на счете (1 есть, 0 нет), PS_BAL - баланс в ПС (если обслуж в ПС),
        GROUP_ACC - группа обслуж счета, CODE - код карточки клиента счета"""
        self.acc_number = acc_number
        self.need_dict = need_dict
        select = """ select l.code as MASK,a.code as ACC_NUM,
           abs(t_pkgaccbal.faccbal(a.dep_id, a.id, trunc(sysdate),0,ag.val_id,0,0)) as COLVIR_BAL,
           abs(T_PkgAccBal.fFulNatVal(a.dep_id,a.id,trunc(sysdate),0,ag.VAL_ID,0,0)) as EQUAL_BAL,
           --Z_026_F_CHECK_BLOCKACC(a.dep_id, a.id) as K2,
           G_PKGCLOSEACCCHK.fCheckAccLim(a.dep_id, a.id) as AREST,
           G_PKGCLOSEACCCHK.fCheckAccLockOrLim(a.dep_id, a.id) as BLOCK,
           --Z_026_F_CHECK_BLOCKACC(a.dep_id, a.id) as INKASSO,
           (SELECT case P_CUSTCODE
              when '026' then
              substr(TO_MONEY(G_PKGCAP.fBAL(A1.DEP_ID,A1.ID,P_OPERDAY,T_VAL.ID) -
              G_PKGCAP.fBAL(A1.DEP_ID, A1.ID,trunc(sysdate),T_VAL.ID,1,null,null,1),0,MULTIPLIER + 2),1,27)
              else substr(TO_MONEY(G_PKGCAP.fBAL(A1.DEP_ID,A1.ID,trunc(sysdate),T_VAL.ID),0,MULTIPLIER + 2),1,27)
              end
              from T_VAL, T_ACC AA, G_ACCBLN A1
              where T_VAL.ID = nvl(AA.VAL_ID, P_NATVAL)
              and A.ID = AA.ID and A.DEP_ID = AA.DEP_ID
               and A1.code = a.code) PS_BAL,
           tg.code as GROUP_ACC, gg.code, nvl(gl_anl.faccanlvalue(a.dep_id, a.id, 'VALUTA'),'KZT') as VAL_CODE,
           substr(l.code, 1, 4) as ACODE, a.id, a.dep_id, Z_026_PKG_KZ_PAY.f_get_dcl_code(a.code) as product_code
           from g_clihst g, g_cli gg, g_accbln a, g_accblnhst ag, ledacc l, t_accgrp tg
           where g.id = gg.id
           and g.dep_id = gg.dep_id and trunc(sysdate) between g.fromdate and g.todate
           and g.id = ag.cli_id and g.dep_id = ag.clidep_id and trunc(sysdate) between ag.fromdate and ag.todate
           and a.id = ag.id and a.dep_id = ag.dep_id and a.cha_id = l.id and tg.dep_id = ag.dep_id
           and tg.id = ag.aut_id and a.code = '""" + self.acc_number + """'
        """
        info_acc = self.OracleHandlerDB(select)
        if self.need_dict is not None and info_acc is not None:
          tuple_acc_fields = ('MASK','ACC_NUM','COLVIR_BAL','EQUAL_BAL','AREST',
                              'BLOCK','PS_BAL','GROUP_ACC','CODE',
                              'VAL_CODE', 'ACODE', 'ID', 'DEP_ID', 'PRODUCT_CODE')
          dict_result = {}
          for rows in info_acc:
            for fields_card, fields_row in zip(tuple_acc_fields, rows):
              dict_result[fields_card] = fields_row
          info_acc = dict_result
        return info_acc

    def GetCliCardFields(self, id_card=None, dep_id_card=None, code_cli_card=None):
        """ Получение основных полей карточки клиента по id и dep_id или по коду карточки клиента
        через запрос к БД """
        self.id_card = id_card
        self.dep_id_card = dep_id_card
        self.code_cli_card = code_cli_card
        if self.code_cli_card is not None:
          check_str_type = " and G.CODE = '"+ str(self.code_cli_card) +"'"
        else:
          check_str_type = " and GH.DEP_ID = "+ str(self.dep_id_card) +" and GH.ID = "+ str(self.id_card) +""
        select = """ select G.CODE, (select LISTAGG(name) WITHIN GROUP (ORDER BY name) from G_ROLDSC
             where substr(G.rolemask, NROLE, 1) = '1') as CLI_ROL,G.JURFL,G.PBOYULFL,GH.ARCFL,GH.NAME,
              GH.LONGNAME,GH.CODEWORD,GH.BIRDATE,GH.TAXCODE,GH.BIN_IIN,GH.ADDRESS,GH.ADDRJUR,
              GH.PHONE,GH.EMAIL,GH.CORPORFL,GH.PASSTYP,GH.PASSSER,GH.PASSNUM,GH.PASSDAT,GH.PASSORG,
              GH.PASSFIN,GH.RESIDFL,GH.BANKFL,GH.SECT_ID,GH.AFFILFL,GH.OKPO,GH.REGDATE,GH.PNAME1,GH.PNAME2,GH.PNAME3,
              GH.PLNAME1,GH.PLNAME2,GH.PLNAME3,GH.PSEX,GH.PTITLE,D1.CODE DEP_CODE,
              T_ACCGRP.CODE AUT_CODE,S_TRFGRP.CODE as TRFCAT_CODE,S_TRFGRP.NAME as TRFCAT_NAME,S.NAME as STATE,
              G.DEP_ID,G.ID, g_pkgcli.fgetregcli(G.DEP_ID, G.ID, '"""+self.GetEnviron("DATE_OPERDAY")+"""') as REG_CONT
             from G_CLI G,G_CLIHST GH,C_DEP D1,T_ACCGRP,S_TRFGRP,T_PROCMEM  M,T_PROCESS  P,T_BOP_STAT S
               where GH.DEP_ID = G.DEP_ID and GH.ID = G.ID
               and M.ORD_ID = G.ORD_ID and M.DEP_ID = G.DEP_ID and P.ID = M.ID and S.NORD = P.NSTAT
               and P.BOP_ID = S.ID and D1.ID = G.DEP_ID and T_ACCGRP.DEP_ID(+) = GH.DEP_ID
               and T_ACCGRP.ID(+) = GH.AUT_ID and S_TRFGRP.ID(+) = GH.TRF_IDCAT """ + check_str_type + \
               """ and '"""+ self.GetEnviron("DATE_OPERDAY")+"""' between gh.fromdate and gh.todate and S.NAME = 'Карточка открыта'  """
        tuple_card_fields = ('CODE','CLI_ROL','JURFL','PBOYULFL','ARCFL','NAME','LONGNAME','CODEWORD','BIRDATE',
                            'TAXCODE','BIN_IIN','ADDRESS', 'ADDRJUR','PHONE','EMAIL','CORPORFL','PASSTYP',
                            'PASSSER','PASSNUM','PASSDAT','PASSORG','PASSFIN','RESIDFL','BANKFL','SECT_ID',
                            'AFFILFL','OKPO','REGDATE','PNAME1','PNAME2','PNAME3','PLNAME1','PLNAME2','PLNAME3','PSEX',
                            'PTITLE','DEP_CODE','AUT_CODE','TRFCAT_CODE','TRFCAT_NAME','STATE','DEP_ID','ID','REG_CONT')
        result = self.OracleHandlerDB(select)
        dict_result = {}
        for rows in result:
          for fields_card, fields_row in zip(tuple_card_fields, rows):
            dict_result[fields_card] = fields_row
        return dict_result

    def GetPlusDailyDate(self, add_days, input_date=''):
        """ Возвращение даты по формуле - входная дата +/-(если add_days < 0) необходимое кол-во дней,
        если необходимая дата не подана на вход, дата будет взята со статусбара.
        Полученная дата будет проверена по внутреннему календарю колвира, чтобы выпадала на рабочий день.
        Если полученная дата выпадает на выходной, будет дополнительно прибавлен/отнят один день"""
        self.add_days = add_days
        self.input_date = input_date
        if self.add_days >= 0:
          abs = 1
        else:
          abs = -1
        #если дата не передана, получаем опердень со статусбара
        if not self.input_date or self.input_date is None:
          self.input_date = self.SystemDateValue()
        # преобразовываем в обрабатываемый формат
        self.input_date = aqConvert.StrToDate(self.input_date)
        new_date = aqDateTime.AddDays(self.input_date, self.add_days)
        new_date = aqConvert.DateTimeToFormatStr(new_date, "%d.%m.%Y")
        exception_list, free_days_list = self.SelectWorkingDates()
        exception_work_days = []
        for key, value in exception_list.items():
          if str(value) == '1':
            free_days_list.append(key) # объединяем два списка с выходными
          else:
            exception_work_days.append(key) # список с рабочими днями месяца
        new_working_date = ''
        for _ in range(7):
          day_week = aqDateTime.GetDayOfWeek(new_date)
          if new_date in free_days_list or (new_date not in exception_work_days and (day_week == 1 or day_week == 7)):
            new_date = aqDateTime.AddDays(new_date, abs)
            new_date = aqConvert.DateTimeToFormatStr(new_date, "%d.%m.%Y")
          else:
            new_working_date = aqConvert.DateTimeToFormatStr(new_date, "%d.%m.%y")
            break
        if not new_working_date:
          Log.Warning('Не удалось определить дату рабочего дня')
        return new_working_date

    def SelectWorkingDates(self):
        """ Получение календаря рабочих дней РК колвира (id 181) и исключающими днями"""
        # 1 выходной, 0 рабочий день
        select_exception_days = """
          select
            substr(to_char(t.doper,'DD.MM.YYYY'),1,10) as doper,
            t.daytyp
            from c_excprule t
            where t.id='181'
            order by
            t.doper desc
         """
        result_excepton = self.OracleHandlerDB(select_exception_days)
        result_ex_dict = {}
        for line in result_excepton:
          result_ex_dict[line[0]] = line[1]
        select_free_days = """
            select
            t.month_in_year as months,
            t.day_in_month as days
            from c_nworkday t
            where
            t.ID = '181'
            order by
            t.month_in_year,
            t.day_in_month
        """
        result_free = self.OracleHandlerDB(select_free_days)
        # приводим в нормальный вид
        normal_result_free = self.FreeDaysConvertor(result_free)
        return result_ex_dict, normal_result_free

    def FreeDaysConvertor(self, list_days):
        """ Приведение даты в формат dd.mm.YYYY для странной записи выходных в календаре выходных дней"""
        self.list_days = list_days
        now_year = datetime.now().year
        normal_list = []
        for line in self.list_days:
          if line[0] is not None and line[1] is not None:
            merged_date = str(int(line[1])) + '.' + str(int(line[0])) + '.' + str(now_year)
            format_date = aqConvert.StrToDate(merged_date)
            format_date= aqConvert.DateTimeToFormatStr(format_date, "%d.%m.%Y")
            normal_list.append(format_date)
        return normal_list

    def CompareDicts(self, dict_one, dict_two):
        """ Проверка изменений значений по двум словарям с одинаковыми ключами
        с помощью множеств"""
        self.dict_one = dict_one
        self.dict_two = dict_two
        set_one, set_two = set(self.dict_one.keys()), set(self.dict_two.keys())
        intersect = set_one.intersection(set_two)
        result_set = set(x for x in intersect if self.dict_one[x] != self.dict_two[x])
        return result_set

    def SetFieldsValidator(self, first_dict, second_dict, no_change='', *need_fields):
        """ Проверка двух словарей с сохраненными полями до и после выполнения операции на изменение полей,
        На вход принимаются названия полей, которые нужно проверить,
        ключ no_change передается если ни одно из полей не должно было измениться."""
        self.first_dict = first_dict
        self.second_dict = second_dict
        self.no_change = no_change
        self.need_fields = need_fields
        # получаем разницу полей
        set_result = self.CompareDicts(self.first_dict, self.second_dict)
        status = False
        if set_result:
          check_fields = set_result.intersection(set(self.need_fields))
          if not self.need_fields:
            Log.Warning("Изменение полей не ожидалось, но изменились " + str(set_result))
          elif len(check_fields) != len(self.need_fields) or len(self.need_fields) != len(set_result):
            Log.Warning("Ожидалось изменение полей " + str(self.need_fields) + ", а изменились " + str(set_result))
          for item in set_result:
            Log.Checkpoint("Поле " + item + " изменилось после выполнения операции, новое значение  " + str(self.second_dict[item]))
            status = True
        elif not set_result and self.no_change:
          Log.Checkpoint("Ни одно из полей не изменилось, как и ожидалось")
          status = True
        else:
          Log.Warning("Ни одно из полей не изменилось")
        return status

    def HotKeysScen(self, name_operation, name_key, name_window, need_scenario=None, count=3):
        """ Метод установка/отключение горячей клавиши, для вызова необходимой операции
        входные параметры - код операции, значение горячей клавиши(к примеру q), наименование окна
        К каждой полученной клавише предусмотрена привязка код сценария (исключяем массовое проставление
        горячей клавиши вне зависимости от бизнес-сценария)
        Важно!! при разработке нового модуля производить подвязку уникальной клавиши к сценарию."""
        self.name_operation = name_operation
        self.name_key = name_key
        self.name_window = name_window
        self.need_scenario = need_scenario
        self.count = count
        if self.need_scenario is not None:
          name_scenario = self.need_scenario
        elif self.name_key in ('h'):
          name_scenario = 'B_WARR'
        elif self.name_key in ('q', 'w'):
          name_scenario = 'CS_CRED'
        elif self.name_key in ('r'):
          name_scenario = 'CS_CR_LIN'
        elif self.name_key in ('z', 'x', 's'):
          name_scenario = 'CS_DEP'
        elif self.name_key in ('u'):
          name_scenario = 'LETTEROFCR'
        elif self.name_key in ('v'):
          name_scenario = 'O_MORTG'
        elif self.name_key in ('y'):
          name_scenario = 'OUT_202'
        elif self.name_key in ('j','t'):
          name_scenario = 'CS_REC'
        elif self.name_key in ('o'):
          name_scenario = 'CLIENTS'
        elif self.name_key in ('k'):
          name_scenario = 'COM'
        else:
          Log.Warning('Отсутствует условие подвязки сценария к переменной, согласно полученной горячей клавиши ' + str(self.name_key))
        # почистим сценарий от клавиш
        self.RemoveHotkey(self.name_key, name_scenario)
        #проверим ранее установленную клавишу либо -1(не установлена) запускаем update по установке
        total_hot = self.CheckingHotKey(self.name_operation, name_scenario)
        if total_hot == '-1':
          query = """  begin
          update c_vcs v set v.usr_id = null where v.code like ('%""" + self.name_operation + """%')
          and v.USR_ID is not null;
          commit;
          update t_scen_std s
            set s.hotkey = 'Ctrl+""" + self.name_key + """'
          where s.arcfl = 0
            and s.code = '""" + self.name_operation +  """'
            and s.id in (select id from t_bop_dscr_std where code = '""" + name_scenario + """');
            commit;
          update c_vcs v set v.usr_id = null where v.code like ('%""" + self.name_operation + """%')
          and v.USR_ID is not null;
          commit;
    	        end; """
          self.OracleHandlerDB(query, dml_query='True')
          Delay(1500)
          #self.ResultHotKeysScen(self.name_operation, self.name_key, name_scenario)
          Sys.Process("COLVIR").VCLObject(self.name_window).Keys("^"+ self.name_key)
          Delay(1500)
          if not Sys.Process("COLVIR").WaitWindow("TMessageForm", "Подтверждение", -1, 25000).Exists and \
          Sys.Process("COLVIR").VCLObject(self.name_window).Enabled:
            Sys.Process("COLVIR").VCLObject(self.name_window).Keys("^"+ self.name_key)
            Log.Event("Повторно вызываем операцию горячей клавишей")
          query = """ begin
          update c_vcs v set v.usr_id = null where v.code like ('%""" + self.name_operation + """%')
          and v.USR_ID is not null;
          commit;
    	  update t_scen_std s
            set s.hotkey = ''
          where s.arcfl = 0
            and s.code = '""" + self.name_operation +  """'
            and s.id in (select id from t_bop_dscr_std where code = '""" + name_scenario + """');
            commit;
          update c_vcs v set v.usr_id = null where v.code like ('%""" + self.name_operation + """%')
          and v.USR_ID is not null;
          commit;
          end;  """
          self.OracleHandlerDB(query, dml_query='True')
        else:
          Sys.Process("COLVIR").VCLObject(self.name_window).Keys("^"+ str(total_hot[5]))
          Delay(1500)
          if not Sys.Process("COLVIR").WaitWindow("TMessageForm", "Подтверждение", -1, 25000).Exists and \
          Sys.Process("COLVIR").VCLObject(self.name_window).Enabled:
            Sys.Process("COLVIR").VCLObject(self.name_window).Keys("^"+ str(total_hot[5]))

    def GenerateRandomString(self, str_lenght):
        """ Генерация рандомной/случайной строки только из символов заданной величины """
        self.str_lenght = str_lenght
        return ''.join(choice(ascii_letters) for _ in range(self.str_lenght))

    def SelectGraficCheck(self, id, dep_id, contract_number):
        """ Проверка формирование планового платежа на выходной/праздничный день
        (входной параметр id/dep_id/номер кредитного/депозитного договора)"""
        self.id = id
        self.dep_id = dep_id
        self.contract_number = contract_number
        select = """ select distinct (s.doper)
        from T_DEASHDPNT s, tt_point t
        where s.tt_id = t.id
        and s.tt_nord = t.nord
        and s.DEP_ID = """  + self.dep_id + """
        and s.ORD_ID = """  + self.id + """
        order  by s.doper """
        result = self.OracleHandlerDB(select)
        exception_list, free_days_list = self.SelectWorkingDates()
        except_dict = dict(exception_list)
        for row in result:
          date_day = aqConvert.StrToDate(row[0])
          date_two = aqConvert.DateTimeToFormatStr(date_day, "%d.%m.%Y")
          is_holiday = False
          for key, value in except_dict.items():
            # Если плановая дата = праздничной дате и 1 - выходной день
            if date_two == key and str(value) == '1':
              Log.Warning("Сбой формирования графика, плановый платеж выпал на праздничный/выходной день " + str(date_two) + '' + str(self.contract_number))
              is_holiday = True
              break
          # Если день недели 1 - воскресенье, 7 - суббота
          day_week = aqDateTime.GetDayOfWeek(date_two)
          if not is_holiday and (date_two in free_days_list or (day_week == 1 or day_week == 7)):
            Log.Warning("Сбой формирования графика, плановый платеж выпал на праздничный/выходной день " + str(date_two) + '' + str(self.contract_number))

    def WaitReportPrintList(self, time_await=120000, no_log=None):
        """ Ожидание окна 'Сформированные отчеты' и нажатие в нем кнопки очистки """
        self.time_await = time_await
        self.no_log = no_log
        if Sys.Process("COLVIR").WaitVCLObject("RptToPrintList", self.time_await).Exists:
          print_clear_btn = self.FindChildField("RptToPrintList", "Name", "VCLObject('btnDelete')")
          print_clear_btn.Click()
          self.ClickNeedButConfirmWindow('OK')
        elif self.no_log is not None:
          Log.Event("Не найдено окно 'Сформированные отчеты' ")
        else:
          Log.Warning("Не найдено окно 'Сформированные отчеты' ")

    def LLPKeys(self, range_key, range_numbers=1, end_key=None):
        """ Обработчик LLPlayer метода клавиатурного ввода, адрес с кодами виртуальных клавиш
        https://docs.microsoft.com/ru-ru/windows/desktop/inputdev/virtual-key-codes
        входные парамерты: range_key - клавиша, прожимаемая в цикле; range_numbers - кол-во итераций цикла;
        end_key - клавиша, прожимаемая по окончанию цикла"""
        self.range_key = range_key
        self.range_numbers = range_numbers
        self.end_key = end_key
        for _ in range(int(self.range_numbers)):
          LLPlayer.KeyDown(self.range_key, 3)
          LLPlayer.KeyUp(self.range_key, 3)
        if self.end_key is not None:
          LLPlayer.KeyDown(self.end_key, 3)
          LLPlayer.KeyUp(self.end_key, 3)

    def GetStatusList(self, need_status, code_scenario):
        """ Получение списка статусов договора и возврат его позиции в списке
        согласно входным параметрам: состояние договора, код сценария (пример CS_DEP)"""
        self.need_status = need_status
        self.code_scenario = code_scenario
        select = """ select st.NORD, st.LONGNAME
              from T_BOP_STAT st, T_BOP_DSCR bp
              where bp.CODE = '""" + self.code_scenario + """'
              and bp.ID=st.ID and st.FORKFL!='1'
              """
        result = self.OracleHandlerDB(select)
        need_index = 0
        for line in result:
          if line[1] == self.need_status:
            break
          need_index += 1
        return need_index

    def LimitAccBlockHandler(self, account_num, wndname="frmShowTextDlg", time_await=2000):
        """ Обработка сообщения о блокировке по счету LIMIT или неоплаченных тратах """
        self.account_num = account_num
        self.wndname = wndname
        self.time_await = time_await
        if Sys.Process("COLVIR").WaitVCLObject(self.wndname, self.time_await).Exists:
          text_message = Sys.Process("COLVIR").VCLObject(self.wndname).VCLObject("Memo").Value
          Log.Warning('По счету '+ self.account_num +' получено сообщение '+ text_message)
          btn_ok_limits = self.FindChildField(self.wndname, "Name", 'VCLObject("btnOK")')
          btn_ok_limits.Click()

    def GetFinancialRecord(self):
        """ Получение данных из Fields по Форме 'Финансовая запись' сформированного фин.документа
        в журнале операции"""
        btn_value = Sys.Process("COLVIR").VCLObject("frmOperJournal").VCLObject("btnDtlView")
        if btn_value.Enabled:
          btn_value.Click()
          if not self.ErrorMessageHandler():
            self.WaitLoadWindow('frmGTrnDtlEdtDetail')
            detail_field = self.GetGridDataFields("frmGTrnDtlEdtDetail", "ID")
            Sys.Process("COLVIR").VCLObject("frmGTrnDtlEdtDetail").Close()
            return detail_field[0].replace("\'",'')
        else:
          Log.Warning('Кнопка "Просмотр финансовой записи" недоступно, ожидалось формирование проводок')

    def SelectAnaliticBal(self, id):
        """ Проверка формирование аналитических проводок - входной параметр TRA_ID из журнала операции"""
        self.id = id
        if self.id:
          select = """ select tt.code as account
          from anlacc a, t_trndtl t, t_anchart tt
          where a.dep_id = t.dep_id
          and a.id  = t.acc_id
          and t.id = """ + self.id + """
          and a.cha_id = tt.id """
          result = self.OracleHandlerDB(select)
          account_list = []
          if result is not None:
            for column in result:
              account_list.append(column[0])
            Log.Message('Сформированые счета ' + str(account_list) + ' в результате выполнение операции')
            return account_list
        else:
          Log.Event('Отсутствует tra_id для исполнение запроса и получение счетов по аналитике')

    def GettingBalanceAccounts(self, tra_id, date_plan):
        """ Получение счетов участвующихся в бух.проводке
        входной параметр TRA_ID из журнала операции, дата формирования фин.записи"""
        self.tra_id = tra_id
        self.date_plan = date_plan
        if self.tra_id:
          select = """ select l.code
          from T_TRNDTL d, g_accbln a, ledacc l
          where d.ID = """ + self.tra_id + """
          and d.INCOMFL in ('1','0')
          and d.doper = '""" + self.date_plan + """'
          and d.acc_id = a.id
          and d.dep_id = a.dep_id
          and a.cha_id = l.id """
          result = self.OracleHandlerDB(select)
          balans_account_list = []
          if result is not None:
            for item in result:
              balans_account_list.append(item[0])
            Log.Message('Сформированые счета ' + str(balans_account_list) + ' в результате выполнение операции')
            return balans_account_list
        else:
          Log.Event('Отсутствует tra_id для исполнение запроса и получение счетов по аналитике')

    def CustomerPayAccount(self, account, amount=''):
        """ Пополнение текущего счета (2204*2203*), только в нац.валюте KZT"""
        self.account = account
        self.amount = amount
        result = """  declare nReq number;
            c_text  clob;
            begin c_pkgconnect.popen();
            c_pkgsession.doper := trunc(sysdate);
            Select COLVIR.Z_026_SEQ_REQUEST.NEXTVAL into nReq From Dual;
            z_026_pkg_terminalpayment.pexecuteterminalpayment('KZ199471398000305968',
            '""" + self.account + """' ,""" + self.amount + """, nReq, c_text);
            end;
            """
        self.OracleHandlerDB(result, dml_query='True')

    def ActivateSqlMonitor(self):
        """ Включает sql-монитор и, если лог sql-монитора не пуст, чистит лог """
        try:
          Sys.Process("COLVIR").VCLObject("frmCssAppl").Keys("!^~l")  #shift+ctrl+alt+l открываем секретное окно
          sql_monitor_form = Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("pnlStatus").VCLObject("chkSQLMonitor")
          if sql_monitor_form.State == 0:
            sql_monitor_form.Click()
            Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK").Click()
          else:
            #нужно очистить sql log
            sql_log_form = Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").ListItem("Лог SQL-монитора")
            sql_log_form.DblClick()
            clear_btn = Sys.Process("COLVIR").VCLObject("frmSQLLogDialog").VCLObject("pnlButtons").VCLObject("btnClear")
            clear_btn.Click()
            #выход из sql log-а
            Sys.Process("COLVIR").VCLObject("frmSQLLogDialog").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK").Click()
            Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK").Click()
        except:
          Log.Warning("Не удалось запустить sql log monitor");

    def GetSqlLogData(self):
        """ Получает данные из лога sql-монитора и выводит их в логе тест комплита """
        Sys.Process("COLVIR").VCLObject("frmCssAppl").Keys("!^~l")#shift+ctrl+alt+l открываем секретное окно
        sql_log_form = Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("LB").ListItem("Лог SQL-монитора")
        sql_log_form.DblClick()
        sql_log_data = Sys.Process("COLVIR").VCLObject("frmSQLLogDialog").VCLObject("Memo").wText
        clear_btn = Sys.Process("COLVIR").VCLObject("frmSQLLogDialog").VCLObject("pnlButtons").VCLObject("btnClear")
        clear_btn.Click()
        Sys.Process("COLVIR").VCLObject("frmSQLLogDialog").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK").Click()
        Sys.Process("COLVIR").VCLObject("frmQueryDlg").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK").Click()
        Log.Message(str(sql_log_data))

    def ValidateCliCardFields(self):
        """ Валидация автоматического заполнения полей в созданной карточке клиента для коммуналки и обменника """
        self.WaitLoadWindow("frmFJCliFizDtl")
        date_reg_card = self.FindChildField("frmFJCliFizDtl", "Name", 'VCLObject("edDREG")', "internal")
        card_cli_fam = self.FindChildField("frmFJCliFizDtl", "Name", 'VCLObject("edtPNAME1")', "internal")
        card_cli_name = self.FindChildField("frmFJCliFizDtl", "Name", 'VCLObject("edtPNAME2")', "internal")
        card_cli_surname = self.FindChildField("frmFJCliFizDtl", "Name", 'VCLObject("edtPNAME3")', "internal")
        card_birthday = self.FindChildField("frmFJCliFizDtl", "Name", 'VCLObject("edtBIRDATE")', "internal")
        docs_type_card = self.FindChildField("frmFJCliFizDtl", "Name", 'VCLObject("edtPASSTYP_NAME")', "internal")
        docs_number_card = self.FindChildField("frmFJCliFizDtl", "Name", 'VCLObject("edtPASSNUM")', "internal")
        docs_date_card = self.FindChildField("frmFJCliFizDtl", "Name", 'VCLObject("edtPASSDAT")', "internal")
        docs_organ_card = self.FindChildField("frmFJCliFizDtl", "Name", 'VCLObject("edtPASSORG")', "internal")
        self.FieldValueValidator('Дата регистрации карточки', date_reg_card, 'number')
        self.FieldValueValidator('Фамилия в карточке', card_cli_fam, 'text')
        self.FieldValueValidator('Имя в карточке', card_cli_name, 'text')
        self.FieldValueValidator('Отчество в карточке', card_cli_surname, 'text')
        self.FieldValueValidator('Дата рождения в карточке', card_birthday, 'number')
        self.FieldValueValidator('Тип уд. документа в карточке', docs_type_card, 'text')
        self.FieldValueValidator('Номер уд. документа в карточке', docs_number_card, 'number')
        self.FieldValueValidator('Дата выдачи в карточке', docs_date_card, 'number')
        self.FieldValueValidator('Кем выдан в карточке', docs_organ_card, 'text')
        Sys.Process("COLVIR").VCLObject("frmFJCliFizDtl").Close()
        Log.Event("Поля карточки клиента успешно валидированы")

    def InstallInterestRate(self, id, dep_id, value_rate, type_amount):
        """ Установщик процентной ставки по видам сумм указанных во вкладке 'Суммы' договоров связанных
        с модулями GRN;LET;SLOAN;SLLOAN;DDEPO. Входные параметры: процентная ставка;
        наименование вид суммы(например: Штраф за просрочку основного долга)"""
        self.id = id
        self.dep_id = dep_id
        self.value_rate = value_rate
        self.type_amount = type_amount
        select = """ begin
        for rec in (
          select s.code from t_ARLDSC s
          where s.longname = '""" + self.type_amount + """') loop
          begin colvir.z_026_pkg_credit.set_ind_rate(""" + self.dep_id + """, """ + self.id + """,
                                                     """ + self.value_rate + """, rec.code);
          commit; end; end loop; end;
          """
        self.OracleHandlerDB(select, dml_query='True')

    def SelectClientAccount(self, id_contract, dep_id_contract):
        """ Получение текущего/клиентского счета привязанного к договору"""
        self.id_contract = id_contract
        self.dep_id_contract = dep_id_contract
        select = """ select distinct code_acc, longname
        from T_ARLDEA o, T_ARLCLC c, T_ARLDSC a, T_DEAPAYATR p
        where o.CLC_ID = c.ID
        and c.ARL_ID = a.ID
        and p.DEP_ID(+) = o.DEP_ID
        and p.ID(+) = o.ORD_ID
        and p.NORD(+) = o.PAY_NORD
        and a.NOPAYFL = '0'
        and o.DEP_ID = """ + self.dep_id_contract + """
        and o.ORD_ID = """ + self.id_contract + """ """
        result = self.OracleHandlerDB(select)
        if result is not None:
          return result[0][0]

    def GetPaymentRequisites(self, id, dep_id):
        """ Метод получение платежных реквизитов привязанных к договору,
        входной параметр ID/DEP_ID договора"""
        self.id = id
        self.dep_id = dep_id
        select = """ select substr(T_PkgPayAtr.fGetPayTypName(t.DEP_ID, t.ID, t.NORD, t.TYP_ID),
                  1,250) as LONGNAME from g_accbln g, g_accblnhst gg, ledacc l, T_DEAPAYATR t
                  where g.id = gg.id and g.dep_id = gg.dep_id
                   and trunc(sysdate) between gg.fromdate and gg.todate
                   and l.id = g.cha_id and t.id = """ + self.id + """
                   and t.dep_id = """ + self.dep_id +  """
                   and l.code like ('220%')
                   and rownum = 1
                   """
        result = self.OracleHandlerDB(select)
        if result is not None:
          return result[0][0]

    def ValueInstaller(self, dep_id, id, **dict_values):
        """ Установщик значения параметра договора. Применим для труднодоступных/скрытых параметров.
        Входные параметры: dep_id/id договора;
        словарь(где ключ = наименование параметра; значение = требуемое значение для записи).
        Производит проверку ранее установленного значения с полученным, иначе обновляет запись
        //формат передаваемого значения в словаре для datetime.date, должен быть равен dd.mm.yy"""
        self.dep_id = dep_id
        self.id = id
        self.dict_values = dict_values
        for key, value in self.dict_values.items():
          # проверим ранее установленное значение
          get_value = self.CheckSetValue(self.id, self.dep_id, key)
          if get_value != value:
            select = """ begin
            for rec in (select id, code from T_DEAPRMDSC_STD s
                       where s.longname = '""" + key + """') loop
            begin
            T_PkgDeaPrm.pSetPrmId(""" + self.id + """, """ + self.dep_id + """, rec.id, '""" + str(value) + """');
            commit; end; end loop; end;
            """
            self.OracleHandlerDB(select, dml_query='True')
          else:
            Log.Event('По параметру ' + str(key) + ' уже установлено перед-мое значение ' + str(value) + ', установка не треб-ся')

    def CheckSetValue(self, id, dep_id, name_parameter):
        """ Считывает значение параметра договора. Входные параметры: id/dep_id договора; наименование
        параметра. Выходной параметр: 1-галка(установлен признак) или вернет иное строковое значение;
        -1-отсутствует признак или отсутствует значение в параметре договора"""
        self.id = id
        self.dep_id = dep_id
        self.name_parameter = name_parameter
        select = """ select nvl(t_Pkgdeaprm.fParByCode(""" + self.id + """,""" + self.dep_id + """,s.code),-1) as value
        from T_DEAPRMDSC_STD s
        where s.longname = '""" + self.name_parameter + """'
        """
        result = self.OracleHandlerDB(select)
        if result is not None:
          Log.Event('Значение параметра ' + str(self.name_parameter) + ' равна: ' + str(result[0][0]))
          return result[0][0]

    def SelectBorrowerReplacement(self, id, dep_id, borrower, contract_number):
        """ Метод проверки параметра 'Заемщик'(проверяет изменение на договоре, где присуще данный параметр)
        входные параметры: id/dep_id договора; код клиента нового заемщика; номер договора """
        self.id = id
        self.dep_id = dep_id
        self.borrower = borrower
        self.contract_number = contract_number
        select = """ select g.code as Borrower
        from t_dea t, g_cli g
        where t.id = """ + self.id + """
        and t.dep_id = """ + self.dep_id + """
        and t.cli_dep_id = g.dep_id
        and t.cli_id = g.id """
        result = self.OracleHandlerDB(select)
        if result is not None:
          for line in result:
            if line[0].startswith(self.borrower):
              Log.Checkpoint('Успешная замена заемщика на ' + self.borrower + ' в параметре Заемщик, договора ' + self.contract_number)
            else:
              Log.Warning("Сбой, ожидался заемщик с кодом  " + self.borrower + " а получен - " + line[0] + self.contract_number)

    def SelectAccountReplacement(self, id, dep_id, borrower, contract_number):
        """ Метод проверки параметра 'Клиент'(проверяет изменение значения на самом счете в DD7) по привязанным счетам
        (за исключением счета 7339) договора, применим в модулях GRN/LET/SLLOAN/SLOAN
        входные параметры: id/dep_id договора; код клиента нового Клиента; номер договора"""
        self.id = id
        self.dep_id = dep_id
        self.borrower = borrower
        self.contract_number = contract_number
        date_statusbar = Sys.Process("COLVIR").VCLObject("frmCssAppl").VCLObject("StatusBar").wText[2]
        select = """ select g.code as Account, ag.code as Borrower
        from g_accbln g, g_accblnhst gg, g_cli ag, ledacc_det l
        where g.id = gg.id
        and g.dep_id = gg.dep_id
        and to_date('""" + date_statusbar + """')
        between gg.fromdate and gg.todate
        and gg.clidep_id = ag.dep_id
        and gg.cli_id = ag.id
        and g.cha_id != '41979'
        and g.id = l.acc_id
        and g.dep_id = l.dep_id
        and l.pk2 = """ + self.id + """
        and l.pk1 = """ + self.dep_id + """
        """
        result = self.OracleHandlerDB(select)
        if result is not None:
          for line in result:
            if line[1].startswith(self.borrower):
              Log.Checkpoint('Успешная замена заемщика на ' + self.borrower + ' по привязанным счетам договора ' + self.contract_number)
            else:
              Log.Warning("Сбой, по привязанному счету: " + line[0] + ' не произведена замена заемщика на ' + self.borrower + ' договора ' + self.contract_number)

    def GetRateContract(self, window_name, view_amount, wnd_name):
        """ Метод получение процентной ставки по виду сумм из вкладки 'Сумма'"""
        self.window_name = window_name
        self.view_amount = view_amount
        self.wnd_name = wnd_name
        btn_wnd = Sys.Process("COLVIR").VCLObject(self.window_name).VCLObject("btnBrowse")
        btn_wnd.Click()
        self.WaitLoadWindow(self.wnd_name, time_await=300000)
        amount_tab = self.FindChildField(self.wnd_name, "Name", "PageTab('Суммы')")
        amount_tab.Click()
        call_amont_value = self.FindChildField(self.wnd_name, "Name", 'VCLObject("grArl")')
        call_amont_value.Click(10,10)
        for _ in range(8):
          amount_value = self.GetGridDataFields(self.wnd_name, "LONGNAME", "PCN", need_tab='qryArl')
          if amount_value[0].replace("\'", '') == self.view_amount.replace(' ', ''):
            rate = amount_value[1].replace("\'", '')
            break
          LLPlayer.KeyDown(VK_DOWN, 3) # нажатие стрелки вниз
          LLPlayer.KeyUp(VK_DOWN, 3)
        Sys.Process("COLVIR").VCLObject(self.wnd_name).Close()
        return float(rate)

    def CheckAccountReserve(self, dep_contract, id_contract):
        """ Проверка корректного открытие счетов провизии (1428) с наличием признака Без/C контроля/ем остатка"""
        self.dep_contract = dep_contract
        self.id_contract = id_contract
        # скрипт выгружает привязанные счета провизии с наличием признака в аналитике Z_026_PROVACCTYPE
        select = """ select
        GL_ANL.FACCANLVALUE(g.DEP_ID, g.ID, 'Z_026_PROVACCTYPE') as ANLACRESULT,
        g.anybalfl as ODPERRESULT,
        ll.code as ODRESULT
        from ledacc_det l, t_acc g, ledacc ll
        where l.PK1 = """ + self.dep_contract + """
        and l.PK2 = """ + self.id_contract +"""
        and l.dep_id = g.dep_id
        and l.acc_id = g.id
        and l.ch_id = ll.id
        and ll.id_hi = 49967
        """
        result = self.OracleHandlerDB(select)
        for line in result:
          if line[0] == '0' and int(line[1]) == 1 and line[2] != 0:
            Log.Checkpoint("Счет провизий по основному долгу с признаком 'Без контроля остатка' открыт")
          elif line[0] == '1' and int(line[1]) == 1 and line[2] != 0:
            Log.Checkpoint("Счет провизий по процентам с признаком 'Без контроля остатка' открыт")
          else:
            Log.Warning('Сбой, при открытии счетов провизий')

    def SelectCloseAccount(self, id, dep_id, state):
        """ Метод проверки закрытие счетов. Входные параметры: id/dep_id договора; состояние
        Добавил исключение счета 2860 в рамках ЗНР 5870"""
        self.dep_id = dep_id
        self.id = id
        self.state = state
        select = """ select distinct g.code as ACCOUNT,
        T_PkgRunOprUtl.fGetStatNameByMainOrd(g.DEP_ID,g.ORD_ID) STATE_NAME
        from LEDACC_DET d, T_ACC a, g_accbln g, g_accblnhst gg, ledacc l
        where d.DEP_ID = a.DEP_ID and d.ACC_ID = a.ID
        and d.SGN_ID = T_ASGN.fCode2Id(nvl('DEA','DEA'))
        and a.id = g.id and a.dep_id = g.dep_id
        and g.id = gg.id and g.dep_id = gg.dep_id
        and gg.cha_id = l.id
        and substr(l.code,1,4) not in ('2860','6126','6626')
        and d.PK1 = to_char(""" + self.dep_id + """) and d.PK2 = to_char(""" + self.id + """)
        """
        result = self.OracleHandlerDB(select)
        for line in result:
          if line[1].startswith(self.state):
            Log.Checkpoint('Привязанные счета ' + line[0] + ' успешно переведены в состояние ' + self.state)
          else:
            Log.Warning("Ожидался статус " + self.state + " а получен - " + line[1] + " по счету " + line[0])

    def CheckGrafikContract(self, contract_number, id, dep_id):
        """ Проверка формирование графика на наличие нулевых сумм /- автотест Credit_RachetGrafic"""
        self.contract_number = contract_number
        self.id = id
        self.dep_id = dep_id
        select = """ select s.AMOUNT / POWER(10, T_PkgVal.fGetFac(1)) as AMOUNT
        from tt_point p, T_DEASHDPNT s, T_ARLCLC c
        where p.ID = s.TT_ID
        and p.NORD = s.TT_NORD
        and s.ord_id = """  + self.id + """
        and s.dep_id = """  + self.dep_id + """
        and s.CLC_ID = c.ID
        and c.arl_id not in ('585','3304','1681','1161','3596')
        """
        result = self.OracleHandlerDB(select)
        for line in result:
          if line[0] == 0:
            Log.Warning("Ошибка формирования графика, сумма платежа равна нулю " + str(self.contract_number))

    def CheckNumberPayments(self, dog_num, id_dog, dep_id, count_plat):
        """ Проверка формирование количество платежей /- автотест Credit_RachetGrafic"""
        self.dog_num = dog_num
        self.id_dog = id_dog
        self.dep_id_ssafe = dep_id
        self.count_plat = count_plat
        select = """ select count(d.longname) as count
        from T_DEASHDPNT s, T_ARLCLC c, T_ARLDSC d
        where s.CLC_ID = c.ID
        and s.ord_id = """  + self.id_dog + """
        and s.dep_id = """  + self.dep_id + """
        and c.ARL_ID = d.ID
        """
        result = self.OracleHandlerDB(select)
        for line in result:
          if int(line[0]) != int(self.count_plat):
            Log.Event(str(int(line[0])))
            Log.Event(str(self.count_plat))
            Log.Warning("Сбой, неправильное количество платежей " + str(self.dog_num))

    def SelectContractSchedule(self, dep_id, id_number):
        """ Получение даты текущего/планового платежа по графику, применим в модулях GRN//SLLOAN/SLOAN.
        входные параметры: id/dep_id договора"""
        self.id_number = id_number
        self.dep_id = dep_id
        select = """ select s.doper
        FROM T_DEASHDPNT S, TT_POINT P
        WHERE S.TT_ID = P.ID
        AND S.TT_NORD = P.NORD
        AND P.REALDATE IS NULL
        AND S.DEP_ID = """ + self.dep_id + """
        AND S.ORD_ID = """ + self.id_number + """
        AND ROWNUM = 1 """
        result = self.OracleHandlerDB(select)
        for daff in result:
          return (aqConvert.DateTimeToFormatStr(daff[0], "%d.%m.%y"))

    def GetAllTransaction(self):
        """ Оптимизированный метод получение балансовых проводок (выгрузит все что надо)"""
        self.WaitLoadWindow('frmOperJournal')
        jornal_field = self.GetGridDataFields("frmOperJournal", "TRA_ID", "ID", "NJRN", "NAMEOPRMOV")
        if jornal_field[0].replace("\'", ''):
          select = """ select distinct(id) as ID from table
          (financial_transac.get_findoc(""" + jornal_field[0] + """, """ + jornal_field[1] + """,
                                                                   """ + jornal_field[2] + """))
          """
          result = self.OracleHandlerDB(select)
          account_list = []
          for value in result:
            value_acc = self.StaticSelectFinancialTransation(tra_id=value[0])
            account_list.extend(value_acc)
          Log.Message('Итоговый результат сформированных счетов ' + str(account_list))
        else:
          Log.Warning('Отсутствует TRA_ID для выгрузки счетов по записи ' + str(jornal_field[3]))
        return account_list

    def CheckValueField(self, wnd_name, field_name, **field_val):
        """ Проверка поля на соответствие контрольному значению.
        Входные параметры: имя окна для поиска поля, название поля для отражения в лог, словарь -
        имя поля для поиска через FindChildField и контрольное значение """
        self.wnd_name = wnd_name
        self.field_name = field_name
        self.field_val = field_val
        for field_code, check_value in self.field_val.items():
          field = self.FindChildField(self.wnd_name, "Name", field_code)
          if 'CheckBox' in field.WndClass:
            Log.Message('Значение проверяемого чекбокса ' + str(field.wState))
            Log.Message('Контрольное значение ' + str(check_value))
            if str(field.wState) == str(check_value):
              Log.Event('Значение проверяемого чекбокса "' + self.field_name + '" совпадает с контрольным')
            else:
              Log.Warning('Значение проверяемого чекбокса "' + self.field_name + '" не совпадает с контрольным')
          else:
            Log.Message('Значение проверяемого поля ' + str(field.Child(0).Value))
            Log.Message('Контрольное значение ' + str(check_value))
            if str(field.Child(0).Value.replace('_', '').strip()) is not None and str(field.Child(0).Value.replace('_', '').strip()):
              if str(check_value.strip()) is not None and str(check_value.strip()):
                if str(field.Child(0).Value.replace('_', '').strip()) == str(check_value.strip()):
                  Log.Event('Значение проверяемого поля "' + self.field_name + '" совпадает с контрольным')
                else:
                  Log.Warning('Значение проверяемого поля "' + self.field_name + '" не совпадает с контрольным')
              else:
                Log.Warning('Отсутствует значение проверяемого поля ' + str((self.field_name)))
            else:
              Log.Warning('Отсутствует значение проверяемого поля ' + str((self.field_val)))

    def SimpleConvertDate(self, date, need_format):
        """ Простое конвертирование строковой даты в datetime и
        обратно в строку по необходимому формату, с помощью встроенных методов
        Testcomplete так как стандатрные Python методы работы с датой работаю в данном ПО
        некорректно """
        self.date = date
        self.need_format = need_format
        convert_date = aqConvert.DateTimeToFormatStr(aqConvert.StrToDate(self.date), self.need_format)
        Log.Message('Сконвертированная дата ' + str(convert_date))
        return convert_date

    def FindNeedDocGrids(self, range_number, wnd_name, **need_fields):
        """ Поиск необходимого документа в окне по филдам """
        self.range_number = range_number
        self.wnd_name = wnd_name
        self.need_fields = need_fields
        all_keys = []
        all_values = []
        state = False
        for keys, values in self.need_fields.items():
          all_keys.append(keys)
          all_values.append(values)
        for _ in range(self.range_number):
          finder = self.GetGridDataFields(self.wnd_name, *all_keys)
          Log.Message("Список из гридов " + str(finder))
          Log.Message("Список из контрольных значений " +str(all_values))
          result = all(list1_item.replace('"', '').replace('\'', '') == list2_item.replace('"', '').replace('\'', '') for list1_item, list2_item in zip(finder, all_values))
          if result:
            state = True
            break
          self.LLPKeys(VK_DOWN)
        return state

    def CheckStatesSums(self, dep_id, id, date, state, contract_number):
        """ Обработчик выставленных сумм во вкладке 'Сумма к оплате и получению' договора,
        входной параметр: ID/DEP_ID договора, дата, состояние (пример: Оплачен)"""
        self.dep_id = dep_id
        self.id = id
        self.date = date
        self.state = state
        self.contract_number = contract_number
        select = """ select a.LONGNAME as vidsumm, s.name state
                    from T_DEAPAY   dp, t_procmem  m,
                         t_process  p, t_bop_stat s,
                         T_ARLCLC   c, T_ARLDSC   a
                   where dp.DEP_ID = """ + self.dep_id + """
                     and dp.DEA_ID = """ + self.id + """
                     and dp.dcalc = '""" + self.date + """'
                     and dp.dep_id = m.dep_id
                     and dp.id = m.ord_id
                     and m.mainfl = 1
                     and p.ID = m.ID
                     and p.ID = m.ID
                     and s.ID = p.BOP_ID
                     and s.NORD = p.NSTAT
                     and c.ID = dp.CLC_ID
                     and a.ID = c.ARL_ID
                   order by s.name
                   """
        result = self.OracleHandlerDB(select)
        result_list = []
        if result is not None:
          for line in result:
            result_list.append(line[1])
            if line[1].startswith(self.state):
              Log.Checkpoint('Выставленные суммы во вкладке Сумма к оплате и получению ' + line[0] + ' успешно переведены в состояние ' + self.state + " " + self.contract_number)
            else:
              Log.Warning("Ожидался статус " + self.state + " во вкладке Сумма к оплате и получению, а получен - " + line[1] + " " + self.contract_number)
        return result_list

    def OracleHandlerDB(self, db_query, dml_query=None, need_zero=None, cap_query=None, bind_name = None, need_dict = None):
        """ Работа с БД оракл через библиотеку python и оракл клиент без драйвера ODAC
        Соединение по tns string из конфига, умеет работать с различными типами данных в БД.
        Необходимо чтобы был установлен python и его разрядность была одинаковой с TestComplete.
        Расположение python библиотек должно быть указано в переменной среде PYTHON.
        Версия python должна быть >=3.6.0 и 3.6.4 <=
        Возвращает результат в виде списка с кортежами, каждый кортеж строка результата.
        Даты возвращаются в datetime формате если в таблице они хранятся типом date.
        Ключ dml_query для запросов, которые не возвращают значений INSERT, UPDATE, DELETE.
        Ключ need_zero для запросов, которые ожидаемо не должны вернуть значений.
        Ключ cap_query для запросов в БД CAP
        Ключ need_dict вернет результат в виде списка со словарями {'Имя столбца':'Значение'}
        В параметр bind_name можно передать значения для подстановки в тело запроса:
         bind_name = dict(my_id='280', my_dep_id= '123456') или bind_name = ['280','123456']
         db_query = 'select * from table where id = :my_id and dep_id = :my_dep_id'
        """
        self.db_query = db_query
        self.need_zero = need_zero
        self.dml_query = dml_query
        self.cap_query = cap_query
        result = None
        server_db,port_db,name_db = self.GetConnString()
        login, password = self.GetLoginPassAdm()
        if self.cap_query is not None:
         login, password, alias_db_cap, get_alias = self.GetCAPConnectInfo()
         name_db = alias_db_cap
         Log.Message(name_db)
         port_db = '1521' # меняем порт для базы капа
        try:
         dsn = cx_Oracle.makedsn(server_db, port_db, service_name=name_db) #'cbs3bt'
         connection = cx_Oracle.connect(user=login, password=password, dsn=dsn, encoding="UTF-8")
         mycursor = connection.cursor()
         Log.AppendFolder("Запрос в БД")
         Log.Message(self.db_query) # отладочный лог готового запроса
         if bind_name is not None:
           Log.Message(f'bind_name = {bind_name}')
         Log.PopLogFolder()
         try:
           if self.cap_query is None:
             mycursor.execute("""begin c_pkgconnect.popen(); end;""")
           if bind_name is None:
             mycursor.execute(self.db_query)
           else:
             mycursor.execute(self.db_query,bind_name)
           if self.dml_query is None:
             result = mycursor.fetchall()
             if need_dict is not None:
               keys = [col[0] for col in mycursor.description]
               Log.Message(f'Имена столбцов: {keys}')
               for row in range(len(result)):
                 result[row] = {k:v for k,v in zip(keys,result[row])}
             if not result and self.need_zero is not None:
                 Log.Message('Запрос ожидаемо не вернул ни одной строки')
                 result = None
             elif not result:
                 Log.Warning('Запрос не вернул ни одной строки')
                 result = None
           else:
             Log.Message('Запрос на модификацию данных отработал успешно')
         except cx_Oracle.DatabaseError as exc:
           error, = exc.args
           if str(error.code) == "ORA-00001":
              Log.Warning(f"Нарушено ограничение уникальности - {str(error.message)}")
           else:
              Log.Warning("OracleDB Error Message: " + str(error.message))
         connection.close()
        except cx_Oracle.DatabaseError as exc:
         error, = exc.args
         Log.Warning("OracleDB Connection Error Message: " + str(error.message))
        # отладочные строки вывода в лог на время переезда
        if result is not None:
         Log.AppendFolder("Ответ на запрос в БД")
         Log.Message(str(result)) # отладочный лог готового запроса
         Log.PopLogFolder()
        return result

    def OracleFunctionExecute(self, name_function, return_type_variable, *params, cap_query=None):
        """ Запуск функции с параметрами через запрос в БД,
          имя функции нужно передавать полностью, пример: t_pkgval.fvalcode2id;
          return_type_variable тип возвращаемой переменной, int, float, str и тд;
          params обязательные параметры, которые необходимо передать для запуска функции,
          необходимо соблюдать порядок параметров"""
        self.name_function = name_function
        self.return_type_variable = return_type_variable
        self.params = params
        self.cap_query = cap_query
        server_db,port_db,name_db = self.GetConnString()
        login, password = self.GetLoginPassAdm()
        if self.cap_query is not None:
          login, password, alias_db_cap, get_alias = self.GetCAPConnectInfo()
          name_db = alias_db_cap
          port_db = '1521' # меняем порт для базы капа
        return_data_function = None
        try:
          dsn = cx_Oracle.makedsn(server_db, port_db, service_name=name_db)
          connection = cx_Oracle.connect(user=login, password=password, dsn=dsn, encoding="UTF-8")
          mycursor = connection.cursor()
          for iter in range(len(self.params)):
              if isinstance(self.params[iter], type):
                  self.params[iter] = cursor.var(self.params[iter])  # Преобразует Python Type в Oracle Type
          Log.AppendFolder("Запрос в БД на запуск функции " + self.name_function)
          Log.Message('Вызов функции ' + self.name_function + ' с параметрами ' + str(self.params))
          Log.PopLogFolder()
          mycursor.execute("""begin c_pkgconnect.popen(); end;""")
          return_data_function = mycursor.callfunc(self.name_function, self.return_type_variable, self.params)
          if not return_data_function or return_data_function is None:
            Log.Warning('Запрос на запуск функции не вернул ни одной строки')
          connection.close()
        except cx_Oracle.DatabaseError as exc:
          error, = exc.args
          Log.Warning("OracleDB Error Code: " + str(error.code))
          Log.Warning("OracleDB Error Message: " + str(error.message))
        if return_data_function is not None:
          Log.AppendFolder("Ответ на запрос в БД к функции " + self.name_function)
          Log.Message(str(return_data_function)) # отладочный лог готового ответа
          Log.PopLogFolder()
        return return_data_function

    def OracleCallProcedure(self, name_procedure, *params, return_value = False, num_out = None):
        """ Выполнение процедуры в БД Oracle. Если не передавать параметр return_value, то процедура не будет ничего возвращать.
            Если передать параметр return_value = True, то процедура будет возвращать данные. Каждый элемент вывода, это список, который содержится в общем списке.
            В num_out передается номер вывода. Пример: '1out'.
            В *params передается параметры передаваемые в процедуру. Каждый параметр в отдельной строке через запятую.
            В name_procedure передается название процедуры в строке.
           """
        self.name_procedure = name_procedure
        self.params = list(params)
        self.return_value = return_value
        self.num_out = num_out
        value_output_list = []
        server_db,port_db,name_db = self.GetConnString()
        login, password = self.GetLoginPassAdm()
        try:
          dsn = cx_Oracle.makedsn(server_db, port_db, service_name=name_db) #'cbs3bt'
          connection = cx_Oracle.connect(user=login, password=password, dsn=dsn, encoding="UTF-8")
          cursor = connection.cursor()
          for iter in range(len(self.params)):
            if isinstance(self.params[iter], type):
              self.params[iter] = cursor.var(self.params[iter])  # Преобразует Python Type в Oracle Type
          Log.AppendFolder("Запрос в БД на запуск процедуры " + self.name_procedure)
          Log.Message('Вызов процедуры ' + self.name_procedure + ' с параметрами ' + str(self.params))
          Log.PopLogFolder()
          try:
            cursor.execute("""begin c_pkgconnect.popen(); end;""")
            cursor.callproc("dbms_output.enable")
            cursor.callproc(self.name_procedure, self.params)
            if self.return_value == True:
                statusVar = cursor.var(cx_Oracle.NUMBER)
                lineVar = cursor.var(cx_Oracle.STRING)
                # Получаем выходные параметры процедуры
                while True:
                    cursor.callproc("dbms_output.get_line", (lineVar, statusVar))
                    if statusVar.getvalue() != 0:
                      break
                    output_value = lineVar.getvalue()
                count_out = 0
                list_value = output_value.split(';') # Делаем список выходных параметров из строки
                # Передаем номер вывода. Проверяем, что номер есть и присваиваем значение данного номера вывода
                if self.num_out is not None:
                    for i in range(len(self.num_out)):
                        for row in list_value:
                            if f'{self.num_out[i]}out' in row:
                                acc_output = str(row)
                                list_acc_out = acc_output.split('->')
                                value_output_list.append(list_acc_out)
                                Log.Event(f'На вывод добавлен - {list_acc_out}')
                                break
                            else:
                                count_out += 1
                        if count_out == len(list_value):
                            Log.Warning(f'Номер вывода {self.num_out[i]} не найден в списке')
                        count_out = 0
                else:
                    Log.Warning(f'{self.num_out} содержит пустой список')
          except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            Log.Warning("OracleDB Error Message: " + str(error.message))
          cursor.close()
          connection.close()
        except cx_Oracle.DatabaseError as exc:
          error, = exc.args
          Log.Warning("OracleDB Connection Error Message: " + str(error.message))
        if value_output_list is not None:
          Log.AppendFolder("Ответ на запрос в БД к процедуре " + self.name_procedure)
          Log.Message(list(value_output_list)) # отладочный лог готового ответа
          Log.PopLogFolder()
        return value_output_list

    def OracleProcedureExecute(self, name_procedure, cap_query=None, *params):
        """ Запуск процедуры с параметрами через запрос в БД,
          имя процедуры нужно передавать полностью, пример: t_pkgval.fvalcode2id;
          return_type_variable тип возвращаемой переменной, int, float, str и тд;
          params обязательные параметры, которые необходимо передать для запуска процедуры,
          необходимо соблюдать порядок параметров. Для выходных или пустых параметров необходимо указывать их
          тип int, float, str и тд"""
        self.name_procedure = name_procedure
        self.params = list(params)
        self.cap_query = cap_query
        return_data_proc = None
        server_db,port_db,name_db = self.GetConnString()
        login, password = self.GetLoginPassAdm()
        if self.cap_query is not None:
          login, password, alias_db_cap, get_alias = self.GetCAPConnectInfo()
          name_db = alias_db_cap
          port_db = '1521' # меняем порт для базы капа
        try:
          dsn = cx_Oracle.makedsn(server_db, port_db, service_name=name_db)
          connection = cx_Oracle.connect(user=login, password=password, dsn=dsn, encoding="UTF-8")
          mycursor = connection.cursor()
          for iter in range(len(self.params)):
            if isinstance(self.params[iter], type):
              self.params[iter] = mycursor.var(self.params[iter])  # Преобразует Python Type в Oracle Type
          Log.AppendFolder("Запрос в БД на запуск процедуры " + self.name_procedure)
          Log.Message('Вызов процедуры ' + self.name_procedure + ' с параметрами ' + str(self.params))
          Log.PopLogFolder()
          try:
            mycursor.execute("""begin c_pkgconnect.popen(); end;""")
            return_data_proc = mycursor.callproc(self.name_procedure, self.params)
            if not return_data_proc or return_data_proc is None:
              Log.Warning('Запрос на запуск процедуры не вернул ни одной строки')
          except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            Log.Warning("OracleDB Error Message: " + str(error.message))
          connection.close()
        except cx_Oracle.DatabaseError as exc:
          error, = exc.args
          Log.Warning("OracleDB Connection Error Message: " + str(error.message))
        if return_data_proc is not None:
          Log.AppendFolder("Ответ на запрос в БД к процедуре " + self.name_procedure)
          Log.Message(str(return_data_proc)) # отладочный лог готового ответа
          Log.PopLogFolder()
        return return_data_proc

    def CheckOperationExecution(self, id, dep_id, longname_operation):
        """ Метод проверки выполнение операции в журнале операции договора
        входные параметры - id/dep_id договора + наименование операции
        метод вернет код операции в случае если операция была уже выполнена, иначе нуль """
        self.id = id
        self.dep_id = dep_id
        self.longname_operation = longname_operation
        sql_run = """ select nvl(bs_operation.fOprCount(p.id, '""" + self.longname_operation +  """'), '0') as scen_code
            from t_ord Z, T_PROCMEM M, T_PROCESS P
             WHERE Z.DEP_ID = M.DEP_ID AND Z.ID = M.ORD_ID
             AND P.ID = M.ID  AND M.MAINFL = '1'
             and z.DEP_ID = """ + self.dep_id + """  and z.ID = """ + self.id + """
             """
        result = self.OracleHandlerDB(sql_run)
        if result is not None:
          return str(result[0][0])

    def ReadingValueForm(self, dep_account, ord_account, longname_value):
        """ Считывает значение из динамической формы документа(атрибуты)(пример доп.атрибуты счета).
        Входные параметры: dep_id/ord_id документа;наименование атрибута.
        Выходной параметр: 1-галка(установлен признак) или вернет иное строковое значение;
        (-1)не найден счет и его доп.атрибуты
        (0)-значение в атрибуте пусто"""
        self.dep_account = dep_account
        self.ord_account = ord_account
        self.longname_value = longname_value
        select = """ select NVL(t_pkgform.fGetById(""" + self.dep_account + """, """ + self.ord_account + """,t.id),-1) AS value
                                from t_frmatr_std t
                                where t.longname = '""" + str(self.longname_value) + """'
                                """
        result = self.OracleHandlerDB(select)
        for column in result:
          Log.Event('Значение параметра ' + str(self.longname_value) + ' равна: ' + str(column[0]))
          return column[0]

    def AttributeInstaller(self, dep_account, ord_account, **dict_value_attribute):
        """ Установщик значение в динамическую форму документа(атрибуты)(пример доп.атрибуты счета).
        Входные параметры: dep_id/ord_id договора; словарь(где ключ = наименование атрибута;
        значение = требуемое значение для записи).
        Производит проверку ранее установленного значение с полученным, иначе обновляет запись
        //формат передаваемого значения в словаре для datetime.date, должен быть равен dd.mm.yy"""
        self.dep_account = dep_account
        self.ord_account = ord_account
        self.dict_value_attribute = dict_value_attribute
        for key, value in self.dict_value_attribute.items():
          # проверим ранее установленное значение
          get_value = self.ReadingValueForm(self.dep_account, self.ord_account, key)
          if get_value != value:
            query = """ begin
            for rec in (select id, code from t_frmatr_std s
                       where s.longname = '""" + key + """') loop
            begin
            t_pkgform.pSetById(""" + self.dep_account + """, """ + self.ord_account + """, rec.id, '""" + str(value) + """');
            commit; end; end loop; end;
            """
            self.OracleHandlerDB(query, dml_query='True')
          else:
            Log.Event('По атрибуту ' + str(key) + ' уже установлено перед-мое значение ' + str(value) + ', установка не треб-ся')

    def GetActualDogNumber(self, product_code):
        """ Метод выгрузки рандомного/случайного номера договора в состоянии 'Актуален'
        входной параметр: код продукта из датасет, выгружает по истинно случайным договорам фл/юл лиц"""
        self.product_code = product_code
        select = """ select * from (select o.code
              from t_ord o, t_dea t, t_deacls tt, T_BOP_STAT, T_PROCESS, T_PROCMEM
             where t.id = o.id
               and t.dep_id = o.dep_id
               and t.dcl_id = tt.id
               and tt.code = '""" + self.product_code + """'
               and T_PROCMEM.MAINFL = '1'
               and T_PROCMEM.DEP_ID = o.dep_id
               and T_PROCMEM.ORD_ID = o.id
               and T_PROCESS.ID = T_PROCMEM.ID
               and T_BOP_STAT.ID = T_PROCESS.BOP_ID
               and T_BOP_STAT.NORD = T_PROCESS.NSTAT
               and T_PKGRUNOPRUTL.fGetStatNameByMainOrd(o.dep_id, o.id) = 'Актуален'
               and t.todate > trunc(sysdate)
               and rownum < 500 order by dbms_random.value) where rownum = 1
               """
        result = self.OracleHandlerDB(select)
        return result[0][0]

    def GetParamsValue(self, code_param, multiparam_alias=None):
        """ Получение значения системного параметра через запрос к бд по коду, включания вложенные параметры.
        Входные данные:
        code_param - код необходимого параметра,
        multiparam_alias - для вложенных параметров с одинаковым кодом, можно плучать
        необходимую инфу по внутреннему полю настройки из поля DET_CODE
        Выходные данные:
        значение параметра"""
        self.code_param = code_param
        self.multiparam_alias = multiparam_alias
        value = None
        select = """ select * from (select p.code, '' as det_code,
         substr(decode(C_fPrm(p.code), null, '', C_fPrm(p.code)), 1,9999999) CommVal
           from c_prmcls p
           where CODE = '""" + self.code_param +"""'
           union all
           select  p.code,NVL(pv.dep_code, pv.user_code) as det_code,
           substr(decode(C_fPrm(p.code,decode(depfl, 1, pv.dep_id, 0),decode(tusfl, 1, pv.tus_id, 0)),
               null,'',C_fPrm(p.code,decode(depfl, 1, pv.dep_id, 0),decode(tusfl, 1, pv.tus_id, 0))),1,9999999) CommVal
               from cv_prmval pv, c_prmcls p
               where pv.prm_id = p.id and CODE = '""" + self.code_param +"""' and nord =
                 (select max(cpv.nord)
                    from c_prmval cpv
                    where cpv.prm_id = p.id
                    and ((pv.tus_id is not null and cpv.tus_id = pv.tus_id) or
                    (pv.dep_id is not null and cpv.dep_id = pv.dep_id)))) P"""
        result = self.OracleHandlerDB(select)
        if self.multiparam_alias is not None and result is not None:
          for lines in result:
            if lines[1] == self.multiparam_alias:
              value = lines[2]
              break
          Log.Message('Системный параметр ' + str(self.code_param) + ' равен ' + str(value))
        elif result is not None and result[0][2] is None:
          value = 'Empty'
          Log.Message('Системный параметр ' + str(self.code_param) + ' пуст')
        elif result is not None:
          value = result[0][2]
          Log.Message('Системный параметр ' + str(self.code_param) + ' равен ' + str(value))
        return value

    def CheckAccCliPSBlocks(self, cli_code=None, cli_iin=None):
        """ Проверка текущих счетов клиента на принадлежность к ПС или АБИС
        по коду карточки клиента или ИИН в карточке.
        Все текущие счета клиента должны либо целиком обслуживаться в ПС либо в АБИС,
        для корректного расчета прожиточного минимума по К2.
        Также проверит счета на выставленные блокировки, лимиты и картотеку и выведет остаток"""
        self.cli_code = cli_code
        self.cli_iin = cli_iin
        date_operday = self.GetEnviron("DATE_OPERDAY")
        if self.cli_code is not None:
          check_part = """  from (select '""" + self.cli_code +"""' code from dual) d
                            left join g_cli g
                              on g.code = d.code
                            left join g_clihst gg
                              on g.id = gg.id
                             and g.dep_id = gg.dep_id
                             and '""" + date_operday +"""' between gg.fromdate and gg.todate """
        elif self.cli_iin is not None:
          check_part = """ from (select '""" + self.cli_iin +"""' taxcode from dual) d
                          left join g_clihst gg
                            on gg.taxcode = d.taxcode
                           and '""" + date_operday +"""'  between gg.fromdate and gg.todate
                          left join g_cli g
                            on g.id = gg.id
                           and g.dep_id = gg.dep_id """

        select = """ select a.code as ACC_NUM, l.code as mask, a.capfl """ + check_part + \
                 """ left join g_accblnhst ag
                      on ag.cli_id = gg.id
                     and ag.clidep_id = gg.dep_id
                     and '""" + date_operday +"""' between ag.fromdate and ag.todate
                     and ag.arcfl = '0'
                    left join g_accbln a
                      on a.id = ag.id
                     and a.dep_id = ag.dep_id
                    left join ledacc_std l
                      on a.cha_id = l.id """

        result = self.OracleHandlerDB(select)
        get_mask_crd = self.GetCrd2AccMask()
        if not get_mask_crd:
          get_mask_crd = ['2204','2203','2206']
        current_acc = []
        if result is not None:
          for lines in result:
            Log.Message('Счет клиента  ' + str(lines))
            if str(lines[1]).startswith('2204') or str(lines[1]).startswith('2203'):
              current_acc.append(lines)
        # проверка на обслуживание в ПС или АБИС
        if current_acc:
          res = (all(int(line[2]) == 0 for line in current_acc)) or (all(int(line[2]) == 1 for line in current_acc))
          if res and int(current_acc[0][2]) == 1:
            Log.Checkpoint('Все текущие счета клиента обслуживаются в ПС')
              # остатки, блоки, аресты, лимиты, к2
            for acc in current_acc:
              acc_full_info = self.GetAccountInfo(acc[0], 'True')
              Log.Message(str(acc_full_info), str(acc_full_info))
          elif res and int(current_acc[0][2]) == 0:
            Log.Checkpoint('Все текущие счета клиента обслуживаются в АБИС')
              # остатки, блоки, аресты, лимиты, к2
            for acc in current_acc:
              acc_full_info = self.GetAccountInfo(acc[0], 'True')
              Log.Message(str(acc_full_info), str(acc_full_info))
          else:
            Log.Warning('Текущие счета клиента частично обслуживаются в ПС и АБИС, необходимо перевести' + \
            ' все текущие счета на обслуживание в ПС или АБИС для корректного расчета ПМ в К2')
        return current_acc

    def GetCrd2AccMask(self):
        """ Получение всех масок счетов и их приоритеты для оплаты к2 и автооплаты к2"""
        select = """ select code_acc, priority, val_acc from S_ACCPAYCRD2 """
        result = self.OracleHandlerDB(select)
        mask_acc = []
        if result is not None:
          for lines in result:
            mask_acc.append(lines[0].replace('%', ''))
          Log.Message('ОТЛАДКА ' + str(mask_acc))
        return mask_acc, result

    def GetAllCliCardsIIN(self, cli_iin):
        """ Получение всех открытых карточек клиента по ИИН"""
        self.cli_iin = cli_iin
        date_operday = self.GetEnviron("DATE_OPERDAY")
        select = """
        select G_CLI.CODE, G_CLIHST.TAXCODE, S.NAME as STATE
        from G_CLI, G_CLIHST, C_DEP, G_ECNDSC, T_PROCMEM M, T_PROCESS P, T_BOP_STAT S
        where G_CLIHST.DEP_ID = G_CLI.DEP_ID and G_CLIHST.ID = G_CLI.ID
          and '""" + date_operday +"""' between G_CLIHST.FROMDATE and G_CLIHST.TODATE
          and M.ORD_ID = G_CLI.ORD_ID
          and M.DEP_ID = G_CLI.DEP_ID
          and M.MAINFL = '1'
          and P.ID = M.ID
          and S.ID = P.BOP_ID
          and S.NORD = P.NSTAT
          and C_DEP.ID = G_CLI.DEP_ID
          and G_CLIHST.SHI_ID = G_ECNDSC.ID(+)
          and S.NAME = 'Карточка открыта'
           and G_CLIHST.TAXCODE = '""" + self.cli_iin +"""'
        """
        result = self.OracleHandlerDB(select)
        cli_card = []
        if result is not None:
          for lines in result:
            Log.Message('Найденные карточки по ИИН ' + str(lines))
            cli_card.append(lines[0])
        return cli_card

    def GetSolutionTable(self, code_table):
        """ По коду ТР возвращает список со словарями, где в каждом словаре содержится строка из ТР.
        Реализовано через запрос к бд. На выходе получаем:
        [{'solution':'value','col_1_name':'val_1_name',...,'col_n_name':'val_n_name'}]
        solution - это решение по строке ТР, col_1_name - название столбца ТР, val_1_name - значение столбца.
        Если ТР пуста вернется пустой список, если ТР по коду не найдена вернется None.
        Пустые значения решения или столбцов вернутся как None"""
        self.code_table = code_table
        # Получаем номера и названия столбцов из ТР
        select = """ select c.code,to_char(c.nord)
              from C_TBLCOL c
              where c.id =(select id  from  C_DECTBL_STD cd
              where  cd.code = '""" + self.code_table + """') order by c.nord desc """
        cols = self.OracleHandlerDB(select)
        # Формируем строку для второго select
        str_cols = ''
        if cols is not None:
          for row in cols:
            if str_cols:
              str_cols = str_cols + ",'" + row[0] + "'"
            else:
              str_cols = "'" + row[0] + "'"
          select = """ SELECT * FROM
              ( SELECT nord,nord_col,ex_value,solution
                FROM ( select c.nord,t.code nord_col,c.ex_value,ctr.solution
                from   c_tblval c,C_TBLROW ctr, C_TBLCOL t
                where c.id = ( select id  from  C_DECTBL_STD cd   where  cd.code = '""" + self.code_table + """')
                and c.nord = ctr.nord
                and c.id = ctr.id
                and t.nord = c.nord_col
                and c.id = t.id ) ) PIVOT(  max(ex_value)  FOR nord_col IN  (""" + str_cols + """)) """
          result = self.OracleHandlerDB(select)
          result_list = []
          if result is not None:
            for row in result:
              if len(row) < 3: # Исходя из того, что в ТР минимум три столбца: Название ячейки, порядковый номер строки, решение
                break
              solution = {'solution':row[1]}
              for col in range(2,len(row)):
                solution.update({cols[col-2][0]:row[col]})
              result_list.append(solution)
          else:
            Log.Warning('Таблица решений ' + self.code_table + ' пуста')
          Log.Message('Строки ТР '+ str(self.code_table) + ' в бд: ' + str(result_list))
          return result_list
        else:
          return None

    def CompareDectblSolutons(self, code_dectbl, **check_solutons):
        """ Получение информации, находится ли необходима строка в заданной таблице решений.
        Входные параметры: код ТР, какую строку нужно найти.
        Выходные параметры: True если есть такая строка в ТР, False в противном случае
        Шаблон строки поиска: **{'solution':'311','OPER_TYPE':'0','DEPOSIT_TYPE':None}
        Для пустых значений столбов указывается None как значение. Все поля и их значения записываются в одинарных кавычках.
        solution - это решение по строке ТР, OPER_TYPE, DEPOSIT_TYPE - названия столбцов ТР,
        между собой должны быть разделены запятой.
        """
        self.code_dectbl = code_dectbl
        self.check_solutons = check_solutons
        check_state = False
        result = self.GetSolutionTable(self.code_dectbl)
        if result is not None and result:
          Log.Message('Строка для проверки: ' + str(self.check_solutons))
          # сравнение двух словарей на предмет идентичности по ключам и значениям
          for lines in result:
            unmatched_item = set(lines.items()) ^ set(self.check_solutons.items())
            if not unmatched_item:
              check_state = True
              break
          else:
            Log.Warning('Строка ' + str(self.check_solutons)+ ' не найдена в таблице решений ' + self.code_dectbl)
          if check_state:
            Log.Checkpoint('В таблице решений ' + self.code_dectbl + ' есть необходимая строка')
        elif result is None:
          Log.Warning('В базе отсутствует таблица решений с кодом ' + self.code_dectbl)
        return check_state

    def NewCustomerPayAccount(self, payer_acc, amount):
        """ Пополнение клиенских и внебалансовых счетов, где пс счета =
        (2204*2203*7*класс), в валюте KZT/USD/EUR/RUB и тд
        """
        self.payer_acc = payer_acc
        self.amount = str(amount)

        date_operday = self.GetEnviron("DATE_OPERDAY")
        to_date = aqConvert.DateTimeToFormatStr(date_operday, "%d.%m.%Y")
        # получаем пс счета
        result_mask = self.GetAccountInfo(self.payer_acc)


        if str(result_mask[0][10]).startswith('2'):
          result = """ begin c_pkgconnect.popen(); c_pkgsession.doper := '""" + to_date + """';
                 Z_PKG_AUTO_TEST.p_reset_accPAY('""" + self.payer_acc + """' ,""" + self.amount + """); end;
                 """
          self.OracleHandlerDB(result, dml_query='True')
          Log.Event('Пополнение счета ' + str(self.payer_acc) + ' на сумму ' + str(self.amount))

        elif str(result_mask[0][10]).startswith('2'):
          result = """ begin c_pkgconnect.popen(); c_pkgsession.doper := '""" + to_date + """';
                 Z_PKG_AUTO_TEST.p_outside_Balance('""" + self.payer_acc + """' ,""" + self.amount + """); end;
                 """
          self.OracleHandlerDB(result, dml_query='True')
          Log.Event('Пополнение счета '  + str(self.payer_acc) + ' на сумму ' + str(self.amount))
        else:
          Log.Warning('Не произведено пополнение счета ' + str(self.payer_acc) + ' не входит ни в одно из условий')
      
    def OpenNewCardMclien(self,code_inn,res,type_doc,cli_role,type_cl,name,surName,nameCom,sex,full_name,name_dep,birthday,dateReg):
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
                            DELETE FROM TESTINGIINFL
                            where IIN = '{self.code_inn}'; commit; END;"""
            self.OracleHandlerDB(selectDelete, dml_query=True)
        elif self.type_cl == 'JUR' or self.type_cl == 'PBOYULS':
            selectDelete = f"""BEGIN
                            DELETE FROM TESTINGIINJUR
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
                          select iin, name, surname, middlename, resident, birthday, sex from TESTINGIINFL
                          where resident = '{self.res}' and rownum = 1
                          """

            slct_cnt_iin = f"""
                            select COUNT(IIN) FROM TESTINGIINFL
                            """
            cnt_iin = self.OracleHandlerDB(slct_cnt_iin)
            for i in range(cnt_iin[0][0]):
                iin_db_fl = self.OracleHandlerDB(select_iin_db_fl)
                dlt_iin = f"""begin delete from TESTINGIINFL where IIN = '{iin_db_fl[0][0]}'; commit; end;"""
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
                    Log.Warning(f"В датасете TESTINGIINFL нет подходящего ИИН физ лица")
            slct_cnt_iin_j = f"""
                            select COUNT(IIN) FROM TESTINGIINJUR
                            """
            cnt_iin_j = self.OracleHandlerDB(slct_cnt_iin_j)
            for i in range(cnt_iin_j[0][0]):
                dlt_iin_j = f"""BEGIN DELETE FROM TESTINGIINJUR where IIN = '{self.code_inn}'; commit; END;"""
                slct_g_iin_j = f""" select count(IIN) from g_iin where IIN = '{self.code_inn}'"""
                slct_iin_jur = f"""SELECT COUNT(IIN) FROM TESTINGIINJUR WHERE IIN = '{self.code_inn}'"""
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
                    Log.Warning(f"В датасете TESTINGIINJUR нет подходящего ИИН юр лица")
        return codeCli[0][1]

    def OpenNewCardMclienNew(self,code_inn,res,type_doc,cli_role,type_cl,name,surName,nameCom,sex,full_name,name_dep,birthday,dateReg,iin_fl = None,iin_jur = None):
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

        self.iin_fl = iin_fl
        Log.Message(self.iin_fl)
        self.iin_jur = iin_jur
        Log.Message(self.iin_jur)
        if self.iin_fl is None:
          self.iin_fl = 'TESTINGIINFL'
        if self.iin_jur is None:
          self.iin_jur = 'TESTINGIINJUR'
        Log.Message(self.iin_fl)
        Log.Message(self.iin_jur)
        if self.type_cl == 'FL' or self.type_cl == 'PBOYUL':
            selectDelete = f"""BEGIN
                            DELETE FROM {self.iin_fl}
                            where IIN = '{self.code_inn}'; commit; END;"""
            self.OracleHandlerDB(selectDelete, dml_query=True)
        elif self.type_cl == 'JUR' or self.type_cl == 'PBOYULS':
            selectDelete = f"""BEGIN
                            DELETE FROM {self.iin_jur}
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
                          select iin, name, surname, middlename, resident, birthday, sex from '{self.iin_fl}'
                          where resident = '{self.res}' and rownum = 1
                          """

            slct_cnt_iin = f"""
                            select COUNT(IIN) FROM {self.iin_fl}
                            """
            cnt_iin = self.OracleHandlerDB(slct_cnt_iin)
            for i in range(cnt_iin[0][0]):
                iin_db_fl = self.OracleHandlerDB(select_iin_db_fl)
                dlt_iin = f"""begin delete from {self.iin_fl} where IIN = '{iin_db_fl[0][0]}'; commit; end;"""
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
                    Log.Warning(f"В датасете TESTINGIINFL нет подходящего ИИН физ лица")
            slct_cnt_iin_j = f"""
                            select COUNT(IIN) FROM {self.iin_jur}
                            """
            cnt_iin_j = self.OracleHandlerDB(slct_cnt_iin_j)
            for i in range(cnt_iin_j[0][0]):
                dlt_iin_j = f"""BEGIN DELETE FROM {self.iin_jur} where IIN = '{self.code_inn}'; commit; END;"""
                Log.Message(dlt_iin_j)
                slct_g_iin_j = f""" select count(IIN) from g_iin where IIN = '{self.code_inn}'"""
                slct_iin_jur = f"""SELECT COUNT(IIN) FROM {self.iin_jur} WHERE IIN = '{self.code_inn}'"""
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
                    Log.Warning(f"В датасете TESTINGIINJUR нет подходящего ИИН юр лица")
        return codeCli[0][1]


    def AddCreditHistory(self, iin):
        """метод добавляет кредитную историю тестовому клиенту"""
        self.iin = iin
        insert_hst = f"""begin insert into L_CLIHSTEXT(CLI_DEP_ID, CLI_ID, DOC_CODE, DOC_TYPE, DOC_DATE, HSTINFO, REASON, DISSUE, DRETURN, PRIM, FLSTATE, REP_ID, REPORT)
                                        values(dep_id, cli_id, doc_code, null, trunc(sysdate), '1', '1', null, null, null, null, '1471', null); commit; end"""
        self.OracleHandlerDB(insert_hst, dml_query=True)

    def CraeteNewAcc(self):
        """ Создание счетов клиента Физ лицо, Юр лицо, ИП"""
        self.cliCode = cliCode
        date_operday = self.GetEnviron("DATE_OPERDAY")
        to_date = aqConvert.DateTimeToFormatStr(date_operday, "%d.%m.%Y")
        result = f""" begin c_pkgconnect.popen(); c_pkgsession.doper := '{to_date}';
            Z_PKG_AUTO_TEST.p_create_acc('{self.cliCode}'); commit; end; 
            """
        accCode = self.OracleHandlerDB(result, dml_query='True')
        return accCode

    def CraeteNewDoc(self, acc_payer, sum_oper, rec_acc, type_doc,oper_code, knp, code):
        """ Создание ПТП и ИР в статусе введен"""
        self.acc_payer = acc_payer
        self.sum_oper = sum_oper
        self.rec_acc = rec_acc
        self.type_doc = type_doc
        self.oper_code = oper_code
        self.knp = knp
        self.code = code
        doc_num = self.GeneratePassNum()
        date_operday = self.GetEnviron("DATE_OPERDAY")
        to_date = aqConvert.DateTimeToFormatStr(date_operday, "%d.%m.%Y")
        result = f""" begin c_pkgconnect.popen(); c_pkgsession.doper := '{to_date}';
            Z_PKG_AUTO_TEST.p_crate_doc_ts('{self.acc_payer}', '{self.sum_oper}', '{self.rec_acc}', '{self.type_doc}', '{self.oper_code}', '{self.knp}', '{self.code}', '{doc_num}' ); end; 
            """
        self.OracleHandlerDB(result, dml_query='True')
        return doc_num

    def PayDetailOrderValidate(self, **fields):
        """ Валидация полей расширенного платежного ордера, который обрабатывается внешними системами.
        На вход подается словарь из полей - код поля на форме: значение для проверки"""
        self.fields = fields
        btn_view = self.FindChildField("frmOperJournal", "Name", 'VCLObject("btnOrd")')
        if btn_view.Exists and btn_view.Enabled:
          btn_view.Click()
          if Sys.Process("COLVIR").WaitVCLObject('VCLObject("frmPayOrdLstJRN")', 5000).Exists:
            btn_ok_picker = self.FindChildField("frmPayOrdLstJRN", "Name", 'VCLObject("btnOK")') # нужный док обычно стоит первый
            btn_ok_picker.Click()
          self.WaitLoadWindow("frmContFPayCardDet")
          knp_tab = self.FindChildField("frmContFPayCardDet", "Name", 'PageTab("КНП")')
          knp_tab.Click()
        else:
          Log.Warning('Кнопка просмотра платежного ордера недоступна или не найдена')
          return
        codes_dict = {'Дата документа':'edDORD','Дата валютирования':'edDVAL','Сумма':'edSDOK',
                    'Валюта':'edVAL_CODE','Курс':'edRATE','Счет плательщика':'edCODE_ACL',
                    'ИИН плательщика':'edRNN_CL','Счет получателя':'edCODE_ACR','ИИН получателя':'edRNN_CR',
                    'Приоритет':'edPriority','Вид документа':'edDocType','КНП':'edKNP','КОД':'edCODE_OD',
                    'КБЕ':'edCODE_BE'}
        for field_code, value in self.fields.items():
          field_fullname = field_code
          for field_name, val in codes_dict.items():
            if val == field_code:
              field_fullname = field_name
          find_field_form = self.FindChildField("frmContFPayCardDet", "Name", 'VCLObject("'+field_code+'")', "internal")
          if find_field_form is not None:
            Log.Message('value ' + str(value))
            Log.Message('find_field_form ' + str(find_field_form.wText))
          if find_field_form is not None and value == find_field_form.wText:
            Log.Checkpoint('Поле ' + field_fullname + ' соответсвует контрольному значению')
          else:
            Log.Warning('Поле ' + field_fullname + ' не соответсвует контрольному значению ' + str(value))
        Sys.Process("COLVIR").VCLObject("frmContFPayCardDet").Close()

    def AccArrestOrBlock(self, account, name_operation, arest_lock_type, reason, summa_arest=None):
        """ Выполнение над переданным счетом блокировки или ареста суммы
        На вход подается счет, который нужно арестовать, наименование операции, тип блокировки и сумму
        блокировки (если блок\арест на сумму).
        name_operation может быть только двух значений: Арест суммы, Приостановка по счету
        reason для подстановки уникальных для платежки значений чтобы искать нужный лимит или блокировку """
        self.account = account
        self.name_operation = name_operation
        self.arest_lock_type = arest_lock_type
        self.summa_arest = summa_arest
        self.reason = reason
        self.TaskInput('DD7')
        self.SetFilter(CODE=self.account)
        self.WaitLoadWindow("frmAccBlnNblList")
        check_acc = self.GetGridDataFields("frmAccBlnNblList", "STATE")
        if check_acc[0].replace("\'", '') == 'Счетоткрыт':
          btn_operations = Sys.Process("COLVIR").VCLObject("frmAccBlnNblList").VCLObject("btnRunOperation")
          btn_operations.Click()
          self.FindNeedOperation(self.name_operation)
          self.ConfirmOperation(self.name_operation)
          if not self.ErrorMessageHandler():
            self.WaitLoadWindow("frmArestop")
            type_arrest = self.FindChildField("frmArestop", "Name", 'VCLObject("edType")')
            type_arrest.Keys(self.arest_lock_type)
            type_arrest.Keys('[Tab]')
            amount_arest = self.FindChildField("frmArestop", "Name", 'VCLObject("edAmount")')
            if self.summa_arest is not None and amount_arest.Enabled:
              amount_arest.Keys(self.summa_arest)
            elif not amount_arest.Enabled and self.summa_arest is not None:
              Log.Warning('Для блокировки '+ self.arest_lock_type +' не предусмотрен ввод суммы')
            date_lock_begin = self.FindChildField("frmArestop", "Name", 'VCLObject("edDateBeg")', "internal")
            self.FieldValueValidator('Дата начала действия', date_lock_begin, 'date')
            date_lock_end = self.FindChildField("frmArestop", "Name", 'VCLObject("edDateEnd")')
            date_lock_end.Keys(self.NormalDateMask(self.GetPlusDailyDate(30)))
            lock_doc_num = self.FindChildField("frmArestop", "Name", 'VCLObject("edDocNum")')
            lock_doc_num.Keys(self.DocNumberGenerator())
            lock_doc_date = self.FindChildField("frmArestop", "Name", 'VCLObject("edDateDoc")', "internal")
            self.FieldValueValidator('Дата документа основания', lock_doc_date, 'date')
            org_name = self.FindChildField("frmArestop", "Name", 'VCLObject("edOrgName")')
            org_name.Keys("Суровые автотесты")
            lock_reason = self.FindChildField("frmArestop", "Name", 'VCLObject("edPrim")')
            lock_reason.Keys(self.reason)
            btn_ok_arrest = self.FindChildField("frmArestop", "Name", 'VCLObject("btnOk")')
            btn_ok_arrest.Click()
            if not self.ErrorMessageHandler(recursive='True'):
              self.CheckOperEndWindow()
              Log.Checkpoint("По счету "+self.account+" выполнена операция "+self.name_operation+" с типом "+ self.arest_lock_type)
            else:
              Log.Warning("Ошибка во время выполнения операции "+self.name_operation+" по счету "+self.account)
        else:
          Log.Warning("Не найден счет "+ self.account +" в состоянии 'Счет открыт'")
        Sys.Process("COLVIR").VCLObject("frmAccBlnNblList").Close()

    def CountSummArest(self, account, type_summ, summ_operation):
        """ Расчет ареста суммы для счета в зависимости от остатка
        на счете и суммы операции над ним.
        На вход подается счет, type_summ = больше остатка, меньше остатка, сумма остатка и
        сумма будущей операции (для расчета ареста меньше суммы остатка, чтобы осталось на проведение операции)
        """
        self.account = account
        self.type_summ = type_summ
        self.summ_operation = summ_operation
        acc_info = self.GetAccountInfo(self.account, need_dict='True')
        if acc_info['PS_BAL'] is not None:
          balans_acc = float(acc_info['PS_BAL'].replace(' ', ''))
        else:
          balans_acc = float(acc_info['COLVIR_BAL'])
        if self.type_summ == 'больше остатка':
          arest_summ = balans_acc + 10000.00
        elif self.type_summ == 'меньше остатка':
          arest_summ = balans_acc - (float(self.summ_operation) * 3)
        elif self.type_summ == 'сумма остатка':
          arest_summ = balans_acc
        Log.Message("Баланс на счете до ареста "+ str(balans_acc))
        Log.Message("Расчитанная сумма ареста " + str(int(arest_summ)))
        return int(arest_summ)

    def CountArrestList(self, proc_id, bsn_id):
        """ Возврат количества всех строк с арестами и блокировками по счету для группового и обычного
         снятия арестов. ID на вход берутся из списка этих блокировок при выполнении операции снятия
         или группового снятия арестов"""
        self.proc_id = proc_id.replace("\'", '').strip()
        self.bsn_id = bsn_id.replace("\'", '').strip()
        select = """
           select replace(replace(DSCR,chr(10)),chr(13))DSCR
          from
            T_OPERJRN j,T_SCEN s,C_USR u
          where
            j.ID = '"""+ self.proc_id +"""'
            and s.ID = '"""+ self.bsn_id +"""'
            and s.CODE = 'ARESTSUM' and s.NORD = j.NOPER
            and j.UNDOFL = 0 and u.ID = j.TUS_ID
          union all
          select replace(replace(DSCR,chr(10)),chr(13))DSCR
          from
            T_OPERJRN j,T_SCEN s,C_USR u
          where
            j.ID = '"""+ self.proc_id +"""'
            and s.ID = '"""+ self.bsn_id +"""'
            and s.CODE = 'PAUSEACC' and s.NORD = j.NOPER and j.UNDOFL = 0
            and u.ID = j.TUS_ID
        """
        result = self.OracleHandlerDB(select)
        return result

    def GetAllLimitsAcc(self, acc_code):
        """ Получение всех лимитов на счете в АБИС """
        self.acc_code = acc_code
        acc_info = self.GetAccountInfo(self.acc_code, need_dict='True')
        select = """
                select substr(G_PkgAccBln.fGetCodeAccByIdAcc(L.ACC_ID,L.DEP_ID),1,30) as ACC_CODE,
                substr(BS_DOM.DName('T_ACCLIM_TYPE',L.LIMTYPE,'N'),1,30) as  LIMNAME,
                L.FROMDATE, decode(L.TODATE,to_date('31.12.4712','DD.MM.YYYY'),null,L.TODATE) as TODATE,
                V.CODE as VALUTA, substr(TO_MONEY(T_PkgLim.fValue(L.ID,greatest(L.FROMDATE,P_OPERDAY)),
                T_PKGVAL.fGetFac(L.VAL_ID)),1,27) as SUMM,
                substr(TO_MONEY(T_PKGVAL.fCrossRate(T_PkgLim.fValue(L.ID,greatest(L.FROMDATE,P_OPERDAY)),
                L.VAL_ID)),1,27) as SUM_NATVAL,
                L.PRIM, T.LONGNAME, T.PRIORITY, L.LIMTYP
                from  T_VAL V, T_LIM L, T_ACCLIMTYP T
                where L.VAL_ID=V.ID(+) and T.ID(+)= L.LIMTYP and L.ACC_ID = '""" + str(acc_info['ID']) + """'
                and L.DEP_ID = '""" + str(acc_info['DEP_ID'])+ """'
                """
        result = self.OracleHandlerDB(select, need_zero='True') # при отсутствии лимитов запрос будет пуст
        if result is None:
          Log.Event('Лимиты на счете в АБИС отсутствуют')
        return result

    def GetAllBlocksAcc(self, acc_code):
        """ Получение всех блокировок на счете в АБИС  """
        self.acc_code = acc_code
        acc_info = self.GetAccountInfo(self.acc_code, need_dict='True')
        select = """
            select b.CODE as ACC_CODE,l.FROMDATE,
            l.TODATE+1 as TODATE,l.PRIM, lt.CODE as LOCK_CODE,
            lt.LONGNAME as LOCK_NAME,u.CODE as USER_CODE,
            l.LORDNUM,l.LORDDATE,l.REFER
          from
            C_USR u,G_ACCBLN b,G_LOCKTYPE lt,G_LOCK l
          where l.LOCKTYPE = lt.ID
            and b.DEP_ID = l.DEP_ID and b.ID = l.ACC_ID
            and U.ID(+) = l.ID_US
            and l.DEP_ID = '""" + str(acc_info['DEP_ID']) + """'
             and l.ACC_ID = '""" + str(acc_info['ID']) + """'
        """
        result = self.OracleHandlerDB(select, need_zero='True') # при отсутствии блокировок запрос будет пуст
        if result is None:
          Log.Event('Блокировки на счете в АБИС отсутствуют')
        return result

    def GetAllHoldsAccPS(self, acc_code, check_refer=None):
        """ Получение открытых (действующих) холдов по счету в ПС.
        По параметру check_refer передается ID холда, состояние которого
        необходимо проверить """
        self.acc_code = acc_code
        self.check_refer = check_refer
        date_operday = self.GetEnviron("DATE_OPERDAY")
        acc_card_dict = self.GetAccountInfoPS(self.acc_code, need_dict='True')
        check_str = """ and tachld.code = '""" + str(self.check_refer) + """' """
        select = """
            select ahld.NAME as HLDCODE, tachld.Amount, tachld.CODE as REFER,
              tachld.CLSTIME
            from
              APT_ACC@CAP tacc, APT_ACCHLD@CAP tachld, APR_HLD@CAP ahld
            where
              tacc.id=tachld.id(+)
              and tachld.hld_id=ahld.id(+)
              and 66<>'0'
              and tacc.ID= '""" + str(acc_card_dict["ID"]) + """'
        """ + check_str
        result = self.OracleHandlerDB(select, need_zero='True') # при отсутствии холдов запрос будет пуст
        if result is None or result[0][0] is None:
          Log.Event('Холды на счете в АБИС отсутствуют')
          result = None
        return result

    def GetBalancePMAccPS(self, acc_code):
        """Получение баланса ПМ (прожиточного минимума) по счету в ПС,
          использованная сумма и сумма ПМ в холде"""
        self.acc_code = acc_code
        acc_card_dict = self.GetAccountInfoPS(self.acc_code, need_dict='True')
        select = """
          select decode(level,1,'Прожиточный минимум (использовано)',2,
            'Прожиточный минимум (захолдировано)') sSumTyp,
            decode(level,1,AP_BALANCE.fBalChkSum('""" + str(acc_card_dict["ID"]) + """', t.cStratFl),2,
            AP_BALANCE.fHldChkSum('""" + str(acc_card_dict["ID"]) + """', t.cStratFl)) nSum
            from dual d, (select ap_cfg.GetParamStr('LV_STRAT') cStratFl from dual) t
            connect by level < 3
        """
        result = self.OracleHandlerDB(select, cap_query='True')
        return result

    def CheckingHotKey(self, name_operation, name_scenario):
        """ Метод вернет клавишу установленную в операции сценария бизнес-процесса
        входные параметры: наименование операции/сценария
        выходные параметры: -1 клавиша отсутствует или вернет клавишу (пример:Ctrl+z)"""
        self.name_operation = name_operation
        self.name_scenario = name_scenario
        select = """ select trim(nvl(s.hotkey,'-1')) as key
                     from t_scen_std s where  s.code = '""" + self.name_operation + """'
                     and s.arcfl = '0'
                     and s.id in (select id from t_bop_dscr_std where code = '""" + str(self.name_scenario) + """')
                     """
        result = self.OracleHandlerDB(select)
        if result is not None and result[0][0] != '-1':
          need_key = result[0][0][5]
          select_check = """ select count(s.hotkey) as key
                     from t_scen_std s where
                     s.arcfl = '0' and s.hotkey = 'Ctrl+""" + need_key + """'
                     and s.id in (select id from t_bop_dscr_std where code = '""" + str(self.name_scenario) + """')
                    """
          counter = self.OracleHandlerDB(select_check)
          if int(counter[0][0]) > 1:
            return '-1'
        return result[0][0]

    def GenerateRandomNumber(self, int_lenght):
        """ Генерация случайной строки только из цифр заданной величины """
        self.int_lenght = int_lenght
        return ''.join(choice(digits) for _ in range(self.int_lenght))

    def GetAccountInfoPS(self, acc_number, need_dict=None):
        """ Возврат данных по номеру счета из карточки ПС обращением в САР БД;
        ID будет полезен для других запросов в CAP;
        BAL_WITH_HOLDS - чистый остаток на счете с учетом холдов, будет отражаться в АБИС;
        'LOCK_CODE', 'LOCK_IDN_CODE' статусы блокировки счета, могут иметь разное значение при
        наличии блокировок на счете"""
        self.acc_number = acc_number
        self.need_dict = need_dict
        select = """ select tacc.ID, racc.code as CODE_ACC, racc.arcfl, rcur.CODE as CUR_ACC,
        decode(rcur.decim,-1,to_char(nvl(tbal.balance,0),'fm9999999999999990'),
        0,to_char(nvl(tbal.balance,0),'fm9999999999999990'),
        1,to_char(nvl(tbal.balance,0),'fm9999999999999990d0'),
        2,to_char(nvl(tbal.balance,0),'fm9999999999999990d00')) as AMOUNT_ACC,
        decode(rcur.decim,-1,to_char(AP_BALANCE.fHld(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        0,to_char(AP_BALANCE.fHld(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        1,to_char(AP_BALANCE.fHld(tacc.ID,tacc.cur_id),'fm9999999999999990d0'),
        2,to_char(AP_BALANCE.fHld(tacc.ID,tacc.cur_id),'fm9999999999999990d00')) as HOLDSUM_ACC,
        decode(rcur.decim,-1,to_char(AP_BALANCE.fOvr(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        0,to_char(AP_BALANCE.fOvr(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        1,to_char(AP_BALANCE.fOvr(tacc.ID,tacc.cur_id),'fm9999999999999990d0'),
        2,to_char(AP_BALANCE.fOvr(tacc.ID,tacc.cur_id),'fm9999999999999990d00')) as OVERDRAFT_ACC,
        decode(rcur.decim,-1,to_char(AP_BALANCE.fBalFree(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        0,to_char(AP_BALANCE.fBalFree(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        1,to_char(AP_BALANCE.fBalFree(tacc.ID,tacc.cur_id),'fm9999999999999990d0'),
        2,to_char(AP_BALANCE.fBalFree(tacc.ID,tacc.cur_id),'fm9999999999999990d00')) as RESTBYHLD_ACC,
        AP_FIN.fId2Code(tacc.FIN_ID) as FINCODE, tidn.CODE as IDNCODE, rlock.CODE as LOCK_CODE,
        accidnlock.CODE as LOCK_ACCIDNCODE, rlock.CODE||':'||rlock.NAME as LOCK_STATUS,
        accidnlock.CODE||':'||accidnlock.NAME as LOCK_ACCIDNSTATUS
        from
        APT_ACC tacc, APR_ACC racc, APR_CUR rcur,APT_BAL tbal, APT_IDN tidn,
        APR_IDN aidn,APR_LOCK rlock,APR_LOCK accidnlock
        where
        tacc.acc_id=racc.ID(+) and tacc.cur_id=rcur.ID(+) and tacc.id=tbal.id(+)
        and tidn.code='""" + self.acc_number + """' and tidn.ACC_ID=tacc.ID
        and tidn.IDN_ID=aidn.ID and accidnlock.id = tidn.lckfl and rlock.id = tacc.lckfl
        UNION ALL
        select tacc.ID, racc.code as CODE_ACC, racc.arcfl, rcur.CODE as CUR_ACC,
        decode(rcur.decim,-1,to_char(nvl(tbal.balance,0),'fm9999999999999990'),
        0,to_char(nvl(tbal.balance,0),'fm9999999999999990'),
        1,to_char(nvl(tbal.balance,0),'fm9999999999999990d0'),
        2,to_char(nvl(tbal.balance,0),'fm9999999999999990d00')) as AMOUNT_ACC,
        decode(rcur.decim,-1,to_char(AP_BALANCE.fHld(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        0,to_char(AP_BALANCE.fHld(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        1,to_char(AP_BALANCE.fHld(tacc.ID,tacc.cur_id),'fm9999999999999990d0'),
        2,to_char(AP_BALANCE.fHld(tacc.ID,tacc.cur_id),'fm9999999999999990d00'))
        as HOLDSUM_ACC,
        decode(rcur.decim,-1,to_char(AP_BALANCE.fOvr(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        0,to_char(AP_BALANCE.fOvr(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        1,to_char(AP_BALANCE.fOvr(tacc.ID,tacc.cur_id),'fm9999999999999990d0'),
        2,to_char(AP_BALANCE.fOvr(tacc.ID,tacc.cur_id),'fm9999999999999990d00'))
        as OVERDRAFT_ACC,
        decode(rcur.decim,-1,to_char(AP_BALANCE.fBalFree(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        0,to_char(AP_BALANCE.fBalFree(tacc.ID,tacc.cur_id),'fm9999999999999990'),
        1,to_char(AP_BALANCE.fBalFree(tacc.ID,tacc.cur_id),'fm9999999999999990d0'),
        2,to_char(AP_BALANCE.fBalFree(tacc.ID,tacc.cur_id),'fm9999999999999990d00'))
        as RESTBYHLD_ACC, AP_FIN.fId2Code(tacc.FIN_ID), tidn.CODE as IDNCODE,
        rlock.CODE as LOCK_CODE, accidnlock.CODE as LOCK_ACCIDNCODE,
        rlock.CODE||':'||rlock.NAME as LOCK_STATUS,
        accidnlock.CODE||':'||accidnlock.NAME as LOCK_ACCIDNSTATUS
        from
        APT_ACC tacc,APR_ACC racc,APR_CUR rcur,APT_BAL tbal,APT_ACCIDN acidn,
        APT_IDN tidn,APR_IDN aidn,APR_LOCK rlock,APR_LOCK accidnlock
        where
        tacc.acc_id=racc.ID(+) and tacc.cur_id=rcur.ID(+) and tacc.id=tbal.id(+)
        and tacc.ID=acidn.acc_ID and acidn.IDN_ID='""" + self.acc_number + """'
        and tacc.ID=tidn.ACC_ID(+) and tidn.IDN_ID=aidn.ID(+) and rlock.id = tacc.lckfl
        and accidnlock.id = tidn.lckfl
        """
        info_acc = self.OracleHandlerDB(select, cap_query='True')
        if self.need_dict is not None and info_acc is not None:
          tuple_acc_fields = ('ID','CODE_ACC','ARCFL','CUR_ACC','BAL_NO_HOLDS','HOLD_SUMM',
                              'OVERDRAFT_SUMM','BAL_WITH_HOLDS','FIN_CODE','IDN_ACC',
                              'LOCK_CODE', 'LOCK_IDN_CODE', 'LOCK_STATUS', 'LOCK_IDN_STATUS')
          dict_result = {}
          for rows in info_acc:
            for fields_card, fields_row in zip(tuple_acc_fields, rows):
              dict_result[fields_card] = fields_row
          info_acc = dict_result
        return info_acc

    def GetAllOpenAccCard(self, cli_code):
        """ Получение всех открытых счетов карточки клиента по коду карточки
        С фильром по маске счетов из задачи CRD2ACC """
        self.cli_code = cli_code
        date_operday = self.GetEnviron("DATE_OPERDAY")
        select = """
        select A.ID, A.DEP_ID, decode( G_PkgLock.fGetAccLockExist(A.DEP_ID, A.ID) +
          T_pkgLim.fValueAcc(A.DEP_ID, A.ID, P_OPERDAY, P_NatVal), 0, 0, 1 ) as ARESTOP_FL,
          nvl(A.CAPFL, '0') as CAPFL, D.CODE as DEP_CODE, L.CODE as CHA_CODE,
          A.CODE, AH.LONGNAME, G.CODE as AUT_CODE,
          GL_Anl.fAccAnlValue(A.DEP_ID, A.ID, 'VALUTA') as VALUTA_ANL,
          V.CODE as VAL_CODE, C.CODE as CLI_CODE, C.ID as CLI_ID,
          C.DEP_ID as CLI_DEP_ID,
          Z_PKG_AUTO_TEST.f_get_dcl_code(a.code) as product_code
        from
          C_DEP D, LEDACC L, LEDGER LD, T_VAL V ,T_ACCGRP G, C_USR U,
          G_CLI C, G_CLIHST CH,  C_DEP D2, G_ACCBLN A, G_ACCBLNHST AH,
          G_ACCBLN A2, G_ACCBLNHST AH2, T_ACC AA, T_PROCMEM PM, T_PROCESS PR, T_BOP_STAT ST
        where
          A.ID=AH.ID and A.DEP_ID=AH.DEP_ID and '""" + date_operday + """'
          between AH.FROMDATE and AH.TODATE
          and A.DEP_ID=D.ID and A.CHA_ID=L.ID and L.LED_ID=LD.ID(+)
          and V.ID(+)=AA.VAL_ID and AH.DEP_ID=G.DEP_ID and AH.AUT_ID=G.ID
          and A.ID=AA.ID and A.DEP_ID=AA.DEP_ID and C.DEP_ID=CH.DEP_ID
          and C.ID=CH.ID and '""" + date_operday + """' between CH.FROMDATE and CH.TODATE
          and C.DEP_ID=AH.CLIDEP_ID and C.ID=AH.CLI_ID and U.ID(+)=AH.ID_US
          and PM.ORD_ID = A.ORD_ID and PM.DEP_ID = A.DEP_ID and PR.ID = PM.ID
          and ST.ID = PR.BOP_ID and ST.NORD = PR.NSTAT
          and D2.CODE(+) = GL_Anl.fAccAnlValue(A.DEP_ID, A.ID, 'DEPARTMENT')
          and A2.DEP_ID(+)=AH.RELDEP_ID and A2.ID(+)=AH.REL_ID
          and A2.ID=AH2.ID(+) and A2.DEP_ID=AH2.DEP_ID(+) and '""" + date_operday + """'
          between AH.FROMDATE(+) and AH.TODATE(+)
          and AH.ARCFL = '0'
          and C.CODE ='""" + str(self.cli_code) + """'
          and SUBSTR(L.CODE, 1, 4) in (2013,2014,2023,2123,2124,2125,2127,2130,2203,
            2204,2205,2206,2207,2208,2211,2213,2214,2215,2217,2219,2220,2221,2223,2229)
        """
        result = self.OracleHandlerDB(select, need_zero='True')
        if result is not None:
          Log.Message("Счета карточки клиента " + str(self.cli_code), str(result))
        else:
          Log.Message('На карточке клиента нет подходящих открытых счетов ' + str(self.cli_code))
        return result

    def GetDocsCard2Acc(self, acc_num, contract_number=None):
        """ Получение документов в К2 по номеру счета и номеру документа(необязательно)"""
        self.acc_num = acc_num
        self.contract_number = contract_number
        contract_number_filter = ""
        if contract_number is not None:
          contract_number_filter = """ and op.txt_dscr like '%""" + self.contract_number + """%' """
        select = """
            select  d.code as KSO_CODE,o.CODE as doc_num,
            op.dep_id, op.id, op.amount,
            substr(TO_MONEY(S_BSPAY.fBalCrd2(op.DEP_ID,op.ID, op.VAL_ID),
            C_PKGVAL.fGetFac(op.VAL_ID)),1,27) CRDBAL,
            substr(bs_dom.dname('S_PRIORITY_CRD2',c2.PRIORITY,'N'),1,1) PRIORITY,
            c2.NPRIOR,
            to_char(op.dop),to_char(op.dval), op.refer, op.code_bcr, op.code_acr, op.rnn_cr,
            op.txt_dscr, op.nocmsfl, op.knp, op.code_od, op.code_be
            from S_ORDPAY op, T_BOP_STAT s, T_PROCESS p, T_PROCMEM m,
                 g_accbln gg,S_ORDDSC_STD d,T_ORD o, S_CRD2 c2
            where op.DEP_ID = m.DEP_ID and op.ID = m.ORD_ID and m.MAINFL = '1'
             and p.ID = m.ID and s.ID = p.BOP_ID and s.NORD = p.NSTAT and op.acc_id = gg.id
             and d.ID = op.KSO_ID and op.dep_id = gg.dep_id
             and op.DEP_ID = o.DEP_ID and op.ID = o.ID
             and c2.id = op.id and c2.dep_id = op.dep_id
             and gg.code = '""" + self.acc_num + """'
             and s.longname in ('В картотеке 2','В картотеке 2П')
        """ + contract_number_filter
        result = self.OracleHandlerDB(select, need_zero='True') # при отсутствии к2 запрос будет пуст
        if result is None:
          Log.Event('К2 на счете в АБИС отсутствует')
        Log.Message("Документы в к2 по счету " + str(self.acc_num), str(result))
        return result

    def GetCommisPay(self, proc_id, amount_comiss=None):
        """ Получение комиссии по платежу (расчетный, МП, кассовый) через его PROC_ID из гридов """
        self.proc_id = proc_id
        select = """ select
                      D.NAME,S.CODE_COM,
                      substr(to_money(S.SCOM,T_pkgval.fgetfac(S.VALCOM_ID)),1,27) as SCOM,
                      substr(T_PKGVAL.FGETISOCODE(S.VALCOM_ID),1,4) as VAL_CODE,S.NDSFL
                    from T_BOP_STAT D, T_PROCESS P, T_PROCMEM M, T_ORDCMS X, S_ORDCMS S,
                      T_PROCINH I
                    where I.CHILD_ID=M.ID and P.ID=M.ID and M.MAINFL=1 and D.ID=P.BOP_ID
                      and D.NORD=P.NSTAT
                      and M.DEP_ID=X.DEP_ID and M.ORD_ID=X.ID and S.LINE_ID=X.LINE_ID
                      and I.PARENT_ID=""" + self.proc_id + """ """
        result = self.OracleHandlerDB(select, need_zero='True') # при отсутствии комиссии запрос будет пуст
        if result is None:
          Log.Checkpoint('Комиссия не начислена и не взята по данному платежу')
          return False
        else:
          for items in result:
            if amount_comiss is not None:
              comiss_from_db = int(items[2].replace(' ','').replace('.00',''))
              if comiss_from_db == amount_comiss:
                Log.Checkpoint("Сумма комиссии соответствует требованиям")
              else:
                Log.Warning("Сумма комиссии не соответствует требуемой, должна быть " + str(amount_comiss) + " а получена " + str(comiss_from_db))
            Log.Checkpoint('Комиссия по платежу: '+ str(items[0])+' '+str(items[1])+' '+ \
              str(items[2])+' '+str(items[3])+' признак НДС '+str(items[4]))
          return True

    def GetPsAccount(self, dep_id_doc, id_code, ps):
        """ Метод наличие пс(маска) счета привязанного к договору. Входные параметры: dep_id/id договора; маска счета.
        пример: 2, 1006282934, '2870'. В случае отсутствие выдаст 0
        Выходной параметр - пс(маска) счета 2870191(пример)"""
        self.dep_id_doc = dep_id_doc
        self.id_code = id_code
        self.ps = ps
        select = """ select Z_PKG_AUTO_TEST.f_get_ps(""" + self.dep_id_doc + """, """ + self.id_code + """,
                      '""" + self.ps + """') from dual
                      """
        result = self.OracleHandlerDB(select)
        if result is not None:
          return result[0][0]
        else:
          Log.Warning('Результат метода GetPsAccount вернул пустое значение, требуется проверить!!')

    def GetCodeAccount(self, dep_id_doc, id_code, ps):
        """ Метод наличие счета по маске(пс) счета привязанного к договору
        входные параметры: dep_id; id договора, маска(пс) счета
        пример: 2, 1006282934, '2870'. В случае отсутствие выдаст 0
        Выходной параметр - счет KZ029472398866874736(пример)"""
        self.dep_id_doc = dep_id_doc
        self.id_code = id_code
        self.ps = ps
        select = """ select Z_PKG_AUTO_TEST.f_get_ps_account(""" + self.dep_id_doc + """, """ + self.id_code + """,
                      '""" + self.ps + """') from dual
                      """
        result = self.OracleHandlerDB(select)
        if result is not None:
          return result[0][0]
        else:
          Log.Warning('Результат метода GetCodeAccount вернул пустое значение, требуется проверить!!')

    def SelectTotalDebt(self, id_contract, dep_id_contract, doper_date=None):
        """ Получение суммарной либо начисленной за определенную дату суммы задолженности"""
        self.id_contract = id_contract
        self.dep_id_contract = dep_id_contract
        self.doper_date = doper_date
        if self.doper_date is None:
          select = """ select sum(paysdok) as amount
          from T_DEAPAY where dea_id = """ + self.id_contract + """ and dep_id = """ + self.dep_id_contract + """
          """
          result = self.OracleHandlerDB(select, need_zero='True')
          if result is None:
            Log.Event('Отсутствует сумма просроченной задолженности')
          Log.Message("Сумма просроченной задолженности равна " + str(result[0][0]))
          return result[0][0]
        else:
          select = """ select sum(paysdok) as amount
          from T_DEAPAY where dea_id = """ + self.id_contract + """ and dep_id = """ + self.dep_id_contract + """
          and dcalc = '""" + self.doper_date + """'
          """
          result = self.OracleHandlerDB(select, need_zero='True')
          if result is None:
            Log.Event('Отсутствует сумма начисленной задолженности за дату ' + str(self.doper_date) )
          Log.Message("Сумма начисленной задолженности за дату " + str(self.doper_date) + ' равна ' + str(result[0][0]))
          return result[0][0]

    def AccountsTypesAmounts(self, dep_id_doc, id_code, acc_code, vid_summ):
        """ Метод наличие привязки счета по виду сумм во вкладке Расчеты по договору
        документарных договорах. Пример: dep_id;id;счет;вид суммы. В случае отсутствие выдаст 0
        Выходной параметр - '1', по виду сумм счет привязан"""
        self.dep_id_doc = dep_id_doc
        self.id_code = id_code
        self.acc_code = acc_code
        self.vid_summ = vid_summ
        select = """ select Z_PKG_AUTO_TEST.f_payment_attribute(""" + self.dep_id_doc + """, """ + self.id_code + """,
                      '""" + self.acc_code + """', '""" + self.vid_summ + """') from dual """
        result = self.OracleHandlerDB(select)
        if result is not None:
          return result[0][0]
        else:
          Log.Warning('Результат метода AccountsTypesAmounts вернул пустое значение, требуется проверить!!')

    def PaymentAttribute(self, dep_id_doc, id_code, acc_code, type_summ):
        """ Метод наличие атрибута платежей в документарных договорах.
        Пример: dep_id;id;счет;тип атрибута. В случае отсутствие выдаст 0
        Выходной параметр - '1', по счету создан атрибут платежей"""
        self.dep_id_doc = dep_id_doc
        self.id_code = id_code
        self.acc_code = acc_code
        self.type_summ = type_summ
        select = """ select Z_PKG_AUTO_TEST.f_cliacc_attribute(""" + self.dep_id_doc + """, """ + self.id_code + """,
                      '""" + self.acc_code + """', '""" + self.type_summ + """') from dual """
        result = self.OracleHandlerDB(select)
        if result is not None:
          return result[0][0]
        else:
          Log.Warning('Результат метода PaymentAttribute вернул пустое значение, требуется проверить!!')

    def RemoveHotkey(self, name_key, name_scenario):
        """ Метод удаляет значение горячих клавиш """
        self.name_key = name_key
        self.name_scenario = name_scenario
        begin = """ begin update t_scen s set s.hotkey = ''
               where s.hotkey = 'Ctrl+""" + self.name_key + """'
               and s.id in (select id from t_bop_dscr_std where code = '""" + self.name_scenario + """');
               commit; end; """
        self.OracleHandlerDB(begin, dml_query='True')

    def RemovalK2ChekingBalance(self, account):
        """ Метод снятие картотеки документов по счету клиента входной параметр - счет клиента (2204*2203*)"""
        self.account = account
        date_operday = self.GetEnviron("DATE_OPERDAY")
        to_date = aqConvert.DateTimeToFormatStr(date_operday, "%d.%m.%Y")
        #получаем dep_id, id всех платежных требований (K2)
        select = """ select nvl(s.dep_id, '0') as dep_id, nvl(s.id, '0') as id
                  from (select '""" + self.account + """' code from dual) d
                  left join g_accbln g
                    on g.code = d.code
                  left join s_crd2 s
                    on s.acc_id = g.id and s.dep_id = g.dep_id
                  and (s.todate is null or s.todate  >= '""" + to_date + """')
                  and s.fromdate >= '""" + to_date + """'
                  """
        result = self.OracleHandlerDB(select)
        #получаем общую сумму задолженности (К2)
        select = """ select nvl(sum(op.amount), '-1') as AMOUNT
                      from S_ORDPAY op, T_BOP_STAT s, T_PROCESS p, T_PROCMEM m, g_accbln gg
                     where op.DEP_ID = m.DEP_ID
                       and op.ID = m.ORD_ID and m.MAINFL = '1'
                       and p.ID = m.ID and s.ID = p.BOP_ID
                       and s.NORD = p.NSTAT and op.acc_id = gg.id
                       and op.dep_id = gg.dep_id and gg.code = '""" + self.account + """'
                       and s.longname in ('В картотеке 2', 'В картотеке 2П')"""
        total_summ = self.OracleHandlerDB(select)
        if total_summ[0][0] == -1:
          Log.Event('Общая сумма выставленной картотеки по счету ' + str(self.account) + ' равна 0, пополнение не требуется!')
        else:
          # пополняем счет для оплаты *3 - с учетом суммы прожиточного минимума
          self.NewCustomerPayAccount(str(self.account), int(total_summ[0][0]) * 3)
        dict_data = {}
        for value in result:
          if value[1]:
            dict_data[value[0]] = value[1]
            for key, value in dict_data.items():
              # проверим была ли частичная оплата
              oper_code = self.CheckOperationExecution(str(value), str(key), 'CRDPAYPART')
              if 'CRDPAYPART' in oper_code:
                # если была частичная оплата, получим сумму остатка по K2 документа платежное-требование поручение
                get_amount = self.GettingDebt(str(value), str(key))
                # вызываем операцию частичная оплата
                result = """ declare begin c_pkgconnect.popen();
                c_pkgsession.doper := '""" + to_date + """';
                      begin T_PkgRunOprUtl.pRunOprByMainOrd(""" + str(key) + """, """ + str(value) + """,
                      'CRDPAYPART', 'nPAY=>' || '""" + get_amount + """'||', nDEBT=>' || 020118);
                      commit; end; end; """
                self.OracleHandlerDB(result, dml_query='True')
                Log.Event('Выполнено частичное погашение картотеки по счету ' + str(self.account))
              else:
                # вызываем операцию полная оплата
                result = """
                 declare begin c_pkgconnect.popen();
                 c_pkgsession.doper := '""" + to_date + """';
                      begin T_PkgRunOprUtl.pRunOprByMainOrd( """ + str(key) + """, """ + str(value) + """, 'CRDPAY', 020118);
                      commit; end; end; """
                self.OracleHandlerDB(result, dml_query='True')
                Log.Event('Выполнено полное погашение картотеки по счету ' + str(self.account))
               # закроем даты -20 дней, update требуется для платежей К2 установленных будущей датой
               # в рамках проверки сценария по операциям К2
              data = """ begin update s_crd2 s
                set s.fromdate = trunc(sysdate) -20, s.todate = trunc(sysdate) -20
                where s.id = """ + str(value) + """ and s.dep_id = """ + str(key) + """;
                commit; end; """
              self.OracleHandlerDB(data, dml_query='True')
              Log.Event('Выполнена установка прошлой даты -20 дней в дате создание/истечение К2')
          else:
            Log.Event('По счету ' + str(self.account) + ' платежных требований(K2) для оплаты не найдено')

    def GettingDebt(self, id, dep_id):
        """ Метод получение суммы остатка задолженности по K2 в случае частичной оплаты  по документу
        платежное требование - поручение (код модуля в colvir BRNCRD2)"""
        self.dep_id = dep_id
        self.id = id
        select = """ select substr(TO_MONEY(S_BSPAY.fBalCrd2(op.DEP_ID, op.ID, op.VAL_ID), '0'), 1, 27) CRDBAL
                 from S_ORDPAY op
                 where op.id = """ + self.id  + """ and op.dep_id = """ + self.dep_id  + """ """
        result = self.OracleHandlerDB(select)
        for value in result:
          return (re.sub(' ', '', str(value[0])))

    def GetDocState(self, id, dep_id):
        """ Метод проверки состояние документа(в рамках проекта К2), входные параметры: id; dep_id договора
        выходной параметр: код состояние, либо -1(некорректные входные параметры либо нет состояние документа)
        """
        self.id = id
        self.dep_id = dep_id
        select = """ select nvl(T_PKGRUNOPRUTL.fGetStatNameByMainOrd
                  (""" + self.dep_id + """, """ + self.id + """),-1) from dual """
        result = self.OracleHandlerDB(select)
        if result is not None:
          return result[0][0]
        Log.Warning('Результат метода GetDocState вернул пустое значение, требуется проверить!!')

    def SelectGraficDogovora(self, dep_id, id, doper, state, state_one='', contract_number=''):
        """ Проверка выставленных сумм в графике"""
        self.dep_id = dep_id
        self.id = id
        self.doper = doper
        self.state = state
        self.state_one = state_one
        self.contract_number = contract_number
        select = """ select d.LONGNAME as Longname,
        substr(T_PkgArlClc.fPntStat(s.TT_ID, s.TT_NORD, c.ARL_ID), 1, 250) as STATE
        from TT_POINT p, T_DEASHDPNT s, T_ARLCLC c, T_ARLDEA ad, T_ARLDSC d
        where s.CLC_ID = c.ID
        and c.ARL_ID = d.ID
        and ad.DEP_ID = s.DEP_ID
        and ad.ORD_ID = s.ORD_ID
        and ad.CLC_ID = c.ID
        and p.ID = s.TT_ID
        and p.NORD = s.TT_NORD
        and s.DEP_ID = """ + self.dep_id + """
        and s.ORD_ID = """ + self.id + """
        and s.doper = '""" + self.doper + """'
        order by s.DOPER, d.LONGNAME, p.NN """
        result = self.OracleHandlerDB(select)
        if result is not None:
          for line in result:
            if line[1].startswith(self.state):
              Log.Checkpoint('Выставленные суммы в графике ' + line[0] + ' успешно переведены в состояние ' + str(self.state) + ' договор ' + str(self.contract_number))
            elif line[1].startswith(self.state_one):
              Log.Checkpoint('Выставленные суммы в графике ' + line[0] + ' успешно переведены в состояние ' + str(self.state_one) + ' договор ' + str(self.contract_number))
            else:
              Log.Warning("Ожидался статус " + self.state_one + " в графике, а получен - " + line[1] + " по виду сумм " + line[0] + ' договор ' + str(self.contract_number))

    def OperationCalls(self, dep_id, id, opercode, name_window, login_user, params=''):
        """ Оптимизированный метод вызова операции АБИС Colvir, вызов на уровне БД (не в клиентской),
        перед вызовом, проверяется доступность операции во вкладке 'Операции';
        входные параметры: подразделение документа, идентификатор документа, код выполняемой операции,
        передача параметров в операцию"""
        self.dep_id = dep_id
        self.id = id
        self.opercode = opercode
        self.name_window = name_window
        self.login_user = login_user
        self.params = params
        # получим опер.день из переменной среды(важно)
        date_operday = self.GetEnviron("DATE_OPERDAY")
        to_date = aqConvert.DateTimeToFormatStr(date_operday, "%d.%m.%Y")
        # проверим доступность операции для документа
        query = """ select T_PkgRunOprUtl.fOprAvailable(To_Number (""" + self.dep_id + """), To_Number (""" + self.id + """),
                                                        '""" + self.opercode + """') from dual
        """
        result = self.OracleHandlerDB(query)
        if result is not None:
          if result[0][0] == 1:
            Log.Warning('Недостаточно прав для выполнения операции ' + self.opercode)
          elif result[0][0] == 2:
            Log.Checkpoint('Операция ' + self.opercode + ' доступно для запуска')
            if self.params:
              query = """
              declare begin c_pkgconnect.popen();
                      colvir.c_pkgconnect.popenlink('""" + login_user + """', 1);
                      c_pkgsession.doper := '""" + to_date + """';
                      begin T_PkgRunOprUtl.pRunOprByMainOrd(""" + self.dep_id + """,""" + self.id + """,
                                '""" + self.opercode + """', """ + self.params + """); commit; end; end;
              """
              self.OracleHandlerDB(query, dml_query='True')
              # нужно кликнуть обновить
              btn_refresh = Sys.Process("COLVIR").VCLObject(self.name_window).VCLObject("btnRefresh")
              btn_refresh.Click()
            else:
              query = """
              declare begin c_pkgconnect.popen();
                      colvir.c_pkgconnect.popenlink('""" + login_user + """', 1);
                      c_pkgsession.doper := '""" + to_date + """';
                      begin T_PkgRunOprUtl.pRunOprByMainOrd(""" + self.dep_id + """,""" + self.id + """,'""" + self.opercode + """');
                      commit; end; end;
              """
              self.OracleHandlerDB(query, dml_query='True')
              # нужно кликнуть обновить
              btn_refresh = Sys.Process("COLVIR").VCLObject(self.name_window).VCLObject("btnRefresh")
              btn_refresh.Click()
          else:
            Log.Warning('Недоступна из данного состояния для выполнение операции ' + self.opercode)
        else:
          Log.Warning('Результат метода OperationCalls вернул пустое значение, требуется проверить!!')

    def CreateDatasetTable(self, tablename):
        """ Метод для работы с датасетами в БД.
        Если в аргумент tablename передать просто имя датасета без цифр, из эталона будет создан датасет с именем
        формата tablename_xxxxx где x это рандомные цифры.
        Если в аргумент tablename передать имя формата tablename_xxxxx где x это цифры в имени,
        то новый датасет не создается проверяется только наличие таблицы заданой в аргументе tablename в БД"""
        self.tablename = tablename.replace('[','').replace(']','').replace('\'','').strip()
        Log.Message('Запрос на создание\проверку наличия датасета в БД ' + self.tablename)
        result = self.OracleFunctionExecute('z_026_fUpdDataset',str,None,self.tablename)
        if result is not None:
          return result
        else:
          Log.Error('Ошибка при работе с датасетом в БД ' + self.tablename)
          result = ''
          return result

    def ReadDatasetFromDB(self, tablename):
        """ Зачитывание таблицы из БД, с возвращением списка с ключами, где поля таблицы БД это ключи,
        и где значения таблицы это значения ключей"""
        self.tablename = tablename
        need_dataset = ''
        exception_list = ['loginpool']
        if self.tablename.lower() not in exception_list:
          get_datasets_str = self.GetEnviron('DATASET_TABLE').replace('[','').replace(']','').replace('\'','')
          Log.Message('Датасеты в переменной среде DATASET_TABLE ' + str(get_datasets_str))
          for dataset in get_datasets_str.split(','):
            # Убераем знак '_' и цифры в окончании таблицы
            if re.sub('_\d+', '', dataset.lower().strip()) == self.tablename.lower():
              need_dataset = dataset.strip()
        else:
          need_dataset = self.tablename
        global_list = []
        column_list = []
        if need_dataset:
          Log.Message('Запрошен из БД датасет ' + need_dataset)
          column = """ select column_name from all_tab_columns where table_name = upper('""" + need_dataset + """') order by column_id """
          select = """ select * from """ + need_dataset + """ """
          result_column = self.OracleHandlerDB(column)
          result_select = self.OracleHandlerDB(select)
          if result_column is not None and result_select is not None:
            for conrs in result_column:
              column_list.append(conrs[0])
            for corts in result_select:
              dict = {}
              for columns,value in zip(column_list,corts):
                dict[columns]=value
              global_list.append(dict)
        else:
          Log.Warning('В переменной среде DATASET_TABLE не найден датасет по алиасу ' + str(self.tablename))
        return global_list

    def UpdateDatasetTableDB(self, tablename, global_list):
        """ Обновление данных таблицы БД, global_list в качестве массива, с которого данные
        вставляются в таблицу БД, а tablename в качестве таблицы БД, которая в свою очередь очищается"""
        self.tablename = tablename
        self.global_list = global_list
        need_dataset = ''
        get_datasets_str = self.GetEnviron('DATASET_TABLE').replace('[','').replace(']','').replace('\'','')
        Log.Message('Датасеты в переменной среде DATASET_TABLE ' + str(get_datasets_str))
        for dataset in get_datasets_str.split(','):
          # Убираем знак '_' и цифры в окончании таблицы
          if re.sub('_\d+', '', dataset.lower().strip()) == self.tablename.lower():
            need_dataset = dataset.strip()
        if need_dataset:
          Log.Message('Обновление данных датасета ' + str(need_dataset))
          truncate = """ TRUNCATE TABLE """ + need_dataset + """ """
          result_truncate = self.OracleHandlerDB(truncate, dml_query='True')
          result_column = ", ".join(self.global_list[0].keys())
          result_select = ''
          for dictionary in self.global_list:
            result_select = ", ".join((map(lambda val: "'"+ str(val).replace('\'','"')+"'" if val is not None else "''", dictionary.values())))
            insert = """ begin INSERT INTO """ + need_dataset + """ ({}) VALUES ({}); commit; end;""".format(result_column,result_select)
            result_insert = self.OracleHandlerDB(insert, dml_query='True')
        else:
          Log.Warning('В переменной среде DATASET_TABLE не найден датасет по алиасу ' + str(self.tablename))

    def ResetStatusDdpvcs(self, name_object):
        """ Сброс статуса объекта в задаче DDPVCS, обязательное применение при изменений/обновлений объекта в АБИС
        """
        self.name_object = name_object
        result = """ begin update c_vcs v set v.USR_ID = null
                     where v.code like ('%""" + self.name_object+ """%');
                     commit; end;
                 """
        self.OracleHandlerDB(result, dml_query='True')
        Log.Event('Сброшен статус объекта '  + self.name_object +  ' в задаче DDPVCS')

    def OperDayValue(self):
        """В данной функции открывается окно с оперднем. Из него берется дата опердня. Окно закрывается"""
        Sys.Process("COLVIR").VCLObject("AppLayer").VCLObject("MainPanel").DblClick(1714, 16) # Вызывается окно с системной датой, в левом верхнем углу
        od_value = Sys.Process("COLVIR").VCLObject("frmOprDayDialog").VCLObject("edOperDay").Window("TClMaskEdit", "__.__.__", 1).Value # Берется значение даты опердня
        Sys.Process("COLVIR").VCLObject("frmOprDayDialog").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnCancel").Click() # Закрывается окно с датой опердня
        return od_value

    def CheckPassOff(self):
        """Функция отключающая проверку OTP пароля и нажимающая кнопку Ок в окне Признак проверки OTP пароля"""
        self.WaitLoadWindow('frmDynamicDialog')
        cansel_sms = self.FindChildField("frmDynamicDialog", "Name", "VCLObject('OTP_FL')")
        cansel_sms.Click()
        but_sms = self.FindChildField("frmDynamicDialog", "Name", "VCLObject('btnOK')")
        but_sms.Click()

    def SystemDateValue(self):
        sys_date = """ select trunc(sysdate) from Dual """
        result_date = self.OracleHandlerDB(sys_date)
        today_date = result_date[0][0].strftime("%d.%m.%Y")
        # добавить условие или новую функцию
        return today_date

    def GetBlockAcc(self, doc_number, number_acc):
        """Функция принимает номер документа и номер счета
        Возвращает тип блокировки и количество блокировок по переданным номеру договора и счета клиента
        Данные из БД возвращаются кортежем в списке"""
        self.doc_number = doc_number
        self.number_acc = number_acc
        date_block = self.SystemDateValue()
        select_block = """ select lt.longname from G_LOCK gl, G_ACCBLN ga, G_LOCKTYPE lt
                           where gl.acc_id = ga.id and gl.dep_id = ga.dep_id and gl.locktype = lt.id 
                                 and ga.code = '""" + self.number_acc + """' and gl.fromdate = '""" + date_block + """' 
                                 and LORDNUM = '""" + self.doc_number + """' and gl.todate is null
                       """
        select_count = """ select count(gl.id) from G_LOCK gl, G_ACCBLN ga, G_LOCKTYPE lt
                           where gl.acc_id = ga.id and gl.dep_id = ga.dep_id and gl.locktype = lt.id 
                           and ga.code = '""" + self.number_acc + """' and gl.fromdate = '""" + date_block + """' 
                           and LORDNUM = '""" + self.doc_number + """' and gl.todate is null
                       """
        type_block_acc = self.OracleHandlerDB(select_block)
        count_block_acc = self.OracleHandlerDB(select_count)
        return type_block_acc, count_block_acc

    def SumHoldByAccCode(self, acc_number):
        """Функция возвращает сумму холдов по переданному счету"""
        self.acc_number = acc_number
        select_amount = """ select SUM(APT_HLD_BALT.amount)
                            from APT_IDN @cap, APT_HLD_BALT @cap
                            where APT_IDN.acc_id = APT_HLD_BALT.acc_id
                                  and APT_IDN.code = '""" + self.acc_number + """'
                        """
        sum_holds = self.OracleHandlerDB(select_amount)
        return sum_holds

    def SumLimByAccCode(self, acc_number, date_lim, doc_number):
        """Функция принимает номер счета, дату выставления лимита, номер документа ИР и возвращает описание лимита
        и сумму лимита. Данные возвращаются кортежами в списке"""
        self.acc_number = acc_number
        self.date_lim = date_lim
        self.doc_number = doc_number
        select_limit = """ select ta.longname, tv.bal from T_ACCLIMTYP_STD ta, T_LIM tl, g_accbln ga, T_LIMVAL tv
                           where ta.id = tl.limtyp and tl.acc_id = ga.id
                           and tl.id = tv.id and ga.code = '""" + self.acc_number + """' and tv.fromdate = '""" + self.date_lim + """' 
                           and tl.prim like '%""" + self.doc_number + """%'
                       """
        list_data_lim = self.OracleHandlerDB(select_limit)
        return list_data_lim

    def CheckAccServInPS(self, acc_number):
        """Функция принимает номер счета и возвращает признак обслуживания в ПС. 0 - не обслуживается.
        1 - обслуживается"""
        self.acc_number = acc_number
        select_capfl = """ select capfl from g_accbln
                           where code = '""" + self.acc_number + """'
                       """
        list_capfl = self.OracleHandlerDB(select_capfl)
        capfl = list_capfl[0][0]
        return capfl

    def GetCodePSAcc(self, acc_code):
        """Функция возвращает ПС счета. На вход подается номер счета"""
        self.acc_code = acc_code
        select_code_ps = """ select ls.code from LEDACC_STD ls, LEDACC l, G_ACCBLN ga
                           where ga.CHA_ID=L.ID and ls.id = l.id 
                                 and ga.code = '""" + self.acc_code + """'
                       """
        list_ps_code = self.OracleHandlerDB(select_code_ps)
        ps_code = list_ps_code[0][0]
        return ps_code

    def GetRateVal(self, code_val):
        """Функция возвращает последний курс в зависимости от переданной валюты"""
        self.code_val = code_val
        select_code_val = """ select RATE from 
                              (SELECT RATE FROM TV_VALRAT
                               WHERE VAL_CODE = '""" + self.code_val + """'
                               ORDER BY FROMDATE DESC)
                              WHERE ROWNUM = 1
                          """
        list_code_val = self.OracleHandlerDB(select_code_val)
        rate = list_code_val[0][0]
        return rate

    def ChangeTypeSuspension(self, type_suspension):
        """Функция выбирает необходимый тип приостановки по счету в зависимости от переданного типа приостановки.
        На вход подается тип приостанвоки"""
        self.type_suspension = type_suspension
        all_suspension = ()
        ed_type = self.FindChildField("frmArestop", "Name", "VCLObject('edType')")
        change_btn = ed_type.VCLObject("TClSpeedButton")
        change_btn.Click()
        self.WaitLoadWindow("frmArestopRef")
        while 0 < 1:
          need_field = self.GetGridDataFields("frmArestopRef", "NAME", need_tab='qryReference')
          need_suspension = need_field[0].replace("\'", '')
          Log.Message(need_suspension)
          if need_suspension in all_suspension:
            Log.Error('Не найден необходимый тип приостановки ' + self.type_suspension)
            break
          all_suspension += (need_suspension,)
          if self.type_suspension == need_suspension:
            btn_confirm = self.FindChildField("frmArestopRef", "Name", "VCLObject('btnOK')")
            btn_confirm.Click()
            break
          else:
            LLPlayer.KeyDown(VK_DOWN, 300) # нажатие стрелки вниз 1 раз
            LLPlayer.KeyUp(VK_DOWN, 300)
        Log.Message(all_suspension)
    
    def GetSysDate(self):
        """Функция получает системную дату и уберает точки. Затем возвращает число"""
        select = """
                 select trunc(sysdate) from dual
                 """
        get_date = self.OracleHandlerDB(select)
        format_date = get_date[0][0].strftime("%d.%m.%Y")
        result = str(format_date).replace('.', '')
        return result
        
    def GetSysDateShort(self):
        """Функция получает системную дату и уберает точки. Затем возвращает число.
        В данной функции возвращаются последние 2 цифры года"""
        select = """
                 select trunc(sysdate) from dual
                 """
        get_date = self.OracleHandlerDB(select)
        format_date = get_date[0][0].strftime("%d.%m.%y")
        result = str(format_date).replace('.', '')
        return result

  
    def GetLastDayMonth(self, full_year = False):
        """Функция возвращает последний день месяца в формате ддммгг
        Если передать флаг full_year = True, то вернется формат ддммгггг"""
        self.full_year = full_year
        currentMonth = datetime.now().month
        currentYear = datetime.now().year
        last_day = calendar.monthrange(currentYear, currentMonth)[1]
        try:
            last_day_month = datetime.strptime(f'{last_day}{currentMonth}{currentYear}', '%d%m%Y')
        except TypeError:
            last_day_month = datetime(*(time.strptime(f'{last_day}{currentMonth}{currentYear}', '%d%m%Y')[0:6]))
        if self.full_year == True:
            str_last_day_month = last_day_month.strftime('%d%m%Y')
        else:
            str_last_day_month = last_day_month.strftime('%d%m%y')
        return str_last_day_month
 
    def SendRequestFromFile(self, name_file):
        """Функция открывает файл и преобразовывает строки файла в список, для отправки запроса в БД"""
        self.name_file = name_file
        try:
            with open(self.name_file, 'r', encoding='utf-8') as file:  # Открытие файла
                sql_statements = file.readlines() # Преобразование строк файла в список
                for row in sql_statements:
                  self.OracleHandlerDB(row, dml_query=True)  # Отправка запросов по строчно
            file.close()   # Закрытие файла
        except FileNotFoundError:
            Log.Warning(f"Не найден файл с указанным названием {self.name_file}")
        except UnicodeDecodeError as utf:
            Log.Warning(f'Возникла ошибка - {utf}')
        except Exception as other:
            Log.Warning(f'Возникла ошибка - {other}')


    def ChangingOperDayInColvir(self, new_date, format):
        """Функция меняет опердень в Колвире на дату, которую ей передать"""
        self.new_date = new_date
        self.format = format # Если дата передается как строка, то необходимо указывать формат даты для преобразования в строку
                             # Например, если дата передается, как 01.12.23, то формат будет -  '%d.%m.%y'
        # Производится форматирование переданной даты, так как для опердня необходимо передавать короткий год и без точек
        if isinstance(self.new_date, str):
            Log.Message(self.new_date)
            Log.Message(self.format)
            try:
                get_date_obj = datetime.strptime(str(self.new_date), str(self.format))
            except TypeError:
                get_date_obj = datetime(*(time.strptime(str(self.new_date), str(self.format))[0:6]))
            get_date_str = get_date_obj.strftime('%d.%m.%y')
            format_date = get_date_str.replace('.', '')
            Log.Event('Объект str переформатирован под нужный формат даты')
        elif isinstance(self.new_date, datetime):
            date_obj = self.new_date.strftime('%d.%m.%y')
            format_date = date_obj.replace('.', '')
            Log.Event('Объект datetime переформатирован под нужный формат даты')
        # Смена опердня
        Sys.Process("COLVIR").VCLObject("AppLayer").VCLObject("MainPanel").DblClick(1714, 16)
        self.WaitLoadWindow('frmOprDayDialog', time_await=80000)
        date_oper = self.FindChildField("frmOprDayDialog", "Name", 'VCLObject("edOperDay")')
        date_oper.DblClick()
        date_oper.Keys(format_date) # Вставляем переформатированную дату
        btn_ok_date = self.FindChildField("frmOprDayDialog", "Name", 'VCLObject("btnOK")')
        btn_ok_date.Click()
        if Sys.Process("COLVIR").WaitDialog("Внимание", 3000).Exists:
            btn_yes = Sys.Process("COLVIR").Dialog("Внимание").VCLObject("Yes")
            btn_yes.Click()
            btn_ok_after = self.FindChildField("frmOprDayDialog", "Name", 'VCLObject("btnOK")')
            btn_ok_after.Click()
        btn_ok_oper = Sys.Process("COLVIR").Dialog("Colvir Banking System").UIAObject("Colvir_Banking_System").Window("CtrlNotifySink", "", 7).Button("OK")
        btn_ok_oper.Click()
        Log.Event(f"Опер день изменен на дату санкционирования - {format_date}")

    def GetNumCassUser(self, user_code):
        """Функция возвращает номер кассы пользователя-кассира.
        Данная функция необходима для автоматизированного открытия кассы
        для конкретного пользователя"""
        self.user_code = user_code
        select = """
                    select distinct op.CODE from C_USR U, M_CSHDSC op, T_ORD o
                    where op.ID_US = U.ID and op.DEP_ID = o.DEP_ID and op.ID = o.ID and U.CODE like '"""+self.user_code+"""%' 
                          and op.DEP_ID = 1552
                          and substr(bs_dom.DLongname('M_CSHDSC_CSHTYPE', op.CSHTYPE),1,50) = 'Касса  РКО'
                 """
        get_num = self.OracleHandlerDB(select)
        result = get_num[0][0]
        return result

    def RenameClient(self, iin, longname, inicials, name, surname, patronymic=None):
        """Функция переименовывает тестовых клиентов, так как они в бд шифруются цифрами и буквами
        и в некоторых случаях контрольки выдают ошибку, так как нельзя использовать в фио
        кириллицу и латиницу, цифры и буквы
        Функция принимает ИИН клиента, ФИО, Имя, Фамилию, Отчество. Если отчества нет, то ничего не передавать"""
        self.iin = iin
        self.longname = longname
        self.inicials = inicials # Фамилия и инициалы
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        select = """
                     begin
                     update g_clihst h
                     set longname = '"""+self.longname+"""', name = '"""+self.inicials+"""', 
                     pname1 = '"""+self.name+"""', pname2 = '"""+self.surname+"""', 
                     pname3 = '"""+self.patronymic+"""'
                     where taxcode = '"""+self.iin+"""';
                     begin
                     commit; end; end;
                 """
        try:
            result = self.OracleHandlerDB(select)
        except Exception:
            Log.Event('Выполнен апдейт в обход ошибки')

    def GetOTPPassword(self):
        """Функция возвращает ОТП пароль. Функция должна вызываться после запуска формы ввода
        ОТП пароля в Колвире, так как она возвращает последний сформированный пароль в БД"""
        select = """
                    select DBMS_LOB.substr(MSG_XML, 3000) as text from c_msgqueuejrn j
                    WHERE j.dord >= trunc(sysdatE)
                        and dscr = 'SingleDirect'
                        and id = (select max(id) from c_msgqueuejrn where dord >= trunc(sysdate) and dscr = 'SingleDirect')
                 """
        result = self.OracleHandlerDB(select)
        Log.Message(result[0][0])
        get_code = re.findall(r'\S\d+', result[0][0]) # с помощью регулярных выражений получаем код пароля
        Log.Message(get_code[-1].strip())
        return get_code[-1].strip() # убираем возможные пробелы в начале и конце строки b возвращаем
      
    def GetOTPPasswordSsafeord(self):
        """Функция возвращает ОТП пароль. Функция должна вызываться после запуска формы ввода
        ОТП пароля в Колвире при регситрации сейфого договора в задаче Ssafeord, так как она возвращает последний сформированный пароль в БД"""
        select = """
                    select DBMS_LOB.substr(MSG_XML, 3000) as text from c_msgqueuejrn j
                    WHERE j.dord >= trunc(sysdatE)
                        and dscr = 'SingleDirect'
                        and id = (select max(id) from c_msgqueuejrn where dord >= trunc(sysdate) and dscr = 'SingleDirect')
                 """
        result = self.OracleHandlerDB(select)
        Log.Message(result[0][0])
        get_code = re.findall(r'\d+', result[0][0]) # с помощью регулярных выражений получаем код пароля
        for row in get_code:
            if len(row) > 3 and len(row) < 5:
                Log.Message(row.strip())
                return row.strip()

    def CashInSoap(self, acc_crd, amount, cur):
        """ Пополнение счета через Soap операцию 2405, для отработки запроса, требуется счет, Cумма, валюта, и порт"""
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.GetRandomNumber()
        # Аргумент port меняем в зависимости от требуемой базы, дописывая в аргументы функции к примеру - "TP" соответственно операция пройдет на базе ТП
        stand, alias = self.GetTestStandAliasDB()
        if alias.lower() in ['cbs3tp']:
          ADDR = "8201"
        elif alias.lower() == 'cbs3bt':
          ADDR = "8181"
        elif alias.lower() in ['cbs3yes']:
          ADDR = "8221"
        elif alias.lower() == 'cbs3test':
          ADDR = "8231"
        # В зависимости от типа
        if "KZ" in acc_crd:
          Type = "IBN"
        else:
          Type = "CRC"
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f''' <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata" xmlns:v1="http://bus.colvir.com/common/v1">
                    <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                    <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2405</wsa:Action>
                    <wsa:MessageID>{randid}</wsa:MessageID>   <!-- Используем генерацию рандомных чисел в ID -->
                       </soapenv:Header>
                       <soapenv:Body>
                          <ws:finaRequest version='3.0'>
                             <v3:header>
                                <v1:channel>OW4</v1:channel>
                                <v1:reference>{randid}</v1:reference>
                                <v1:date>{today}T{dt_string}</v1:date>            
                                <v1:language>en</v1:language>            
                             </v3:header>
                             <ws:body>
                                <fina:operation>2405</fina:operation>            
                                <fina:description>Note Acceptance</fina:description>
                                <fina:amount currency="{cur}">{amount}</fina:amount>    <!-- Указываем сумму пополнения -->                    
                                <fina:account type="{Type}">{acc_crd}</fina:account>       <!-- Вписываем счет для пополнения, если хотим карточный счет IBN меняем на CRC и вписываем IDN карты -->                 
                                <xdat:xData>
                                   <xdat:trn>                  
                                      <xdat:card>                     
                                         <xdat:a>{amount}</xdat:a>  <!-- Указываем сумму пополнения -->   
                                         <xdat:c>{cur}</xdat:c>                                          
                                         <xdat:pan>{acc_crd}</xdat:pan> <!-- Используем переменную счета -->
                                         <xdat:panm>7777_7777</xdat:panm>  <!-- Используем зашифрованные цифры карты -->              
                                         <xdat:auth>534892</xdat:auth>                                          
                                         <xdat:acq>00001</xdat:acq>
                                         <xdat:mcc>6012</xdat:mcc>                     
                                         <xdat:acqc>398</xdat:acqc>                     
                                         <xdat:term>00130866</xdat:term>                     
                                         <xdat:caid>TestCashIn</xdat:caid> <!-- Используем IDN карты -->
                                         <xdat:loc>TESTCENTER</xdat:loc>
                                         <xdat:termtype>POS</xdat:termtype>
                                         <xdat:psys>ON-US</xdat:psys>                     
                                         <xdat:posmode/>
                                      </xdat:card>                  
                                   </xdat:trn>
                                </xdat:xData>
                             </ws:body>
                          </ws:finaRequest>
                       </soapenv:Body>
                    </soapenv:Envelope>        
         '''
        data=data.encode()
        response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap11/v3', data=data, headers=headers)
        # Обрабатываем процедуры с джобами для перевода суммы с ПС в АБС
        for i in range(5):
            prosedure_6975 = """
                              begin
                                  c_pkgconnect.popen(); 
                                  c_pkgsession.doper := trunc(sysdate);
                                  G_PKGCAPIMPORTABS.pProcImportToTblJob(p_dNextDate => trunc(sysdate),
                                                                        p_nJobID    => 6975);
                              end; 
                             """
            procedure_6973 = """
                              begin
                                  c_pkgconnect.popen(); 
                                  c_pkgsession.doper := trunc(sysdate);
                                  G_PKGCAPIMPORTABS.pProcImportToABSJobNoSync(p_dNextDate => trunc(sysdate),
                                                                        p_nJobID    => 6973);
                              end; 
                           """
            execute_6975 = self.OracleHandlerDB(prosedure_6975, dml_query = True, need_zero = True)
            execute_6973 = self.OracleHandlerDB(procedure_6973, dml_query = True, need_zero = True)
            Delay(2000)

    def GetDataArcClient(self, pboyulfl, jurfl):
        """Функция принимает  параметры клиента, ип и юр. лицо и возвращает
        Если передать pboyulfl = 0 , jurfl = 0, то вернутся физ лицо без ИП
        Если передать pboyulfl = 1 , jurfl = 0, то вернутся физ лицо ИП
        Если передать pboyulfl = 0 , jurfl = 1, то вернутся юр лицо
        ИИН клиента, дату рождения и пол"""
        self.pboyulfl = pboyulfl
        self.jurfl = jurfl
        select = """
                    select gh.taxcode, g.BIRDATE, gh.PSEX from g_cli g
                    left join g_clihst gh ON g.id = gh.id and g.dep_id = gh.dep_id
                    left join g_accblnhst ag ON g.id = ag.cli_id and g.dep_id = ag.clidep_id
                    left join g_accbln a ON a.id = ag.id and a.dep_id = ag.dep_id
                    WHERE trunc(sysdate) between gh.fromdate and gh.todate
                          and gh.ARCFL = 1 and gh.taxcode is not null and g.BIRDATE is not null and gh.PSEX is not null
                          and PBOYULFL = '"""+str(self.pboyulfl)+"""'
                          and JURFL = '"""+str(self.jurfl)+"""'
                          and (select g.code from g_cli g
                               left join g_clihst gh ON g.id = gh.id and g.dep_id = gh.dep_id
                               left join g_accblnhst ag ON g.id = ag.cli_id and g.dep_id = ag.clidep_id
                               left join g_accbln a ON a.id = ag.id and a.dep_id = ag.dep_id
                               where gh.ARCFL = 1 and gh.taxcode is not null and g.BIRDATE is not null and gh.PSEX is not null
                                     and PBOYULFL = '"""+str(self.pboyulfl)+"""'
                                     and JURFL = '"""+str(self.jurfl)+"""'
                                     and rownum = 1
                               group by g.code
                               having count(g.code) = 1) is not null
                          and a.CODE is null
                          and rownum = 1
                 """
        result = self.OracleHandlerDB(select)
        if result is None:
            Log.Warning('Запрос не вернул ни одной строки')
        else:
            Log.Event('Запрос вернул данные')
        return result

    def ConvertDateToString(self, date_object, format):
        """Функция принимает объект даты и фоормат, и возвращает строку с датой в необходимом формате
        Передается формат типа '%d.%m.%Y'"""
        self.date_object = date_object
        self.format = format
        date_string = self.date_object.strftime(self.format)
        return date_string

    def DateIncrease(self, date_str, format, cnt_inc, type_inc = 'days', type_year = 'yy'):
        """метод принимает строку с датой
        format - строка формата даты. К примеру, если дата 01.01.2000, то формат %d.%m.%Y
        количество увеличения (cnt_inc)
        тип увеличения (type_inc): days, weeks. По умолчанию type_inc = days
        и увеличивает дату type_year - тип кода (yy или yyyy). По умолчанию yy"""
        self.date_str = date_str
        self.cnt_inc = cnt_inc
        self.type_inc = type_inc
        self.type_year = type_year
        Log.Message(self.date_str)
        try:
            Begindate = datetime.strptime(self.date_str, format)
        except TypeError:
            Begindate = datetime(*(time.strptime(self.date_str, format)[0:6]))
        except Exception as e:
            Log.Error(f"При конвертации даты возникла ошибка - {e}. По всей видимости передано неверное значение в параметр date_str. Формат даты должен быть dd.mm.yyyy")
        if type_inc == 'days':
            Enddate = Begindate + timedelta(days=cnt_inc)
        elif type_inc == 'weeks':
            Enddate = Begindate + timedelta(weeks=cnt_inc)
        else:
            Log.Warning(f'Передан неверное значение {type_inc} в параметр type_inc')
        if type_year == 'yy':
            date_inc = self.ConvertDateToString(Enddate, "%d%m%y")
        elif type_year == 'yyyy':
            date_inc = self.ConvertDateToString(Enddate, "%d%m%Y")
        else:
            Log.Warning(f'Передан неверное значение {type_year} в параметр type_year')
        return date_inc

    def GetDocNumber(self):
        """Функция возвращает девятизначное рандомное число"""
        return randint(100000001, 999999999)

    def GetLoginIndex(self):
        """метод возвращает словарь с неймингами и индексами пользователей из переменной среды LOGIN_INDEX_LIST"""
        get_variable = self.GetEnviron('LOGIN_INDEX_LIST')
        normal_list = get_variable.replace(' ', '').split(':')
        list_log_pas = normal_list[1].replace(' ', '').split(',')
        list_log_pas = [item.split('=') for item in list_log_pas]
        dict_index = dict(list_log_pas) # преобразуем в словарь
        return dict_index

    def GetDataUser(self, login_index):
        """метод возвращает логин пользователя и принимает нейминг пользователя в LOGIN_INDEX_LIST"""
        self.login_index = login_index
        # получаем словарь с индексами пользователей в LOGIN_INDEX_LIST
        dict_index = self.GetLoginIndex()
        # получаем логин пользователя в датасете Loginpool
        # где индекс в LOGIN_INDEX_LIST = ID пользователя в Loginpool
        select = """ SELECT TEST_LOGIN FROM LOGINPOOL WHERE INDEX_LOGIN = """+ str(dict_index[self.login_index]) +""" """
        try:
            result = self.OracleHandlerDB(select)
            return result[0]
        except KeyError as e:
            Log.Warning(f'Переданный ключ отсутствует в словаре - {str(e)}')

    def TakeOffAdminUserPrm(self, login_index):
        """метод принимает наименование пользователя в loginIndexListStorage
        и убирает признак администратора пользователя, если данный признак
        установлен по данному пользователя
        данный метод необходим, чтобы убрать признак администратора
        так как в кейсах где есть несколько санкционирований операции разными пользователями
        пользователь с признаком админа будет санкционировать за всех"""
        self.login_index = login_index
        # получаем логин пользователя по неймингу в loginIndexListStorage
        login = self.GetDataUser(self.login_index)
        Log.Message(login)
        self.OracleCallProcedure("Z_PKG_AUTO_TEST.AddTakeOffAdmPrm", login[0], 0) # процедура убирает признак админа
      
    def ReturnAdminUserPrm(self, login_index):
        """метод принимает наименование пользователя в loginIndexListStorage
        и устанавливает признак администратора пользователя, если данный признак
        установлен по данному пользователя
        данный метод необходим, чтобы вернуть признак администратора
        после санкционироввания операции под данным пользователем"""
        self.login_index = login_index
        # получаем логин пользователя по неймингу в loginIndexListStorage
        login = self.GetDataUser(self.login_index)
        Log.Message(login)
        self.OracleCallProcedure("Z_PKG_AUTO_TEST.AddTakeOffAdmPrm", login[0], 1) # процедура возвращает признак админа
      
    def SetUserGrn(self, id_user_pos, type_grn, id_grn, id_grn_2 = None):
        """Метод устанавливает необходимое полномочие пользователю"""
        self.id_user_pos = id_user_pos # id позиции пользователя в usrgrn
        self.type_grn = type_grn # тип полномочия
        self.id_grn = id_grn # id полномочия
        self.id_grn_2 = id_grn_2 # id профиля, если необходимо передавать
        try:
            self.OracleCallProcedure("Z_PKG_AUTO_TEST.AT_pSetGrn", self.id_grn, self.id_grn_2, self.id_user_pos, self.type_grn)
            Log.Event("Пользователю добавлено полномочие для открытия опердня")
        except Exception as error:
            Log.Event(f"Возникла ошибка - {error}")
          
    def CreateDeaSks(self, cli_code, type_dea, num_dea, trf_id):
        """метод вызывает процедуру для создания договора СКС"""
        self.cli_code = cli_code # код клиента
        self.type_dea = type_dea # тип договора
        self.num_dea = num_dea # номер договора (Рандомный)
        self.trf_id = trf_id # id тарифной категории
        try:
            result = self.OracleCallProcedure("Z_PKG_AUTO_TEST.AT_pCreSKSDea", self.cli_code, self.type_dea, self.num_dea, self.trf_id, return_value = True, num_out = ["1"])
            if result[0][1].strip() == f"Создан договор СКС по номеру договора - {self.num_dea}":
                Log.Event(f"Создан договор СКС - {self.num_dea}")
            else:
                Log.Warning(f"Не создан договор СКС - {self.num_dea}")
        except Exception as error:
            Log.Event(f"Возникла ошибка - {error}")
        return result[0][1]
      
    def CreCardPool(self, dep_code, product_card, val_code, count_card):
        """метод вызывает процедуру для создания пула неименованных карт"""
        self.dep_code = dep_code
        self.product_card = product_card
        self.val_code = val_code
        self.count_card = count_card
        try:
            result = self.OracleCallProcedure("Z_PKG_AUTO_TEST.AT_pCreNoPersonalCard", self.dep_code, self.product_card, self.val_code, self.count_card)
            Log.Event("Создан пул неименованных карт")
        except Exception as error:
            Log.Event(f"Возникла ошибка - {error}")
      
    def CreCardDea(self,dep_id,dea_code_sks,dcl_code,crd_id,cardcode,embossedname,cli_code,acc_code,val_code,
                   trf_code,code_idn,noembfl):
        self.dep_id = dep_id # id департамента карточного договора, который будет создаваться в данном методе
        self.dea_code_sks = dea_code_sks # номер договора СКС к которому будет добавлен карточный договор
        self.dcl_code = dcl_code # код продукта карточного договора с которым будет создавать карт договор
        self.crd_id = crd_id # id типа карты. Для неименных 897
        self.cardcode = cardcode # код карточки из пула crdreq
        self.embossedname = embossedname # имя клиента на карточке
        self.cli_code = cli_code # код клиента
        self.acc_code = acc_code # номер текущего счета клиента
        self.val_code = val_code # код валюты
        self.trf_code = trf_code # код тарифа
        self.code_idn = code_idn # idn карточки из пула crdreq
        self.noembfl = noembfl # признак неименной карточки. 0 - нет, 1 - да
        try:
            result = self.OracleCallProcedure("Z_PKG_AUTO_TEST.AT_pCreCardDea", self.dep_id,
                                                                                self.dea_code_sks,
                                                                                self.dcl_code,
                                                                                self.crd_id,
                                                                                self.cardcode,
                                                                                self.embossedname,
                                                                                self.cli_code,
                                                                                self.acc_code,
                                                                                self.val_code,
                                                                                self.trf_code,
                                                                                self.code_idn,
                                                                                self.noembfl,
                                                                                )
            Log.Event("Создан карточный договор")
        except Exception as error:
            Log.Event(f"Возникла ошибка - {error}")

class GenerateTestingData(ColvirState):
    """Класс с функциями для подготовки тестовых данных перед запуском автотестов"""

    def ColvirPassChange(self, login_index):
        """@title: Изменение пароля пользователю системы
           @custom_preconds: Пользователь: Пользователь: Colvir
           Пользователю можно сменить пароль даже если под ним уже кто-то работает в клиенте,
           так что желательно уточнять по занятости логинов у других тестировщиков или
           использовать непопулярные подразделения, так же можно подсмотреть в PL\SQL Developer
           активные сессии логинов. Так же система запоминает 5 последних паролей, поэтому
           он всегда должен быть новым. После смены пароля, необходимо залогиниться под новым
           паролем и дополнительной сменой на другой новый пароль подтвердить изменение
           пароля - кейс [C4404]. Пароли должны соответствовать парольной политике -
           минимум 8 символов, большие и маленькие буквы и цифры.
           *Важно: выбранный логин может быть в архиве или заблокирован, для того чтобы снять
           ограничения необходимо перед сменой или подтверждением пароля зайти в задачу MUSERL,
           Найти свой логин и с помощью коррекции снять признаки архива и\или блокировки.**
           @custom_autotestslink: COLVIR_PreState/Login_Poll_Pass_Change
           @custom_expected: Если вы попытаетесь сменить пароль, который уже был установлен ранее,
                              то получите ошибку - 'Заданный пароль для учетной записи уже был применен'
        """
        self.login_index = login_index
        data_user = self.GetDataUser(self.login_index) # получаем данные пользователя из LoginPool
        login = data_user[0] # получаем логин пользователя из кортежа
        self.LoginInColvir()
        #start, finish = PassChanger.GetLoginPass('PERIOD')
        data_list = self.ReadDatasetFromDB('LoginPool')
        for counter, row in enumerate(data_list):
          if row['TEST_LOGIN'] == str(login): #and (counter >= str(start) and counter <= str(finish)):
            if self.GetLoginStatus(row['TEST_LOGIN']):
              self.SetLoginUnlock(row['TEST_LOGIN'])
            self.UpdateUserPosition(row['TEST_LOGIN'])
            """ @content: Запустить задачу CPSWRD """
            """ @expected: Откроется окно 'Пользователи' """
            self.TaskInput('CPSWRD')
            """ @content: В окне 'Пользователи' найти необходимый логин или воспользоваться поиском, 
                          нажав любую буквенную клавишу на клавиатуре, затем нажать кнопку 'Ок' """
            """ @expected: Откроется окно 'Смена пароля для %логин%' """
            self.WaitLoadWindow("frmcUserRefer")
            users_window = Sys.Process("COLVIR").VCLObject("frmcUserRefer")
            users_window.Keys('j')  #надо что-нибудь нажать, чтобы открылось окно поиска
            finder_window = Sys.Process("COLVIR").VCLObject("frmFndDialog").VCLObject("edSeek").Window("TClMaskEdit", "j", 1)
            finder_window.DblClick() #затираем мусор последующим вводом
            finder_window.Keys(row['TEST_LOGIN'])
            ok_win_finder = Sys.Process("COLVIR").VCLObject("frmFndDialog").VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK")
            ok_win_finder.Click()
            ok_users_window = users_window.VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK")
            ok_users_window.Click()
            pass_window = Sys.Process("COLVIR").VCLObject("frmPswDialog_1")
            window_title = pass_window.TitleBar(0).Value
            need_user = re.findall(r'\b'+ row['TEST_LOGIN'] + r'\b', window_title) #проверяем на окне ввода пароля, нужный ли логин выбран
            """ @content: В окне 'Смена пароля для %логин%' заполнить поля: 'Новый пароль', 'Подтверждение' 
                          и нажать кнопку 'Ок'.
                          Пароли должны соответствовать парольной политике - минимум 8 символов, большие и маленькие буквы и цифры. """
            if need_user:
              new_pass = pass_window.VCLObject("edtPassword")
              new_pass.Keys(row['TEMP_PASSWORD'])
              confirm_pass = pass_window.VCLObject("edConform")
              confirm_pass.Keys(row['TEMP_PASSWORD'])
              ok_pass_win = pass_window.VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK")
              ok_pass_win.Click()
              if (Sys.Process("COLVIR").WaitVCLObject("ErrMessageForm", 2500).Exists):    #если вылезла ошибка использованного ранее пароля
                Log.Warning("Заданный пароль для учетной записи " + row['TEST_LOGIN'] + " уже был применен")
                err_window = Sys.Process("COLVIR").VCLObject("ErrMessageForm")
                err_window.Close()
                users_window.Close()
              elif (Sys.Process("COLVIR").WaitWindow("#32770", "Colvir Banking System", -1, 2000).Exists):
                """ @expected: Появится окно об успешном назначении нового пароля """
                info_win = Sys.Process("COLVIR").Dialog("Colvir Banking System")
                info_win.Close()
                users_window.Close()
                Log.Checkpoint("Пароль для учетной записи " + row['TEST_LOGIN'] + " успешно изменен!")
            else:
              Log.Warning("Логин пользователя " + row['TEST_LOGIN'] + " не совпадает с логином в окне смены пароля (выбран неверный пользователь из списка)")
              pass_window.Close()
              users_window.Close()
              Log.Warning("Пароль для учетной записи " + row['TEST_LOGIN'] + " не будет изменен")

    def ReloginInColvirPoll(self, login_index):
        """ @title: Подтверждение измененного пароля пользователю системы
            @custom_preconds: Пользователь: Colvir
                              Выполняется после кейса [C4403]
                              Пользователю можно сменить пароль даже если под ним уже кто-то работает в клиенте,
                              так что желательно уточнять по занятости логинов у других тестировщиков или
                              использовать непопулярные подразделения, так же можно подсмотреть в PL\SQL Developer
                              активные сессии логинов. Так же система запоминает 5 последних паролей, поэтому
                              он всегда должен быть новым. После смены пароля, необходимо залогиниться под новым
                              паролем и дополнительной сменой на другой новый пароль подтвердить изменение пароля.
                              Пароли должны соответствовать парольной политике - минимум 8 символов,
                              большие и маленькие буквы и цифры.
                              **Важно: выбранный логин может быть в архиве или заблокирован, для того чтобы
                              снять ограничения необходимо перед сменой или подтверждением пароля зайти в задачу
                              MUSERL, найти свой логин и с помощью коррекции снять признаки архива и\или блокировки.**
            @custom_autotestslink: COLVIR_PreState/Login_Poll_Pass_Confirm
            @custom_expected: Если вы попытаетесь сменить пароль, который уже был установлен ранее,
                              то получите ошибку - 'Заданный пароль для учетной записи уже был применен'
        """
        self.login_index = login_index
        data_user = self.GetDataUser(self.login_index) # получаем данные пользователя из LoginPool
        login = data_user[0] # получаем логин пользователя из кортежа
        # получаем данные типа БД из системной переменной CONFIG_COLVIR
        alias_db = self.GetEnviron('CONFIG_COLVIR')
        alias_db = alias_db.replace(' ', '').replace(':', ',').split(',')[1]
        # получаем временный пароль из БД и постоянный пароль
        db_pass = f'PASSWORD_{alias_db[3:]}'
        select_pass = f""" SELECT TEMP_PASSWORD, {db_pass.upper()} FROM LOGINPOOL WHERE TEST_LOGIN = '{login}' """
        result_pass = self.OracleHandlerDB(select_pass)
        temp_pass = result_pass[0][0]
        db_pass = result_pass[0][1]
        off_block = self.GetAccountStatusDB(login)
        but_login = self.WindowUser()
        if (Sys.Process("COLVIR").WaitVCLObject("frmLoginDlg", 1500).Exists):
          login_window = Sys.Process("COLVIR").VCLObject("frmLoginDlg")
          login_field = login_window.VCLObject("pnlClient").VCLObject("edtName")
          login_field.Keys(login)
          passwd_field = login_window.VCLObject("pnlClient").VCLObject("edtPassword")
          passwd_field.Keys(temp_pass)
          #проверка есть ли поле с алиасом БД
          if (Sys.Process("COLVIR").VCLObject("frmLoginDlg").WaitVCLObject("pnlAlias", 1000).Visible):
            alias_field = login_window.VCLObject("pnlAlias").VCLObject("cbALIAS").Window("Edit", "", 1)
            alias_field.Keys(alias_db)
          ok_login = login_window.VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK")
          ok_login.Click()
           #если вылезла ошибка при входе в систему
          if self.ErrorMessageHandler() and (Sys.Process("COLVIR").WaitWindow("TMessageForm", "Ошибка", -1, 1500).Exists):
            error_limit_window = Sys.Process("COLVIR").Dialog("Ошибка")
            error_limit_window.Close()
            self.KillProcessApp('COLVIR')
            TestedApps.Items[stand].Run() #перезапускаем колвир
            if (Sys.Process("COLVIR").WaitVCLObject("frmLoginDlg", 18000).Exists):
              cancel_but_login_win = login_window.VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnCancel")
              cancel_but_login_win.Click()
          elif (Sys.Process("COLVIR").WaitWindow("TMessageForm", "Внимание", -1, 1500).Exists):
            """ @expected: Появится окно 'Смена пароля для %логин%' """
            """ @content: В окне 'Смена пароля для %логин%' заполнить поля: 'Старый пароль' 
                          (тот под которым вошли), 'Новый пароль', 'Подтверждение' и нажать кнопку 'Ок'.
                          Пароли должны соответствовать парольной политике - минимум 8 символов, 
                          большие и маленькие буквы и цифры.  """
            ok_atten_window = Sys.Process("COLVIR").Dialog("Внимание").VCLObject("OK")
            ok_atten_window.Click()
            pass_window = Sys.Process("COLVIR").VCLObject("frmPswDialog")
            new_pass = pass_window.VCLObject("edtPassword")
            new_pass.Keys(db_pass)
            confirm_pass = pass_window.VCLObject("edConform")
            confirm_pass.Keys(db_pass)
            ok_pass_window = pass_window.VCLObject("pnlButtons").VCLObject("pnlRight").VCLObject("btnOK")
            ok_pass_window.Click()
            if (Sys.Process("COLVIR").WaitVCLObject("ErrMessageForm", 1500).Exists):
              error_pass_window = Sys.Process("COLVIR").VCLObject("ErrMessageForm")
              error_pass_window.Close()
              Log.Warning("Для учетной записи " + login + " пароль уже подтвержден!")
            elif (Sys.Process("COLVIR").WaitWindow("#32770", "Colvir Banking System", -1, 1500).Exists):
              info_win = Sys.Process("COLVIR").Dialog("Colvir Banking System")
              info_win.Close()
              self.WarningMessageHandler('no_log')
              """ @expected: Появится окно с текстом, что новый пароль пользователю назначен. Пароль успешно изменен. """
              Log.Checkpoint("Удачно подтвердили пароль для учетной записи " + login)
              self.ClickNeedButConfirmWindow('No', time_await=2000)
          elif (Sys.Process("COLVIR").WaitVCLObject("frmCssMenu", 2500).Exists):  #ожидание подключения к БД, ждем окно выбор задач
            self.WarningMessageHandler('no_log')  #Закрытие различных окон 'предупреждений' при входе в колвир
            Log.Checkpoint("Удачно авторизовались под учетной записью " + login)
        else:
          Log.Error("Неудалось запустить колвир, либо истекло время ожидания окна логина в приложение")

    def CheckBalBlockC2(self, acc_num):
        """В данной функции проверяется счет из датасета на наличие необходимого баланса,
        блокировок по счету и наличие задолженности в К2"""
        self.acc_num = acc_num
        select = """
                               select 
                   abs(t_pkgaccbal.faccbal(a.dep_id, a.id, trunc(sysdate),0,ag.val_id,0,0)) as COLVIR_BAL,
                   (select count(gl.id) from G_LOCK gl, G_LOCKTYPE lt
                   where gl.acc_id = a.id and gl.dep_id = a.dep_id and gl.locktype = lt.id and gl.todate is null) as count_block_acc,
                   (select count(c.id) as count_c2 from S_CRD2 c
                   where c.acc_id = a.id and c.todate is null) as count_c2
                   from g_clihst g, g_cli gg, g_accbln a, g_accblnhst ag, ledacc l
                   where g.id = gg.id
                   and g.dep_id = gg.dep_id and trunc(sysdate) between g.fromdate and g.todate
                   and g.id = ag.cli_id and g.dep_id = ag.clidep_id and trunc(sysdate) between ag.fromdate and ag.todate
                   and a.id = ag.id and a.dep_id = ag.dep_id and a.cha_id = l.id
                   and a.code = '"""+self.acc_num+"""'
                 """
        result = self.OracleHandlerDB(select)
        return result

    def CheckBalBlockC2Lim(self, acc_num):
        """В данной функции проверяется счет из датасета на наличие необходимого баланса, блокировок по счету,
        наличие задолженности в К2 и количество лимитов по счету"""
        self.acc_num = acc_num
        select = """
                   select 
                   abs(t_pkgaccbal.faccbal(a.dep_id, a.id, trunc(sysdate),0,ag.val_id,0,0)) as COLVIR_BAL,
                   (select count(gl.id) from G_LOCK gl, G_LOCKTYPE lt
                   where gl.acc_id = a.id and gl.dep_id = a.dep_id and gl.locktype = lt.id and gl.todate is null or gl.todate > trunc(sysdate)) as count_block_acc,
                   (select count(c.id) as count_c2 from S_CRD2 c
                   where c.acc_id = a.id and c.todate is null) as count_c2,
                   (select count(tl.id) as COUNT_LIM from T_ACCLIMTYP_STD ta, T_LIM tl, T_LIMVAL tv
                   where ta.id = tl.limtyp and tl.acc_id = a.id
                   and tl.id = tv.id and tl.todate > trunc(sysdate)) as COUNT_LIM
                   from g_clihst g, g_cli gg, g_accbln a, g_accblnhst ag, ledacc l
                   where g.id = gg.id
                   and g.dep_id = gg.dep_id and trunc(sysdate) between g.fromdate and g.todate
                   and g.id = ag.cli_id and g.dep_id = ag.clidep_id and trunc(sysdate) between ag.fromdate and ag.todate
                   and a.id = ag.id and a.dep_id = ag.dep_id and a.cha_id = l.id
                   and a.code = '"""+self.acc_num+"""'
                 """
        result = self.OracleHandlerDB(select)
        return result

    def CheckCountLimit(self, acc_num):
        """В данной функции проверяется счет на наличие лимитов и возвращается количество действующих лимитов"""
        self.acc_num = acc_num
        select = """
                    select count(tl.id) as COUNT_LIM from T_ACCLIMTYP_STD ta, T_LIM tl, T_LIMVAL tv, g_accbln a
                    where ta.id = tl.limtyp and tl.acc_id = a.id
                    and tl.id = tv.id and tl.todate > trunc(sysdate) and a.code = '"""+self.acc_num+"""'
                 """
        result = self.OracleHandlerDB(select)
        return result

    def GetJurTestingIin(self):
        """Функция возвращает сформированный ИИН юр лица или ИП"""
        # получаем рандомный месяц регистрации
        digit = str(randint(1, 12))
        month = (len(str(12))-len(digit))*'0'+digit
        # получаем последние 2 цифры рандомного года
        last_year = str(int(datetime.now().year))[2:]
        digit = str(randint(0, (int(last_year)-1)))
        year = (len(last_year) - len(digit)) * '0'+ digit
        # передаем тип организации от 4 до 6. 4 - юр рез 5 - юр нерез 6 - ип совм
        type_org = str(randint(4, 6))
        # тип представительства. ГО, филиал, представительство, крест хозяйство
        type_office = choice('0124')
        # получаем номер регистрации. Номер создается рандомна и содержит 5 цифр
        digit = str(randint(1, 99999))
        reg_num = (len('99999') - len(digit)) * '0'+ digit
        # Расчитываем разряд ИИН. Он формируется по специальной формуле
        iin = year + month + type_org + type_office + reg_num
        weight_control_num = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] # вес контрольного разряда
        control_num = 0
        for i in range(11):
            control_num += (int(weight_control_num[i]) * int(iin[i]))
        mod = control_num / 11
        mod = int(mod) * 11
        control_num -= mod
        # если контрольный разряд = 10, то используем другой вес разряда. Если и тогда разряд = 10, то данный ИИН не используется
        # а возвращаться будут одни нули
        if control_num >= 10:
            weight_control_num_other = [3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 2]
            for i in range(11):
                control_num += (int(weight_control_num_other[i]) * int(iin[i]))
            mod_oth = control_num / 11
            mod_oth = int(mod_oth) * 11
            control_num -= mod_oth
            if control_num >= 10:
                return '000000000000'
        iin = year + month + type_org + type_office + reg_num + str(control_num)
        return iin

    def GetFlTestingIin(self):
        """Функция возвращает сформированный ИИН физ лица"""
        # получаем век рождения
        #0 - для иностранных граждан
        #1 - для мужчин, родившихся в XIX веке НЕ ИСПОЛЬЗУЕТСЯ ЗДЕСЬ
        #2 - для женщин, родившихся в XIX веке НЕ ИСПОЛЬЗУЕТСЯ ЗДЕСЬ
        #3 - для мужчин, родившихся в XX веке
        #4 - для женщин, родившихся в XX веке
        #5 - для мужчин, родившихся в XXI веке
        #6 - для женщин, родившихся в XXI веке
        century_and_sex = choice('03456')
        # получаем последние 2 цифры рандомного года
        if century_and_sex in ('0', '3', '4'):
            digit = str(randint(50, 99))
            year = (len('99') - len(digit)) * '0'+ digit
        elif century_and_sex in ('5', '6'):
            digit = str(randint(0, 3))
            year = (len('99') - len(digit)) * '0'+ digit
        # получаем рандомный месяц регистрации
        digit = str(randint(1, 12))
        month = (len(str(12))-len(digit))*'0'+digit
        # получаем рандомный день рождения
        if month in ('01', '03', '05', '07', '08', '10', '12'):
            count_day = 31
        elif month in ('04', '06', '09', '11'):
            count_day = 30
        else:
            count_day = 28
        digit = str(randint(1, count_day))
        day = (len(str(count_day))-len(digit))*'0'+digit
        # получаем номер регистрации. Номер создается рандомна и содержит 5 цифр
        digit = str(randint(1, 9999))
        reg_num = (len('9999') - len(digit)) * '0'+ digit
        # Расчитываем разряд ИИН. Он формируется по специальной формуле
        iin = year + month + day + century_and_sex + reg_num
        weight_control_num = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] # вес контрольного разряда
        control_num = 0
        for i in range(11):
            control_num += (int(weight_control_num[i]) * int(iin[i]))
        mod = control_num / 11
        mod = int(mod) * 11
        control_num -= mod
        # если контрольный разряд = 10, то используем другой вес разряда. Если и тогда разряд = 10, то данный ИИН не используется
        # а возвращаться будут одни нули
        if control_num >= 10:
            weight_control_num_other = [3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 2]
            for i in range(11):
                control_num += (int(weight_control_num_other[i]) * int(iin[i]))
            mod_oth = control_num / 11
            mod_oth = int(mod_oth) * 11
            control_num -= mod_oth
            if control_num >= 10:
                return '000000000000'
        iin = year + month + day + century_and_sex + reg_num + str(control_num)
        return iin

    def GeneratePhoneNumber(self):
        """Метода генерирует номер мобильного телефона, которого нет в БД.
        Чтобы создание карточки не падало на ошибку из-за дубляжа номера в другой карточке"""
        while True: # если сгенерированный контакт существует в БД, будет повторная генерация пока не вернется уникальный контакт
            num_provider = choice(['705', '701', '747', '771', '777', '702', '708'])
            num_phone = str(randint(1000000, 9999999))
            full_num_phone = f'+7{num_provider}{num_phone}'
            # проверяем существование номера телефона в БД
            select_cont = f"""
                            select CONT from G_CLICONT
                            where ATYP = '8' and CONT = '{full_num_phone}'
                          """
            result_request = self.OracleHandlerDB(select_cont, need_zero=True)
            # если вернулся None значит номер уникальный, прерываем цикл и возвращаем его.
            # если вернулся номер, который есть в БД, то цикл идет на след итерацию
            if result_request is None:
                break
        return full_num_phone

    def GeneratePassNum(self):
        """Метод генерирует случайный номер документа удостоверяющего личность
        проверяем существование номера документа в БД"""
        while True: # если сгенерированный контакт существует в БД, будет повторная генерация пока не вернется уникальный контакт
            get_pass_num = str(randint(100000000, 999999999))
            select_pass = f"""
                            select DISTINCT PASSNUM from G_CLIHST
                            where PASSNUM = '{get_pass_num}' 
                           """
            result_request = self.OracleHandlerDB(select_pass, need_zero=True)
            # если вернулся None значит номер уникальный, прерываем цикл и возвращаем его.
            # если вернулся номер, который есть в БД, то цикл идет на след итерацию
            if result_request is None:
                break
        return get_pass_num

    def GetIdRecord(self):
        """Генерация уникального ID"""
        while True: # если сгенерированный номер id существует в балицах, то будет сгенерирован новый
            # получаем id записи в таблицах, которые используются при создании юр лица
            get_id = str(randint(10000, 99999))
            select_id = f"""
                        select ID_GBDUL_MAIN from z_077_ent_gbdul_main
                        where ID_GBDUL_MAIN = '{get_id}'
                        UNION
                        select ID_GBDUL_MAIN from z_077_ent_gbdul_leaders
                        where ID_GBDUL_MAIN = '{get_id}'
                        UNION
                        select ID_GBDUL_MAIN from z_077_ent_gbdul_founders
                        where ID_GBDUL_MAIN = '{get_id}'
                        """
            check_id_db = self.OracleHandlerDB(select_id, need_zero=True)
            if check_id_db is None:
                break
        return get_id

    def GenName(self,sex):
        """Генерация имени"""
        begin_name = ["Гори","Свято","Яро","Влади","Изя","Вяче","Мечи","Бори","Дан","Тыкв","Бер","Ван","Сер","Шух","Ал","Арт","Ксен","Мөл","Еле","Але","Ам","Анд","Тать"]
        name_end = ["ил","мир","люб","рад","мил","зар","мысл","дан","гор","яр","вед","бор","мысл","свет","ос","су","ин","сек","д","ик","рат","ия","ем","ия","с","дір","н","ксей","ир","рей","ян"]
        random_begin_name = randint(0, 22)
        randon_name_end = randint(0, 30)
        collect_name = begin_name[random_begin_name-1] + name_end[randon_name_end-1]
        wom_name = collect_name+"а"
        if sex =="M":
          complete_name = collect_name
        elif sex =="F":
          complete_name = wom_name
        else:
          complete_name = wom_name
        return complete_name

    def GenSerName(self, sex):
        """Генерация фамилии"""
        begin_sername = ["Кузне","Сага","Абда","Краси","Каб","Гумар","Омаро","Кисли","Сквор","Егор","Саут","Нуртаз","Туреб","Белоц","Байт","Голи","Каме","Ус","Якуш","Сар","Ребр","Бел","Пан","Хам","Кульназ","Гир"]
        end_sername = ["цов","мир","лы","любов","ков","цев","зар","мыс","цын","гор","зын","дын","ев","ес", "ен", "ас", "сур", "им", "сек", "ус", "ик","цов","ова","ов","ин","еков","ерковец","орбай","ков","шев","енков","иев","ов","итов","аров","ин"]
        random_begin_sername = randint(0, 25)
        random_end_sername = randint(0, 35)
        collect_sername = begin_sername[random_begin_sername-1] + end_sername[random_end_sername-1]
        wom_sername = collect_sername+"а"
        if sex =="M":
          complete_sername = collect_sername
        elif sex =="F":
          complete_sername = wom_sername
        else:
          complete_sername = wom_sername
        return complete_sername

    def GenJurName(self, resid, type):
        """метод принмает резиденство юр лица и возвращает сгенерированное название
        если резидент, то название генерируется на кириллице
        если не резидент, то название генерируется на латинице"""
        self.resid = resid
        self.type = type
        name_company = ''
        if self.resid == '1':
            fake = Faker('ru_RU')
            Log.Event(f'Передан резидент с типом - {self.type}')
        elif self.resid == '0':
            fake = Faker('en_US')
            Log.Event(f'Передан не резидент с типом - {self.type}')
        else:
            Log.Warning(f'Передан неверный тип резиденства - {self.resid}')
        get_name_company = fake.unique.company() # получаем сгенерированное название компании
        name_company = get_name_company
        Log.Message(f'Сгенерировано имя комапнии - {get_name_company}')
        # в ру локализации убираем ООО и т.д. если сгенерированное имя передается резиденту РК
        if self.resid == '1':
            for i in range(len(get_name_company)):
                if get_name_company[i] == '«':
                    Log.Event(f'Встретился символ - {get_name_company[i]}, производим замену на пустую строку')
                    for k in range(i+1):
                        name_company = name_company.replace(name_company[i-k], '', 1)
                    Log.Event(f'Произведена замена до символа - {get_name_company[i+1]}')
                elif get_name_company[i] == '»':
                    Log.Event(f'Встретился символ - {get_name_company[i]}, производим замену на пустую строку')
                    for j in range(1):
                        name_company = name_company.replace(name_company[-1], '', 1)
                    Log.Event(f'Произведена замена после символа символа - {get_name_company[i]}')
        if self.type == 'JUR' and self.resid == '1':
            name_company = f'ТОО "{name_company}"'
            Log.Event(f'Передан тип организации - {self.type}')
        elif self.type == 'PBOYUL' and self.resid == '1':
            name_company = f'ИП "{name_company}"'
            Log.Event(f'Передан тип организации - {self.type}')
        elif self.type == 'JUR' and self.resid == '0':
            Log.Event(f'Передан тип организации - {self.type}, не резидент')
            name_company = get_name_company
        else:
            Log.Warning(f'Передан неверный тип организации - {self.type}')
        return name_company

    def CreateUserColvir(self, login, fio, password, email, phone, arm_id, dep_code, fromdate, todate,
                         prim, virtualfl, web_type, adm, grpfl, arcfl_pos, arcfl_user, arestfl_pos, arestfl_user):
        """метод создает пользователя Колвир"""
        self.login = login # login - соответственно логин пользователя
        self.fio = fio # fio - ФИО пользователя
        self.password = password # password - пароль пользователя
        self.email = email # email - почта пользователя
        self.phone = phone # phone - сотовый пользователя
        self.arm_id = arm_id # arm_id - айдишник рабочего места пользователя
        self.dep_code = dep_code # dep_code - код департамента (Например CNT)
        self.fromdate = fromdate # fromdate - дата начала действия учетки пользователя. Формат - дд.мм.гггг
        self.todate = todate # todate - дата окончания действия учетки пользователя. Формат - дд.мм.гггг
        self.prim = prim # prim - примечания к учетке пользователя
        self.virtualfl = virtualfl # virtualfl - признак виртуальной учетки пользователя
        self.web_type = web_type # web_type - тип учетки пользователя
        self.adm = adm # adm - признак админа учетки пользователя
        self.grpfl = grpfl # grpfl - признак группы пользователя
        self.arcfl_pos = arcfl_pos # arcfl_pos - признак архива позиции пользователя
        self.arcfl_user = arcfl_user # arcfl_user - признак архива учетки пользователя
        self.arestfl_pos = arestfl_pos # arestfl_pos - признак приостановки действия позиции пользователя
        self.arestfl_user = arestfl_user # arestfl_user - признак приостановки действия учетки пользователя
        # Для начала проверяем, что пользователя, которого хотим создать, еще не создан
        # Если не создан, то идем дальше
        check_login_before = f"""
                              select COUNT(CODE) from C_USER
                              where CODE = '{login}' 
                             """
        result_login_before = self.OracleHandlerDB(check_login_before)
        if result_login_before[0][0] == 0:
            Log.Event(f"Пользователь {self.login} не существует на данный момент")
            # вызываем процедуру по созданию пользователя
            self.OracleCallProcedure("Z_PKG_AUTO_TEST.CREATEUSERCOLVIR", self.login, self.password, self.fio, self.fio, self.email, self.phone, self.arm_id, self.dep_code,
                                     self.fromdate, self.todate, self.prim, self.virtualfl, self.web_type, self.adm, self.grpfl, self.arcfl_pos, self.arcfl_user,
                                     self.arestfl_pos, self.arestfl_user)
            # проверяем, что пользователь создался
            result_login_after = self.OracleHandlerDB(check_login_before)
            if result_login_after[0][0] == 1:
                Log.Checkpoint(f"Пользователь {login} успешно создан")
            elif result_login_after[0][0] == 0:
                Log.Error(f"Пользователь {login} не создан")
            else:
                Log.Warning(f"Создано больше одной записи по пользователю {login}")
        else:
            Log.Event(f"Пользователь {login} уже существует в БД")

    def SetGrnTestUser(self, id_pos_test_user, id_pos_real_user):
        """метод вызывает процедуру для установки полномочию тестовому пользователю от реального юзера"""
        self.id_pos_test_user = id_pos_test_user
        self.id_pos_real_user = id_pos_real_user
        self.OracleCallProcedure("Z_PKG_AUTO_TEST.AT_pSetUsrGrn", self.id_pos_test_user, self.id_pos_real_user)
        # проверяем, что полномочия назначились и в полном количестве
        # получаем количество всех полномочий реального пользователя
        select_real_grn = f"""SELECT COUNT(*) FROM (SELECT ROL_ID FROM C_USRROL WHERE USR_ID = '{self.id_pos_real_user}' UNION
                         SELECT GRN_ID FROM C_USRGRN WHERE USR_ID = '{self.id_pos_real_user}' UNION
                         SELECT HDR_ID from C_USRGRP WHERE DTL_ID = '{self.id_pos_real_user}')"""
        result_real_grn = self.OracleHandlerDB(select_real_grn)
        # получаем количество всех полномочий тестового пользователя
        select_test_grn = f"""SELECT COUNT(*) FROM (SELECT ROL_ID FROM C_USRROL WHERE USR_ID = '{self.id_pos_test_user}' UNION
                         SELECT GRN_ID FROM C_USRGRN WHERE USR_ID = '{self.id_pos_test_user}' UNION
                         SELECT HDR_ID from C_USRGRP WHERE DTL_ID = '{self.id_pos_test_user}')"""
        result_test_grn = self.OracleHandlerDB(select_test_grn)
        # сравниваем количество полномочий. Если у реального и тестового оно совпадает, значит все полномочия назначились
        if result_real_grn[0][0] == result_test_grn[0][0]:
            Log.Checkpoint(f"Назначены все полномочия от реального id - self.id_pos_real_user тестовому - self.id_pos_test_user")
        else:
            Log.Warning(f"Не назначены или назначены не в полном объеме полномочия от реального id - self.id_pos_real_user тестовому - self.id_pos_test_user")
          
    def CheckGrn(self, usr_id, grn_id, grn_id_2, type_grn):
        """метод для проверки существования полномочия"""
        self.usr_id = usr_id
        self.grn_id = grn_id
        self.grn_id_2 = grn_id_2
        self.type_grn = type_grn
        if self.type_grn == 'ROL':
            select_grn = f"""SELECT DISTINCT COUNT(ROL_ID) FROM C_USRROL WHERE USR_ID = {self.usr_id} and ROL_ID = {self.grn_id}"""
            result_grn = self.OracleHandlerDB(select_grn)
        elif self.type_grn == 'GRN':
            select_grn = f"""SELECT COUNT(ID) FROM C_USRGRN WHERE USR_ID = {self.usr_id} and GRN_ID = {self.grn_id} and ID = {self.grn_id_2}"""
            result_grn = self.OracleHandlerDB(select_grn)
        elif self.type_grn == 'GRP':
            select_grn = f"""SELECT DISTINCT COUNT(HDR_ID) FROM C_USRGRP WHERE DTL_ID = {self.usr_id} and HDR_ID = {self.grn_id}"""
            result_grn = self.OracleHandlerDB(select_grn)
        result = result_grn[0][0]
        return result

class CreateJsonReport(ColvirState):
    """Класс с функциями для создания отчета json. Данный отчет необходим для добавления данных в Аллюр"""


    def CreateJsonFile(self, name_test, json_body=''):
        """Функция создает файл Json с названием, которое передается в функцию
        в функцию также можно передать тело json. Если ничего не передавать, то создастся пустое тело
        в ввиде словаря питона - {}"""
        self.name_test = name_test
        self.json_body = json_body
        allure_path = self.GetEnviron('NEW_PATH')
        file = f"{allure_path}{self.name_test}.json"
        if json_body == '':
            self.json_body = {}
        with open(f'{file}', 'w', encoding='utf-8') as file:
            file.write(f'{self.json_body}') #Передаваемые значение необходимо оборачивать строку, так как другие типы данных не поддерживаются при редак файла
            file.close
        Log.Event(f"Создан файл - {file}")

    def AddKeyValueJson(self, path_to_file, key, value):
        """Функция добавляет в файл json параметры ключ: значение
        #Функция принимает списки с ключами и значениями. Один список с ключами, второй список с значениями.
        #Порядок расположения ключей и значений должен совпадать для каждой пары"""
        self.key = key
        self.value = value
        self.path_to_file = path_to_file
        required_key = ["attachments", "steps", "labels"] # Данные ключи будут добавляться всегда, с пустым словарем, если они не существуют в словаре
        required_value = [[], [], []]
        count = 0
        if type(self.key) == list and type(self.value) == list: # Передаваемый тип данных должен быть list
            for i in range(len(required_key)):
                if required_key[i] in self.key:
                    count += 1
                    Log.Warning(f'В функцию нельзя передавать ключ {required_key[i]}')
            if count > 0:
                Log.Error(f'В функцию передаются запрещенные ключи')
            else:
                self.key += required_key
                self.value += required_value
                with open(self.path_to_file, 'r+') as file:
                        data = json.load(file)
                        file.close
                        default_data = defaultdict(dict, data)
                        for i in range(len(self.key)):
                            if self.key[i] in ("steps", "attachments", "labels") and self.key[i] in default_data:
                                Log.Event(f'Ключ {self.key[i]} уже существует в словаре')
                            else:
                                default_data[self.key[i]] = self.value[i]
                with open(self.path_to_file, 'w') as file:
                    file.write(json.dumps(dict(default_data)))
                    file.close
        else:
            Log.Warning(f'Передаваемые данные не являются списком - {type(self.key)}, {type(self.value)}. Данные необходимо передавать в списке')

    def FindAbsPathFile(self, file_name):
        """Функция, которая принимает название файла и возвращает его абсолютный путь
        В названии файла необходимо указывать тип расширения. В данном случае .json"""
        self.file_name = file_name
        user_name = getpass.getuser() #Получение логина пользователя, чтобы функция работала под разнымми пользователями
        allure_path = self.GetEnviron('NEW_PATH')
        allure_path = allure_path[:-1]
        if ".json" in self.file_name:
            self.file_name = f"{self.file_name}.json"
            new_name = self.file_name.replace(".json", "-result", 1)
            try:
                os.rename(f"{allure_path}/{self.file_name}", f'{allure_path}/{new_name}')
            except FileNotFoundError as error:
                Log.Event(f"Не найден файл {self.file_name}. Возможно он уже был переименован")
                Log.Event(error)
        else:
            self.file_name = f"{self.file_name}.json"
            new_name = f"{self.file_name[:-5]}-result.json"
            try:
                os.rename(f"{allure_path}/{self.file_name}", f'{allure_path}/{new_name}')
            except FileNotFoundError as error:
                Log.Event(f"Не найден файл {self.file_name}. Возможно он уже был переименован")
                Log.Event(error)
        full_path = os.path.join(allure_path, new_name)
        Log.Message(full_path)
        p = os.path.normpath(os.path.abspath(full_path)) #После того, как файл найден в переменную записывается его абсолютный путь
        Log.Message(p)
        return p.replace("\\", "/") #возвращается абс путь с изменненным слешем

    def ReMoveFile(self, file_name, new_path):
        """Функция перемещает файл в директорию, которая передается в функцию
        В функцию также передается имя файла который необходимо переместить
        По имени файла будет определен текущий путь расположения файла
        В названии файла обязательно не должно быть точек, кроме той, что разделяет название и расширение файла"""
        self.file_name = file_name
        self.new_path = new_path
        try:
            abs_path = self.FindAbsPathFile(self.file_name) # Получение абсолютного пути
            shutil.move(abs_path, self.new_path) # Перемещение файла
            for i in range(len(self.file_name)):
                if self.file_name[i] == '.':
                    new_name = self.file_name[0:i-1] + '-result' + self.file_name[i:]
            os.rename(self.new_path+self.file_name, self.new_path+new_name)
            Log.Event(f'Файл перемещен в директорию - {self.new_path}')
        except FileNotFoundError as error:
            Log.Warning(f'Не найден файл {self.file_name}, по переданному пути - {abs_path}. {error}')

    def AddNestedElements(self, path_to_file, path_to_key, key, value, need_list=True):
        """Функция принимает наименование элемента. Может принимать и дочерние элементы. Пример: element["step"]["step"]
        Принимает значение элемента. Если флаг list = True, то передаваемые значения словаря будут обернуты в список
        Если флаг list = False, то будет добавлен только словарь
        В данной реализации пока предусмотрена передача только словаря"""
        self.path_to_file = path_to_file
        self.value = value
        self.path_to_key = path_to_key
        self.key = key
        required_key = ["steps", "attachments", "labels"] # Данные ключи будут добавляться всегда, с пустым словарем, если они не существуют в словаре
        required_value = [[], [], []]
        count = 0
        with open(self.path_to_file, 'r+') as file: # Выгружаем данные из файла в переменную
            data = json.load(file)
            file.close
        for i in range(len(required_key)):
            if required_key[i] in self.key:
                count += 1
                Log.Warning(f'В функцию нельзя передавать ключ {required_key[i]}')
        if count > 0:
            Log.Error(f'В функцию передаются запрещенные ключи')
        else:
            if type(self.key) is list and type(self.value) is list: # Передаваемый тип данных должен быть list
                if isinstance(dp.get(data, self.path_to_key), (list, dict)):
                    if isinstance(dp.get(data, self.path_to_key), list):
                        Log.Event(f'тип ключа - {type(dp.get(data, self.path_to_key))}')
                        self.key += required_key
                        self.value += required_value

                        new_dict = zip(self.key, self.value)
                        new_dict = dict(new_dict)
                        value_list = dp.get(data, self.path_to_key)
                        value_list.append(new_dict)
                        with open(self.path_to_file, 'w') as file:
                            file.write(json.dumps(data))
                            file.close
                    if isinstance(dp.get(data, self.path_to_key), dict):
                        Log.Event(f'тип ключа - {type(dp.get(data, self.path_to_key))}')
                        new_dict = zip(self.key, self.value)
                        new_dict = dict(new_dict)
                        value_dict = dp.get(data, self.path_to_key)
                        value_dict.update(new_dict)
                        with open(self.path_to_file, 'w') as file:
                            file.write(json.dumps(data))
                            file.close
                else:
                    Log.Warning(f'Значение ключа не является списком или словарем - {type(dp.get(data, self.path_to_key))}')
            else:
                Log.Warning(f'Передаваемые данные не являются списком - {type(self.key)}, {type(self.value)}. Данные необходимо передавать в списке')

    def GetDefaultDict(self, path_to_file):
        """Функция принимает в себя путь к файлу json. Забирает из него данные.
        И возвращает их в defaultdict.
        defaultdict необходим для возможности передачи пути словаря без возникновения ошибки KeyError"""
        self.path_to_file = path_to_file
        try:
            with open(self.path_to_file, 'r') as file:
                Log.Event(f'Открываю файл - {self.path_to_file}')
                data = json.load(file)
                file.close
                Log.Event(f'Закрываю файл - {self.path_to_file}')
                default_data = defaultdict(dict, data)
            return default_data
        except FileNotFoundError as name:
            Log.Warninng(f'Не найден файл по переданному пути - {self.path_to_file}. {name}')

    def GetUserName(self):
        """Получение логина пользователя"""
        user_name = getpass.getuser()
        return user_name

    def GetDateTimeMilli(self):
        """Получение времени"""
        milliseconds = int(round(time.time() * 1000))
        return milliseconds

    def GetRandomNumber(self):
        """Возвращает случайное число от 1 до 1000000"""
        return randint(1, 1000000)

    def AllureReportTemplate(self, abs_path, name_file, name_step, status_step, message, pic_object, name_pic, new_path, status_test, step_id, substep_id, rm = False):
        """Шаблон для заполнения json файла с отчетом для Allure
        Если после отработки функции необходимо переместить файл, то при вызове функции указываем rm = True"""
        self.abs_path = abs_path # Абсолютный путь до файла
        self.name_file = name_file # Наименование файла
        self.pic_object = pic_object # Объект, который необходимо заскринить
        self.name_step = name_step # Имя шага
        self.status_step = status_step # Статус шага
        self.message = message # Сообщение в шаге
        self.name_pic = name_pic # Имя изображения
        self.new_path = new_path
        self.status_test = status_test # Статус всего теста
        self.step_id = step_id # Номер шага. Если указывается первый шаг, то в функцию надо передавать в step_id - 1, substep_id - 1.
                               # Если добавляется подшаг, то передаем step_id - 1, substep_id - 2
                               # Если указываем второй шаг в скрипте, то передаем step_id - 2, substep_id - 1
        self.substep_id = substep_id # Номер подшага
        self.rm = rm #
        self.step_id -= 1
        if self.substep_id == 1:
            path_step = 'steps'
        else:
            path_step = 'steps' + (f'/{self.step_id}/steps' * (self.substep_id - 1))
        path_to_pic = (f'steps/{self.step_id}/' * self.substep_id) + 'attachments'
        stop_time = f'steps/{self.step_id}/' * self.substep_id
        stop_time = stop_time[:-1]
        key_steps = ["name", "status", "statusDetails", "start"]
        value_steps = [self.name_step, self.status_step, self.message, self.GetDateTimeMilli()]
        self.AddNestedElements(abs_path, path_step, key_steps, value_steps)
        # Сначала проверяется, передается ли значение desktop. Если да, то создается скрин всего рабочего стола
        # Необходимо в местах где нет конкретного названия объекта, которое необходимо передать для скриншота
        if self.pic_object == 'desktop':
            name_pic_step_1 = f'{self.GetRandomNumber()}.png'
            Sys.Desktop.Picture().SaveToFile(f'{self.new_path}{name_pic_step_1}')
            key_attach = ["name", "source", "type"]
            val_attach = [self.name_pic, name_pic_step_1, "image/png"]
            self.AddNestedElements(abs_path, path_to_pic, key_attach, val_attach)
        # Если значение desktop не передается, то выполняется проверка на not None и если значение есть, то создается скриншот
        # Передаваемого объекта
        # Если передавать название объекта, то ТС удет его скринить, если не передавать, то данный блок выполняться не будет
        elif self.pic_object is not None and self.name_pic is not None:
            get_pict = Sys.Process("COLVIR").Find("Name", self.pic_object)
            name_pic_step_1 = f'{self.GetRandomNumber()}.png'
            get_pict.Picture().SaveToFile(f'{self.new_path}{name_pic_step_1}')
            key_attach = ["name", "source", "type"]
            val_attach = [self.name_pic, name_pic_step_1, "image/png"]
            self.AddNestedElements(abs_path, path_to_pic, key_attach, val_attach)
        self.AddNestedElements(abs_path, stop_time, ["stop"], [self.GetDateTimeMilli()])
        self.AddKeyValueJson(abs_path, ["status", "stop"], [self.status_test, self.GetDateTimeMilli()])
        if self.rm == True:
            Log.Message("Перемещение не требуется по новой логике")

    def CreateTemplateAllureReport(self, key_dict, value_dict, value_labels, name_file):
        """Создание отчета json с главным словарем. Ключи и значения необходимо передавать в списках, внутри списка
        Пример: [['name', 'value'], ['name', 'value']]
                [['suite', 'Значение'], ['subSuite', 'Значение']]"""
        self.key_dict = key_dict
        self.value_dict = value_dict
        self.value_labels = value_labels
        self.name_file = name_file
        new_path = self.GetEnviron('NEW_PATH')
        self.CreateJsonFile(self.name_file) #Создание файла джейсон с пустым словарем в теле
        abs_path = self.FindAbsPathFile(self.name_file) # Получение абсолютного пути файла
        if isinstance(self.key_dict, list) and isinstance(self.value_dict, list):
            self.AddKeyValueJson(abs_path, self.key_dict, self.value_dict)
            def_dict = self.GetDefaultDict(abs_path)
            for i in range(len(self.value_labels)):
                self.AddNestedElements(abs_path, 'labels', ["name", "value"], self.value_labels[i])
                Log.Event(f'Добавлен {self.value_labels[i][0]}')
            Log.Event('Создан файл с главным словарем')
        else:
            Log.Error('Ключи и значения словаря необходимо передавать в двойном списке')

    def CreateAllureReport(self, module_name: str, sub_suite: str, name_suite: str, name_file: str):
        # Создание главной иерархии json отчета
        self.module_name = module_name  # имя модуля
        self.sub_suite = sub_suite  # имя группы тестов
        self.name_suite = name_suite  # имя теста
        self.name_file = name_file  # имя файла
        Log.Message(self.name_suite)
        Log.Message(self.name_file)
        new_path = self.GetEnviron('NEW_PATH')
        name_pict = self.name_file.replace("json", "png")
        self.CreateJsonFile(self.name_file)  # Создание файла джейсон с пустым словарем в теле
        key = ["name", "description", "start"]
        value = [self.name_suite, self.name_suite, self.GetDateTimeMilli()]
        abs_path = self.FindAbsPathFile(self.name_file)  # Получение абсолютного пути файла
        self.AddKeyValueJson(abs_path, key, value)
        def_dict = self.GetDefaultDict(abs_path)
        key_labels_suite = ["name", "value"]
        value_labels_suite = ["suite", f"{self.module_name}"]
        self.AddNestedElements(abs_path, 'labels', key_labels_suite, value_labels_suite)
        key_labels_subsuite = ["name", "value"]
        value_labels_subsuite = ["subSuite", self.sub_suite]
        self.AddNestedElements(abs_path, 'labels', key_labels_subsuite, value_labels_subsuite)

    def GetLoginInfo(self, login_user):
        """ Получение логина через запрос к БД"""
        self.login_user = login_user
        if self.login_user is None:
          self.login_user = 'COLVIR'
        return login_user
