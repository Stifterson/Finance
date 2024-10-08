import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from steuertarif_24 import *

class Taxes():
    max_income = 200000
    # Paramters to be checked each year
    steuerfuss_kanton = 105 #St.Gallen
    steuerfuss_gemeinde = 127 #Uzwil
    steuersatz = 115 #Bund
    ahv_abzug = 5.3 #%
    alv_abzug = 1.1 #%
    nbu_abzug = 0.4 #%
    bvg_abzug = {25: 7,
                 35: 10,
                 45: 15,
                 55: 18}
    bvg_limit = [3675, 88200]
    saeule3a_abzug = 7056 #3a / Person
    essen_abzug = 1600 #Kantine / Person Ermässigung
    versicherung_abzug = 3000 #4560/person #Schnitt Verheiratete
    transport_abzug = 2000 #Schnitt / Person ÖV
    berufskosten_abzug = 2000 #Min
    bildung_abzug = 400 #Min / Person
    gesundheit_abzug = 300 #Schnitt

    def __init__(self, einkommen_steuerbar, age=30, married=False, netto=True, plot=False):
        self.einkommen_persoenlich = einkommen_steuerbar
        self.einkommen_nachAbzug = self.einkommen_abzuege(self.einkommen_persoenlich, age=age, married=married, netto=netto)

        self.steuer_rechner_allgemein()
        self.steuer_rechner_persoenlich(self.einkommen_nachAbzug)
        if plot:
            print(f"Ihre direkte Bundessteuer beträgt: {int(self.steuer_persoenlich['Bund'])} CHF")
            print(f"Ihre Kantonssteuer beträgt: {int(self.steuer_persoenlich['Kanton'])} CHF")
            print(f"Ihre Gemeindesteuer beträgt: {int(self.steuer_persoenlich['Gemeinde'])} CHF")
            print(f"Ihre totalen Steuern betragen: {int(self.steuer_persoenlich['Total'])} CHF")
            self.plot_subplots()

    def einkommen_abzuege(self, income, age, married, netto=True):
        print(f"Einkommen OHNE Abzüge: {income} CHF")
        if not netto:
            bvg_key = self.check_range(age, self.bvg_abzug)
            if self.bvg_limit[0] <= income < self.bvg_limit[-1]:
                abzuge_percent = self.ahv_abzug + self.alv_abzug + self.nbu_abzug + self.bvg_abzug[bvg_key]
                income_abzug = income * abzuge_percent/100
            elif income > self.bvg_limit[-1]:
                abzuge_percent = self.ahv_abzug + self.alv_abzug + self.nbu_abzug
                income_abzug = income * abzuge_percent/100
                income_abzug += self.bvg_limit[-1] * self.bvg_abzug[bvg_key]/100
            else:
                abzuge_percent = self.ahv_abzug + self.alv_abzug + self.nbu_abzug
                income_abzug = income * abzuge_percent/100
        else:
            income_abzug = 0
        income_after = income - np.round(income_abzug, 0)
        if married:
            factor = 2
        else:
            factor = 1
        income_abzug = factor * (self.essen_abzug + self.transport_abzug + self.bildung_abzug + self.saeule3a_abzug) + self.berufskosten_abzug + self.gesundheit_abzug + self.versicherung_abzug
        income_after -= np.round(income_abzug, 0)
        # print(f"Abzüge: {int(income - income_after)} CHF")
        print(f"Zur Berechnung verwendetes Einkommen MIT Abzügen: {int(income_after)} CHF")
        return income_after

    @staticmethod
    def check_range(value, dictionary):
        # Get the keys of the dictionary
        keys = list(dictionary.keys())

        for i in range(len(keys) - 1):
            if keys[i] <= value < keys[i + 1]:
                return keys[i]
        if value < keys[0]:
            return None
        elif value >= keys[-1]:
            return keys[-1]

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
    vermoegen_steuersatz = 17 #Kantonssatz in Promille
    vermoegen_steuerfuss = 2.2 #Gemeindefuss in Promille
    estimate_inflation_loss = 1.0 #Inflation Teuerung
    estimate_bank_growth = 1.1 #Growth in Percent
    estimate_etf_growth = 8 #Growth in Percent
    def __init__(self, plot=True):
        self.invest_rate = 3 #Months/Saving
        self.invest_duration = 5 #Years
        self.invest_amount = 5000 #CHF/Month
        self.saved = [0]
        self.matress = [0]
        self.bank = [0]
        self.etfs = [0]
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.date = [f"{self.current_month}-{self.current_year}"]

        self.investment_solo()

        # Show final values
        print(15*"--")
        print(f"Value: {int(self.etfs[-1])} CHF by ETFs")
        print(f"Value: {int(self.saved[-1])} CHF by Saved")
        print(f"Value: {int(self.bank[-1])} CHF by Bank")
        print(15*"--")
        print(f"Difference: {int(self.etfs[-1] - self.saved[-1])} CHF ETF to Saved")

        if plot:
            self.plot_subplots()

    def investment_solo(self):
        self.savings = 0
        for year in range(1, self.invest_duration):
            # print(f"Year: {year}")
            for month in range(12):
                # print(f"Month: {month}")
                self.savings += self.invest_amount
                if month % self.invest_rate == 0:
                    # print(f"Saving: True")
                    self.saved.append(self.saved[-1] + self.savings)
                    self.matress.append(self.matress[-1] * (100 - self.estimate_inflation_loss)/100 + self.savings)
                    self.bank.append(self.bank[-1] * (100 + self.estimate_bank_growth - self.estimate_inflation_loss)/100 + self.savings)
                    self.etfs.append(self.etfs[-1] * (100 + self.estimate_etf_growth - self.estimate_inflation_loss)/100 + self.savings)

                    self.date.append(f"{self.current_month}-{self.current_year}")
                    self.savings = 0
                self.current_month += 1
                if self.current_month > 12:
                    self.current_month = 1
                    self.current_year += 1

            # TODO: Implement the right taxes strategy for property instead of wealth!!!!
            print(f"You saved CHF {self.invest_amount*12} this year.")
            wealth_taxes = (self.vermoegen_steuersatz + self.vermoegen_steuerfuss) / 1000
            self.matress[-1] = (1 - wealth_taxes) * self.matress[-1]
            self.bank[-1] = (1 - wealth_taxes) * self.bank[-1]
            self.etfs[-1] = (1 - wealth_taxes) * self.etfs[-1]
            # Additional pay raises lead to higher investments
            self.invest_amount += 2*250 # Salary increase / Person / Year

    def plot_subplots(self):
            plt.plot(self.date, self.saved, ':', color='lightgrey', label='Saved')
            plt.plot(self.date, self.matress, '-', color='tomato', label='Matress')
            plt.plot(self.date, self.bank, '-', color='violet', label='Bank')
            plt.plot(self.date, self.etfs, '-', color='mediumpurple', label='ETFs')
            saving_period = 12/self.invest_rate
            for i in range(1, len(self.date), int(saving_period)):
                plt.hlines(self.saved[i], 0, self.date[i], 'lightgrey', linestyles=':')

            for i in range(1, len(self.saved), int(saving_period)):
                plt.vlines(self.date[i], 0, self.saved[i], 'lightgrey', linestyles=':')
            plt.xticks(rotation=90, ha='right')
            plt.xlabel("Period by Quarters")
            plt.ylabel("Savings / CHF")
            plt.legend(loc='lower right')
            # plt.grid('--', color='lightgrey')
            plt.tight_layout()
            plt.show()



if __name__ == '__main__':

    # Geben Sie hier ihr steuerbares Einkommen (Netto oder Brutto) ein:
    einkommen_steuerbar = 100000
    # steuern = Taxes(einkommen_steuerbar, netto=False, married=True, plot=True)
    invest = Investement(plot=True)