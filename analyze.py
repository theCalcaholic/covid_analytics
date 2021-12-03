import tempfile

from matplotlib import pyplot, dates as mdates, ticker as mticker
import csv
from pathlib import Path
from datetime import datetime

FREE_BEDS_NO_EMG_CAPA = "Freie_Intensivbetten_Erwachsene (ohne Notfallreserve)"
keys_to_plot = [
    "Aktuelle_COVID_Faelle_Erwachsene_ITS","Belegte_Intensivbetten_Erwachsene","Freie_Intensivbetten_Erwachsene"
]

states_to_plot = ["DEUTSCHLAND"]


def divi_plot():

    with Path('data/divi/bundesland-zeitreihe.csv').open() as f:

        raw = csv.reader(f, delimiter=',')
        titles = next(raw)
        data = []
        for row in raw:
            data.append({titles[i]: v for i, v in enumerate(row)})
            data[-1]['Datum'] = datetime.fromisoformat(data[-1]['Datum'])
            for title in titles[2:]:
                data[-1][title] = int(data[-1][title])

        fig, ax = pyplot.subplots()

        all_plts = {}
        for row in data:
            state = row['Bundesland']
            if state not in states_to_plot:
                continue
            if state not in all_plts:
                all_plts[state] = {FREE_BEDS_NO_EMG_CAPA: {}}
            for subject in keys_to_plot:
                if subject not in all_plts[state]:
                    all_plts[state][subject] = {}
                all_plts[state][subject][row['Datum']] = row[subject]

            all_plts[state][FREE_BEDS_NO_EMG_CAPA][row['Datum']] = \
                all_plts[state]["Freie_Intensivbetten_Erwachsene"][row['Datum']]
            all_plts[state]["Freie_Intensivbetten_Erwachsene"][row['Datum']] += row["7_Tage_Notfallreserve_Erwachsene"]

        for state in all_plts.keys():
            for subject in all_plts[state].keys():
                average_over = 3
                xs = list(all_plts[state][subject].keys())[average_over:]
                ys = list(all_plts[state][subject].values())
                ys = [sum(ys[i-average_over-1:i]) / average_over
                      for i in range(average_over-1, len(ys)-1)]
                linestyle = '--' if subject == FREE_BEDS_NO_EMG_CAPA else '-'
                ax.plot(xs, ys,
                        label=f'{subject} [{state}]',
                        alpha=0.7, linestyle=linestyle)

        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.yaxis.set_minor_locator(mticker.NullLocator())
        ax.yaxis.set_major_locator(mticker.AutoLocator())

        pyplot.legend(loc='best')
        pyplot.xlabel('day')
        pyplot.ylabel('value')
        fig.autofmt_xdate()

        pyplot.show()



if __name__ == '__main__':
    divi_plot()
