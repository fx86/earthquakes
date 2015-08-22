# earthquakes
Collection of earthquake data and related analysis 

Source: USGS (for now)

### How to run scraper.py

As of 22-Aug-2015, this script gets data only from USGS. Which is already bunched-together and available in `earthquakes_data_USGS.7z` and you don't need to run the scraper. 

But, in the unlikely case that you have to, the following will help.

There are two user inputs required:
1. Start date - from which you want to collect earthquake events
   At the time of writing, USGS has data from the year 1900 so you can provide <br>"1900-01-01" (without quotes) to start from the beginning<br>
   OR specify date yourself in YYYY-MM-DD format<br>
   OR let the script start from the last event in your data by hitting Enter key.
   
2. How many years of data do you need ? 
   Just type a number. No input will default to 1 year.

When you run the script you should see an output like this - 
```
> python scraper.py
We need a start date in YYYY-MM-DD format.
If you want to continue from last date in the data, just hit Enter:
Get data for how many years ?
```
P.S:
If you see an error like below, please set `DAYS` parameter to 30 or 60 or 90 or even 180.:
```HTTP Error 400: Bad Request
Please set DAYS parameter in the script to a lower number.
USGS does not return more than 20 thousand events per request.
``` 
