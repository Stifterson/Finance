import os
import pandas as pd
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
            if arbeitsblatt_name[-5:] == 'Total' or arbeitsblatt_name[:2] != '23' or arbeitsblatt_name == 'Predictions':
                continue

            arbeitsblatt = pd.read_excel(excel_arbeitsmappe, arbeitsblatt_name, header=None)
            arbeitsblatt.drop(arbeitsblatt.columns[:-2], axis=1, inplace=True)
            arbeitsblatt.columns = ['Rubrik', 'Wert']
            arbeitsblatt.dropna(how='all', inplace=True)

            arbeitsblatt['Jahr'] = arbeitsblatt_name[:2]
            arbeitsblatt['Monat'] = arbeitsblatt_name[3:]

            self.gesamtdaten = pd.concat([self.gesamtdaten, arbeitsblatt], ignore_index=False)

    def analyze_data(self, threshold=500):
        self.gesamtdaten = self.gesamtdaten[(self.gesamtdaten['Rubrik'] != 'Gesamtergebnis') & (self.gesamtdaten['Rubrik'] != 'Zeilenbeschriftungen')]

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
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15, 10))

        self.plot_category_data(axes[0, 0], 'Lebensmittel', 'Lebensmittel Ausgaben')
        self.plot_category_data(axes[0, 1], 'Ausgang', 'Ausgang Ausgaben')

        for rubrik, rubrik_data in self.gesamtdaten_ueber.groupby('Rubrik'):
            axes[1, 0].plot(rubrik_data['Monat'], rubrik_data['Wert'], '.-', label=rubrik)

        self.plot_total_expenses(axes[1, 1])

        plt.tight_layout()
        plt.show()

    def plot_category_data(self, ax, rubrik_keyword, title):
        category_data = self.gesamtdaten[self.gesamtdaten['Rubrik'].str.contains(rubrik_keyword, case=False)]
        ax.plot(category_data['Monat'], category_data['Wert'])
        ax.set_title(title)
        ax.set_ylabel('Wert [CHF]')
        ax.invert_xaxis()
        ax.tick_params(axis='x', rotation=45)

    def plot_total_expenses(self, ax):
        ax.bar(self.rubriken_alle, self.gesamtdaten_alle.groupby('Rubrik')['Wert'].sum())
        ax.set_title('Gesamtausgaben')
        ax.set_xlabel('Rubrik')
        ax.set_ylabel('Wert [CHF]')
        ax.invert_xaxis()
        ax.set_xticklabels(self.rubriken_alle, rotation=45, ha='right')

if __name__ == "__main__":

    # Example usage
    root_path = r'C:\Users\misch\OneDrive\Bäckerweg_7'
    excel_file_path = 'Ausgaben_23.xlsx'

    expenses_analyzer = ExpensesAnalyzer(root_path, excel_file_path)
    expenses_analyzer.analyze_data(500)
    expenses_analyzer.plot_data()
