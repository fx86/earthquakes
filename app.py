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

    import pdb; pdb.set_trace()  # Debugging breakpoint
    if data.empty:
        st.warning("No earthquake records found in the source CSV file.")
        return

    min_year = int(data["year"].min())
    max_year = int(data["year"].max())

    control_col1, control_col2 = st.columns([1.2, 1.8])
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
        if min_date == max_date:
            st.caption(f"Date range: {min_date}")
            selected_dates = (min_date, max_date)
        else:
            selected_dates = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )

    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = selected_dates
        end_date = selected_dates

    if start_date > end_date:
        st.error("Start date must be before or equal to end date.")
        return

    filtered = year_filtered[year_filtered["date"].between(start_date, end_date)].copy()

    st.subheader("Earthquake Stats")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total earthquakes", f"{len(filtered):,}")
    col2.metric("Average magnitude", f"{filtered['mag'].mean():.2f}" if not filtered.empty else "N/A")
    col3.metric("Max magnitude", f"{filtered['mag'].max():.2f}" if not filtered.empty else "N/A")
    col4.metric("Average depth (km)", f"{filtered['depth'].mean():.1f}" if not filtered.empty else "N/A")
    col5.metric("Median magnitude", f"{filtered['mag'].median():.2f}" if not filtered.empty else "N/A")
    col6.metric("Max depth (km)", f"{filtered['depth'].max():.1f}" if not filtered.empty else "N/A")

    st.subheader("Earthquakes Map")
    if filtered.empty:
        st.info("No earthquakes found in the selected date range.")
    else:
        layer = build_earthquake_layer(filtered)
        view_state = pdk.ViewState(
            latitude=float(filtered["latitude"].mean()),
            longitude=float(filtered["longitude"].mean()),
            zoom=1,
            min_zoom=1,
            max_zoom=10,
            pitch=20,
        )

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
