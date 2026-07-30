import streamlit as st
from get_time_info import add_2_months, convert_to_ddmmmyyyy, minus_1_min, plus_1_min
from main import main
# from create_word_doc import edit_existing_doc
from get_bearing_and_dist import get_location_info, within_5_km
import pandas as pd
from format_coords import round_coords
# from googleearth import generate_crane_kml
from st_supabase_connection import SupabaseConnection
from authenticate import check_password
import zipfile
from validate_data import validate_data
import os
from supabase import create_client


url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


st.set_page_config(page_title="AIP SUP Generator", page_icon="🏗️")
st.sidebar.info("Made by Model. Model is super duper awesome.")

st.title("🏗️ AIPSUP - AIP Supplements and Crane Tracking")
st.markdown("""
    Paste crane PDF text to:
    * **Extract** Text and Information.
    * **Calculate** Period and Range Information.
    * **Generate** AIP SUP Word Documents.
    * **Track** Active Cranes in the Database.\n
    Made by Model. Model is awesome.
""")

st.divider()

# uploaded_file = st.file_uploader("Upload Crane PDF", type="pdf")
def reset_session_state():
    st.session_state.acknowledged_warning = False
    st.session_state.added_2_months = False
    st.session_state.new_session = True
    st.session_state.looks_good_clicked = False
    st.session_state.start_dateTime = ""
    st.session_state.start_date = ""
    st.session_state.NOTAM_start = ""
    st.session_state.NOTAM_end = ""
    st.session_state.easter = 0
    st.session_state.aip_not_required = False
    st.session_state.require_take_notam = True
    st.session_state.manual_add_cause_user_is_dumb = False
    st.session_state.download_clicked = False
    st.session_state.saved_clicked = False

if "added_2_months" not in st.session_state:
    st.session_state.added_2_months = False
if "acknowledged_warning" not in st.session_state:
    st.session_state.acknowledged_warning = False
if "current_file" not in st.session_state:
    st.session_state.current_file = False
if "start_dateTime" not in st.session_state:
    st.session_state.start_dateTime = ""
if "start_date" not in st.session_state:
    st.session_state.start_date = ""
if "end_dateTime" not in st.session_state:
    st.session_state.end_dateTime = ""
if "end_date" not in st.session_state:
    st.session_state.end_date = ""  
if "new_session" not in st.session_state:
    st.session_state.new_session = False
if "looks_good_clicked" not in st.session_state:
    st.session_state.looks_good_clicked = False
if "NOTAM_start" not in st.session_state:
    st.session_state.NOTAM_start = ""
if "NOTAM_end" not in st.session_state:
    st.session_state.NOTAM_end = ""
if "easter" not in st.session_state:
    st.session_state.easter = 0
if "aip_not_required" not in st.session_state:
    st.session_state.aip_not_required = False
if "require_take_notam" not in st.session_state:
    st.session_state.require_take_notam = True
if "manual_add_cause_user_is_dumb" not in st.session_state:
    st.session_state.manual_add_cause_user_is_dumb = False
if "download_clicked" not in st.session_state:
    st.session_state.download_clicked = False
if "saved_clicked" not in st.session_state:
    st.session_state.saved_clicked = False
if "data" not in st.session_state:
    st.session_state.data = None

st.subheader("📄 Paste crane PDF text here")
st.markdown("`CTRL + A`, `CTRL + C`, `CTRL + V` to copy all text from the crane PDF and paste it here.")
pasted_text = st.text_area(
    label="Text from PDF:",
    height=300,
    placeholder="Copy all text from the crane PDF and paste it here..."
)
process_button = st.button("⏩ Process Text")

if process_button:
    if pasted_text.strip() == "":
        st.error("Seriously?")
        st.stop()

    reset_session_state()
   
    with st.spinner("Processing text..."):
        data = main(pasted_text)
        st.session_state.data = data

data = st.session_state.data

if data is None:
    st.info("Paste the crane PDF text above and click Process Text to begin.")
    st.stop()

if st.session_state.start_dateTime == "":
    st.session_state.start_dateTime = data.get("start(yyyymmddhhmmz)", "")
    st.session_state.start_date = data.get("start(ddmmmyyyy)", "")
    st.session_state.end_dateTime = data.get("end(yyyymmddhhmmz)", "")
    st.session_state.end_date = data.get("end(ddmmmyyyy)", "")
        
        
# Due to built-in limitation by Streamlit where session state variables cannot be updated when being used as 
# values for input fields in a form, the workaround is to assign the session state variables to temporary variables.
current_startdt = st.session_state.start_dateTime
current_startd= st.session_state.start_date
enddt = st.session_state.end_dateTime
endd = st.session_state.end_date
NOTAM_startdt = st.session_state.NOTAM_start
NOTAM_enddt = st.session_state.NOTAM_end

# If there is any error extracting/calculating info, the whol e process will be killed
if "Error" not in data:
    failed_variables = []
    for key, value in data.items():
        if value == "Error":
            failed_variables.append(key)
    if len(failed_variables) > 0:
        st.error(f"❌ Something went wrong with extracting the following fields: {', '.join(failed_variables)}. Please ensure the PDF is correctly formatted. Else, use manual data entry.")
        st.stop()
        
    else:
        st.toast("Data extracted successfully!")
        with st.expander("View extracted JSON data (for dev use only)", expanded=False):
            st.json(data)

        st.divider()

        st.subheader("Confirm & edit details")

        if not within_5_km(data.get("lat"),data.get("long")):
            st.error("⚠️ Crane is outside of PAYA LEBAR CTR! Are you sure you want to proceed?")
            
        # If cranes starts aft 2 months, just take AIP straight away. No requirement for NOTAM at all.
        if data.get("start_in_less_than_2_months") == False:
            st.success("✅ No requirement to take a NOTAM. **Remember to download the AIP SUP word doc, and save the crane into the Database!**")
            st.session_state.require_take_notam = False
            pass
        
        # If start within 2 mnths, and duration less than 60 days, recommend taking 1x NOTAM instead.
        elif data.get("duration_days") <= 60:
            st.warning(f"⚠️ Duration is <= 2 months. Recommend taking 1x NOTAM instead.  **No requirement for AIP. Just save the crane into the Database.**")
        

            st.session_state.aip_not_required = True
            st.session_state.require_take_notam = True
            
            if st.session_state.NOTAM_start == "" or st.session_state.NOTAM_end == "":
                # so NOTAM start/end is auto populated if AIP not required, only NOTAM
                st.session_state.NOTAM_start = data.get('start(yyyymmddhhmmz)')
                st.session_state.NOTAM_end = data.get('end(yyyymmddhhmmz)')

                st.rerun()

            
        # If start within 2 mnths, and duration less than 4 mnths, recommend taking 2x NOTAM instead (as per NOTAM flowchart).
        elif 60 < data.get("duration_days") <= 120:
            if data.get("start_in_less_than_2_months") == True:
                st.warning(f"⚠️ NOTAM starts within 2 months and Duration is <= 4 months. Recommend taking 2x NOTAM instead. **No requirement for AIP. Just save the crane into the Databasee.**")

                st.session_state.aip_not_required = True
                st.session_state.require_take_notam = True
            else:
                pass

        # If more than 4 mnths, but start within 2 mnths, recommend taking 1x NOTAM first (as per flowchart)
        elif data.get("duration_days") > 120 and data.get("start_in_less_than_2_months") == True:
            st.warning("⚠️ Crane starts within 2 months. Recommend taking 1x 2 month NOTAM first. **Add 2 months for the start date of AIP! Remember to download the AIP SUP word doc, and save the crane into the Database**")
            if not st.session_state.acknowledged_warning:
                
                # If acknowledged hasn't been pressed (either first time upload or new file uploaded)
                if st.button("Acknowledge"):
                    st.session_state.acknowledged_warning = True  
                    st.rerun() 
                
                # Pause code until user acknowledges warning
                st.stop()

        # Raw regex results
        with st.expander("View raw text extracted from PDF", expanded=True):
            st.caption("Raw regex results:")

            col_ref1, col_ref2 = st.columns(2)
            with col_ref1:
                st.write(f"**Appication Number:** {data.get('ref_application_num','')}")
                st.write(f"**Number of Cranes:** {data.get('ref_num_cranes','')}")
                st.write(f"**Height(m):** {data.get('ref_height(m)','')}")
            with col_ref2:
                st.write(f"**Coordinates:** {data.get('ref_raw_coords','')}")
                st.write(f"**Period:** {data.get('ref_period','')}")

        # Data entry form
        with st.form("edit_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                app_num = st.text_input("Application Number*", value=data.get("application_num", ""))
                num_cranes = st.number_input("Number of Cranes*", value=int(data.get("num_cranes")), min_value=1)
                height = st.number_input("Height (ft)*", value=int(data.get("height(ft)")), min_value=1)
                mref = st.text_input("NOTAM Mref (last 5 digits)", max_chars=5, help="Mandatory if NOTAM is required. Ensure Mref is written correctly.",)
                taken_by = st.text_input("NOTAM taken by*",help ="Mandatory if NOTAM is required.")

            with col2:
                coords = st.text_input("RAW Coordinates*", value=data.get("raw_coordinates", ""),help="Use the full coordinates with decimal points (or .0 if not applicable). This coordinate will be automatically rounded for the AIP SUP.")
                start_datetime = st.text_input("AIP Start (YYMMDDHHMMz)*", value=current_startdt, help="If AIP not required, disregard the datetime here. Do not remove it.")
                start_date = st.text_input("AIP Start (DDMMMYYYYz)*", value=current_startd, disabled = True)
                NOTAM_start_datetime = st.text_input("NOTAM Start (YYMMDDHHMMz)", value=NOTAM_startdt)

            with col3:
                bearing_range = st.text_input("Bearing/Range", value=f"{data.get('bearing', '')}° / {data.get('distance', '')} NM", disabled=True)
                end_datetime = st.text_input("AIP End (YYMMDDHHMMz)*", value=enddt,help="If AIP not required, disregard the datetime here. Do not remove it.")
                end_date = st.text_input("AIP End (DDMMMYYYYz)*", value=endd,disabled = True)
                NOTAM_end_datetime = st.text_input("NOTAM End (YYMMDDHHMMz)", value=NOTAM_enddt) #, value=data.get("end(yyyymmddhhmmz)","")

            # Disables add 2 mnths btn if AIP not required (crane duration less than 2 mnths)
            if data.get("duration_days") <= 60:
                st.session_state.added_2_months = True

            if st.session_state.added_2_months == True:
                if st.session_state.require_take_notam == True:
                    st.info(f"""
                        Please take the following NOTAM:
                            
                        STARTDTG: **{st.session_state.NOTAM_start}**

                        END DTG: **{st.session_state.NOTAM_end}**

                        UPPER FL: **{data.get("upper_FL")}**

                        CORD: **{data.get("rounded_coord_for_notam")}**
                            
                        **{data.get("num_temp")} {data.get("crane_plural_temp")}**, HGT **{data.get("height(ft)")}**FT AMSL, ERECTED AT **{data.get("rounded_coordinates")}**
                        (BRG **{data.get("bearing")}**DEG, DIST **{data.get("distance")}**NM FM WSAP ARP-WI WSAP CTR). CRANE MARKED AND
                        LGTD AT NGT.
                        
                        """)
                
            st.markdown("If crane starts within 2 months, click the 'Add 2 months' button to automatically add 2 months to the AIP start date, and automatically generate the NOTAM dates! If there is no requirement for a NOTAM, don't click this!")
            add_2_months_button = st.form_submit_button("Add 2 months to AIP start date", disabled=st.session_state.added_2_months)
            submit_button = st.form_submit_button("⏩ Proceed",disabled=st.session_state.looks_good_clicked) 

        if add_2_months_button:
            st.session_state.added_2_months = True

            # Add 2 mnths to AIP START, and make NOTAM START to start of crane, and NOTAM END to 1 min before start of AIP
            st.session_state.start_dateTime = add_2_months(data.get("start(yyyymmddhhmmz)"))
            st.session_state.start_date = add_2_months(data.get("start(ddmmmyyyy)"))
            st.session_state.NOTAM_start = data.get("start(yyyymmddhhmmz)")
            
            end = minus_1_min(str(st.session_state.start_dateTime)) 
            st.session_state.NOTAM_end = end
            st.rerun()

        #To make sure this success msg only shows up when NOTAM start/end date isnt empty (notam taken)
        #, and the added 2 mnths btn is pressed. Else, it wld show up even when the btn isn't pressed (user manually add notam dates).
        #Purely for UX only.
        if st.session_state.added_2_months == True: 
            if NOTAM_start_datetime != "" and NOTAM_end_datetime != "":
                if NOTAM_start_datetime != start_datetime: 
                    if st.session_state.manual_add_cause_user_is_dumb == False:
                        st.success(f"🆕 Start date updated till end of next month! {data.get('start(yyyymmddhhmmz)')} ({data.get('start(ddmmmyyyy)')}) -> {st.session_state.start_dateTime} ({st.session_state.start_date})")
                        st.warning(f"🔔 Please take NOTAM from {data.get('start(yyyymmddhhmmz)')}z to {st.session_state.NOTAM_end}z.")

        # Data validation
        if submit_button:
            data_to_validate = {
                "coordinates": coords,
                "true_start": start_datetime,
                "true_end": end_datetime,
                "notam_start": NOTAM_start_datetime,
                "notam_end": NOTAM_end_datetime,
                "mref": mref,
                "taken_by": taken_by,
                "application_num": app_num,
                "height(ft)": height,
                "NOTAM_start_datetime": NOTAM_start_datetime,
                "NOTAM_end_datetime": NOTAM_end_datetime,
                "ref_height(m)": data.get("ref_height(m)") 
            }

            validation_result = validate_data(data_to_validate, st.session_state.require_take_notam)
            if "error" in validation_result:
                st.error(validation_result["error"])
                st.stop()
            
            # Sets AIP start to 1 min after NOTAM ends (user manually adds dates)
            if st.session_state.looks_good_clicked == False:
                if NOTAM_end_datetime.strip() != "":
                    st.session_state.start_dateTime = plus_1_min(NOTAM_end_datetime)
                    start_datetime = plus_1_min(NOTAM_end_datetime)
                    st.session_state.manual_add_cause_user_is_dumb = True
                    
            st.session_state.NOTAM_start = NOTAM_start_datetime
            st.session_state.NOTAM_end = NOTAM_end_datetime

            st.session_state.looks_good_clicked = True 
            st.session_state.added_2_months = True          

            # new start/end date after adding 2 mnths
            st.session_state.start_date = convert_to_ddmmmyyyy(start_datetime)
            st.session_state.end_date = convert_to_ddmmmyyyy(end_datetime)

            st.rerun()

        # data dictionary will be updated with any new values
        if st.session_state.looks_good_clicked == True:
            data["application_num"] = app_num
            data["num_cranes"] = num_cranes
            data["height(ft)"] = height
        
            # If user edits coordinates, rerun get location info()
            if data["raw_coordinates"] != coords:
                st.warning(f"⚠️ Coordinates edited. Old distance:{data.get('distance', '')}, Old bearing: {data.get('bearing', '')}. Recalculating...")

                data["raw_coordinates"] = coords
                location_info = get_location_info(coords)

                data["rounded_coordinates"] = round_coords(coords)
                data["distance"] = location_info.get("distance", "")
                data["bearing"] = location_info.get("bearing", "")

                data["lat"] = location_info.get("lat", "")
                data["long"] = location_info.get("long", "")

                st.success(f"🆕 Updated Distance: {data.get('distance', '')} NM, Updated Bearing: {data.get('bearing', '')}°")

            data["start(yyyymmddhhmmz)"] = start_datetime
            data["end(yyyymmddhhmmz)"] = end_datetime
            data["start(ddmmmyyyy)"] = start_date
            data["end(ddmmmyyyy)"] = end_date

            if st.session_state.require_take_notam == True:
                data["notam_required"] = "Yes"
            else:
                data["notam_required"] = "No"

            data["mref"] = mref 

            if st.session_state.aip_not_required is True:
                data["aip_required"] = "No"
            else:
                data["aip_required"] = "Yes"

            
            # if st.session_state.aip_not_required == True:
            #     st.success("✅ AIP not required for this crane operation.")
            # else:
            #     st.warning("⚠️ AIP is required for this crane operation.")

            # # WORD DOC
            # with st.spinner("Creating Word Document..."):
            #     output_filename = edit_existing_doc(data) 

            # st.subheader("📄 AIP SUP Word Document")
            # st.markdown("Save under `AWAIT SIGN > Batch X` *(whichever batch folder is the most current)*.")

            # if st.session_state.aip_not_required == False:
            #     st.success("**AIP REQUIRED! DOWNLOAD THIS!**")
            # else:
            #     st.error("**AIP NOT REQUIRED!**")

            # with open(output_filename, "rb") as f:
            #     btn_download = st.download_button(
            #         label=f"📥 Download {output_filename}",
            #         data=f,
            #         file_name=output_filename,
            #         mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            #         disabled= st.session_state.aip_not_required
            #     )
                
            # if btn_download:
            #     st.session_state.download_clicked = True
    
            try:         
                if st.button("💾 Save crane record into Database"):

                    record_data = {
                        "application_num": str(app_num),
                        "num_cranes": data.get("num_cranes"),
                        "coordinates": str(coords),
                        "rounded_coordinates" : str(data.get("rounded_coordinates", "")),
                        "bearing": str(data.get("bearing", "")),
                        "distance": str(data.get("distance", "")),
                        "height(ft)": str(data.get("height(ft)", "")),
                        "mref": str(data.get("mref", "N/A")),
                        "kcq": "",  # Manual entry placeholder
                        "civil_ref": "",  # Manual entry placeholder
                        "true_start": data.get("true_start(ddmmmyyyy)"),
                        "true_end": data.get("end(ddmmmyyyy)"),
                        "notam_start": str(NOTAM_start_datetime),
                        "notam_end": str(NOTAM_end_datetime),
                        "notam_required": str(data.get("notam_required", "")),
                        "taken_by": str(taken_by),
                        "aip_required": str(data.get("aip_required", "")),
                        "aip_start": str(start_datetime) if data.get("aip_required") != "No" else "",
                        "aip_end": str(end_datetime) if data.get("aip_required") != "No" else "",
                        "lat": data.get("lat"),
                        "long": data.get("long"),
                        "full_text": data.get("full_text"),
                        "status": "N" 
                    }

                    supabase.table("crane_records").insert(record_data).execute()
                    
                    st.success(f"Crane successfully saved!")
                    st.session_state.saved_clicked = True
            except Exception as e:
                st.error(f"Failed to save record! {e}")
                st.session_state.saved_clicked = True

            if st.button("🔄 Refresh page for New Entry"):
                if st.session_state.saved_clicked != True:
                    st.error("(Attempt to) Save the crane into the database!")
                    st.stop()
                # if st.session_state.aip_not_required == False and st.session_state.download_clicked == False:
                #     st.error("Download the AIP SUP word document!")
                #     st.stop()
                st.html(
                    "<script>parent.window.location.reload()</script>",
                    unsafe_allow_javascript=True
                )

                # st.subheader("📋 Copy Data for Excel")
                # st.markdown("Click the copy button and paste the row directly into the `Crane Tracker` spreadsheet. ")
                # st.success("**TRACK THIS CRANE WITHIN EXCEL!**")

                # excel_ready_row = "\t".join([
                #         str(app_num), #CRANE REF NO.
                #         str(coords), #ROUNDED COORDS
                #         str(data.get("bearing", "")), #BEARING
                #         str(data.get("distance", "")), #DISTANCE
                #         str(data.get("height(ft)", "")), #HEIGHT
                #         str(data.get("mref", "N/A")), #MREF
                #         "", #KCQ (to fill in manually)
                #         "", #CIVIL REF (to fill in manually)
                #         str(NOTAM_start_datetime), #NOTAM START
                #         str(NOTAM_end_datetime), #NOTAM END
                #         str(data.get("notam_required", "")), #NOTAM REQUIRED (Yes/No)
                #         str(taken_by), #TAKEN BY
                #         str(data.get("aip_required", "")), #AIP REQUIRED (Yes/No)

                #         # If AIP is NOT required, leave start/end blank
                #         str(start_datetime) if data["aip_required"] != "No" else "", # AIP START
                #         str(end_datetime) if data["aip_required"] != "No" else ""    # AIP END
                        
                #     ])
                # st.code(excel_ready_row, language="text")


                # if st.button("🔄 Refresh page for New Entry"):
                #     # Native Streamlit component to inject the exact same JS line directly
                #     st.components.v1.html(
                #         "<script>parent.window.location.reload();</script>",
                #         height=0, 
                #         width=0
                #     )

                # st.button("Add data into database (WIP!!)", disabled=True)

                # st.divider()
                # st.markdown("...or manually download the files 👇")

                # st.subheader("📄 AIP SUP Word Document")
                # st.markdown("Save under `AWAIT SIGN > Batch X` *(whichever batch folder is the most current)*.")

                # if st.session_state.aip_not_required == False:
                #     st.info("**AIP REQUIRED, DOWNLOAD THE ZIP FILE INSTEAD!**")
                # else:
                #     st.error("**AIP NOT REQUIRED!**")

                # with open(output_filename, "rb") as f:
                #     st.download_button(
                #         label=f"📥 Download {output_filename}",
                #         data=f,
                #         file_name=output_filename,
                #         mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                #         disabled= st.session_state.aip_not_required
                #     )
                
                # st.subheader("🌍 Google Earth")
                # st.markdown("Save under the `Google Earth Archive` folder. WIP when we have access back to Google Earth!")
                
                # if st.session_state.aip_not_required == False:
                #     st.info("**AIP REQUIRED, DOWNLOAD THE ZIP FILE INSTEAD!**")
                # else:
                #     st.success("**AIP NOT REQUIRED, BUT DOWNLOAD THIS KML FILE!**")

                # with open(kml_file, "rb") as f:
                #     st.download_button(
                #         label=f"📥 Download KML file for Google Earth",
                #         data=f,
                #         file_name=kml_file,
                #         mime="application/vnd.google-earth.kml+xml"
                #     )

                # text_for_google_earth =  google_earth_data.get("text")
                # st.text_area("...or manually copy and paste into Google Earth 👇", value=text_for_google_earth, height=300)
                
                
                
else:
    st.error(f"❌ {data.get('Error')}")