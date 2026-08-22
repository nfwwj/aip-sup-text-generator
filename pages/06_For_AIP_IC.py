from validate_data import validate_zulu_time
from get_time_info import convert_to_ddmmmyyyy, plus_1_min
import streamlit as st
import pandas as pd
from datetime import datetime
from authenticate import check_password
import zipfile
import io
from create_word_doc import edit_existing_doc
from dotenv import load_dotenv
from fetch_crane_data import fetch_crane_records, supabase

load_dotenv()
if "updated_success" not in st.session_state:
    st.session_state.updated_success = 0
if "edit_record" not in st.session_state:
    st.session_state.edit_record = None
if "confirm_bulk_update" not in st.session_state:
    st.session_state.confirm_bulk_update = False

if check_password():

    if "just_purged_count" not in st.session_state:
        st.session_state.just_purged_count = 0
    if "deleted_app_success" not in st.session_state:
        st.session_state.deleted_app_success = False

    st.sidebar.info("Made by Model. Model is super duper awesome.")
    
    st.set_page_config(page_title="Admin Controls", page_icon="⚙️")
    st.title("⚙️ Administrative Control for Crane AIP IC")
    st.markdown("""
        This control panel allows you to manage crane records within the database and track active AIP allocations.
        Available Operations:
    * **Perform CRUD** (Create, Read, Update, Delete) on crane records.
    * **Database Maintenance:** Please periodically purge expired crane records to optimize and lower database storage usage.
                
        This page is only intended for the AIP IC! This page will be locked after exiting.
    """)

    st.divider()
    column_order = [
            "application_num",
            "mref",
            "ui_status",          
            "num_cranes",
            "bearing",
            "distance",
            "height(ft)",         
            "coordinates",
            "aip_start",
            "aip_end",
            # "kcq",
            # "civil_ref",
            "true_start",
            "true_end",
            "notam_start",
            "notam_end",
            "notam_required",
            "taken_by",
            "aip_required",
             "status"           
        ]
    
    def parse_crane_date(date_str):
        if not date_str:
            return None
        date_str = str(date_str).strip()
        # DDMMMYYYY
        try:
            return datetime.strptime(date_str, "%d %b %Y")
        except:
            pass
            
        return None

    def display_crane_data(all_records, type):
        try:
            df = pd.DataFrame(all_records)

            if not df.empty:
                if type == "X":
                    # For displaying every crane records where aip_required is No
                    df = df[df["aip_required"] == "No"].reset_index(drop=True)
                else:
                    df = df[(df["status"] == type) & (df["aip_required"] == "Yes")].reset_index(drop=True)

            if not df.empty:
                df['dtime'] = pd.to_datetime(df['aip_start'], format='%y%m%d%H%M')
                df = df.sort_values(by='dtime',ascending=True)
                df = df.reset_index(drop=True)

                if type == "X":
                    st.data_editor(df,disabled=[col for col in df.columns])
                    return
                 
                else: 
                    apply_checkbox(df,type)
            else:
                st.info("Database is empty.")

        except Exception as e:
            st.error(f"Something went wrong: {e}")

    def apply_checkbox(df,type):
        '''Adds checkbox to indicate whether AIP taken or not. Sends a PUT request
        to update the crane record. Honestly i have no idea what is going on here.'''

        df['ui_status'] = df['status'].apply(lambda x: True if x == 'Y' else False)

        editor_key = f"ledger_view_{type}"

        st.data_editor(
            df[column_order],
            column_config={
                "ui_status": st.column_config.CheckboxColumn(
                    "AIP Sent?",
                    default=False,
                )
            },
            disabled=[col for col in df.columns if col != "ui_status"], # LOCK everything except the checkbox
            hide_index=True,
            key= editor_key
        )

       
        if editor_key in st.session_state and st.session_state[editor_key].get("edited_rows"):
            edited_rows = st.session_state[editor_key]["edited_rows"]
            
            for idx_str, changes in edited_rows.items():
                if "ui_status" in changes:
                    # Look up corresponding row ID from original dataframe index position
                    row_index = int(idx_str)
                    db_id = int(df.iloc[row_index]['id'])
                    new_status = "Y" if changes["ui_status"] else "N"
                    supabase.table("crane_records").update({"status": new_status}).eq("id", db_id).execute()

            fetch_crane_records.clear()
            st.rerun()
    def apply_checkbox_to_all():
        try:
            response = supabase.table("crane_records").update({"status": "Y"}).eq("status","N").eq("aip_required","Yes").execute()
            fetch_crane_records.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
        

    def delete_expired_records():
        try:
            response = supabase.table("crane_records").select("*").execute()

            df = pd.DataFrame(response.data)  
            
            if df.empty: 
                st.info("Database is empty.")

            else:
                now = datetime.now()
                purged_count = 0
                
                for index,row in df.iterrows():
                    converted_dt = parse_crane_date(row['true_end'])

                    if converted_dt and converted_dt < now:
                        supabase.table("crane_records").delete().eq("id", int(row['id'])).execute()
                        purged_count += 1
                
                if purged_count > 0:
                    fetch_crane_records.clear()
                    st.session_state.just_purged_count = purged_count
                    st.rerun()
                else:
                    st.warning("No expired crane records found.")

        except Exception as e:
            st.error(f"Something went wrong: {e}")

    def delete_crane_record(app_num):
        try:
            response = supabase.table("crane_records").delete().eq("application_num", app_num).execute()

            if response.data and len(response.data) > 0:
                fetch_crane_records.clear()
                st.session_state.deleted_app_success = True
                st.rerun()
            else:
                st.session_state.deleted_app_success = False
                st.error(f"{app_num} not found!")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

    def generate_docs():
        try:
            response = supabase.table("crane_records").select("*").eq("status","N").eq("aip_required","Yes").execute()
            records = response.data

            # Create a ZIP file in memory
            zip_buffer = io.BytesIO()
            failed = []

            
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for record in records:
                    try:
                        doc_data = {
                            "application_num": record.get("application_num", ""),
                            "num_cranes": record.get("num_cranes", 1),
                            "height(ft)": record.get("height(ft)", ""),
                            "start(yymmddhhmmz)": record.get("aip_start", ""),
                            "end(yymmddhhmmz)": record.get("aip_end", ""),
                            "start(ddmmmyyyy)": convert_to_ddmmmyyyy(record.get("aip_start","")),
                            "end(ddmmmyyyy)": convert_to_ddmmmyyyy(record.get("aip_end","")),
                            "rounded_coordinates": record.get("rounded_coordinates", ""),
                            "bearing": record.get("bearing", ""),
                            "distance": record.get("distance", ""),
                        }

                        output_filename = edit_existing_doc(doc_data)

                        # output_filename can be a string (successful) or a dict (error)
                        if isinstance(output_filename, dict):
                            failed.append(f"{record.get('application_num', '?')}: {output_filename['error']}")
                            continue
                                
                        with open(output_filename, "rb") as f:
                            zf.write(output_filename, arcname=output_filename)

                    except Exception as e:
                        failed.append(f"{record.get('application_num', '?')}: {e}")
                        continue

            
            # Required to read the ZIP file from memory
            zip_buffer.seek(0)

            st.download_button(
                label=f"📥 Download ZIP ({len(records) - len(failed)} docs)",
                data=zip_buffer,
                file_name="AIP_SUP_Batch.zip",
                mime="application/zip"
            )

            if failed:
                st.warning(f"⚠️ {len(failed)} doc(s) failed to generate:")
                for f in failed:
                    st.caption(f)

        except Exception as e:
            st.error(f"Something went wrong: {e}")
    def render_edit_form(record):
        def safe_str(value):
            if value is None:
                return ""
            return str(value)

        with st.form("edit_record_form"):
            col1, col2 = st.columns(2)
            with col1:
                app_num = st.text_input("Application Number", value=safe_str(record.get("application_num")), disabled=True)
                mref = st.text_input("Mref", value=safe_str(record.get("mref")),max_chars=5)
                taken_by = st.text_input("Taken By", value=safe_str(record.get("taken_by")))
                num_cranes = st.number_input("Number of Cranes", value=int(record.get("num_cranes") or 1), min_value=1, disabled= True)
                height = st.text_input("Height (ft)", value=safe_str(record.get("height(ft)")), disabled= True)
                
                coordinates = st.text_input("Coordinates", value=safe_str(record.get("coordinates")), disabled= True)
                bearing = st.text_input("Bearing", value=safe_str(record.get("bearing")), disabled= True) #will be recalculated if changed
                distance = st.text_input("Distance", value=safe_str(record.get("distance")), disabled= True)#will be recalculated if changed
            with col2:
                # kcq = st.text_input("KCQ", value=safe_str(record.get("kcq")), disabled=True)
                # civil_ref = st.text_input("Civil Ref", value=safe_str(record.get("civil_ref")), disabled=True)
                # true_start = st.text_input("True Start", value=safe_str(record.get("true_start")))
                # true_end = st.text_input("True End", value=safe_str(record.get("true_end")))
                notam_start = st.text_input("NOTAM Start", value=safe_str(record.get("notam_start")))
                notam_end = st.text_input("NOTAM End", value=safe_str(record.get("notam_end")))
                aip_start = st.text_input("AIP Start", value=safe_str(record.get("aip_start")), disabled=True) #1 min after notam end
                aip_end = st.text_input("AIP End", value=safe_str(record.get("aip_end")), disabled=True)

            update_btn = st.form_submit_button("💾 Update Record")

        if update_btn:      
            try:
                if not validate_zulu_time(notam_start) or not validate_zulu_time(notam_end):
                    st.error("⚠️ Invalid NOTAM start/end datetime format!")
                    st.stop()

                update_data = {
                    "mref" : mref,
                    "taken_by" : taken_by,
                    "notam_start" : notam_start,
                    "notam_end" : notam_end,
                          
                }
                if aip_end != "":
                    aip_start = plus_1_min(notam_end)
                    update_data["aip_start"] = aip_start


                supabase.table("crane_records").update(update_data).eq("id", record["id"]).execute()
                fetch_crane_records.clear()
                st.success(f"✅ Record {app_num} updated successfully!")
                st.session_state.edit_record = None
                st.session_state.updated_success = 1
                st.rerun() 

            except Exception as e:
                st.error(f"Something went wrong: {e}")

    try:
        all_records = fetch_crane_records()

        st.subheader("🏗️❌ Crane Records (status N)")
        st.markdown("Crane records that require AIP (aip_required is 'Yes') and status is N (AIP not sent).")

        display_crane_data(all_records, "N")
        
        if st.button("📥 Generate ZIP file of AIP SUP Documents"):
            generate_docs()

        
        if st.button("✅ Mark all as AIP Sent"):
            st.session_state.confirm_bulk_update = True
            st.rerun()
        if st.session_state.confirm_bulk_update:
            st.warning("⚠️ Are you sure you want to mark all records as AIP Sent? This action cannot be undone.")
            # col1, col2 = st.columns(2, gap="small")
            # with col1:
            if st.button("Proceed", type="primary"):
                apply_checkbox_to_all()
                st.session_state.confirm_bulk_update = False
                st.rerun()
            # with col2:
            if st.button("Cancel"):
                st.session_state.confirm_bulk_update = False
                st.rerun()

        st.divider()

        st.subheader("🔥 Delete expired crane records")
        st.markdown("Remove expired cranes where their end dates < today's date. Referenced from true_end.")    
        
        if st.button("Delete Expired Cranes"):
            delete_expired_records()
        
        if st.session_state.just_purged_count > 0:
            st.success(f"Successfully deleted {st.session_state.just_purged_count} expired records.")
            st.session_state.just_purged_count = 0 

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

        st.subheader("🏗️✅ Crane Records (status Y)")
        st.markdown("Crane records that require AIP (aip_required is 'Yes') and status is Y (AIP sent).")
        
        display_crane_data(all_records, "Y")

        st.divider()

        st.subheader("🏗️🆗 Crane Records (AIP not required)")
        st.markdown("Crane records that **DO NOT** require AIP (aip_required is 'No').")

        display_crane_data(all_records, "X")

        st.divider()

        st.subheader("✏️ Edit Crane Record")
        st.warning("⚠️ There isn't an option to edit specific crane details like coordinates, height and number of cranes as these rely on the regex pattern as the strict source of truth. So, if they're wrong, the regex pattern is wrong, so you should probably consult the developer.")
        st.markdown("Enter Crane Application No. to edit:")
        app_num_input = st.text_input("Application Number:")
        search_btn = st.button("Fetch Record")

        if search_btn:
            app_num_to_search = app_num_input.strip()
            if app_num_to_search == "":
                st.warning("Input an application number to edit!")
            else:
                response = supabase.table("crane_records").select("*").eq("application_num", app_num_input.strip()).execute()
                if response.data:
                    st.session_state.edit_record = response.data[0] # Save the dictionary here
                else:
                    st.error(f"No record found.")
                    st.session_state.edit_record = None

        if st.session_state.edit_record:
            render_edit_form(st.session_state.edit_record)

        if st.session_state.updated_success == 1:
            st.success("Crane record has been successfully updated.")
            st.session_state.updated_success = 0
                

    except Exception as e:
        st.error(f"Something went wrong. {e}")


