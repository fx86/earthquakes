'''Gently scrapes earthquake events from USGS website'''
import pandas as pd
import os
import time
import random
from glob import glob

# scraper uses the DAYS variable as interval generator
# It tries to get earthquake events between these dates.
DAYS = 30

BASE_URL = '''http://earthquake.usgs.gov/fdsnws/event/1/query?
starttime={:s}+00%3A00%3A00&endtime={:s}+23%3A59%3A59
&minmagnitude=0&maxmagnitude=&mindepth=&maxdepth=
&maxlatitude=&minlongitude=&maxlongitude=
&minlatitude=&latitude=&longitude=&minradiuskm=
&maxradiuskm=&mingap=&maxgap=&reviewstatus=&eventtype=
&minsig=&maxsig=&alertlevel=&minmmi=&maxmmi=&mincdi=
&maxcdi=&minfelt=&catalog=&contributor=&producttype=
&format=csv&kmlcolorby=age&callback=&orderby=time
&limit=&offset='''

BASE_URL = ''.join(BASE_URL.split('\n'))


def PD_TO_DATESTR(x): return x.date().strftime('%Y-%m-%d')


def date_after(date_string, days=180):
    '''returns relative date after months specified'''
    date_string = pd.to_datetime(date_string)
    return date_string + pd.to_timedelta(days, unit='D')


def read_data(source, engine='c'):
    '''reads csv source, converts 'time' column
    and return data'''
    data = pd.read_csv(source, parse_dates=['time'], engine=engine)
    return data


def get_data(data, url, engine='c'):
    '''does the dirty work of appending data'''
    if data is not None and isinstance(data, pd.DataFrame) and not data.empty:
        data = data.append(read_data(url, engine))
    else:
        data = read_data(url, engine)
    return data


if __name__ == '__main__':
    PRESENT_DATES = []

    START_DATE = input('''We need a start date in YYYY-MM-DD format.
    If you want to continue from last date in the data, just hit Enter: ''')
    if START_DATE == '':
        FILE_LIST = glob('*.csv')
        if len(FILE_LIST):
            for d in FILE_LIST:
                try:
                    PRESENT_DATES.append(pd.read_csv(d))
                except ValueError:
                    os.remove(d)
            PRESENT_DATES = pd.concat(PRESENT_DATES, ignore_index=True)
            PRESENT_DATES = PRESENT_DATES['time'].map(
                lambda x: str(x)[:10]).unique()
        START_DATE = max(PRESENT_DATES) or '1900-01-01'
    INTERVALS = int(float(input("How many years do you want to get data for ? ")
                     or 1) * 365.0/DAYS)  # years

    while INTERVALS:
        END_DATE = PD_TO_DATESTR(date_after(START_DATE, days=DAYS))
        if END_DATE not in PRESENT_DATES or START_DATE not in PRESENT_DATES:
            UPDATED_URL = BASE_URL.format(START_DATE, END_DATE)
            print("{:s} TO {:s}".format(START_DATE, END_DATE))
            try:
                print(UPDATED_URL)
                DATA = read_data(UPDATED_URL, engine='c')
            except pd.errors.ParserError as error:
                print("\t ", error)
                print("\t  trying with python engine")
                DATA = read_data(UPDATED_URL, engine='python')
            # except urllib2.HTTPError as error:
            #     print("\t ", error)
            #     print("\n\nPlease set DAYS parameter in the script to a lower number.")
            #     print("USGS does not return more than 20 thousand events per request.")
            #     os._exit(0)
            finally:
                filename = "{:s}_{:s}.csv".format(START_DATE, END_DATE)
                DATA.to_csv(filename, index=False)
        else:
            print("Already present: {:s} TO {:s}".format(START_DATE, END_DATE))

        START_DATE = END_DATE
        INTERVALS -= 1
        #time.sleep(random.randint(1, 10))
