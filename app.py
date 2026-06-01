import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
import osmnx as ox
import networkx as nx
import os
import time

st.set_page_config(page_title='Mapleview Cemetery Finder', layout='wide')

st.markdown(
    """
    <style>
    [data-testid="stElementToolbar"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 15-MINUTE TIMEOUT SECURITY ---
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = time.time()

elapsed_time = time.time() - st.session_state['start_time']

if elapsed_time > 900:
    st.error("⏳ **Session Expired**")
    st.write("For security, access is limited to 15 minutes. Please rescan the QR code to start a new session.")
    st.stop()

@st.cache_data
def load_data():
    # Notice: '/content/' is gone!
    file_path = 'Grave_Sites_with_Coords - Grave_Sites_with_Coords.csv'
    if not os.path.exists(file_path):
        st.error(f'File not found: {file_path}')
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    df['Name'] = df['Name'].fillna('Unknown').astype(str)
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    return df.dropna(subset=['Latitude', 'Longitude'])

@st.cache_resource
def get_graph():
    cf = '["highway"~"service|footway|path|track"]'
    try:
        center_lat, center_lon = 35.9835, -86.5100
        G = ox.graph_from_point((center_lat, center_lon), dist=400, network_type='all', custom_filter=cf)
        return ox.utils_graph.get_undirected(G)
    except:
        return ox.graph_from_point((center_lat, center_lon), dist=400, network_type='walk')

col1, col2 = st.columns([1, 4])
with col1:
    # Notice: '/content/' is gone here too!
    if os.path.exists('Smyrna Seal.png'): st.image('Smyrna Seal.png', width=200)
with col2:
    st.title('Town of Smyrna', anchor=False)
    st.subheader('Mapleview Cemetery Navigation', anchor=False)
    st.markdown('**Hours:** 6:00 AM – 7:00 PM')

st.divider()

try:
    df = load_data()
    G = get_graph()
    s_lat, s_lon = 35.982977, -86.5105326

    search_term = st.text_input('Search for a loved one (Last name, First name):').upper()

    if search_term:
        matches = df[df['Name'].str.contains(search_term, na=False)]

        if not matches.empty:
            selected_name = st.selectbox(f'Found {len(matches)} results:', matches['Name'].unique())
            person = matches[matches['Name'] == selected_name].iloc[0]
            g_lat, g_lon = person['Latitude'], person['Longitude']

            st.success(f'📍 Record found for: {selected_name}')
            
            st.markdown(f'### [🚶 Open Walking Directions in Google Maps](https://www.google.com/maps/dir/{s_lat},{s_lon}/{g_lat},{g_lon}/data=!4m2!4m1!3e2)')

            n_start = ox.distance.nearest_nodes(G, X=s_lon, Y=s_lat)
            n_end = ox.distance.nearest_nodes(G, X=g_lon, Y=g_lat)

            try:
                route = nx.shortest_path(G, n_start, n_end, weight='length')
                path_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
            except:
                path_coords = [(s_lat, s_lon)]

            # Lower the default zoom slightly just in case
            m = folium.Map(location=[(s_lat+g_lat)/2, (s_lon+g_lon)/2], zoom_start=17, max_zoom=24, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',attr='Esri')

            folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri World Imagery',
                name='Satellite',
                max_zoom=24,
                max_native_zoom=19
            ).add_to(m)

            folium.PolyLine(path_coords, color='#39FF14', weight=6, opacity=0.9).add_to(m)
            folium.PolyLine([path_coords[-1], (g_lat, g_lon)], color='orange', weight=4, opacity=0.8, dash_array='5').add_to(m)

            folium.Marker([s_lat, s_lon], popup='Entrance', icon=folium.Icon(color='blue')).add_to(m)
            folium.Marker([g_lat, g_lon], popup=selected_name, icon=folium.Icon(color='red', icon='star')).add_to(m)

            # --- ADD THIS NEW LINE ---
            # This forces the map to automatically frame both the entrance and the grave!
            m.fit_bounds([[s_lat, s_lon], [g_lat, g_lon]])
            # -------------------------

            LocateControl(auto_start=False, flyTo=True).add_to(m)
            
            # (Note: use_container_width=True is already making it fit the phone screen nicely)
            st_folium(m, width=800, height=600, use_container_width=True)
        else:
            st.warning('No names found matching that search.')
except Exception as e:
    st.error(f'Navigation load error: {e}')

            folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri World Imagery',
                name='Satellite',
                max_zoom=24,
                max_native_zoom=19
            ).add_to(m)

            folium.PolyLine(path_coords, color='#39FF14', weight=6, opacity=0.9).add_to(m)
            folium.PolyLine([path_coords[-1], (g_lat, g_lon)], color='orange', weight=4, opacity=0.8, dash_array='5').add_to(m)

            folium.Marker([s_lat, s_lon], popup='Entrance', icon=folium.Icon(color='blue')).add_to(m)
            folium.Marker([g_lat, g_lon], popup=selected_name, icon=folium.Icon(color='red', icon='star')).add_to(m)

            LocateControl(auto_start=False, flyTo=True).add_to(m)
            st_folium(m, width=800, height=600, use_container_width=True)
        else:
            st.warning('No names found matching that search.')
except Exception as e:
    st.error(f'Navigation load error: {e}')
