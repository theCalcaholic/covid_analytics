from matplotlib import pyplot, dates as mdates, ticker as mticker
import csv
from pathlib import Path
from datetime import datetime
from urllib import request


def divi_download_data():
    target_path = Path('data/divi/bundesland-zeitreihe.csv')
    if target_path.exists():
        return
    with request.urlopen('https://diviexchange.blob.core.windows.net/%24web/bundesland-zeitreihe.csv') as resp:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open('w') as f:
            f.write(resp.read().decode('utf-8'))


def divi_plot():

    # List of columns that should be plotted
    columns_to_plot = [
        "Aktuelle_COVID_Faelle_Erwachsene_ITS",
        "Belegte_Intensivbetten_Erwachsene",
        "Freie_Intensivbetten_Erwachsene",
        "7_Tage_Notfallreserve_Erwachsene"
    ]

    # states (including DEUTSCHLAND) that should be plotted
    states_to_plot = ["DEUTSCHLAND"]

    FREE_BEDS_NO_EMG_CAPA = "Freie_Intensivbetten_Erwachsene (ohne Notfallreserve)"

    # Download CSV from DIVI, if it doesn't already exist locally
    divi_download_data()
    with Path('data/divi/bundesland-zeitreihe.csv').open() as f:

        raw = csv.reader(f, delimiter=',')
        titles = next(raw)
        data = []

        # iterate through the imported csv data
        for row in raw:
            data.append({titles[i]: v for i, v in enumerate(row)})

            # convert all date values to python datetime objects
            data[-1]['Datum'] = datetime.fromisoformat(data[-1]['Datum'])
            # convert all numeric data to int
            for title in titles[2:]:
                data[-1][title] = int(data[-1][title])

        fig, ax = pyplot.subplots()

        # ## generate plots ## #

        all_plts = {}
        for row in data:
            state = row['Bundesland']

            # Filter states that should be plotted
            if state not in states_to_plot:
                continue

            if state not in all_plts:
                all_plts[state] = {FREE_BEDS_NO_EMG_CAPA: {}}

            # Gather data for all subjects that should be plotted
            for subject in columns_to_plot:
                if subject not in all_plts[state]:
                    all_plts[state][subject] = {}
                all_plts[state][subject][row['Datum']] = row[subject]

            # Since the total amount of IV beds is distributed over two values in the data,
            # add those (and show the individual values as extra plots)
            all_plts[state][FREE_BEDS_NO_EMG_CAPA][row['Datum']] = \
                all_plts[state]["Freie_Intensivbetten_Erwachsene"][row['Datum']]
            all_plts[state]["Freie_Intensivbetten_Erwachsene"][row['Datum']] += row["7_Tage_Notfallreserve_Erwachsene"]

        for state in all_plts.keys():
            for subject in all_plts[state].keys():

                # Use X-day average as value, in order to smooth out heavy fluctuation in the data
                average_over = 3
                xs = list(all_plts[state][subject].keys())[average_over+1:]
                ys = list(all_plts[state][subject].values())

                # Average is calulated for day_x with the following formular:
                #
                # avg_over = the amount of days for which to calculate the average
                # (day_{x} + day_{x-1} + ... day_{x-average_over}) / average_over
                ys = [sum(ys[i-average_over:i]) / average_over
                      for i in range(average_over, len(ys)-1)]

                # Set linestyle to dashed for partial free bed counts (total shown as "Freie_Intensivbetten_Erwachsene")
                linestyle = '--' if subject in [FREE_BEDS_NO_EMG_CAPA, "7_Tage_Notfallreserve_Erwachsene"] else '-'

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
