from ColvirFramework import *
from datetime import datetime

class Date:
    colvir = CommonOperation()
            
    def MonthsToDays(self, start_date: str, months_cnt: int) -> str:
        self.start_date = start_date
        self.months_cnt = months_cnt
        days_cnt = self.months_cnt * 30
        
        try:
            date_obj = datetime.strptime(self.start_date, '%d%m%y')
        except TypeError:
            date_obj = datetime(*(time.strptime(self.start_date, '%d%m%y')[0:6]))
        Log.Message(date_obj)
        end_date = date_obj + timedelta(days=days_cnt)
        date_str = datetime.strftime(end_date, '%d.%m.%y')
        return date_str
    
    def SetOperDayToJrn(self, cntDays: int):
        ''' метод для добавления будущего опердня в журнал опердней '''
        self.cntDays = cntDays # количество дней до будущей даты от текущей
        self.colvir.OracleCallProcedure('Z_PKG_AUTO_TEST.AT_pSetFutureOperDayToJrn', self.cntDays, return_value = False)