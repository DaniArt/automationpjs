from TaskMethods import *

class Buttons(TaskMethods):
    """ Класс работы с кнопками """

    def BtnBrowse(self, parent_obj: str):
        """ метод производит нажатие по кнопке btnBrowse"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'VCLObject("btnBrowse")', need_tab = False)
    
    def BtnAcc(self, parent_obj: str):
        """ метод производит нажатие по кнопке btnAcc"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'VCLObject("btnAcc")', need_tab = False)
        
    def BtnOst(self, parent_obj: str):
        """ метод производит нажатие по кнопке btnOst"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'VCLObject("btnOst")', need_tab = False)
        
    def BtnMove(self, parent_obj: str):
        """ метод производит нажатие по кнопке Движения"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'MenuItem("Движения")', type_parent_obj = "Popup", need_tab = False)
        
    def BtnDeaPay(self, parent_obj: str):
        """ метод производит нажатие по кнопке Контроль сумм"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'VCLObject("btnDeaPay")', need_tab = False)
        
    def BtnInsert(self, parent_obj: str):
        """ метод производит нажатие по кнопке Создать"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'VCLObject("btnInsert")', need_tab = False)
        
    def BtnAddAgr(self, parent_obj: str):
        """ метод производит нажатие по кнопке Доп соглашения"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'VCLObject("btnAddAgr")', need_tab = False)
        
    def BtnSave(self, parent_obj: str):
        """ метод производит нажатие по кнопке Создать"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'VCLObject("btnSave")', need_tab = False)
        
    def BtnDelete(self, parent_obj: str):
        """ метод производит нажатие по кнопке Удалить"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'VCLObject("btnDelete")', need_tab = False)
        
    def BtnYes(self, parent_obj: str):
        """ метод производит нажатие по кнопке Удалить"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'VCLObject("Yes")', type_parent_obj = "Dialog", need_tab = False)

    def BtnOk(self, parent_obj: str):
        """ метод производит нажатие по кнопке Ok"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'VCLObject("btnOK")', need_tab = False)

    def BtnRunOperation(self, parent_obj: str):
        """ метод производит нажатие по кнопке Ok"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'VCLObject("btnRunOperation")', need_tab = False)

    def BtnClose(self, parent_obj: str):
        """ метод производит нажатие по кнопке Ok"""
        self.parent_obj = parent_obj # имя родительского объекта
        self.ClickInputField(self.parent_obj, 'Button("Закрыть")', need_tab = False)


        
        