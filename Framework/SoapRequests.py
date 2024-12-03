from CardFramework import *
from TaskMethods import *
from SQL import Sql


class SoapRequests(CardFramework):
    """ Данный класс содердит в себе все SOAP запросы """

    def ATM2405(self, acc_crd, amount, cur):
        """ Пополнение счета через Soap операцию 2405, для отработки запроса, требуется счет, Cумма, валюта, и порт"""
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
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
        data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata" xmlns:v1="http://bus.colvir.com/common/v1">
                  <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                  <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2405</wsa:Action>
                  <wsa:MessageID>{randid}</wsa:MessageID>   <!-- Используем генерацию рандомных чисел в ID -->
                     </soapenv:Header>
                     <soapenv:Body>
                        <ws:finaRequest version="3.0">
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
                                       <xdat:panm>777_{randid}</xdat:panm>  <!-- Используем зашифрованные цифры карты -->              
                                       <xdat:auth>534892</xdat:auth>                                          
                                       <xdat:acq>00001</xdat:acq>
                                       <xdat:mcc>6012</xdat:mcc>                     
                                       <xdat:acqc>398</xdat:acqc>                     
                                       <xdat:term>00004723</xdat:term>                     
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
                  </soapenv:Envelope>'''
        data=data.encode()
        response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap12/v3', data=data, headers=headers)      
        result = {'HTTP Status':None, 'Результат операции': ''}
        try:
          status_code = response.status_code
          content = response.content
        except:
          Log.Warning('Ошибка при выполнении http-запроса:',str(response))
          result['HTTP Status'] = str(response)
          return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
          Log.Warning('Ответ от сервиса ATM2405 содержит ошибку')
          result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
          return result
        else:
          result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id
          
    def POS2416(self, acc_crd, amount, cur, card_num, psys, pos_term, mcc):
        """ Покупка через Soap операцию POS2416, для отработки запроса, требуется счет, Cумма, валюта, и порт"""
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
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
        data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata" xmlns:v1="http://bus.colvir.com/common/v1">
                  <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                  <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2416</wsa:Action>
                  <wsa:MessageID>{randid}</wsa:MessageID>
                     </soapenv:Header>
                     <soapenv:Body>
                        <ws:finaRequest version="3.0">
                           <v3:header>
                              <v1:channel>OW4</v1:channel>
                              <v1:reference>{randid}</v1:reference>
                              <v1:date>{today}T{dt_string}</v1:date>            
                              <v1:language>en</v1:language>            
                           </v3:header>
                           <ws:body>
                              <fina:operation>2416</fina:operation>            
                              <fina:description>Retail</fina:description>
                              <fina:amount currency="{cur}">{amount}</fina:amount>            
                              <fina:account type="{Type}">{acc_crd}</fina:account>            
                              <xdat:xData>
                                 <xdat:trn>                  
                                    <xdat:card>                     
                                       <xdat:a>{amount}</xdat:a>
                                       <xdat:c>{cur}</xdat:c>                     
                                       <xdat:pan>{acc_crd}</xdat:pan>
                                       <xdat:panm>{card_num}</xdat:panm>
                                       <xdat:dt>{today}T{dt_string}</xdat:dt>                     
                                       <xdat:rrn>{randid}</xdat:rrn>                     
                                       <xdat:auth>742398</xdat:auth>                     
                                       <xdat:acq>089992</xdat:acq>
                                       <xdat:mcc>{mcc}</xdat:mcc>                     
                                       <xdat:acqc>398</xdat:acqc>
                                        <xdat:term>{pos_term}</xdat:term>                     
                                        <xdat:caid>01APOST16004002</xdat:caid>
                                        <xdat:loc>ТОО InterMedService-AST</xdat:loc>
                                       <xdat:termtype>POS</xdat:termtype>
                                       <xdat:psys>{psys}</xdat:psys>                     
                                       <xdat:posmode>PBT</xdat:posmode>
                                    </xdat:card>                 
                                 </xdat:trn>
                              </xdat:xData>
                           </ws:body> 
                        </ws:finaRequest>
                     </soapenv:Body>
                  </soapenv:Envelope>'''
        data=data.encode()
        response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap11/v3', data=data, headers=headers)      
        result = {'HTTP Status':None, 'Результат операции': ''}
        try:
          status_code = response.status_code
          content = response.content
        except:
          Log.Warning('Ошибка при выполнении http-запроса:',str(response))
          result['HTTP Status'] = str(response)
          return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
          Log.Warning('Ответ от сервиса ATM2401 содержит ошибку')
          result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
          return result
        else:
          result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id
        
    def ATM2401(self, account, amount, cur):
        """ Покупка через Soap операцию ATM2401, для отработки запроса, требуется счет, Cумма, валюта, и порт"""
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
        # Аргумент port меняем в зависимости от требуемой базы, дописывая в аргументы функции к примеру - "TP" соответственно операция пройдет на базе ТП
        stand, alias = self.GetTestStandAliasDB()
        if alias.lower() in ['cbs3tp']:
          ADDR = "8201"
        elif alias.lower() == 'cbs3bt':
          ADDR = "8181"
        elif alias.lower() in ['cbs3yes',]:
          ADDR = "8221"
        elif alias.lower() == 'cbs3test':
          ADDR = "8231"
        # В зависимости от типа
        if "KZ" in account:
          Type = "IBN"
        else:
          Type = "CRC"
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata" xmlns:v1="http://bus.colvir.com/common/v1">
              <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
              <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2401</wsa:Action>
              <wsa:MessageID>{randid}</wsa:MessageID>
                 </soapenv:Header>
                 <soapenv:Body>
                    <ws:finaRequest version="3.0">
                       <v3:header>
                          <v1:channel>OW4</v1:channel>
                          <v1:reference>{randid}</v1:reference>
                          <v1:date>{today}T{dt_string}</v1:date>            
                          <v1:language>en</v1:language>            
                       </v3:header>
                       <ws:body>
                          <fina:operation>2401</fina:operation>
                          <fina:description>ATM</fina:description>
                          <fina:amount currency="{cur}">{amount}</fina:amount>
                          <fina:account type="{Type}">{account}</fina:account>
                          <xdat:xData>
                             <xdat:trn>
                                <xdat:card>
                                   <xdat:a>{amount}</xdat:a>
                                   <xdat:c>{cur}</xdat:c>                     
                                   <xdat:pan>{account}</xdat:pan>
                                   <xdat:panm>7777_7777</xdat:panm>
                                   <xdat:dt>{today}T{dt_string}</xdat:dt>                     
                                   <xdat:rrn>{randid}</xdat:rrn>
                                   <xdat:auth>962558</xdat:auth>                     
                                   <xdat:acq>00001</xdat:acq>
                                   <xdat:mcc>6011</xdat:mcc>
                                   <xdat:acqc>398</xdat:acqc>
                                   <xdat:term>00011845</xdat:term>
                                   <xdat:caid>TestId</xdat:caid>
                                   <xdat:loc>Saturn</xdat:loc>                     
                                   <xdat:termtype>ATM</xdat:termtype>
                                   <xdat:psys>ON-US</xdat:psys>
                                   <xdat:posmode>PBT</xdat:posmode>
                                </xdat:card>
                             </xdat:trn>
                          </xdat:xData>
                       </ws:body>
                    </ws:finaRequest>
                 </soapenv:Body>
              </soapenv:Envelope>'''
        data=data.encode()
        response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap11/v3', data=data, headers=headers)      
        result = {'HTTP Status':None, 'Результат операции': ''}
        try:
          status_code = response.status_code
          content = response.content
        except:
          Log.Warning('Ошибка при выполнении http-запроса:',str(response))
          result['HTTP Status'] = str(response)
          return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
          Log.Warning('Ответ от сервиса ATM2401 содержит ошибку')
          result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
          return result
        else:
          result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id

    def ATM_2402(self, acc_crd, amount, cur, psys_type):
        """ Пополнение через Soap операцию ATM2402, для отработки запроса, требуется счет, Cумма, валюта, и тип АТМ(ON-US, LOCAL)"""
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
        # Аргумент port меняем в зависимости от требуемой базы, дописывая в аргументы функции к примеру - "TP" соответственно операция пройдет на базе ТП
        stand, alias = self.GetTestStandAliasDB()
        if alias.lower() in ['cbs3tp']:
          ADDR = "8201"
        elif alias.lower() == 'cbs3bt':
          ADDR = "8181"
        elif alias.lower() in ['cbs3yes',]:
          ADDR = "8221"
        elif alias.lower() == 'cbs3test':
          ADDR = "8231"
        # В зависимости от типа
        if "KZ" in acc_crd:
          Type = "IBN"
        else:
          Type = "CRC"
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata" xmlns:v1="http://bus.colvir.com/common/v1">
              <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
              <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2402</wsa:Action>
              <wsa:MessageID>{randid}</wsa:MessageID>
                 </soapenv:Header>
                 <soapenv:Body>
                    <ws:finaRequest version="3.0">
                       <v3:header>
                          <v1:channel>OW4</v1:channel>
                          <v1:reference>{randid}</v1:reference>
                          <v1:date>{today}T{dt_string}</v1:date>            
                          <v1:language>en</v1:language>            
                       </v3:header>
                       <ws:body>
                          <fina:operation>2402</fina:operation>
                          <fina:description>ATM</fina:description>
                          <fina:amount currency="{cur}">{amount}</fina:amount>
                          <fina:account type="{Type}">{acc_crd}</fina:account>            
                          <xdat:xData>
                             <xdat:trn>                  
                                <xdat:card>                     
                                   <xdat:a>{amount}</xdat:a>
                                   <xdat:c>{cur}</xdat:c>                     
                                   <xdat:pan>{acc_crd}</xdat:pan>
                                   <xdat:panm>checktest</xdat:panm>
                                   <xdat:dt>{today}T{dt_string}</xdat:dt>                     
                                   <xdat:rrn>{randid}</xdat:rrn>                     
                                   <xdat:auth>410441</xdat:auth>                     
                                   <xdat:acq>409663</xdat:acq>
                                   <xdat:mcc>6011</xdat:mcc>                     
                                   <xdat:acqc>398</xdat:acqc>                     
                                   <xdat:term>00002010</xdat:term>                     
                                   <xdat:caid>GTA BANK</xdat:caid>
                                   <xdat:loc>Moon</xdat:loc>                     
                                   <xdat:termtype>ATM</xdat:termtype>
                                   <xdat:psys>{psys_type}</xdat:psys>                     
                                   <xdat:posmode>PBT</xdat:posmode>
                                </xdat:card>
                             </xdat:trn>
                          </xdat:xData>
                       </ws:body>
                    </ws:finaRequest>
                 </soapenv:Body>
              </soapenv:Envelope>'''
        data=data.encode()
        response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap11/v3', data=data, headers=headers)      
        result = {'HTTP Status':None, 'Результат операции': ''}
        try:
          status_code = response.status_code
          content = response.content
        except:
          Log.Warning('Ошибка при выполнении http-запроса:',str(response))
          result['HTTP Status'] = str(response)
          return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
          Log.Warning('Ответ от сервиса ATM2402 содержит ошибку')
          result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
          return result
        else:
          result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id
        

    def POS2411(self, acc_idn, amount, cur, card_num, psys, term_id, mcc):
        """ Снятие через Soap операцию POS2411, для отработки запроса, требуется счет, Cумма, валюта, и порт"""
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
        # Аргумент port меняем в зависимости от требуемой базы, дописывая в аргументы функции к примеру - "TP" соответственно операция пройдет на базе ТП
        stand, alias = self.GetTestStandAliasDB()
        if alias.lower() in ['cbs3tp']:
          ADDR = "8201"
        elif alias.lower() == 'cbs3bt':
          ADDR = "8181"
        elif alias.lower() in ['cbs3yes',]:
          ADDR = "8221"
        elif alias.lower() == 'cbs3test':
          ADDR = "8231"
        # В зависимости от типа
        if "KZ" in acc_idn:
          Type = "IBN"
        else:
          Type = "CRC"
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata" xmlns:v1="http://bus.colvir.com/common/v1">
                  <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                  <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2411</wsa:Action>
                  <wsa:MessageID>{randid}</wsa:MessageID>
                     </soapenv:Header>
                     <soapenv:Body>
                        <ws:finaRequest version="3.0">
                           <v3:header>
                              <v1:channel>OW4</v1:channel>
                               <v1:reference>{randid}</v1:reference>
                              <v1:date>{today}T{dt_string}</v1:date>            
                              <v1:language>en</v1:language>            
                           </v3:header>
                           <ws:body>
                              <fina:operation>2411</fina:operation>            
                              <fina:description>Cash Withdrawal</fina:description>
                              <fina:amount currency="{cur}">{amount}</fina:amount>            
                              <fina:account type="{Type}">{acc_idn}</fina:account>            
                              <xdat:xData>
                                 <xdat:trn>                  
                                    <xdat:card>                     
                                       <xdat:a>{amount}</xdat:a>
                                       <xdat:c>{cur}</xdat:c>                     
                                       <xdat:pan>{acc_idn}</xdat:pan>
                                       <xdat:panm>{card_num}</xdat:panm>
                                       <xdat:dt>{today}T{dt_string}</xdat:dt>                     
                                       <xdat:rrn>{randid}</xdat:rrn>                     
                                       <xdat:auth>323838</xdat:auth>                     
                                       <xdat:acq>089992</xdat:acq>
                                       <xdat:mcc>{mcc}</xdat:mcc>                     
                                       <xdat:acqc>398</xdat:acqc>
                                       <xdat:term>{term_id}</xdat:term>                     
                                       <xdat:caid>9694155847     </xdat:caid>
                                       <xdat:loc>MAGNUM CASH&amp;CARRY       &gt;ALMATY       KZ</xdat:loc>                     
                                       <xdat:termtype>POS</xdat:termtype>
                                       <xdat:psys>{psys}</xdat:psys>                    
                                       <xdat:posmode>PBT</xdat:posmode>
                                    </xdat:card>                 
                                 </xdat:trn>
                              </xdat:xData>
                           </ws:body>
                        </ws:finaRequest>
                     </soapenv:Body>
                  </soapenv:Envelope>'''
        data=data.encode()
        response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap11/v3', data=data, headers=headers)      
        result = {'HTTP Status':None, 'Результат операции': ''}
        try:
          status_code = response.status_code
          content = response.content
        except:
          Log.Warning('Ошибка при выполнении http-запроса:',str(response))
          result['HTTP Status'] = str(response)
          return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
          Log.Warning('Ответ от сервиса POS2411 содержит ошибку')
          result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
          return result
        else:
          result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id
        
        
    def SetInstallment(self, acc_num):
        """ Снятие через Soap операцию POS2411, для отработки запроса, требуется счет, Cумма, валюта, и порт"""
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
        # Аргумент port меняем в зависимости от требуемой базы, дописывая в аргументы функции к примеру - "TP" соответственно операция пройдет на базе ТП
        stand, alias = self.GetTestStandAliasDB()
        if alias.lower() in ['cbs3tp']:
          ADDR = "8201"
        elif alias.lower() == 'cbs3bt':
          ADDR = "8181"
        elif alias.lower() in ['cbs3yes',]:
          ADDR = "8221"
        elif alias.lower() == 'cbs3test':
          ADDR = "8231"
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata" xmlns:v1="http://bus.colvir.com/common/v1">
                  <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                  <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2411</wsa:Action>
                  <wsa:MessageID>{randid}</wsa:MessageID>
                     </soapenv:Header>
                     <soapenv:Body>
                        <ws:finaRequest version="3.0">
                           <v3:header>
                              <v1:channel>OW4</v1:channel>
                               <v1:reference>{randid}</v1:reference>
                              <v1:date>{today}T{dt_string}</v1:date>            
                              <v1:language>en</v1:language>            
                           </v3:header>
                           <ws:body>
                              <fina:operation>2411</fina:operation>            
                              <fina:description>Cash Withdrawal</fina:description>
                              <fina:amount currency="{cur}">{amount}</fina:amount>            
                              <fina:account type="{Type}">{acc_idn}</fina:account>            
                              <xdat:xData>
                                 <xdat:trn>                  
                                    <xdat:card>                     
                                       <xdat:a>{amount}</xdat:a>
                                       <xdat:c>{cur}</xdat:c>                     
                                       <xdat:pan>{acc_idn}</xdat:pan>
                                       <xdat:panm>{card_num}</xdat:panm>
                                       <xdat:dt>{today}T{dt_string}</xdat:dt>                     
                                       <xdat:rrn>{randid}</xdat:rrn>                     
                                       <xdat:auth>323838</xdat:auth>                     
                                       <xdat:acq>089992</xdat:acq>
                                       <xdat:mcc>{mcc}</xdat:mcc>                     
                                       <xdat:acqc>398</xdat:acqc>
                                       <xdat:term>{term_id}</xdat:term>                     
                                       <xdat:caid>9694155847     </xdat:caid>
                                       <xdat:loc>MAGNUM CASH&amp;CARRY       &gt;ALMATY       KZ</xdat:loc>                     
                                       <xdat:termtype>POS</xdat:termtype>
                                       <xdat:psys>{psys}</xdat:psys>                    
                                       <xdat:posmode>PBT</xdat:posmode>
                                    </xdat:card>                 
                                 </xdat:trn>
                              </xdat:xData>
                           </ws:body>
                        </ws:finaRequest>
                     </soapenv:Body>
                  </soapenv:Envelope>'''
        data=data.encode()
        response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap11/v3', data=data, headers=headers)      
        result = {'HTTP Status':None, 'Результат операции': ''}
        try:
          status_code = response.status_code
          content = response.content
        except:
          Log.Warning('Ошибка при выполнении http-запроса:',str(response))
          result['HTTP Status'] = str(response)
          return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
          Log.Warning('Ответ от сервиса POS2416 содержит ошибку')
          result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
          return result
        else:
          result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id    
        

    def ATMNonCard2541(self, acc_num, cur, sum):
        """ Пополнение счета клиента без пластиковой карты по операции 2541  """
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
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
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f'''<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:v1="http://bus.colvir.com/common/v1" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata">
                 <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                    <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2541</wsa:Action>
                    <wsa:MessageID>{randid}</wsa:MessageID>
                 </soapenv:Header>
                 <soapenv:Body>
                    <ws:finaRequest version="3.0">
                       <v3:header>
                          <v1:channel>SRB</v1:channel>
                          <v1:reference>{randid}</v1:reference>
                          <v1:date>{today}T{dt_string}</v1:date>
                          <v1:language>RU</v1:language>
                       </v3:header>
                       <ws:body>
                          <fina:operation>2541</fina:operation>
                          <fina:description>BCC Deposit Increase</fina:description>
                          <fina:amount currency="{cur}">{sum}</fina:amount>
                          <fina:fee currency="{cur}">{sum}</fina:fee>
                          <fina:account type="IBN">{acc_num}</fina:account>
                       </ws:body>
                    </ws:finaRequest>
                 </soapenv:Body>
              </soapenv:Envelope>'''
        data = data.encode()
        try:
            response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap11/v3', data=data, headers=headers)      
            result = {'HTTP Status': None, 'Результат операции': ''}
            status_code = response.status_code
            content = response.content
        except Exception as e:
            Log.Warning('Ошибка при выполнении http-запроса:', str(e))
            result['HTTP Status'] = f"Error: {str(e)}"
            return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
            Log.Warning('Ответ от сервиса ATM2541 содержит ошибку')
            result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
            return result
        else:
            result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id
        
        
    def CardDebit2423(self, acc_num, card_num, cur, sum):
        """ Переводы P2P Card Debit """
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
        result = ''
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
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f'''<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope"  xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:v1="http://bus.colvir.com/common/v1" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata">
                  <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                  <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2423</wsa:Action>
                  <wsa:MessageID>{randid}</wsa:MessageID>
                     </soapenv:Header>
                     <soapenv:Body>
                        <ws:finaRequest version="3.0">
                           <v3:header>
                              <v1:channel>SRB</v1:channel>
                              <v1:reference>{randid}</v1:reference>
                              <v1:date>{today}T{dt_string}</v1:date>
                              <v1:language>en</v1:language>
                           </v3:header>
                           <ws:body>
                              <fina:operation>2423</fina:operation>
                              <fina:description>CH Debit</fina:description>
                              <fina:amount currency="{cur}">{sum}</fina:amount>
                              <fina:account type="IBN">{acc_num}</fina:account>
                              <xdat:xData>
                                 <xdat:trn>
                                    <xdat:card>
                                       <xdat:a>{sum}</xdat:a>
                                       <xdat:c>{cur}</xdat:c>
                                       <xdat:pan>{acc_num}</xdat:pan>
                                       <xdat:panm>{card_num}</xdat:panm>
                                       <xdat:dt>{today}T{dt_string}</xdat:dt>
                                       <xdat:rrn>{randid}</xdat:rrn>
                                       <xdat:auth>320817</xdat:auth>
                                       <xdat:acq>431433</xdat:acq>
                                       <xdat:mcc>6012</xdat:mcc>
                                       <xdat:acqc>398</xdat:acqc>
                                       <xdat:term>98128487</xdat:term>
                                       <xdat:caid>KAZKOMMERTSBANK</xdat:caid>
                                       <xdat:loc>P2P CARD2CARD            ALMATY       KZ</xdat:loc>
                                       <xdat:termtype>INET</xdat:termtype>
                                       <xdat:psys>LOCAL</xdat:psys>
                                       <xdat:posmode>CVC2</xdat:posmode>
                     <xdat:eci>05</xdat:eci>
                                    </xdat:card>
                                    <xdat:cardinfo>
                                       <xdat:bin>466720</xdat:bin>
                                    </xdat:cardinfo>
                                 </xdat:trn>
                              </xdat:xData>
                           </ws:body>
                        </ws:finaRequest>
                     </soapenv:Body>
                  </soapenv:Envelope>'''
        data = data.encode()
        try:
            response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap12/v3', data=data, headers=headers)      
            result = {'HTTP Status': None, 'Результат операции': ''}
            status_code = response.status_code
            content = response.content
        except Exception as e:
            Log.Warning('Ошибка при выполнении http-запроса:', str(e))
            result['HTTP Status'] = f"Error: {str(e)}"
            return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
            Log.Warning('Ответ от сервиса ATM2541 содержит ошибку')
            result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
            return result
        else:
            result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id
        
    def CardDeposit2424(self, acc_num, card_num, cur, sum):
        """ Пополнение через P2P Card Debit """
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
        result = ''
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
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f'''<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:v1="http://bus.colvir.com/common/v1" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA">
                    <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">   
                    <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2424</wsa:Action>
                       <wsa:MessageID>{randid}</wsa:MessageID>
                     </soap:Header>
                       <soap:Body>
                          <ws:finaRequest version="3.0">
                             <v3:header>
                                <v1:channel>SRB</v1:channel>
                                <v1:reference>{randid}</v1:reference>
                                <v1:date>{today}T{dt_string}</v1:date>
                             </v3:header>
                             <ws:body>
                                <fina:operation>2424</fina:operation>
                                 <fina:description>SRB</fina:description>
                                <fina:amount currency="{cur}">{sum}</fina:amount>
                                <fina:account type="IBN">{acc_num}</fina:account>
                                <xdat:xData>
                                   <xdat:trn>
                                      <xdat:card>
                                         <xdat:a>{sum}</xdat:a>
                                         <xdat:c>{cur}</xdat:c>
                                         <xdat:pan>{acc_num}</xdat:pan>
                                         <xdat:panm>{card_num}</xdat:panm>
                                         <xdat:dt>{today}T{dt_string}</xdat:dt>
                                         <xdat:rrn>624581792010</xdat:rrn>
                                         <xdat:auth>320817</xdat:auth>
                                         <xdat:acq>431433</xdat:acq>
                                         <xdat:mcc>6012</xdat:mcc>
                                         <xdat:acqc>398</xdat:acqc>
                                         <xdat:term>98128487</xdat:term>
                                         <xdat:caid>KAZKOMMERTSBANK</xdat:caid>
                                         <xdat:loc>P2P CARD2CARD            ALMATY       KZ</xdat:loc>
                                         <xdat:termtype>INET</xdat:termtype>
                                         <xdat:psys>LOCAL</xdat:psys>
                                         <xdat:posmode>CVC2</xdat:posmode>
                            			 <xdat:eci>05</xdat:eci>
                                      </xdat:card>
                                      <xdat:cardinfo>
                                         <xdat:bin>466720</xdat:bin>
                                      </xdat:cardinfo>
                                   </xdat:trn>
                                </xdat:xData>
                             </ws:body>
                          </ws:finaRequest>
                       </soap:Body>
                    </soap:Envelope>'''
        data = data.encode()
        try:
            response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap12/v3', data=data, headers=headers)      
            result = {'HTTP Status': None, 'Результат операции': ''}
            status_code = response.status_code
            content = response.content
        except Exception as e:
            Log.Warning('Ошибка при выполнении http-запроса:', str(e))
            result['HTTP Status'] = f"Error: {str(e)}"
            return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
            Log.Warning('Ответ от сервиса ATM2541 содержит ошибку')
            result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
            return result
        else:
            result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id

    def CardCashIn2543(self, acc_num, cur, sum):
        """ Пополнение баланса с КНП_АТМ """
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
        result = ''
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
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:v1="http://bus.colvir.com/common/v1" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata">
                  <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                  <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2543</wsa:Action>
                  <wsa:MessageID>{randid}</wsa:MessageID>
                     </soapenv:Header>
                     <soapenv:Body>
                        <ws:finaRequest version="3.0">
                           <v3:header>
                              <v1:channel>ATM</v1:channel>
                              <v1:reference>{randid}</v1:reference>
                              <v1:date>{today}T{dt_string}</v1:date>            
                              <v1:language>en</v1:language>            
                           </v3:header>
                           <ws:body>
                              <fina:operation>2543</fina:operation>            
                              <fina:amount currency="{cur}">{sum}</fina:amount>                        
                              <fina:account type="IBN">{acc_num}</fina:account>                      
                              <xdat:xData>
                                 <xdat:trn>                  
                                    <xdat:card>                     
                                       <xdat:a>{sum}</xdat:a>
                                       <xdat:c>{cur}</xdat:c>                                          
                                      <xdat:panm/>
                                       <xdat:dt>{today}T{dt_string}</xdat:dt>       
                                       <sttldt>{today}T{dt_string}</sttldt>                                   
                                       <xdat:rrn/>                     
                                       <xdat:auth>0000000</xdat:auth>                                          
                                      <xdat:mcc>9999</xdat:mcc>                     
                                       <xdat:term>00170374</xdat:term>                     
                                      <xdat:loc>AST</xdat:loc>                    
                                       <country>KZ</country>
                                       <adr>device address</adr>
                                       <xdat:termtype>ATM</xdat:termtype>
                                       <xdat:psys>LOCAL</xdat:psys>                  
                                   </xdat:card>            
                                 </xdat:trn>
                              </xdat:xData>
                           </ws:body>
                        </ws:finaRequest>
                     </soapenv:Body>
                  </soapenv:Envelope>'''
        data = data.encode()
        try:
            response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap12/v3', data=data, headers=headers)      
            result = {'HTTP Status': None, 'Результат операции': ''}
            status_code = response.status_code
            content = response.content
        except Exception as e:
            Log.Warning('Ошибка при выполнении http-запроса:', str(e))
            result['HTTP Status'] = f"Error: {str(e)}"
            return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
            Log.Warning('Ответ от сервиса ATM2541 содержит ошибку')
            result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
            return result
        else:
            result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id

    def B2BTrasnfer(self, acc_num, card_num, cur, sum):
        """ Переводы B2B межбанковский перевод """
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
        result = ''
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
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:v1="http://bus.colvir.com/common/v1" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata">
                  <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                  <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2560</wsa:Action>
                  <wsa:MessageID>{randid}</wsa:MessageID>
                     </soapenv:Header>
                     <soapenv:Body>
                        <ws:finaRequest version="3.0">
                           <v3:header>
                              <v1:channel>SRB</v1:channel>
                              <v1:reference>{randid}</v1:reference>
                              <v1:date>{today}T{dt_string}</v1:date>
                               <v1:language>en</v1:language>  
                           </v3:header>
                           <ws:body>
                              <fina:operation>2560</fina:operation>
                              <fina:amount currency="{cur}">{sum}</fina:amount>
                              <fina:account type="IBN">{acc_num}</fina:account>
                               <xdat:xData>
                                 <xdat:trn>          
                                      <xdat:national_bank_payment>
                                      <xdat:processingMethod>NORMAL</xdat:processingMethod>
                                      <xdat:beneficiary>
                             		  <xdat:accountIban>KZ96722C000021629332</xdat:accountIban>
                              			<xdat:name>Test Testov Testovich</xdat:name>
                             			 <xdat:legalIdentificationCode>890806400795</xdat:legalIdentificationCode>
                            			  <xdat:partyCode>19</xdat:partyCode>
                                             </xdat:beneficiary>
                                             <xdat:beneficiaryBank>CASPKZKA</xdat:beneficiaryBank>
                                       <xdat:purposeCode>119</xdat:purposeCode>
                                        <xdat:paymentDetails/>
                                    </xdat:national_bank_payment>               
                                 </xdat:trn>
                              </xdat:xData>
                           </ws:body>
                        </ws:finaRequest>
                     </soapenv:Body>
                  </soapenv:Envelope>'''
        data = data.encode()
        try:
            response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap12/v3', data=data, headers=headers)      
            result = {'HTTP Status': None, 'Результат операции': ''}
            status_code = response.status_code
            content = response.content
        except Exception as e:
            Log.Warning('Ошибка при выполнении http-запроса:', str(e))
            result['HTTP Status'] = f"Error: {str(e)}"
            return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
            Log.Warning('Ответ от сервиса ATM2541 содержит ошибку')
            result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
            return result
        else:
            result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id

    def ServiceCommis(self, acc_num, cur, sum):
        """ Сервисная комиссия 2553 """
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
        result = ''
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
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f'''<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:v1="http://bus.colvir.com/common/v1" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA">
                   <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                   <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2553</wsa:Action>
                  <wsa:MessageID>{randid}</wsa:MessageID>
                     </soapenv:Header>
                     <soapenv:Body>
                        <ws:finaRequest version="3.0">
                           <v3:header>
                              <v1:channel>SRB</v1:channel>
                              <v1:reference>{randid}</v1:reference>
                              <v1:date>{today}T{dt_string}</v1:date>
                              <!--Optional:-->
                              <v1:language>RU</v1:language>
                           </v3:header>
                  <ws:body>
                              <fina:operation>2553</fina:operation>
                              <!--Optional:-->
                              <fina:description>BCC Domestic Payment</fina:description>
                              <fina:amount currency="{cur}">{sum}</fina:amount>
                              <!--Optional:-->
                              <fina:fee currency="{cur}">{sum}</fina:fee>
                              <!--You have a CHOICE of the next 2 items at this level-->
                              <fina:account type="IBN">{acc_num}</fina:account>
                              <!--You have a CHOICE of the next 1 items at this level-->
                           </ws:body>
                        </ws:finaRequest>
                     </soapenv:Body>
                  </soapenv:Envelope>'''
        data = data.encode()
        try:
            response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap12/v3', data=data, headers=headers)      
            result = {'HTTP Status': None, 'Результат операции': ''}
            status_code = response.status_code
            content = response.content
        except Exception as e:
            Log.Warning('Ошибка при выполнении http-запроса:', str(e))
            result['HTTP Status'] = f"Error: {str(e)}"
            return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
            Log.Warning('Ответ от сервиса ATM2553 содержит ошибку')
            result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
            return result
        else:
            result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id       
        
    def MiniExtract(self, acc_num, cur, sum):
        """ Мини выписка 2451 """
        today = date.today() #  Переменные для даты и времени внутри запроса
        dt_string = datetime.now().strftime("%H:%M:%S") #  Переменные для даты и времени внутри запроса
        randid = self.generate_reference() 
        result = ''
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
        headers = {'Content-Type': 'text/xml;charset=UTF-8'} # Устанавливаем то, что принимает наш сервер
        data = f'''<soap:Envelope 
                   xmlns:soap="http://www.w3.org/2003/05/soap-envelope" 
                   xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" 
                   xmlns:v3="http://bus.colvir.com/service/cap/v3" 
                   xmlns:v1="http://bus.colvir.com/common/v1" 
                   xmlns:stmt="http://bus.colvir.com/service/cap/v3/STMT">
                <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">   
                <wsa:Action>http://bus.colvir.com/service/cap/v3/STMT/STMT2451</wsa:Action>
                   <wsa:MessageID>{randid}</wsa:MessageID>
                 </soap:Header>
                   <soap:Body>
                      <ws:stmtRequest version="3.0">
                         <v3:header>
                            <v1:channel>OW4</v1:channel>
                            <v1:reference>{randid}</v1:reference>
                            <v1:date>{today}T{dt_string}</v1:date>
                         </v3:header>
                         <ws:body>
                            <stmt:operation>2451</stmt:operation>
                            <stmt:description>Mini Statement</stmt:description>
                            <stmt:account type="{cur}">{acc_num}</stmt:account>
                            <stmt:transactionsLimit>1</stmt:transactionsLimit>
                           <!--You have a CHOICE of the next 3 items at this level-->
                            <stmt:idRange>
                               <stmt:from>1</stmt:from>
                            </stmt:idRange>
                        </ws:body>
                      </ws:stmtRequest>
                   </soap:Body>
                </soap:Envelope>'''
        data = data.encode()
        try:
            response = requests.post(f'http://10.15.23.213:{ADDR}/cxf/cap/soap12/v3', data=data, headers=headers)      
            result = {'HTTP Status': None, 'Результат операции': ''}
            status_code = response.status_code
            content = response.content
        except Exception as e:
            Log.Warning('Ошибка при выполнении http-запроса:', str(e))
            result['HTTP Status'] = f"Error: {str(e)}"
            return result
        if not (status_code == 200 and \
        self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}status') == '1'):
            Log.Warning('Ответ от сервиса ATM2541 содержит ошибку')
            result['HTTP Status'] = str(response.status_code) +' '+ str(response.text)
            return result
        else:
            result['HTTP Status'] = '200' 
        tran_id = self.GetXmlValue(response.content,'.//{http://bus.colvir.com/service/cap/v3}colvirId')
        return tran_id                             