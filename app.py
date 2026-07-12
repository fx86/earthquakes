import pandas as pd
import pydeck as pdk
import streamlit as st

DATA_FILES = ("all-earthquakes.csv", "all_earthquakes.csv")


def color_for_magnitude(magnitude):
    if pd.isna(magnitude):
        return [160, 160, 160, 120]
    if magnitude >= 7:
        return [190, 30, 45, 200]
    if magnitude >= 5:
        return [225, 110, 40, 190]
    if magnitude >= 3:
        return [240, 180, 60, 180]
    return [60, 140, 210, 170]


def extract_country(place):
    if pd.isna(place):
        return "Unknown"

    place_text = str(place).strip()
    if not place_text:
        return "Unknown"

    if "," in place_text:
        return place_text.split(",")[-1].strip()

    return place_text


@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path, low_memory=False)
    data["time"] = pd.to_datetime(data["time"], errors="coerce", utc=True)

    numeric_columns = ["latitude", "longitude", "mag", "depth"]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["time", "latitude", "longitude"])
    data["date"] = data["time"].dt.date
    data["year"] = data["time"].dt.year
    data["country"] = data["place"].apply(extract_country) if "place" in data.columns else "Unknown"
    return data


def resolve_data_file():
    for candidate in DATA_FILES:
        try:
            with open(candidate, "r", encoding="utf-8"):
                return candidate
        except FileNotFoundError:
            continue
    raise FileNotFoundError


def build_earthquake_layer(data):
    map_data = data[["latitude", "longitude", "mag", "place", "time", "depth"]].copy()
    map_data["radius"] = map_data["mag"].fillna(0).clip(lower=0) * 4000 + 2000
    map_data["color"] = map_data["mag"].apply(color_for_magnitude)

    return pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position="[longitude, latitude]",
        get_radius="radius",
        get_fill_color="color",
        pickable=True,
        opacity=0.7,
        stroked=True,
        get_line_color=[20, 20, 20, 120],
        line_width_min_pixels=1,
    )


def get_zoom_from_span(span):
    if span > 120:
        return 1
    if span > 60:
        return 2
    if span > 30:
        return 3
    if span > 15:
        return 4
    if span > 8:
        return 5
    if span > 4:
        return 6
    if span > 2:
        return 7
    return 8


def build_view_state(data):
    lat_min = float(data["latitude"].min())
    lat_max = float(data["latitude"].max())
    lon_min = float(data["longitude"].min())
    lon_max = float(data["longitude"].max())

    lat_span = abs(lat_max - lat_min)
    lon_span = abs(lon_max - lon_min)
    span = max(lat_span, lon_span)

    zoom = get_zoom_from_span(span)

    return pdk.ViewState(
        latitude=float(data["latitude"].mean()),
        longitude=float(data["longitude"].mean()),
        zoom=zoom,
        min_zoom=1,
        max_zoom=12,
        pitch=20,
    )


def main():
    st.set_page_config(page_title="Earthquake Explorer", page_icon="🌍", layout="wide")
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1rem; padding-bottom: 0.6rem;}
        div[data-testid="stMetricValue"] {font-size: 1.25rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Earthquake Explorer")
    st.caption("Filter earthquakes by date and explore activity on a global map.")

    try:
        data_file = resolve_data_file()
        data = load_data(data_file)
    except FileNotFoundError:
        st.error("Could not find all-earthquakes.csv or all_earthquakes.csv. Run the scraper first.")
        return

    if data.empty:
        st.warning("No earthquake records found in the source CSV file.")
        return

    min_year = int(data["year"].min())
    max_year = int(data["year"].max())

    control_col1, control_col2, control_col3, control_col4, control_col5 = st.columns([1.6, 1.2, 1.0, 1.0, 1.0])
    with control_col1:
        if min_year == max_year:
            st.caption(f"Year range: {min_year}")
            selected_year_range = (min_year, max_year)
        else:
            selected_year_range = st.slider(
                "Year range",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                step=1,
            )

    year_filtered = data[
        data["year"].between(selected_year_range[0], selected_year_range[1])
    ].copy()

    if year_filtered.empty:
        st.warning("No earthquake records found for the selected year range.")
        return

    min_date = year_filtered["date"].min()
    max_date = year_filtered["date"].max()

    with control_col2:
        selected_dates = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
        time_filtered = year_filtered[
            year_filtered["date"].between(start_date, end_date)
        ].copy()
    else:
        time_filtered = year_filtered.copy()

    if time_filtered.empty:
        st.warning("No earthquake records found for the selected date range.")
        return

    with control_col3:
        country_options = sorted(time_filtered["country"].dropna().unique().tolist())
        selected_countries = st.multiselect(
            "Country",
            options=country_options,
            default=[],
            placeholder="All countries",
        )

    if selected_countries:
        country_filtered = time_filtered[time_filtered["country"].isin(selected_countries)].copy()
    else:
        country_filtered = time_filtered

    with control_col4:
        place_options = sorted(country_filtered["place"].dropna().unique().tolist()) if "place" in country_filtered.columns else []
        selected_places = st.multiselect(
            "Place",
            options=place_options,
            default=[],
            placeholder="All places",
        )

    if selected_places:
        place_filtered = country_filtered[country_filtered["place"].isin(selected_places)].copy()
    else:
        place_filtered = country_filtered

    with control_col5:
        mag_type_options = sorted(place_filtered["magType"].dropna().unique().tolist()) if "magType" in place_filtered.columns else []
        selected_mag_types = st.multiselect(
            "Magnitude type",
            options=mag_type_options,
            default=[],
            placeholder="All types",
        )

    if selected_mag_types:
        filtered = place_filtered[place_filtered["magType"].isin(selected_mag_types)].copy()
    else:
        filtered = place_filtered

    st.subheader("Earthquake Stats")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total earthquakes", f"{len(filtered):,}")
    col2.metric("Average magnitude", f"{filtered['mag'].mean():.2f}" if not filtered.empty else "N/A")
    col3.metric("Max magnitude", f"{filtered['mag'].max():.2f}" if not filtered.empty else "N/A")
    col4.metric("Average depth (km)", f"{filtered['depth'].mean():.1f}" if not filtered.empty else "N/A")
    col5.metric("Median magnitude", f"{filtered['mag'].median():.2f}" if not filtered.empty else "N/A")
    col6.metric("Max depth (km)", f"{filtered['depth'].max():.1f}" if not filtered.empty else "N/A")

    st.subheader("Earthquake Timeline")
    # Buckets ordered lightest -> heaviest so the heaviest stack on top.
    magnitude_bins = [-float("inf"), 2, 4, 6, 8, float("inf")]
    magnitude_labels = ["0–2", "2–4", "4–6", "6–8", "8+"]
    magnitude_colors = ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"]

    timeline_data = filtered.copy()
    timeline_data["mag_bucket"] = pd.cut(
        timeline_data["mag"], bins=magnitude_bins, labels=magnitude_labels
    )

    year_span = selected_year_range[1] - selected_year_range[0]
    if year_span <= 20:
        timeline = (
            timeline_data.set_index("time")
            .groupby([pd.Grouper(freq="MS"), "mag_bucket"], observed=False)
            .size()
            .unstack("mag_bucket")
        )
    else:
        timeline = (
            timeline_data.groupby(["year", "mag_bucket"], observed=False)
            .size()
            .unstack("mag_bucket")
        )

    timeline = timeline.reindex(columns=magnitude_labels, fill_value=0)
    st.bar_chart(timeline, color=magnitude_colors)

    st.subheader("Earthquakes Map")
    if filtered.empty:
        st.info("No earthquakes found in the selected filters.")
    else:
        layer = build_earthquake_layer(filtered)
        view_state = build_view_state(filtered)

        deck = pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v10",
            initial_view_state=view_state,
            layers=[layer],
            tooltip={
                "html": "<b>{place}</b><br/>Magnitude: {mag}<br/>Depth: {depth} km<br/>Time: {time}",
                "style": {"backgroundColor": "#111", "color": "#fff"},
            },
        )
        st.pydeck_chart(deck, use_container_width=True)

    st.subheader("Earthquake Table")
    table_columns = [
        "time",
        "place",
        "mag",
        "depth",
        "latitude",
        "longitude",
        "type",
        "id",
    ]
    available_columns = [column for column in table_columns if column in filtered.columns]
    table_left, table_right = st.columns([1.5, 1])
    with table_left:
        max_rows = st.slider("Rows to display", min_value=100, max_value=5000, value=1000, step=100)
    with table_right:
        sort_by = st.selectbox("Sort by", options=[c for c in ["time", "mag", "depth"] if c in filtered.columns], index=0)

    ascending = sort_by not in ("mag", "depth")
    table_data = filtered.sort_values(by=sort_by, ascending=ascending).head(max_rows)
    st.dataframe(table_data[available_columns], use_container_width=True, height=360)


if __name__ == "__main__":
    main()
