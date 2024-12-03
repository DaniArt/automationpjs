from ColvirFramework import *


class Core(CommonOperation, GenerateTestingData, CreateJsonReport):
    """ Класс работы с ядром колвира, задачами DD1, DD6, DD5, SBJAREA, MCHROP, DOP1 и тд """
  
  
    def CloseNoSave(self, need_window):
        """ Закрытие окна создания объекта в словаре данных без сохранения при возникновении ошибок """
        self.need_window = need_window
    
        if Sys.Process("COLVIR").WaitWindow("TMessageForm", "Внимание", -1, 500).Exists:
          txt_warning = Sys.Process("COLVIR").Dialog("Внимание").VCLObject("Message").Caption
          Log.Warning(str(txt_warning))
          Sys.Process("COLVIR").Dialog("Внимание").VCLObject("OK").Click()
        self.ErrorMessageHandler()
        Sys.Process("COLVIR").VCLObject(self.need_window).Close()
        self.ClickNeedButConfirmWindow('No')
        Delay(2500)
        self.WaitLoadWindow("frmMainBrowserObj")
        Sys.Process("COLVIR").VCLObject("frmMainBrowserObj").Close()

    def StdFinder(self, str_to_find):
        """ Обработчик стандартного поиска по списку в окне """
        self.str_to_find = str_to_find
        state_find = False    
        if Sys.Process("COLVIR").WaitVCLObject("frmTreeFndDialog", 2500).Exists:
          btn_new_search = self.FindChildField("frmTreeFndDialog", "Name", 'VCLObject("btnNew")')
          btn_new_search.Click()
        self.WaitLoadWindow("frmFindDlg")
        need_str = self.FindChildField("frmFindDlg", "Name", 'VCLObject("edValue")')
        need_str.Keys(self.str_to_find)
        btn_ok_finder = self.FindChildField("frmFindDlg", "Name", 'VCLObject("btnOK")')
        btn_ok_finder.Click()
        self.WaitLoadWindow("frmTreeFndDialog")
        btn_move_on = self.FindChildField("frmTreeFndDialog", "Name", 'VCLObject("btnOK")')
        if not btn_move_on.Enabled:
          Log.Warning('Поиск не выдал результата по запросу - ' + self.str_to_find)
          Sys.Process("COLVIR").VCLObject("frmTreeFndDialog").Close()
        else:
          btn_move_on.Click()
          state_find = True
        return state_find
