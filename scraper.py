"""Gently scrapes earthquake events from the USGS API in date intervals."""

import re
from glob import glob
from urllib.error import HTTPError
from urllib.parse import urlencode

import pandas as pd

# Scraper uses DAYS as interval generator between START_DATE and END_DATE.
DAYS = 30
BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
RANGE_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.csv$")


def pd_to_datestr(value):
    return value.date().strftime("%Y-%m-%d")


def date_after(date_string, days=180):
    """Return date offset by `days` from date_string."""
    date_value = pd.to_datetime(date_string)
    return date_value + pd.to_timedelta(days, unit="D")


def build_url(start_date, end_date):
    params = {
        "starttime": f"{start_date} 00:00:00",
        "endtime": f"{end_date} 23:59:59",
        "minmagnitude": 0,
        "format": "csv",
        "orderby": "time",
    }
    return f"{BASE_URL}?{urlencode(params)}"


def read_data(source, engine="c"):
    """Read CSV source, parse `time` as datetime and return DataFrame."""
    return pd.read_csv(source, parse_dates=["time"], engine=engine)


def fetch_interval_data(start_date, end_date):
    """Fetch interval data, splitting the interval when USGS rejects a wide query."""
    url = build_url(start_date, end_date)
    try:
        return read_data(url, engine="c")
    except pd.errors.ParserError as error:
        print("\t", error)
        print("\ttrying with python engine")
        return read_data(url, engine="python")
    except HTTPError as error:
        if error.code != 400:
            raise

        start_ts = pd.to_datetime(start_date)
        end_ts = pd.to_datetime(end_date)
        total_days = (end_ts - start_ts).days
        if total_days <= 1:
            raise

        split_ts = start_ts + pd.to_timedelta(total_days // 2, unit="D")
        split_date = pd_to_datestr(split_ts)
        next_date = pd_to_datestr(split_ts + pd.to_timedelta(1, unit="D"))

        print(
            f"\tUSGS rejected {start_date} to {end_date} (HTTP 400); "
            f"splitting into {start_date} to {split_date} and {next_date} to {end_date}."
        )

        first_half = fetch_interval_data(start_date, split_date)
        second_half = fetch_interval_data(next_date, end_date)
        combined = pd.concat([first_half, second_half], ignore_index=True)
        if "id" in combined.columns:
            combined = combined.drop_duplicates(subset=["id"])
        return combined


def discover_existing_ranges():
    """Return set of already-downloaded date ranges from file names."""
    ranges = set()
    for path in glob("*.csv"):
        match = RANGE_FILE_RE.match(path)
        if match:
            ranges.add((match.group(1), match.group(2)))
    return ranges


if __name__ == "__main__":
    existing_ranges = discover_existing_ranges()

    start_date = input(
        """We need a start date in YYYY-MM-DD format.
If you want to continue from last date in saved files, just hit Enter: """
    ).strip()

    if not start_date:
        if existing_ranges:
            start_date = max(range_end for _, range_end in existing_ranges)
        else:
            start_date = "1900-01-01"

    intervals = int(float(input("How many years do you want to get data for ? ") or 1) * 365.0 / DAYS)

    while intervals:
        end_date = pd_to_datestr(date_after(start_date, days=DAYS))
        current_range = (start_date, end_date)

        if current_range not in existing_ranges:
            print(f"{start_date} TO {end_date}")
            data = fetch_interval_data(start_date, end_date)

            filename = f"{start_date}_{end_date}.csv"
            data.to_csv(filename, index=False)
            existing_ranges.add(current_range)
        else:
            print(f"Already present: {start_date} TO {end_date}")

        start_date = end_date
        intervals -= 1
