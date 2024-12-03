from ColvirFramework import *


class FindMethods(CommonOperation, GenerateTestingData, CreateJsonReport):

    def FindObject(self, type_obj: str, parent_obj: str, child_obj: str, 
                   name_property: str = "Name", internal='', log_event=None):
        # метод ищет объект Колвира и возвращает его
        self.type_obj = type_obj # тип объекта VCL, Text, Dialog и т.д.
        self.parent_obj = parent_obj # имя родительского объекта
        self.child_obj = child_obj # имя дочернего объекта
        self.name_property = name_property # имя свойства по которому будет происходить поиск
        # по умолчанию Name
        self.internal = internal # доп флаг для получения внутреннего значения поля name_property
        self.log_event = log_event
        if self.type_obj == "VCLObject":
            parent_window = Sys.Process("COLVIR").VCLObject(self.parent_obj)
        elif self.type_obj == "TextObject":
            parent_window = Sys.Process("COLVIR").TextObject(self.parent_obj)
        elif self.type_obj == "Dialog":
            parent_window = Sys.Process("COLVIR").Dialog(self.parent_obj)
        elif self.type_obj == "Popup":
            parent_window = Sys.Process("COLVIR").Popup(self.parent_obj)
        need_object = parent_window.FindChild(self.name_property, self.child_obj, 15)
        if need_object.Exists and self.internal:
            internal_val = need_object.Child(0)
            Log.Message("Найденное поле " + str(internal_val.FullName))
            Log.Message("Значение поля " + str(internal_val.Value))
            return internal_val
        elif need_object.Exists:
            Log.Message("Найденное поле " + str(need_object.FullName))
            return need_object
        elif log_event is not None:
            Log.Event("Искомый объект " + str(self.child_obj) + " не найден")
            return None
        else:
            Log.Warning("Искомый объект " + str(self.child_obj) + " не найден")
            return None
        
        
        