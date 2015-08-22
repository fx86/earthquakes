# Earthquakes
Collection of earthquake data and related analysis 

Source: USGS (for now)

As of 22-Aug-2015, `scraper.py` gets data only from USGS. This is already bunched-together and available in `earthquakes_data_USGS.7z` for *1900 to Aug 2015* and you don't need to run the scraper. 

But, in the unlikely case that you have to, the section `how to run scraper` will help.


### Column names and meaning

Source - http://earthquake.usgs.gov/earthquakes/feed/v1.0/glossary.php

`time` - Time when the event occurred. Times are reported in milliseconds since the epoch ( 1970-01-01T00:00:00.000Z), and do not include leap seconds. In certain output formats, the date is formatted for readability.

`latitude` - Decimal degrees latitude. Negative values for southern latitudes

`longitude` - Decimal degrees longitude. Negative values for western longitudes.

`depth` - Depth of the event in kilometers.

`mag` - magnitude of earthquake 

`magType` - The method or algorithm used to calculate the preferred magnitude for the event.

`nst` - The total number of Number of seismic stations which reported P- and S-arrival times for this earthquake.

`gap` - gap between azimuthally adjacent stations (in degrees). In general, the smaller this number, the more reliable is the calculated horizontal position of the earthquake.

`dmin` - Horizontal distance from the epicenter to the nearest station (in degrees). 1 degree is approximately 111.2 kilometers. In general, the smaller this number, the more reliable is the calculated depth of the earthquake.

`rms`  - This parameter provides a measure of the fit of the observed arrival times to the predicted arrival times for this location. Smaller numbers reflect a better fit of the data.

`net` - Identifies the network considered to be the preferred source of information for this event.

`id`  - A code consisting of source, type, code, updateTime. Eg: us20002wt7 

`updated` - Time when the event was most recently updated.

`place` - Textual description of named geographic region near to the event

`type`  - Type of seismic event

### How to run scraper

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
