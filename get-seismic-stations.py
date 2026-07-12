#!/usr/bin/env python3
"""
Build a CSV of permanent/regional seismic stations worldwide using real
FDSN (International Federation of Digital Seismograph Networks) web services.

Sources:
  - EarthScope (formerly IRIS) FDSN station service — most global/regional networks
  - RESIF (France)                                   — FR network
  - ORFEUS (Europe)                                  — NL network

Output columns:
  network_code, network_name, station_code, latitude, longitude,
  elevation_m, site_description, start_date, end_date, data_source
"""

import csv
import urllib.request
import urllib.error

# Curated list of well-known PERMANENT global/regional seismic networks.
# (FDSN network codes are not a reliable "permanent vs temporary" signal on
# their own, so this list was hand-picked from known operational networks.)
EARTHSCOPE_NETWORKS = [
    "IU", "II", "IC", "G", "GE", "CU", "GT",           # Global Seismographic Network
    "US", "BK", "CI", "NC", "NN", "UU", "UW", "AK",     # US regional
    "HV", "AV", "CN", "LD", "NM",
    "MN", "CH", "SL", "RO", "KO", "IV", "OX",           # Europe / Mediterranean
    "AU", "NZ", "MX", "C1", "C", "PS", "IM", "GB",
    "BE", "OE", "HL", "HT",
]

EARTHSCOPE_BASE = "https://service.earthscope.org/fdsnws/station/1/query"
RESIF_BASE = "https://ws.resif.fr/fdsnws/station/1/query"
ORFEUS_BASE = "https://www.orfeus-eu.org/fdsnws/station/1/query"

OUTPUT_FILE = "seismic_stations_global.csv"


def fetch_text(url: str) -> str:
    """Fetch a URL and return its text content, or '' on failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        print(f"  HTTP error {e.code} for {url}")
    except Exception as e:
        print(f"  Failed to fetch {url}: {e}")
    return ""


def parse_station_text(raw: str):
    """Parse FDSN 'format=text&level=station' pipe-delimited output."""
    rows = []
    lines = raw.strip().split("\n")
    for line in lines[1:]:  # skip header line
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 8:
            net, sta, lat, lon, elev, site, start, end = parts
            rows.append((net, sta, lat, lon, elev, site, start, end))
    return rows


def fetch_network_descriptions() -> dict:
    """Get human-readable network names from the network-level endpoint."""
    print("Fetching network descriptions...")
    raw = fetch_text(f"{EARTHSCOPE_BASE}?level=network&format=text")
    desc = {}
    for line in raw.strip().split("\n")[1:]:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 2:
            code, description = parts[0], parts[1]
            desc.setdefault(code, description)
    return desc


def main():
    net_desc = fetch_network_descriptions()
    all_rows = []

    # 1. Pull all curated networks in one batched query from EarthScope
    print("Fetching EarthScope station data...")
    net_param = ",".join(EARTHSCOPE_NETWORKS)
    raw = fetch_text(f"{EARTHSCOPE_BASE}?net={net_param}&level=station&format=text")
    for net, sta, lat, lon, elev, site, start, end in parse_station_text(raw):
        if net in EARTHSCOPE_NETWORKS:
            all_rows.append([
                net, net_desc.get(net, ""), sta, lat, lon, elev, site,
                start, end, "EarthScope/FDSN",
            ])
    print(f"  {len(all_rows)} rows so far")

    # 2. RESIF for France (FR) — not reliably mirrored on EarthScope
    print("Fetching RESIF (FR) station data...")
    raw = fetch_text(f"{RESIF_BASE}?net=FR&level=station&format=text")
    fr_rows = parse_station_text(raw)
    for net, sta, lat, lon, elev, site, start, end in fr_rows:
        all_rows.append([
            net, "RESIF Broadband Network (France)", sta, lat, lon, elev,
            site, start, end, "RESIF/FDSN",
        ])
    print(f"  +{len(fr_rows)} FR rows")

    # 3. ORFEUS for Netherlands (NL) — not reliably mirrored on EarthScope
    print("Fetching ORFEUS (NL) station data...")
    raw = fetch_text(f"{ORFEUS_BASE}?net=NL&level=station&format=text")
    nl_rows = parse_station_text(raw)
    for net, sta, lat, lon, elev, site, start, end in nl_rows:
        all_rows.append([
            net, "Netherlands Seismic and Acoustic Network (KNMI)", sta,
            lat, lon, elev, site, start, end, "ORFEUS/FDSN",
        ])
    print(f"  +{len(nl_rows)} NL rows")

    # Sort by network, then station code
    all_rows.sort(key=lambda r: (r[0], r[2]))

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "network_code", "network_name", "station_code", "latitude",
            "longitude", "elevation_m", "site_description", "start_date",
            "end_date", "data_source",
        ])
        writer.writerows(all_rows)

    print(f"\nDone. Wrote {len(all_rows)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()