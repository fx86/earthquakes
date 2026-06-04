"""Gently scrapes earthquake events from the USGS API in date intervals."""

import argparse
import re
import time
from glob import glob
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

import pandas as pd

# Scraper uses DAYS as interval generator between START_DATE and END_DATE.
DAYS = 30
BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
RANGE_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.csv$")
MASTER_FILE = "all_earthquakes.csv"
DEFAULT_START_DATE = "1900-01-01"
MAX_RETRIES = 4
RETRY_WAIT_SECONDS = 3


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


def deduplicate_data(data):
    """Remove duplicate earthquake rows using stable keys when available."""
    if data is None or data.empty:
        return data

    if "id" in data.columns:
        return data.drop_duplicates(subset=["id"])

    fallback_cols = [col for col in ["time", "latitude", "longitude", "mag", "depth"] if col in data.columns]
    if fallback_cols:
        return data.drop_duplicates(subset=fallback_cols)

    return data.drop_duplicates()


def fetch_interval_data(start_date, end_date, attempt=1):
    """Fetch interval data, splitting the interval when USGS rejects a wide query."""
    url = build_url(start_date, end_date)
    try:
        return read_data(url, engine="c")
    except pd.errors.ParserError as error:
        print("\t", error)
        print("\ttrying with python engine")
        return read_data(url, engine="python")
    except HTTPError as error:
        # Retry transient failures like throttling / server hiccups.
        if error.code in (408, 429, 500, 502, 503, 504):
            if attempt >= MAX_RETRIES:
                raise
            wait_seconds = RETRY_WAIT_SECONDS * attempt
            print(
                f"\tHTTP {error.code} for {start_date} to {end_date}; "
                f"retrying in {wait_seconds}s ({attempt}/{MAX_RETRIES})."
            )
            time.sleep(wait_seconds)
            return fetch_interval_data(start_date, end_date, attempt=attempt + 1)

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
        return deduplicate_data(combined)
    except URLError as error:
        if attempt >= MAX_RETRIES:
            raise
        wait_seconds = RETRY_WAIT_SECONDS * attempt
        print(
            f"\tNetwork error for {start_date} to {end_date}: {error}. "
            f"Retrying in {wait_seconds}s ({attempt}/{MAX_RETRIES})."
        )
        time.sleep(wait_seconds)
        return fetch_interval_data(start_date, end_date, attempt=attempt + 1)


def discover_existing_ranges():
    """Return set of already-downloaded date ranges from file names."""
    ranges = set()
    for path in glob("*.csv"):
        match = RANGE_FILE_RE.match(path)
        if match:
            ranges.add((match.group(1), match.group(2)))
    return ranges


def rebuild_master_file():
    """Combine all interval CSVs into a single all_earthquakes.csv file."""
    interval_files = []
    for path in sorted(glob("*.csv")):
        if RANGE_FILE_RE.match(path):
            interval_files.append(path)

    if not interval_files:
        return

    frames = [read_data(path) for path in interval_files]
    merged = pd.concat(frames, ignore_index=True)
    merged = deduplicate_data(merged)
    if "time" in merged.columns:
        merged = merged.sort_values(by="time")
    merged.to_csv(MASTER_FILE, index=False)
    print(f"Updated {MASTER_FILE} with {len(merged)} rows from {len(interval_files)} interval files.")


def parse_args():
    parser = argparse.ArgumentParser(description="USGS earthquake scraper")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Pull full history from 1900-01-01 to current date.",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Start date in YYYY-MM-DD format. Overrides resume behavior.",
    )
    return parser.parse_args()


def determine_start_date(args, existing_ranges):
    if args.full:
        return DEFAULT_START_DATE

    if args.start_date:
        return pd.to_datetime(args.start_date).strftime("%Y-%m-%d")

    if existing_ranges:
        return max(range_end for _, range_end in existing_ranges)

    return DEFAULT_START_DATE


def run_scraper():
    args = parse_args()
    existing_ranges = discover_existing_ranges()
    start_date = determine_start_date(args, existing_ranges)
    target_date = pd.Timestamp.utcnow().date().strftime("%Y-%m-%d")

    print(f"Starting from {start_date}; scraping until {target_date}.")

    while pd.to_datetime(start_date) < pd.to_datetime(target_date):
        end_date = pd_to_datestr(
            min(
                date_after(start_date, days=DAYS),
                pd.to_datetime(target_date),
            )
        )
        current_range = (start_date, end_date)

        if current_range not in existing_ranges:
            print(f"{start_date} TO {end_date}")
            data = fetch_interval_data(start_date, end_date)
            data = deduplicate_data(data)

            filename = f"{start_date}_{end_date}.csv"
            data.to_csv(filename, index=False)
            existing_ranges.add(current_range)
        else:
            print(f"Already present: {start_date} TO {end_date}")

        start_date = end_date

    rebuild_master_file()


if __name__ == "__main__":
    run_scraper()
