import streamlit as st
import folium
from streamlit_folium import st_folium
from supabase import create_client
import pandas as pd
from authenticate import remove_auth
from folium.plugins import Geocoder, Search
import os
from dotenv import load_dotenv

load_dotenv()
remove_auth()
if "updated_success" not in st.session_state:
    st.session_state.updated_success = 0
if "edit_record" not in st.session_state:
    st.session_state.edit_record = None

def delete_crane_record(app_num):
    try:
        response = supabase.table("crane_records").delete().eq("application_num", app_num).execute()

        if response.data and len(response.data) > 0:
            st.session_state.deleted_app_success = True
            st.rerun()
        else:
            st.session_state.deleted_app_success = False
            st.error(f"{app_num} not found!")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

def render_edit_form(record):
    def safe_str(value):
        if value is None:
            return ""
        return str(value)
    with st.form("edit_record_form"):
        # Streamlit reads these inputs perfectly on rerun because this block is active
        app_num = st.text_input("Application Number", value=safe_str(record.get("application_num", "")), disabled=True)
        mref = st.text_input("Mref", safe_str(value=str(record.get("mref", ""))))
        taken_by = st.text_input("Taken By", value=safe_str(str(record.get("taken_by", ""))))
        
        # Add as many fields here as you want—no individual session states needed!

        update_btn = st.form_submit_button("💾 Update Record")
        
    if update_btn:
        try:
            # When pressed, mref and taken_by hold your newly typed text!
            supabase.table("crane_records").update({
                "mref": mref, 
                "taken_by": taken_by
            }).eq("application_num", record["application_num"]).execute()
            
            st.session_state.edit_record = None  # Clear the form
            st.session_state.updated_success = 1
            st.rerun()  

        except Exception as e:
            st.error(f"Something went wrong: {e}")

if "deleted_app_success" not in st.session_state:
    st.session_state.deleted_app_success = False

st.set_page_config(page_title="Live Crane Tracker", page_icon="🗺️")
st.sidebar.info("Made by Model. Model is super duper awesome.")


st.title("🗺️ Live Crane Tracker")
st.markdown("""
    This map displays the active cranes in the database.
""")

st.divider()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


PLAB_CTR_COORDS = [
    (103.8594, 1.1833),
    (104.0302, 1.55),
    (103.8955, 1.5333),
    (103.915, 1.4261),
    (103.8888, 1.4288),
    (103.8661, 1.3741),
    (103.8377, 1.3755),
    (103.7816, 1.35),
    (103.7608, 1.3402),
    (103.7497, 1.3097),
    (103.749,1.183),
    (103.8594, 1.1833)
    
]
PLAB_CTR_COORDS_LATLONG = [(lat, long) for long, lat in PLAB_CTR_COORDS]

try:
    response = supabase.table("crane_records").select("*").execute()
    st.subheader("📍 Active cranes tracker")
    st.markdown(f"Current number of cranes: **{len(response.data)}**")

    df_map = pd.DataFrame(response.data)
    
    if not df_map.empty:
        df_map['lat'] = pd.to_numeric(df_map['lat'], errors='coerce')
        df_map['long'] = pd.to_numeric(df_map['long'], errors='coerce')

        # Drop rows with NaN lat/long before doing anything map-related
        df_map_valid = df_map.dropna(subset=['lat', 'long'])

        if df_map_valid.empty:
            st.warning("No valid coordinates found in the database.")
        else:
            df_map = df_map_valid  # Use the cleaned DataFrame for mapping
        
            avg_lat = df_map['lat'].mean()
            avg_lng = df_map['long'].mean()
            
            # Initialize the folium map object
            m = folium.Map(location=[avg_lat, avg_lng], zoom_start=11, tiles="OpenStreetMap")
            geojson_data = {
                "type": "FeatureCollection",
                "features": []
            }
            for i, row in df_map.iterrows():
                coordinates = [row["long"], row["lat"]]
                application_num = row.get("application_num")

                feature = {   
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": coordinates
                        },
                        "properties": {
                            "application_num": application_num
                        }             
                }
                geojson_data["features"].append(feature)
                
            geojson_layer = folium.GeoJson(geojson_data, name="Search Index",
            style_function=lambda x: {"opacity": 0, "fillOpacity": 0},  # invisible
    marker=folium.CircleMarker(radius=0, fill=False, fill_opacity=0, opacity=0))
            geojson_layer.add_to(m)

            Search(
                layer=geojson_layer,
                geom_type="Point",
                search_label="application_num",
                placeholder="Search application number...",
                collapsed=False,
                move_to_location=True,
                search_zoom=14
            ).add_to(m)

            # Draw the PLAB CTR boundary as a solid closed polygon
            folium.Polygon(
                locations=PLAB_CTR_COORDS_LATLONG,
                color="blue",
                weight=2,
                fill=True,
                fill_color="blue",
                fill_opacity=0.05

            ).add_to(m)
            
            # Iterate over every coordinate row and build map markers
            for index, row in df_map.iterrows():
                # Helper lambda to turn Python None, empty strings, or string "None" into "N/A"
                def clean(val):
                    try:
                        if val is None or str(val).strip() in ["","None"]:
                            return "N/A"
                        else:
                            return val
                    except:
                        return "N/A"
          
                popup_content = f"""
                    <div style="font-family: sans-serif; width: 280px; font-size: 13px; line-height: 1.4;">
                        <div style="color: #ff4b4b; font-weight: bold; font-size: 11px; margin-bottom: 4px;">
                            OFFICIAL (CLOSED) / SENSITIVE NORMAL
                        </div>
                        <h5 style="margin: 0 0 5px 0; color: #1f77b4;">Application No: {clean(row.get('application_num'))}</h5>
                        <h7>Model is pretty awesome. Did you know that?</h7>
                        <hr style="margin: 5px 0; border: 0; border-top: 1px solid #ccc;">
                        
                        <b>Mref:</b> {clean(row.get('mref'))}<br/>
                        <b>Number of Cranes:</b> {clean(row.get('num_cranes'))}<br/>
                        <b>Height:</b> {clean(row.get('height(ft)'))}ft<br/>
                        <b>Coordinates:</b> {clean(row.get('coordinates'))}<br/>
                        <b>Start:</b> {clean(row.get('true_start'))}<br/>
                        <b>End:</b> {clean(row.get('true_end'))}<br/>
                        
                        <hr style="margin: 5px 0; border: 0; border-top: 1px dotted #ccc;">
                        <details style="cursor: pointer; color: #555;">
            <summary><b>📄 View Full Text</b></summary>
            <div style="font-size: 11px; color: #888; margin-top: 4px;">Phone numbers are masked!</div>
            <div style="max-height: 150px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word; background: #f9f9f9; padding: 6px; border-radius: 4px; margin-top: 5px;">
                {clean(row.get('full_text'))}
            </div>
        </details>
                    </div>
                """
                
                # Generate the individual pin drop
                folium.Marker(
                    location=[row['lat'], row['long']],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=f"App: {row.get('application_num', 'N/A')}",  
                    icon=folium.Icon(color="red")
                ).add_to(m)
                
            st_folium(m, width=800, height=500, key="fpo_master_map")

            st.divider()
            st.subheader("🏗️ Crane records")
            column_order = [
                "application_num",
                # "num_cranes",           
                # "bearing",
                # "distance",
                # "height(ft)",
                "mref",
                "full_text",
                "coordinates",
                # "kcq",
                # "civil_ref",
                "true_start",
                "true_end",
                # "notam_start",
                # "notam_end",
                # "notam_required",
                "taken_by",
                # "aip_required",
                # "aip_start",
                # "aip_end",
                # "status"
            ]
            st.dataframe(df_map[column_order], hide_index=True)

            st.divider()

            st.subheader("🗑️ Single Record Removal")
            st.markdown("Enter Crane Application No. to remove:")
            application_input = st.text_input("Application Number:", key="delete_app_input")
                
            delete_btn = st.button("Delete")

            if delete_btn:
                app_to_delete = application_input.strip()
                if app_to_delete == "":
                    st.warning("Input an application number to delete!")
                else:
                    delete_crane_record(app_to_delete)

            if st.session_state.deleted_app_success:
                delete_btn = ""
                st.success(f"Crane has been successfully deleted.")
                st.session_state.deleted_app_success = False
            
            st.divider()
            st.subheader("✏️ Edit Crane Record")
            st.markdown("Enter Crane Application No. to edit. Note that you are only limited to editing the NOTAM Mref and Taken By fields. If you need to edit other fields, delete the record and reupload the crane PDF. Else, get assistance from AIP IC. (This feature is still a WIP)")
            app_num_input = st.text_input("Application Number:")
            search_btn = st.button("Fetch Record")

            if search_btn:
                if app_num_input.strip() == "":
                    st.warning("Input an application number to edit!")
                else:
                    response = supabase.table("crane_records").select("*").eq("application_num", app_num_input.strip()).execute()
                    if response.data:
                        st.session_state.edit_record = response.data[0] # Save the dictionary here
                    else:
                        st.error(f"No record found.")
                        st.session_state.edit_record = None

            # B. The Form Trigger (Runs completely independent of the search button)
            if st.session_state.edit_record:
                render_edit_form(st.session_state.edit_record)

            # C. Success Message Action
            if st.session_state.updated_success == 1:
                st.success("Crane record has been successfully updated.")
                st.session_state.updated_success = 0

        
        

    else:
        st.info("The database is empty.")
        
        
except Exception as e:
    st.error(f"Something went wrong: {e}")