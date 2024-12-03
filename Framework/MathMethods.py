from functools import reduce
from datetime import datetime 
from dateutil.relativedelta import relativedelta
 
class MathMethods():
    """ Класс для работы с методами математических вычислений """
    # вычмсление суммы от процента
    GetSumPcn = lambda self, x, y: round((x * (y / 100)), 2)
    
    def SumItems(self, *args):
        # Метод вычисляет сумму передаваемых переменных
        return reduce(lambda x, y: x + y, args)
            
    def MultItems(self, *args):
        # Метод вычисляет сумму передаваемых переменных
        return reduce(lambda x, y: x * y, args)
   
        
       
