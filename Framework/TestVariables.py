from ColvirFramework import *
from FindMethods import *


class TestVariables():         
           
    def __init__(self):
        self._dcmnt_nt_fnd = "Документ не найден. Предидущие условия или операции не были выполнены."   
        
    # Универсальный геттер
    def get_var(self, var_name):
        return getattr(self, var_name, None)

    # Универсальный сеттер
    def set_var(self, var_name, value):
        setattr(self, var_name, value)