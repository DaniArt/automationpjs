from ColvirFramework import *

class Credits(CommonOperation, GenerateTestingData, CreateJsonReport):
    def CreateCreditDoc(self, cli_code: str, num_contract: str, product_code: str,
                        dep_contract: str, fromdate: str, todate: str, val_code: str,
                        amount: str, period: str, purpose: str, trf_code, individ_rate: str,
                        individ_prim: str, date_decision_kk: str, source_finance: str,
                        sign_finance: str, note_finance: str, source_finance_km: str,
                        date_agreement: str, market_rate: str, sppi: str, balance_debt: str,
                        credit_officer: str, credit_admin: str, issuing_approval: str,
                        date_schedule: str, app_loan: int, date_signing: str, prim: str = None):
                        # перенос строки
        # Метод вызывает процедуру для создания кредитнного договора
        self.cli_code = cli_code # код карточки клиента
        self.num_contract = num_contract # номер договора, который будет создаваться
        self.product_code = product_code # код продукта договора
        self.dep_contract = dep_contract # Департамент договора
        self.fromdate = fromdate # дата начала
        self.todate = todate # дата окончания
        self.val_code = val_code # код валюты
        self.amount = amount # сумма договора
        self.period = period # срок кредита
        self.purpose = purpose # цель кредита
        self.trf_code = trf_code # код тарифа
        # данные для установки индивидуальной ставки
        self.individ_rate = individ_rate # значение индивидуальной процентной ставки во вкладке суммы
        self.individ_prim = individ_prim # примечание индивидуальной процентной ставки
        #-----------
        # параметры договора
        self.date_decision_kk = date_decision_kk # дата решения КК
        self.source_finance = source_finance # источник финансирования
        self.sign_finance = sign_finance # признак финансирования
        self.note_finance = note_finance # примечание по финансированию
        self.source_finance_km = source_finance_km # источник финансирования КМ
        self.date_agreement = date_agreement # дата соглашения
        self.market_rate = market_rate # рыночная ставка
        self.sppi = sppi # результат SPPI
        self.balance_debt = balance_debt # остаток задолженности по беззалоговым займам
        self.credit_officer = credit_officer # кредитный офицер
        self.credit_admin = credit_admin # кредитный администратор
        self.issuing_approval = issuing_approval # орган одобрения выдачи
        self.date_schedule = date_schedule # дата начала формирования графика
        self.app_loan = app_loan # заявка на кредит без комиссии
        self.date_signing = date_signing # дата подписания
        #-----------
        self.prim = prim # примечание к договору. По умолчанию None

        self.OracleCallProcedure("Z_PKG_AUTO_TEST.AT_pCreCreditContract", self.dep_contract, self.product_code, self.fromdate, self.todate,
                                                     self.val_code, self.amount, self.period, self.cli_code, self.prim,
                                                     self.num_contract, self.purpose, self.trf_code, self.individ_rate,
                                                     self.individ_prim, self.date_decision_kk, self.source_finance,
                                                     self.sign_finance, self.note_finance, self.source_finance_km,
                                                     self.date_agreement, self.market_rate, self.sppi, self.balance_debt,
                                                     self.credit_officer, self.credit_admin, self.issuing_approval,
                                                     self.date_schedule, self.app_loan, self.date_signing,
                                                     return_value = False)
                                                     # перенос строки
