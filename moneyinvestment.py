import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from steuertarif_24 import *

class Taxes():
    def __init__(self, einkommen_steuerbar, plot=False):
        self.einkommen_persoenlich = einkommen_steuerbar
        self.max_income = 200000

        self.steuerfuss_kanton = 105 #St.Gallen
        self.steuerfuss_gemeinde = 127 #Uzwil
        self.steuersatz = 115 #Bund

        self.steuer_rechner_allgemein()
        self.steuer_rechner_persoenlich(self.einkommen_persoenlich)
        if plot:
            self.plot_subplots()
            print(f"Ihre direkte Bundessteuer beträgt: {self.steuer_persoenlich['Bund']}CHF")


    def steuer_rechner_persoenlich(self, income=0):
        bundes_steuer = []
        kantons_steuer = []
        gemeinde_steuer = []
        totale_steuer = []

        if income < steuertarif_einkommen[0]:
            bundes_steuer = 0
            kantons_steuer = 0
            gemeinde_steuer = 0
            totale_steuer = 0
            grenzsteuersatz = 0
            pass
        else:
            bundes_steuer = self.werte_finden(income)
            kantons_steuer = bundes_steuer * (self.steuersatz + self.steuerfuss_kanton)/100
            gemeinde_steuer = bundes_steuer * (self.steuersatz + self.steuerfuss_gemeinde)/100
            totale_steuer = bundes_steuer + kantons_steuer + gemeinde_steuer
            grenzsteuersatz = self.grenzsteuersatz(income, income+100)

        self.steuer_persoenlich = {"Einkommen": income,
                                   "Bund": bundes_steuer,
                                   "Kanton": kantons_steuer,
                                   "Gemeinde": gemeinde_steuer,
                                   "Total": totale_steuer,
                                   "Progression": grenzsteuersatz}

    def grenzsteuersatz(self, val_small, val_big):
        tax_small = self.werte_finden(val_small) * (1 + self.steuersatz + self.steuerfuss_gemeinde + self.steuerfuss_kanton)/100
        tax_big = self.werte_finden(val_big) * (1 + self.steuersatz + self.steuerfuss_gemeinde + self.steuerfuss_kanton)/100
        return np.round((tax_big - tax_small)/100*100, 0)

    def werte_finden(self, income):
        index = 0
        val = 0
        while income >= val:
            index += 1
            val = steuertarif_einkommen[index]
        key_prev = 0
        for key in steuertarif_zusatz:
            if income <= key:
                diff_factor = (income - steuertarif_einkommen[index-1]) / 100
                additional_percent = steuertarif_zusatz[key_prev]
                val = steuertarif_steuer[index-1] + round(diff_factor,0) * additional_percent
                break
            else:
                key_prev = key
        return val

    def steuer_rechner_allgemein(self):
        income_all = np.arange(0, self.max_income, 1000)
        bundes_steuer = []
        kantons_steuer = []
        gemeinde_steuer = []
        totale_steuer = []
        grenzsteuersatz = []
        for income in income_all:
            if income < steuertarif_einkommen[0]:
                bundes_steuer.append(0)
                kantons_steuer.append(0)
                gemeinde_steuer.append(0)
                totale_steuer.append(0)
                grenzsteuersatz.append(0)
                pass
            else:
                val = self.werte_finden(income)
                grenzsteuersatz.append(self.grenzsteuersatz(income, income+100))

                bundes_steuer.append(val)
                kantons_steuer.append(bundes_steuer[-1] * (self.steuersatz + self.steuerfuss_kanton)/100)
                gemeinde_steuer.append(bundes_steuer[-1] * (self.steuersatz + self.steuerfuss_gemeinde)/100)
                totale_steuer.append(bundes_steuer[-1] + kantons_steuer[-1] + gemeinde_steuer[-1])

        self.steuer_allgemein = {"Einkommen": income_all,
                                 "Bund": bundes_steuer,
                                 "Kanton": kantons_steuer,
                                 "Gemeinde": gemeinde_steuer,
                                 "Total": totale_steuer,
                                 "Progression": grenzsteuersatz}

    def plot_subplots(self):
        fig, axs = plt.subplots(figsize=(10, 5))  # Creating a figure with two subplots
        
        # Plotting data1 on the first subplot
        colors = ["royalblue", "mediumpurple", "mediumorchid", "mediumvioletred", "tomato"]
        factor = 0.01

        axs.set_title("Steuern Uzwil")
        axs.set_xlabel("Einkommen / CHF")
        axs.set_ylabel("Steuern / CHF")
        
        axs.plot(self.steuer_allgemein["Einkommen"], self.steuer_allgemein["Bund"], linestyle=':', color=colors[0], label="Bund")
        axs.plot(self.steuer_allgemein["Einkommen"], self.steuer_allgemein["Kanton"], linestyle=':', color=colors[1], label="Kanton")
        axs.plot(self.steuer_allgemein["Einkommen"], self.steuer_allgemein["Gemeinde"], linestyle=':', color=colors[2], label="Gemeinde")
        axs.plot(self.steuer_allgemein["Einkommen"], self.steuer_allgemein["Total"], color=colors[3], label="Total")

        axs.plot([0,self.steuer_persoenlich["Einkommen"]], [self.steuer_persoenlich["Total"],self.steuer_persoenlich["Total"]], linestyle='-.', color='lightgrey', zorder=0) #horizontal line
        axs.text(0, self.steuer_persoenlich["Total"]+factor*np.max(self.steuer_allgemein["Total"]), f'{int(self.steuer_persoenlich["Total"])} CHF', ha='left', color='grey', fontsize=10)  # Steuer Value

        axs2 = axs.twinx()
        axs2.text(self.max_income, self.steuer_persoenlich["Progression"]+factor*np.max(self.steuer_allgemein["Progression"]), f'{self.steuer_persoenlich["Progression"]}%', ha='right', color='grey', fontsize=10)  # Progression Value
        axs2.plot(self.steuer_allgemein["Einkommen"], self.steuer_allgemein["Progression"], '--', color=colors[4])
        axs2.plot([self.steuer_persoenlich["Einkommen"],self.max_income], [self.steuer_persoenlich["Progression"],self.steuer_persoenlich["Progression"]], linestyle='-.', color='lightgrey', zorder=0) #horizontal line
        axs2.plot([self.steuer_persoenlich["Einkommen"],self.steuer_persoenlich["Einkommen"]], [0,self.steuer_persoenlich["Progression"]], linestyle='-.', color='lightgrey', zorder=0) #vertical line
        axs2.tick_params(axis='y', labelcolor=colors[4])
        axs2.set_ylabel("Progressionsschritt / %")

        axs.tick_params(axis='y', labelcolor=colors[3])
        axs.legend(loc='upper left')
        plt.tight_layout()  # Adjust layout to prevent overlapping
        plt.show()


class Investement():
    def __init__(self, plot=True):
        self.invest_rate = 3 #months
        self.invest_duration = 5 #years
        self.invest_amount = 5000 #CHF
        self.bank = [0]
        self.etfs = [0]
        self.percent = 6
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.date = [f"{self.current_month}-{self.current_year}"]

        self.investment_solo()

        if plot:
            self.plot_subplots()

    def investment_solo(self):
        self.savings = 0
        for _ in range(0, self.invest_duration):
            for month in range(12):
                self.savings += self.invest_amount
                if month % self.invest_rate == 0:
                    self.bank.append(self.bank[-1] + self.savings)
                    self.etfs.append(self.etfs[-1] * (100 + self.percent)/100 + self.savings)
                    self.date.append(f"{self.current_month}-{self.current_year}")
                    self.savings = 0
                self.current_month += 1
                if self.current_month > 12:
                    self.current_month = 1
                    self.current_year += 1

            # TODO: Implement the right taxes strategy for property instead of wealth!!!!
            # bank_taxes = Taxes(self.bank[-1])
            # bank_tax = bank_taxes.steuer_persoenlich["Total"]
            # self.bank[-1] = self.bank[-1]-bank_tax
            # etf_taxes = Taxes(self.etfs[-1])
            # etf_tax = etf_taxes.steuer_persoenlich["Total"]
            # self.etfs[-1] = self.etfs[-1]-etf_tax

    def plot_subplots(self):
            plt.plot(self.date, self.bank, '-', color='lightblue', label='Bank')
            plt.plot(self.date, self.etfs, '-', color='orange', label='ETFs')
            plt.xticks(rotation=90, ha='right')
            plt.legend(loc='lower right')
            plt.tight_layout()
            plt.show()



if __name__ == '__main__':

    # Geben Sie hier ihr steuerbares Einkommen ein:
    einkommen_steuerbar = 100000
    steuern = Taxes(einkommen_steuerbar, plot=True)
    invest = Investement(plot=False)