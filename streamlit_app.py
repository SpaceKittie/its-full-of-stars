import streamlit as st
import pandas as pd
import snowflake.connector
import pydeck as pdk
from streamlit_autorefresh import st_autorefresh

# --- Page Configuration ---
st.set_page_config(
    page_title="🚀 Space Cadet Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st_autorefresh(interval=60 * 1000, key="data_refresh")

# --- Snowflake Connection ---
@st.cache_resource
def get_snowflake_conn():
    conn = snowflake.connector.connect(
        **st.secrets.snowflake,
        client_session_keep_alive=True
    )
    return conn

conn = get_snowflake_conn()

# --- Helper function to run queries ---
def run_query(query: str) -> pd.DataFrame:
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetch_pandas_all()

def get_iss_latest_location():
    query = """
    SELECT 
        LATITUDE, 
        LONGITUDE,
        RETRIEVED_AT,
        DISTANCE_TRAVELED_KM,
        SPEED_KPH
    FROM 
        SPACE_CADET_DB.MISSION_CONTROL.MC_ISS_LOCATION
    WHERE 
        RETRIEVED_AT IS NOT NULL
    ORDER BY 
        RETRIEVED_AT DESC
    LIMIT 1
    """
    return run_query(query)

@st.cache_data(ttl=3600)
def get_astronauts_data():
    query = "SELECT * FROM SPACE_CADET_DB.MISSION_CONTROL.MC_ASTRONAUTS"
    return run_query(query)

@st.cache_data(ttl=600)
def get_apod_data():
    query = """
    SELECT * FROM SPACE_CADET_DB.MISSION_CONTROL.MC_APOD
    WHERE APOD_DATE = (SELECT MAX(APOD_DATE) FROM SPACE_CADET_DB.MISSION_CONTROL.MC_APOD)
    """
    return run_query(query)

# --- Main App ---
st.markdown("<h1 style='text-align: center; margin-bottom: 1rem;'>🚀 Space Cadet Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Bringing you the latest and greatest from the final frontier, powered by Airflow and dbt.</p>", unsafe_allow_html=True)

# --- NASA Picture of the Day ---
with st.container():
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔭 NASA Picture of the Day</h2>", unsafe_allow_html=True)
        apod_df = get_apod_data()
        if not apod_df.empty:
            apod = apod_df.iloc[0]
            st.markdown(f"<h3 style='text-align: center;'>{apod['TITLE']}</h3>", unsafe_allow_html=True)
            if apod['MEDIA_TYPE'] == 'image':
                st.image(apod['IMAGE_URL'], use_column_width=True)
            elif apod['MEDIA_TYPE'] == 'video':
                st.video(apod['URL'])
            with st.expander("Read the explanation"):
                st.write(apod['EXPLANATION'])
        else:
            st.warning("Could not retrieve the Picture of the Day.")

st.markdown("---")

# --- Astronauts in Space ---
st.header("👨‍🚀 Astronauts in Space")
astronauts_df = get_astronauts_data()

if not astronauts_df.empty:
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 0

    show_all_toggle = st.toggle("Show all astronauts (not just those in space)", value=False)

    if not show_all_toggle:
        st.session_state.page_number = 0 # Reset page when viewing only in-space
        display_df = astronauts_df[astronauts_df['IS_IN_SPACE'] == True]
    else:
        display_df = astronauts_df
        
    st.metric("Total Astronauts Displayed", len(display_df))

    if show_all_toggle:
        PAGE_SIZE = 12
        start_idx = st.session_state.page_number * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        astronauts_to_display = display_df.iloc[start_idx:end_idx]
    else:
        astronauts_to_display = display_df

    astronauts_list = astronauts_to_display.to_dict('records')
    num_cols = 4

    for i in range(0, len(astronauts_list), num_cols):
        cols = st.columns(num_cols)
        row_astronauts = astronauts_list[i:i+num_cols]

        for j, astronaut in enumerate(row_astronauts):
            with cols[j]:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        img_url = astronaut['PROFILE_IMAGE']
                        if not img_url or img_url.endswith("nasa-logo.svg"):
                            img_url = "https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg"
                        st.image(img_url, width=100)
                    with col2:
                        st.markdown(f"**{astronaut['NAME']}**")
                        st.caption(f"Agency: {astronaut['AGENCY']}")
                        st.caption(f"Nationality: {astronaut['NATIONALITY']}")
                        st.caption(f"Status: {astronaut['STATUS']}")
                        if astronaut.get('IS_IN_SPACE') and astronaut.get('CURRENT_CRAFT'):
                            st.caption(f"🚀 Onboard: {astronaut['CURRENT_CRAFT']}")
                        if astronaut.get('WIKIPEDIA_URL'):
                            st.markdown(f"[Wikipedia]({astronaut['WIKIPEDIA_URL']})", unsafe_allow_html=True)
                        if astronaut.get('BIO'):
                            with st.expander("Bio"):
                                st.write(astronaut['BIO'])
    
    if show_all_toggle:
        total_pages = (len(display_df) // PAGE_SIZE)
        if len(display_df) % PAGE_SIZE > 0:
            total_pages += 1
            
        st.write("")
        
        prev_col, page_col, next_col = st.columns([1.5, 7, 1.5])
        
        with prev_col:
            if st.button("⬅️ Previous", use_container_width=True, disabled=(st.session_state.page_number < 1)):
                st.session_state.page_number -= 1
                st.rerun()

        with page_col:
            st.markdown(f"<p style='text-align: center; margin-top: 0.5rem;'>Page {st.session_state.page_number + 1} of {total_pages}</p>", unsafe_allow_html=True)

        with next_col:
            if st.button("Next ➡️", use_container_width=True, disabled=(st.session_state.page_number >= total_pages - 1)):
                st.session_state.page_number += 1
                st.rerun()
else:
    st.warning("Could not retrieve astronaut data. The data pipeline may be running.")

st.markdown("---")

# --- ISS Tracker ---
st.header("🛰️ Where is the ISS?")
st.markdown("Live location of the International Space Station. The dashboard will auto-refresh every 60 seconds.")

iss_df = get_iss_latest_location()

if iss_df.empty:
    st.warning("Could not retrieve ISS location. The data pipeline may be running.")
else:
    iss_df["RETRIEVED_AT_DISPLAY"] = pd.to_datetime(iss_df["RETRIEVED_AT"]).dt.strftime("%H:%M:%S UTC")
    latest_speed = iss_df['SPEED_KPH'].iloc[0]
    st.metric(label="Current Orbital Speed", value=f"{latest_speed:,.0f} km/h")

    ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/f/f2/ISS_spacecraft_model_1.png"
    icon_data = {
        "url": ICON_URL,
        "width": 256,
        "height": 256,
        "anchorY": 128,
    }
    iss_df["icon_data"] = [icon_data] * len(iss_df)
    icon_layer = pdk.Layer(
        type="IconLayer",
        id="icon-layer",
        data=iss_df,
        get_icon="icon_data",
        get_size=5,
        size_scale=20,
        get_position="[LONGITUDE, LATITUDE]",
        pickable=True,
    )
    view_state = pdk.ViewState(
        latitude=iss_df["LATITUDE"].iloc[0],
        longitude=iss_df["LONGITUDE"].iloc[0],
        zoom=1.5,
        pitch=45,
    )
    st.pydeck_chart(pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        initial_view_state=view_state,
        layers=[icon_layer],
        tooltip={"html": "<b>Current ISS Location</b><br/>Time: {RETRIEVED_AT_DISPLAY}<br/>Lat: {LATITUDE}, Lon: {LONGITUDE}"}
    ))

st.markdown("---")