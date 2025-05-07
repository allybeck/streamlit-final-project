"""
Name:       Ally Beck
CS230:      Section 2
Data:       New England Airports
URL:

Description:
This program creates a streamlit website that displays charts and information based on data about airports in New England.
This program includes data to create a bar chart, pie charts, pivot tables, and an icon map to show users different information contained in the dataset.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
from PIL import Image

df = pd.read_csv("new_england_airports.csv").set_index("id")

#[DA1]/[DA7]
df.drop(columns = ["continent", "iata_code", "home_link", "wikipedia_link", "keywords"], inplace = True)

#[DA1]
df.rename(columns={"latitude_deg":"lat", "longitude_deg": "lon"}, inplace= True)

#[DA2]
df = df.sort_values(by = "elevation_ft", ascending = False)

#[DA3]
max_elevation = df["elevation_ft"].max()

#[PY5]/[DA8]
elevation_by_states = {}

for index, row in df.iterrows():
    state = row["iso_region"][-2:]
    elevation = row["elevation_ft"]

    if state in elevation_by_states:
        elevation_by_states[state].append(elevation)
    else:
        elevation_by_states[state] = [elevation]

#[PY4]
max_elevation_states = {state: max(elevations) for state, elevations in elevation_by_states.items()}

airport_types = {}
for index, row in df.iterrows():
    state = row["iso_region"][-2:]
    type = row["type"]

    if state not in airport_types:
        airport_types[state] = {}
    if type not in airport_types[state]:
        airport_types[state][type] = 1
    else:
        airport_types[state][type] += 1

#[ST1]
page = st.sidebar.radio("Choose a page", ["Home", "Airport Elevation by State", "Airport Types by State", "Elevation by State and Airport Type", "Airport Map"])

# Home page code
if page == "Home":
    st.title(f"New England Airports Data")

    # [ST4]
    img = Image.open("Logan-Takeoff-GettyImages-143183998-8e734debd82248b6b59ef908d9f1bb44.jpg")
    st.image(img, width=800)

    """
    The New England Airports dataset contains data about every airport in New England. There is information about
    the elevations of the airports, as well as data about the location and type of each airport. 
    """

    # [PY2]/[DA8]
    def get_highest_airport_info(df, max_elevation):
        for index, row in df.iterrows():
            if row["elevation_ft"] == max_elevation:
                return row["name"], row["type"]
        return None, None
    highest_airport, highest_airport_type = get_highest_airport_info(df, max_elevation)

    st.write(f"The airport with the highest elevation in New England is {highest_airport}, at an elevation of {max_elevation} ft. {highest_airport} is a {highest_airport_type}.")

elif page == "Airport Elevation by State":
    st.title("Airport Elevation by State")

    #[VIZ1]
    fig1, ax1 = plt.subplots(figsize = (10, 8))
    ax1.bar(max_elevation_states.keys(), max_elevation_states.values(), color = ["blue"])

    ax1.set_xlabel("States")
    ax1.set_ylabel("Maximum Airport Elevation (ft)")
    ax1.set_title("Maximum Airport Elevations by State")

    st.pyplot(fig1)

elif page == "Airport Types by State":
    st.title("Airport Types by State")
    #[ST2]
    pie_state = st.selectbox("Please select the state you would like to view data on", airport_types.keys())

    #[VIZ2]
    fig2, ax2 = plt.subplots(figsize = (5, 5))
    ax2.pie(airport_types[pie_state].values(), labels = airport_types[pie_state].keys(), autopct = '%.1f%%')
    st.pyplot(fig2)

elif page == "Elevation by State and Airport Type":
    st.title("Elevation by State and Airport Type")

    #[ST3]
    agg_function = st.text_input("Enter aggregation function (mean, max, min, count):", value = "mean").lower()
    valid_inputs = ["mean", "max", "min", "count"]

    #[VIZ3]/[PY3]/[DA6]
    if agg_function in valid_inputs:
        try:
            pivot = pd.pivot_table(data = df, values = "elevation_ft", index = "iso_region", columns = "type", aggfunc = agg_function).round(2)
            st.dataframe(pivot)
        except:
            st.error("Something went wrong while creating the pivot table")
    else:
        st.warning("Please enter a valid aggregation function (mean, max, min, or count)")

elif page == "Airport Map":
    st.title("Airport Map")
    #[MAP]
    ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/4/42/NotoSans_-_Small_Airplane_-_1F6E9.svg"
    icon_data = {
        "url": ICON_URL,
        "width": 100,
        "height": 100,
        "anchorY": 1
    }

    df["icon_data"] = None
    for i in df.index:
        df.at[i, "icon_data"] = icon_data

    icon_layer = pdk.Layer(type="IconLayer",
                           data=df,
                           get_icon="icon_data",
                           get_position='[lon,lat]',
                           get_size=4,
                           size_scale=10,
                           pickable=True)
    view_state = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=8,
        pitch=0
    )

    icon_map = pdk.Deck(
        map_style='mapbox://styles/mapbox/navigation-day-v1',
        layers=[icon_layer],
        initial_view_state=view_state,
    )
    st.pydeck_chart(icon_map)



