import streamlit as st
from get_time_info import plus_1_min, convert_to_ddmmmyyyy
from get_bearing_and_dist import get_location_info
from format_coords import round_coords
from authenticate import remove_auth

# from create_word_doc import edit_existing_doc
from validate_data import validate_data,validate_coord, validate_zulu_time
# from googleearth import generate_crane_kml
# import io
# import zipfile
from dotenv import load_dotenv
from fetch_crane_data import fetch_crane_records, supabase

load_dotenv()
# Front end UI and logic for Streamlit. This is the file that gets deployed.

remove_auth()

st.title("✍️ (MANUAL) AIPSUP - AIP Supplements and Crane Tracking")
st.sidebar.info("Made by Model. Model is super duper awesome.")
st.markdown("""
    For manual data entry instead of uploading PDF. For the printed stack of crane requests.
    * **Calculate** Period and Range information.
    * **Generate** AIP SUP Word Documents.
\n
    Made by Model. Model is awesome.
""")

st.divider()
st.warning("⚠️ Please ensure that the NOTAM has **already been taken/extended** till end of next month! There is no logic in place to determine the remaining duration of the crane/ whether it starts within 2 months, so exercise your own judgement whether to take the NOTAM first, or take a NOTAM for the rest of the crane duration. If you don't know what you're doing, don't use this page!")
st.warning("⚠️ Note that this record will be stored as AIP REQUIRED `(aip_required = 'Y')` and NOT SENT `(status = 'N')`.")

if "looks_good_clicked" not in st.session_state:
    st.session_state.looks_good_clicked = False
if "aip_start_datetime" not in st.session_state:
    st.session_state.aip_start_datetime = ""
if "aip_start_date" not in st.session_state:
    st.session_state.aip_start_date = ""
if "aip_end_date" not in st.session_state:
    st.session_state.aip_end_date = ""
if "final_data" not in st.session_state:
    st.session_state.final_data = {}
if "bearing_range" not in st.session_state:
    st.session_state.bearing_range = ""
if "saved_clicked" not in st.session_state:
    st.session_state.saved_clicked = False

asdt = st.session_state.aip_start_datetime
asd = st.session_state.aip_start_date
aed = st.session_state.aip_end_date
b_range = st.session_state.bearing_range

data = {
    "application_num": "",
    "num_cranes": 1,
    "height(ft)": "",
    "start(yyyymmddhhmmz)": "",
    "end(yyyymmddhhmmz)": "",
    "start(ddmmmyyyy)" : "",
    "end(ddmmmyyyy)" : "",
    "raw_coordinates": "",
    "rounded_coordinates": "",
    "bearing": "",
    "distance":"",
    "lat": 0.0,
    "long": 0.0,
    "month_year_end": "",
    "mref": ""
}
with st.form("edit_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        app_num = st.text_input("Application Number*",key="input_app_num")
        num_cranes = st.number_input("Number of Cranes*",min_value=1,key="input_num_cranes")
        height = st.number_input("Height (ft)* FEET NOT METRES!!!",min_value=1,key="input_height")
        mref = st.text_input("NOTAM Mref (last 5 digits)*", max_chars=5,help ="If a NOTAM hasn't been taken yet, please take the NOTAM till end of next month first!")
        taken_by = st.text_input("NOTAM taken By*",help ="If a NOTAM hasn't been taken yet, please take the NOTAM till end of next month first!")

    with col2:
        coords = st.text_input( "RAW Coordinates*",key="input_coords",help="Use the full coordinates with decimal points (or .0 if not applicable). This coordinate will be automatically rounded for the AIP SUP." )
        start_datetime = st.text_input("AIP Start (YYMMDDHHMMz)",disabled=True,value=asdt)
        start_date = st.text_input("AIP Start (DDMMMYYYYz)",disabled=True,value=asd)
        NOTAM_start_datetime = st.text_input("NOTAM Start (YYMMDDHHMMz)*",key="input_notam_start")
        
    with col3:
        bearing_range_display = st.text_input("Bearing/Range", value=b_range, disabled=True)
        end_datetime = st.text_input("AIP/Crane End (YYMMDDHHMMz)*",key="input_aip_end")
        end_date = st.text_input("AIP End (DDMMMYYYYz)", disabled=True,value=aed)
        NOTAM_end_datetime = st.text_input("NOTAM End (YYMMDDHHMMz)*",key="input_notam_end") #, value=data.get("end(yyyymmddhhmmz)","")

    submit_button = st.form_submit_button("⏩ Proceed",disabled=st.session_state.looks_good_clicked)


if submit_button:
    #VALIDATION HERE
    # data_to_validate = {
    #             "coordinates": coords,
    #             "true_start": start_datetime,
    #             "true_end": end_datetime,
    #             "notam_start": NOTAM_start_datetime,
    #             "notam_end": NOTAM_end_datetime,
    #             "mref": mref,
    #             "taken_by": taken_by,
    #             "application_num": app_num,
    #             "height(ft)": height,
    #             "NOTAM_start_datetime": NOTAM_start_datetime,
    #             "NOTAM_end_datetime": NOTAM_end_datetime,
    #             "ref_height(m)": data.get("ref_height(m)") 
    #         }

    # validation_result = validate_data(data_to_validate, False)
    # if "error" in validation_result:
    #     st.error(validation_result["error"])
    #     st.stop()

    if app_num.strip() == "":
        st.error("⚠️ Missing application number!")
        st.stop()

    coords_clean = coords.strip()
    if not validate_coord(coords_clean):
        st.error("⚠️ Invalid Coordinate Format! Must be: 012124.3N 1035558.1E (DECIMAL and SPACE)")
        st.stop()

    if not validate_zulu_time(end_datetime.strip()):
        st.error("⚠️ Invalid AIP DateTime Format! AIP End Datetime must be in YYMMDDHHMM format!")
        st.stop()

    if NOTAM_start_datetime.strip() != "" or NOTAM_end_datetime.strip() != "":
        if not validate_zulu_time(NOTAM_start_datetime.strip()) or not validate_zulu_time(NOTAM_end_datetime.strip()):
            st.error("⚠️ Invalid NOTAM DateTime Format! NOTAM Start/End Datetime must be in YYMMDDHHMM format!")
            st.stop()

    if mref.strip() == "":
        st.error("⚠️ Mref cannot be empty!")
        st.stop()

    else:
        if not mref.strip().isdigit():
            st.error("⚠️ Ensure Mref is written correctly.")
            st.stop()
        
        if len(mref.strip()) != 5:
            st.error("⚠️ Mref must be exactly 5 digits.")
            st.stop()
    
    if app_num == "":
        st.error("⚠️ Application number cannot be empty!")
        st.stop()
        
    if taken_by == "":
        st.error("⚠️ NOTAM taken by cannot be empty! If a NOTAM hasn't been taken yet, please take a NOTAM till end of next month first!")
        st.stop()
        
    st.session_state.aip_start_datetime = plus_1_min(NOTAM_end_datetime)
    st.session_state.aip_start_date = convert_to_ddmmmyyyy(st.session_state.aip_start_datetime)
    st.session_state.aip_end_date = convert_to_ddmmmyyyy(end_datetime.strip())

    loc_info = get_location_info(coords_clean)
    
    # Store everything in a persistent session_state dictionary
    st.session_state.final_data = {
        "application_num": app_num,
        "num_cranes": num_cranes,
        "height(ft)": height,
        "start(yyyymmddhhmmz)": st.session_state.aip_start_datetime,
        "end(yyyymmddhhmmz)": end_datetime,
        "start(ddmmmyyyy)": st.session_state.aip_start_date,
        "end(ddmmmyyyy)": st.session_state.aip_end_date,
        "true_start(ddmmmyyyy)": convert_to_ddmmmyyyy(NOTAM_start_datetime),
        "rounded_coordinates": round_coords(coords_clean),
        "raw_coordinates": coords,
        "distance": loc_info["distance"],
        "bearing": loc_info["bearing"],
        "lat": loc_info["lat"],
        "long": loc_info["long"],
        "mref": mref,

        "aip_start" : st.session_state.aip_start_datetime,
        "aip_end": end_datetime,
        "notam_start": NOTAM_start_datetime,
        "notam_end": NOTAM_end_datetime,
        "taken_by" :taken_by
    }

    st.session_state.looks_good_clicked = True
    st.session_state.bearing_range = f"{loc_info['bearing']}° / {loc_info['distance']} NM"
    st.rerun()

if st.session_state.looks_good_clicked == True:
    data = st.session_state.final_data

    st.success("Data Validated!")
    with st.expander("View extracted JSON data (for dev use only)", expanded=False):
            st.json(data)
    
    # st.warning("🔔 Remember to download and save the AIP SUP word document as required.")

    # st.subheader("📄 AIP SUP Word Document")
    # st.markdown("Save under `AWAIT SIGN > Batch X` *(whichever batch folder is the most current)*.")

    # with st.spinner("Creating Word Document..."):
    #     output_filename = edit_existing_doc(data)
    
    # with open(output_filename, "rb") as f:
    #     st.download_button(
    #         label=f"📥 Download {output_filename}",
    #         data=f,
    #         file_name=output_filename,
    #         mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    #     )

    try:         
        if st.button("💾 Save crane record into Database"):
            record_data = {
                "application_num": str(data.get("application_num","")),
                "num_cranes": data.get("num_cranes",""),
                "coordinates": str(data.get("raw_coordinates","")),
                "rounded_coordinates": str(data.get("rounded_coordinates", "")),
                "bearing": str(data.get("bearing", "")),
                "distance": str(data.get("distance", "")),
                "height(ft)": str(data.get("height(ft)", "")),
                "mref": str(data.get("mref","")), 
                "kcq": "",  
                "civil_ref": "",  
                "true_start": data.get("true_start(ddmmmyyyy)"),
                "true_end": data.get("end(ddmmmyyyy)"),
                "notam_start": data.get("notam_start"), 
                "notam_end": data.get("notam_end"),  
                "notam_required": "Y",  
                "taken_by": data.get("taken_by"),  # not in `data` -- pulled from variable directly
                "aip_required": "Y", 
                "aip_start": str(data.get("aip_start", "")) if data.get("aip_required") != "No" else "",
                "aip_end": str(data.get("aip_end", "")) if data.get("aip_required") != "No" else "",
                "lat": data.get("lat"),
                "long": data.get("long"),
                "full_text": data.get("full_text"),  # not in `data` -- will always be None
                "status": "N"
            }

            supabase.table("crane_records").insert(record_data).execute()
            fetch_crane_records.clear()

            st.success(f"Crane successfully saved!")
            st.session_state.saved_clicked = True
    except Exception as e:
        st.error(f"Failed to save record! {e}")
        st.session_state.saved_clicked = True

    if st.button("🔄 Refresh page for New Entry"):
        if st.session_state.saved_clicked != True:
            st.error("(Attempt to) Save the crane into the database!")
            st.stop()

        st.html(
            "<script>parent.window.location.reload()</script>",
            unsafe_allow_javascript=True
        )
    


    

    # #KML FILE
    # with st.spinner("Generating KML..."):
    #     google_earth_data = generate_crane_kml(data)
    #     kml_file = google_earth_data.get("filename")

    # # ZIP FILE 
    # st.subheader("📦 Download documents")
    # st.markdown("Download a ZIP file containing the AIP SUP Word Document and the KML file.")
    # zip_buffer = io.BytesIO()
    # with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
    #     # Add Word Document to ZIP
    #     with open(output_filename, "rb") as f_word:
    #         zip_file.writestr(output_filename, f_word.read())
            
    #     # Add KML File to ZIP
    #     with open(kml_file, "rb") as f_kml:
    #         zip_file.writestr(kml_file, f_kml.read())
    # zip_buffer.seek(0)
    
    # st.download_button(
    #     label="📥 Download ZIP File",
    #     data=zip_buffer,
    #     file_name=f"{app_num}.zip",
    #     mime="application/zip"
    # )


    # st.subheader("📋 Copy Data for Excel")
    # st.markdown("Copy and paste into the designated Excel sheet for tracking.")

#     excel_ready_row = "\t".join([
#     str(app_num), #CRANE REF NO.
#     str(coords), #ROUNDED COORDS
#     str(data.get("bearing", "")), #BEARING
#     str(data.get("distance", "")), #DISTANCE
#     str(data.get("height(ft)", "")), #HEIGHT
#     str(data.get("mref", "N/A")), #MREF
#     "", #KCQ (to fill in manually)
#     "", #CIVIL REF (to fill in manually)
#     str(NOTAM_start_datetime), #NOTAM START
#     str(NOTAM_end_datetime), #NOTAM END
#     "Yes", #NOTAM REQUIRED YES BY DEFAULT
#     str(taken_by), #TAKEN BY
#     "Yes", #AIP REQUIRED YES BY DEFAULT
#     str(start_datetime), #AIP START
#     str(end_datetime)  #AIP END
# ])
#     st.code(excel_ready_row, language="text")

#     st.divider()
#     st.markdown("...or manually download the files 👇")

#     st.subheader("📄 AIP SUP Word Document")
#     st.markdown("Remember to move the file into the correct folder.")


    # with open(output_filename, "rb") as f:
    #     st.download_button(
    #         label=f"📥 Download {output_filename}",
    #         data=f,
    #         file_name=output_filename,
    #         mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    #     )

    # st.subheader("🌍 Google Earth")
    # st.markdown("Remember to save the points on Google Earth!")

    # with open(kml_file, "rb") as f:
    #     st.download_button(
    #         label=f"📥 Download KML file for Google Earth",
    #         data=f,
    #         file_name=kml_file,
    #         mime="application/vnd.google-earth.kml+xml"
    #     )
    # text_for_google_earth =  google_earth_data.get("text")
    # st.text_area("...or manually copy and paste into Google Earth 👇", value=text_for_google_earth, height=300)

    
    



        
        

