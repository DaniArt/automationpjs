from CardFramework import *

def CashIn2405_AllDataSet():
    """ Отправка на акцептование карты клиента по всему датасету """
    NCRD = CardFramework()
    NCRD.LoginInColvir()
    data_list = NCRD.ReadDatasetFromDB('crdreq_data')
    for row in data_list:
        if row['DEPO_CODE'] == 'AA6':
            NCRD.StartDebugLog()
            form_data = CashIn2405(row['ACC_CRD'])
            NCRD.SaveDebugLog()
            
def CashIn2405(acc_crd):
    """ Отправка на акцептование карты клиента """
    NCRD = CardFramework()
    NCRD.TaskInput('NCRD')
    NCRD.WaitLoadWindow('frmFilterParams')
    url = "http://10.15.23.213:8181/cxf/cap/soap12/v3"
    headers = {'content-type': 'text/xml'}
    body = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fina="http://bus.colvir.com/service/cap/v3/FINA" xmlns:ws="http://bus.colvir.com/service/cap/v3/ws" xmlns:v3="http://bus.colvir.com/service/cap/v3" xmlns:xdat="http://bus.colvir.com/service/cap/v3/FINA/xdata" xmlns:v1="http://bus.colvir.com/common/v1">
    <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
    <wsa:Action>http://bus.colvir.com/service/cap/v3/FINA/FINA2405</wsa:Action>
    <wsa:MessageID>${=java.util.UUID.randomUUID()}</wsa:MessageID>
       </soapenv:Header>
       <soapenv:Body>
          <ws:finaRequest version="3.0">
             <v3:header>
                <v1:channel>OW4</v1:channel>
                <v1:reference>TEST${=(int)(Math.random()*9999)}</v1:reference>
                <v1:date>${=new Date().format("yyyy-MM-dd'T'HH:mm:ss")}</v1:date>            
                <v1:language>en</v1:language>            
             </v3:header>
             <ws:body>
                <fina:operation>2405</fina:operation>            
                <fina:description>Note Acceptance</fina:description>
                <fina:amount currency="KZT">1500000</fina:amount>                        
                <fina:account type="IBN">KZ888562204115582199</fina:account>                        
                <xdat:xData>
                   <xdat:trn>                  
                      <xdat:card>                     
                         <xdat:a>1500000</xdat:a>
                         <xdat:c>KZT</xdat:c>                                          
                         <xdat:pan>${#TestCase#bValue}</xdat:pan>
                         <xdat:panm>${#TestCase#aValue}</xdat:panm>
                         <xdat:dt>${=new Date().format("yyyy-MM-dd'T'HH:mm:ss")}</xdat:dt>                                          
                         <xdat:rrn>${=(int)(Math.random()*999999)}</xdat:rrn>                     
                         <xdat:auth>534892</xdat:auth>                                          
                         <xdat:acq>00001</xdat:acq>
                         <xdat:mcc>6012</xdat:mcc>                     
                         <xdat:acqc>398</xdat:acqc>                     
                         <xdat:term>00004723</xdat:term>                     
                         <xdat:caid>2096574-DC/200744</xdat:caid>
                         <xdat:loc>AST                     &gt;ASTANA       KZ</xdat:loc>                    
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
  response = NCRD.request.post(url,data=body,headers=headers)
  Log.Message(response)