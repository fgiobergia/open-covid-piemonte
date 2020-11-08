# Open Covid Piemonte

This is an unofficial open data repository for the COVID19 cases in Piemonte, Italy. To date, there is no official open data initiative for Regione Piemonte, hence this repository.

The data is collected from the [dashboard](https://www.regione.piemonte.it/web/covid-19-mappa-piemonte) published on the website of Regione Piemonte. As great as that project may be, it does not constitute - by itself - an open data initiative: data is not readily available for everyone to download and use.

This project is aimed at collecting data from that dashboard and making it available in an easy-to-use format (namely, CSV). 

## Purpose of the project
While I appreciate the effort put by Regione Piemonte to build a daily cases dashboard, I believe there is more to be done in terms of data "openness". I am apparently not the only one with this kind of concern (indeed -- [#datiBeneComune](https://datibenecomune.it/) asks for just this). Hence, I decided to follow through and figure out how to download and read the raw data that is used for the dashboard of Regione Piemonte. 

The ultimate hope is that this unofficial project will spark an interest in having an official open data for COVID19 in Piemonte and/or other regions.

If you use this data for data visualizations/data analysis, please let me know! I will add a link to all projects in this page. 

## Data
You will find all the data available in the `dataset/` directory of this repository. For each day, you will find a CSV file named `YYYYMMDD_hhmm.csv` (YYYY = year, MM = month, DD = day, hh = hour, mm = minute). The file is a standard CSV file, with various rows, described below:
* `id_comune`: a unique identifier for each municipality in Piemonte (6-digits, 0-padded values, as [defined by Istat](https://www.istat.it/it/archivio/6789)) - string
* `denominazione`: the name of the municipality - string
* `datetime`: the date and time of the measure (the same one found in the file name), following the YYYY-MM-DD hh:mm:ss format - string (datetime format)
* `positivi`: the current (as of `datetime`) number of active cases in the specific municipality - integer
* `positivi_1000`: the number of active cases per 1,000 people in the specific municipality - float

Unless drastic changes occur, each file should contain 1,182 rows (one for each of the 1,181 municipalities in Piemonte, plus 1 header row). 

The following is an example of access to a file (specifically, for the data collected on [2020-11-07 11:00](dataset/20201107_1100.csv)) using python's Pandas library (this example can be found in `example.py`):
```python
import pandas as pd

df = pd.read_csv("dataset/20201107_1100.csv", index_col="id_comune")
print(df)
```
Output:
```
             denominazione             datetime  positivi  positivi_1000
id_comune                                                               
103079     Valle Cannobina  2020-11-07 11:00:00         2           4.12
103078     Borgomezzavalle  2020-11-07 11:00:00         3           9.52
103077             Vogogna  2020-11-07 11:00:00        10           5.69
103076            Villette  2020-11-07 11:00:00         1           3.60
103075        Villadossola  2020-11-07 11:00:00        66          10.12
...                    ...                  ...       ...            ...
1006                Almese  2020-11-07 11:00:00        56           8.78
1004       Albiano d'Ivrea  2020-11-07 11:00:00        22          13.37
1003          Ala di Stura  2020-11-07 11:00:00         5          11.04
1002               Airasca  2020-11-07 11:00:00        36           9.78
1001                 Agliè  2020-11-07 11:00:00        27          10.25

             [1181 rows x 4 columns]
```

## Missing data
This project collects daily data from the Regione Piemonte interactive dashboard. As such, the data is only available from November 6, 2020 onwards (i.e. since the day the project was created).

If you happen to have downloaded previous data (in.dat and va.dat files), or know how previous data can be collected (e.g. parameters to be added to the requests), please get in touch!

