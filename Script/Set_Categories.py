from CardFramework import *

def Set_cat_AllDataSet():
    """ Отправка на акцептование карты клиента по всему датасету """
    NCRD = CardFramework()
    data_list = NCRD.ReadDatasetFromDB('cliacc_cashback')
    for row in data_list:
        if row['TERM_TYPE'] == '40132620':
            form_data = Set_cat(row['cli_id'])
 

def Set_cat(cli_id):
    card = CardFramework()
    set_cli_cat = f"""declare
                            l_clicode varchar(2000 char) := {cli_id};
                            l_cat_id1 number := 1000; 
                            l_cat_id2 number := 700;

                            l_nNumErr number;
                            l_cErrMsg varchar2(2000 char);

                            begin
                              delete from bcm_user.bcm_clicat_hst
                               where trunc(sysdate) between fromdate and todate
                                 and (dep_id, id) in (select cli_dep_id, cli_id
                                                        from bcm_user.bcm_cliprm
                                                       where type_ref = 'CODE'
                                                         and cvalue = l_clicode);

                              commit;

                              bcm_user.bcm_pkg_cat.pSaveBonusClass(pClicode  => l_clicode,
                                                                   pCatId_1  => l_cat_id1,
                                                                   pCatId_2  => l_cat_id2,
                                                                   pOperType => 'ACTIVATE',
                                                                   p_nNumErr => l_nNumErr,
                                                                   p_cErrMsg => l_cErrMsg);
                              commit;
                              dbms_output.put_line(l_nNumErr || ' - ' || l_cErrMsg);
                            end;"""
    card.OracleHandlerDB(set_cli_cat, dml_query='True')