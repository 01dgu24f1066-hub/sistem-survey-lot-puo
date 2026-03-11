import streamlit as st
import pandas as pd
import numpy as np
import json
import folium
from streamlit_folium import st_folium
from pyproj import Transformer
import base64
import os
from folium.plugins import Fullscreen

# Set layout halaman luas
st.set_page_config(page_title="Sistem Survey Lot PUO", layout="wide")

# --- FUNGSI UNTUK LOGO ---
def get_base64_logo():
    if os.path.exists("puo.png"):
        try:
            with open("puo.png", "rb") as f:
                data = f.read()
                return base64.b64encode(data).decode()
        except Exception as e:
            st.error(f"Ralat membaca fail puo.png: {e}")
            return None
    return None

# --- 1. SISTEM KESELAMATAN ---
if 'users' not in st.session_state:
    st.session_state['users'] = {
        "1": {"nama": "Afifah", "pwd": "admin123"},
        "2": {"nama": "Lydia", "pwd": "admin123"},
        "3": {"nama": "Aisyah", "pwd": "admin123"}
    }

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_id' not in st.session_state:
    st.session_state['current_id'] = ""

def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; border: 2px solid #1E3A8A; text-align: center;">
                <h2 style="color: #1E3A8A; margin-bottom:10px;">🔐 Log Masuk Sistem Penjana Lot</h2>
                <p style="color: #555;">Sila Taip ID Username Anda (1, 2, atau 3)</p>
            </div>
            """, unsafe_allow_html=True)
        
        user_id = st.text_input("Username (ID)", key="login_user_id")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        
        if st.button("Login Sekarang", use_container_width=True):
            if user_id in st.session_state['users'] and pwd == st.session_state['users'][user_id]['pwd']:
                st.session_state['logged_in'] = True
                st.session_state['current_id'] = user_id
                st.rerun()
            else:
                st.error("ID atau Password salah!")

def change_password():
    uid = st.session_state['current_id']
    with st.sidebar.expander("🔑 Tukar Kata Laluan"):
        old_pwd = st.text_input("Kata Laluan Lama", type="password", key="old_pwd")
        new_pwd = st.text_input("Kata Laluan Baru", type="password", key="new_pwd")
        if st.button("Simpan Password"):
            if old_pwd == st.session_state['users'][uid]['pwd']:
                st.session_state['users'][uid]['pwd'] = new_pwd
                st.success("Berjaya ditukar!")
            else:
                st.error("Lama salah!")

# --- 2. LOGIK UTAMA ---
def main_app():
    uid = st.session_state['current_id']
    nama_surveyor = st.session_state['users'][uid]['nama']

    # --- FIX ICON FULLSCREEN (CSS) ---
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.fullscreen/1.0.2/Control.FullScreen.css" />
        <style>
            .leaflet-control-fullscreen-button {
                background-image: url(https://cdn-icons-png.flaticon.com/512/159/159605.png) !important;
                background-size: 16px 16px !important;
                background-repeat: no-repeat !important;
                background-position: center !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- SIDEBAR ---
    st.sidebar.markdown(f"""
        <div style="background-color: #13d675; padding: 20px; border-radius: 15px; text-align: center; color: white; margin-bottom: 10px;">
            <img src="https://cdn-icons-png.flaticon.com/512/4140/4140047.png" width="100" style="border-radius: 50%; background: white; padding: 5px;">
            <h3 style="margin-top: 10px; margin-bottom: 0;">Hai, {nama_surveyor}!</h3>
            <p style="font-weight: bold; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">{nama_surveyor}</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.sidebar.button("Log Keluar", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['current_id'] = ""
        st.rerun()
    
    st.sidebar.write("---")
    change_password()
    
    sidebar_export_placeholder = st.sidebar.empty()
    st.sidebar.write("---")

    st.sidebar.header("⚙️ Tetapan Paparan")
    poly_color = st.sidebar.color_picker("Warna Isi Poligon", "#FFFF00")
    line_color = st.sidebar.color_picker("Warna Garisan Sempadan", "#00FFFF")
    poly_opacity = st.sidebar.slider("Ketelusan Poligon", 0.0, 1.0, 0.4)
    text_size = st.sidebar.slider("Saiz Teks Bering (pt)", 6, 16, 10)
    stn_size = st.sidebar.slider("Saiz Bulatan Stesen", 15, 30, 20)
    
    st.sidebar.header("🔍 Kawalan Zoom")
    min_z = st.sidebar.slider("Zoom Min", 1, 15, 10)
    max_z = st.sidebar.slider("Zoom Max", 16, 22, 21)

    # --- HEADER UTAMA ---
    col_logo, col_text = st.columns([1, 3])
    with col_logo:
        logo_data = get_base64_logo()
        if logo_data:
            st.markdown(f"""
                <div style="background-color: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; display: flex; align-items: center; justify-content: center; height: 120px;">
                    <img src="data:image/png;base64,{logo_data}" style="max-width: 100%; max-height: 100%;">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background-color: white; color: #cc0000; padding: 20px; border-radius: 10px; border: 2px solid #cc0000; text-align: center; font-weight: bold;">Ralat:<br>Fail puo.png tiada</div>""", unsafe_allow_html=True)
            
    with col_text:
        st.markdown(f"""<div style="margin-top: 15px; margin-left: 15px;"><h1 style="margin-bottom: 0; color: #1E3A8A; font-family: 'Arial Black';">SISTEM SURVEY LOT</h1><p style="font-size: 1.2rem; color: #333; margin-top: 0;"><b>Politeknik Ungku Omar</b> | Jabatan Kejuruteraan Awam | 👤 <b>Surveyor: {nama_surveyor}</b></p></div>""", unsafe_allow_html=True)
    
    st.write("---")

    # --- KAWALAN FAIL ---
    st.markdown("### 💠 Kawalan Fail")
    uploaded_file = st.file_uploader("Upload fail CSV (STN, E, N)", type=["csv"], key="file_uploader")
    
    def transform_coords(df):
        transformer = Transformer.from_crs("EPSG:4390", "EPSG:4326", always_xy=True)
        lons, lats = transformer.transform(df['E'].values, df['N'].values)
        df['lat'], df['lon'] = lats, lons
        return df

    if uploaded_file:
        try:
            df_raw = pd.read_csv(uploaded_file)
            if not all(col in df_raw.columns for col in ['E', 'N']):
                st.error("Fail CSV mesti mengandungi kolum 'E' dan 'N'.")
            else:
                df = transform_coords(df_raw)
                e_coords, n_coords = df['E'].values, df['N'].values
                coords_wgs = df[['lat', 'lon']].values.tolist()
                
                area = 0.5 * np.abs(np.dot(e_coords, np.roll(n_coords, 1)) - np.dot(n_coords, np.roll(e_coords, 1)))
                perimeter = sum(np.sqrt((e_coords[(i+1)%len(df)] - e_coords[i])**2 + (n_coords[(i+1)%len(df)] - n_coords[i])**2) for i in range(len(df)))
                center_lat, center_lon = df['lat'].mean(), df['lon'].mean()

                # --- BINA PETA ---
                m = folium.Map(location=[center_lat, center_lon], zoom_start=19, min_zoom=min_z, max_zoom=max_z, tiles=None)
                folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='Google Hybrid', max_zoom=max_z, overlay=False).add_to(m)

                # --- TAMBAH FULLSCREEN ---
                Fullscreen(position='topleft', title='Skrin Penuh', title_cancel='Keluar', force_separate_button=True).add_to(m)

                # --- LAYER GROUPS ---
                fg_poligon = folium.FeatureGroup(name="Lapisan Poligon Lot").add_to(m)
                fg_stesen = folium.FeatureGroup(name="Lapisan Stesen & Label").add_to(m)

                # Info Lot Poligon
                info_lot_html = f"<div style='width:150px;font-family:Arial;'><b>LOT 11487</b><br>Luas: {area:.3f}m²<br>Perimeter: {perimeter:.3f}m<hr>Surveyor: {nama_surveyor}</div>"
                
                folium.Polygon(
                    locations=coords_wgs + [coords_wgs[0]], 
                    color=line_color, 
                    weight=3, 
                    fill=True, 
                    fill_color=poly_color, 
                    fill_opacity=poly_opacity, 
                    popup=folium.Popup(info_lot_html, max_width=250)
                ).add_to(fg_poligon)

                # --- MARKER & LABEL ---
                data_jadual = []
                for i, row in df.iterrows():
                    stn_val = int(row['STN']) if 'STN' in df.columns else (i+1)
                    stn_popup_html = f'<div style="font-family: Arial; width: 120px;"><b style="color: #1E3A8A;">STESEN {stn_val}</b><br><b>E:</b> {row["E"]:.3f}<br><b>N:</b> {row["N"]:.3f}</div>'
                    
                    folium.Marker(
                        [row['lat'], row['lon']],
                        popup=folium.Popup(stn_popup_html, max_width=200),
                        icon=folium.DivIcon(html=f"""<div style="display:flex;align-items:center;justify-content:center;background-color:red;color:white;font-weight:bold;font-size:{stn_size/2.5}pt;width:{stn_size}px;height:{stn_size}px;border-radius:50%;border:2px solid white;transform:translate(-50%,-50%);box-shadow: 1px 1px 3px rgba(0,0,0,0.5);">{stn_val}</div>""")
                    ).add_to(fg_stesen)

                for i in range(len(df)):
                    p1_idx, p2_idx = i, (i + 1) % len(df)
                    stn_dari = int(df.iloc[p1_idx]['STN']) if 'STN' in df.columns else (p1_idx + 1)
                    stn_ke = int(df.iloc[p2_idx]['STN']) if 'STN' in df.columns else (p2_idx + 1)
                    p1_c, p2_c = [e_coords[p1_idx], n_coords[p1_idx]], [e_coords[p2_idx], n_coords[p2_idx]]
                    p1_w, p2_w = coords_wgs[p1_idx], coords_wgs[p2_idx]
                    
                    dist = np.sqrt((p2_c[0]-p1_c[0])**2 + (p2_c[1]-p1_c[1])**2)
                    brg = np.degrees(np.arctan2(p2_c[0]-p1_c[0], p2_c[1]-p1_c[1])) % 360
                    d = int(brg); m_f = (brg - d) * 60; mi = int(m_f); s = round((m_f - mi) * 60)
                    if s == 60: s = 0; mi += 1
                    
                    label_text = f"{d}°{mi:02d}' {dist:.2f}m"
                    data_jadual.append({"Stesen": f"{stn_dari} - {stn_ke}", "Bering": f"{d}° {mi:02d}' {s:02d}\"", "Jarak (m)": f"{dist:.3f}"})

                    angle = -np.degrees(np.arctan2(p2_w[0]-p1_w[0], p2_w[1]-p1_w[1]))
                    if angle > 90 or angle < -90: angle += 180
                    mid_lat, mid_lon = (p1_w[0] + p2_w[0]) / 2, (p1_w[1] + p2_w[1]) / 2
                    folium.Marker([mid_lat, mid_lon], icon=folium.DivIcon(html=f'<div style="transform: rotate({angle}deg); color: #00FF00; font-weight: bold; font-size: {text_size}pt; text-shadow: 1px 1px 2px black; white-space: nowrap; text-align: center; width: 150px; margin-left: -75px;">{label_text}</div>')).add_to(fg_stesen)

                folium.LayerControl(position='topright', collapsed=False).add_to(m)
                st_folium(m, width="100%", height=600, key="map_display")

                st.markdown("### 📊 Jadual Data Survey")
                st.table(pd.DataFrame(data_jadual))

                polygon_coords = [[ [row['lon'], row['lat']] for _, row in df.iterrows() ]]
                polygon_coords[0].append([df.iloc[0]['lon'], df.iloc[0]['lat']])
                geojson_output = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"No_Lot": "11487", "Luas_m2": round(area, 3), "Surveyor": nama_surveyor}, "geometry": {"type": "Polygon", "coordinates": polygon_coords}}]}

                with sidebar_export_placeholder:
                    st.write("---")
                    st.markdown("### 📂 EXPORT DATA")
                    st.download_button(label=f"🚀 Export GeoJSON ({nama_surveyor})", data=json.dumps(geojson_output, indent=4), file_name=f"Lot_11487_{nama_surveyor}.geojson", mime="application/json", use_container_width=True, key="download_geojson")
                
                st.success(f"✅ Data diproses oleh {nama_surveyor}. Luas: {area:.3f} m²")
        except Exception as e:
            st.error(f"Ralat memproses fail: {e}")

# RUN
if not st.session_state['logged_in']:
    login_page()
else: 
    main_app()