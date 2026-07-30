import streamlit as st
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import re

def validate_zulu_time(time_str):
    """
    Validates the yymmddhhmm format. Also ensures the year is within +/- 2 of the current year (to ensure the year of the crane start or and end isn't far from current year.)
    Though, WIP to imrpove the logic eventually. 

    The ddmmmyyyy format isn't validated (with no function to do so as well) because it's only after the user presses Proceed (and this date is validated), the ddmmmyyyy will generated.

    Used in Upload_PDF.py and Manual_Entry.py when the Proceed btn is clicked.

    """
    # Basic length and digit check
    if not time_str.isdigit() or len(time_str) != 10:
        return False

    try:
        # Check the year 
        current_year_short = int(datetime.now().strftime("%y")) 
        input_year_short = int(time_str[:2])
        
        # Check if input year is outside the [current-2, current+2] range
        if abs(input_year_short - current_year_short) > 2:
            return False

        # Standard date validation
        datetime.strptime(time_str, "%y%m%d%H%M")
        return True
        
    except ValueError:
        return False

def validate_coord(coords_str):
    pattern = r"^\d{4}\d+\.\d+N\s\d{5}\d+\.\d+E$"
    return bool(re.match(pattern, coords_str))

def validate_data(data,require_take_notam):
    coords = str(data.get("coordinates", "")).strip()
    start_datetime = str(data.get("true_start", "")).strip()
    end_datetime = str(data.get("true_end", "")).strip()
    notam_start = str(data.get("notam_start", "")).strip()
    notam_end = str(data.get("notam_end", "")).strip()
    mref = str(data.get("mref", "")).strip()
    taken_by = str(data.get("taken_by", "")).strip()
    app_num = str(data.get("application_num", "")).strip()
    height = data.get("height(ft)", 0)
    NOTAM_start_datetime = data.get("NOTAM_start_datetime","").strip()
    NOTAM_end_datetime = data.get("NOTAM_end_datetime","").strip()
    if app_num.strip() == "":
        return {"error": "⚠️ Missing application number!"}
    
    if not validate_coord(coords):
        return {"error": "⚠️ Invalid Coordinate Format! Must be: 012124.3N 1035558.1E (DECIMAL and SPACE)"}

    # 3. AIP DateTime Check
    if not validate_zulu_time(start_datetime) or not validate_zulu_time(end_datetime):
        return {"error": "⚠️ Invalid AIP DateTime Format! AIP Start/End Datetime must be in YYMMDDHHMM format!"}
    
    if notam_start != "" or notam_end != "":
        if not validate_zulu_time(notam_start) or not validate_zulu_time(notam_end):
            return {"error": "⚠️ Invalid NOTAM DateTime Format! NOTAM Start/End Datetime must be in YYMMDDHHMM format!"}

    if require_take_notam == True:
        if NOTAM_start_datetime == "" or NOTAM_end_datetime == "":
            return {"error": "⚠️ A NOTAM is required for this crane operation. Please take the NOTAM and provide the start and end datetimes for the NOTAM."}

        
    if require_take_notam == True:
        if mref == "":
            return {"error": "⚠️ A NOTAM is required for this crane operation. Please take the NOTAM and provide the Mref."}
        
        if taken_by == "":
            return {"error": "⚠️ A NOTAM is required for this crane operation. Please take the NOTAM and fill in the Taken By field."}
        
    else:
        if NOTAM_start_datetime.strip() != "" or NOTAM_end_datetime.strip() != "":
            if mref.strip() == "":
                return {"error": "⚠️ You indicated that a NOTAM is required for this crane operation. Please take the NOTAM and provide the Mref. Else, remove the NOTAM dates."}
            if taken_by.strip() == "":
                return {"error": "⚠️ You indicated that a NOTAM is required for this crane operation. Please take the NOTAM and provide the Mref. Else, remove the NOTAM dates."}

    if mref != "":
        if not mref.isdigit():
            return {"error": "⚠️ Ensure Mref is written correctly!"}
        
        if len(mref) != 5:
            return {"error": "⚠️ Mref must be exactly 5 digits. Ensure Mref is written correctly."}

    if app_num == "":
        return {"error": "⚠️ Application number cannot be empty!"}
    
    if int(height) == int(data.get("ref_height(m)")):
        return {"error": "⚠️ Ensure height is in feet, not meters!"}

    return {"success":"success!"}
       