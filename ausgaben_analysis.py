import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class ExpensesAnalyzer:
    def __init__(self, root, excel_datei_pfad):
        self.root = root
        self.excel_datei_pfad = excel_datei_pfad
        self.gesamtdaten = pd.DataFrame(columns=['Jahr', 'Monat', 'Rubrik', 'Wert'])
        self.import_data()

    def import_data(self):
        excel_arbeitsmappe = pd.ExcelFile(os.path.join(self.root, self.excel_datei_pfad))
        arbeitsblatt_namen = excel_arbeitsmappe.sheet_names

        for arbeitsblatt_name in arbeitsblatt_namen:
            if arbeitsblatt_name[-5:] == 'Total' or arbeitsblatt_name == 'Predictions' or arbeitsblatt_name == 'Mittel_HalbJahr':
                continue

            arbeitsblatt = pd.read_excel(excel_arbeitsmappe, arbeitsblatt_name, header=None)
            arbeitsblatt.drop(arbeitsblatt.columns[:-2], axis=1, inplace=True)
            arbeitsblatt.columns = ['Rubrik', 'Wert']
            arbeitsblatt.dropna(how='all', inplace=True)

            arbeitsblatt['Jahr'] = arbeitsblatt_name[:2]
            arbeitsblatt['Monat'] = arbeitsblatt_name[3:]
            arbeitsblatt['Datum'] = arbeitsblatt_name

            self.gesamtdaten = pd.concat([self.gesamtdaten, arbeitsblatt], ignore_index=False)

    def analyze_data(self, threshold=500):
        self.gesamtdaten = self.gesamtdaten[(self.gesamtdaten['Rubrik'] != 'Gesamtergebnis') &
                                            (self.gesamtdaten['Rubrik'] != 'Zeilenbeschriftungen') &
                                            (self.gesamtdaten['Rubrik'] != 'Totalbetrag') &
                                            (self.gesamtdaten['Rubrik'] != 'Grand Total') &
                                            (self.gesamtdaten['Rubrik'] != '(blank)') &
                                            (self.gesamtdaten['Rubrik'] != 'Row Labels')]

        rubrik_summen = self.gesamtdaten.groupby('Rubrik')['Wert'].sum().reset_index()
        rubrik_summen['Wert'] = pd.to_numeric(rubrik_summen['Wert'], errors='coerce')
        rubrik_summen = rubrik_summen.sort_values(by='Wert', ascending=False)

        self.rubriken_alle = rubrik_summen['Rubrik']
        
        # Convert 'Rubrik' to categorical with sorted order
        self.gesamtdaten_alle = self.gesamtdaten[self.gesamtdaten['Rubrik'].isin(self.rubriken_alle)].sort_values(by='Rubrik', ascending=True)
        self.gesamtdaten_alle['Rubrik'] = pd.Categorical(self.gesamtdaten_alle['Rubrik'], categories=self.rubriken_alle, ordered=True)
        
        self.rubriken_ueber = rubrik_summen[rubrik_summen['Wert'] > threshold]['Rubrik']
        self.gesamtdaten_ueber = self.gesamtdaten[self.gesamtdaten['Rubrik'].isin(self.rubriken_ueber)]

    def plot_data(self):
        cmap = plt.get_cmap('plasma')
        # Generate 12 equally spaced values between 0 and 1
        j = 0
        colors = [cmap(i) for i in np.linspace(0, 1, len(self.gesamtdaten_ueber.groupby('Rubrik')))]

        fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(14, 12))
        # fig.autofmt_xdate(bottom=0.2, rotation=-45, ha='left')

        self.plot_category_data(axes[0, 0], 'Ausgang', 'Ausgang')
        self.plot_category_data(axes[0, 1], 'Ferien', 'Ferien', ticks_right=True)
        self.plot_category_data(axes[1, 0], 'Gesundheit', 'Gesundheit')
        self.plot_category_data(axes[1, 1], 'Lebensmittel', 'Lebensmittel', ticks_right=True)

        for rubrik, rubrik_data in self.gesamtdaten_ueber.groupby('Rubrik'):
            if rubrik not in ["Steuern", "Wohnungsmiete", "Grand Total"]:
                axes[2, 0].plot(rubrik_data['Datum'], rubrik_data['Wert'], '.-', color=colors[j], label=rubrik)
            j += 1
        axes[2, 0].legend(loc='lower center', bbox_to_anchor=(0.5, -0.8),
                          ncol=4, fancybox=True, shadow=True)
        axes[2, 0].invert_xaxis()
        axes[2, 0].tick_params(axis='x', rotation=-45)
        axes[2, 0].set_ylabel('Wert [CHF]')
        axes[2, 0].set_title('Ausgaben-Tracking')

        self.plot_total_expenses(axes[2, 1], ticks_right=True)

        plt.tight_layout()
        plt.show()

    def plot_category_data(self, ax, rubrik_keyword, title, ticks_right=False):
        category_data = self.gesamtdaten[self.gesamtdaten['Rubrik'].str.contains(rubrik_keyword, case=False)]
        ax.plot(category_data['Datum'], category_data['Wert'], color='mediumorchid')
        ax.set_title(title)
        ax.set_ylabel('Wert [CHF]')
        ax.invert_xaxis()
        ax.tick_params(axis='x', rotation=-45)
        if ticks_right:
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")

    def plot_total_expenses(self, ax, ticks_right=False):
        ax.bar(self.rubriken_alle, self.gesamtdaten_alle.groupby('Rubrik')['Wert'].sum(), color='slateblue')
        ax.set_title('Gesamtausgaben')
        # ax.set_xlabel('Rubrik')
        ax.set_ylabel('Wert [CHF]')
        ax.invert_xaxis()
        ax.set_xticklabels(self.rubriken_alle, rotation=-45, ha='left')
        if ticks_right:
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")

if __name__ == "__main__":

    # Example usage
    root_path = r'C:\Users\0011323\OneDrive - Metrohm Group\Dokumente\Finance'
    excel_file_path = 'Ausgaben_Budget.xlsx'

    expenses_analyzer = ExpensesAnalyzer(root_path, excel_file_path)
    expenses_analyzer.analyze_data(500)
    expenses_analyzer.plot_data()
