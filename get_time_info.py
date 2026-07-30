import re
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

def process_period(period_str):
    """
    Parses the period str from the PDF into different formats.
    - YYMMDDHHMM (2606011600)
    - DD MMM YYYY (01 JUN 2026)
    - retrieves other relevant period information like true start, duration etc.

    Called in main.py, initializing the period information when the PDF text is uploaded into Upload_PDF.py

    """
    try:
        # split and clean period str e.g. 3rd Jul 2026 0000hrs to 2nd Mar 2027 2359hrs 
        parts = period_str.split(" to ")
        raw_start = parts[0].strip() #3rd Jul 2026 0000hrs
        raw_end = parts[1].strip() #2nd Mar 2027 2359hrs 
 
        # Removes suffix e.g. st, nd, rd and hrs
        def clean_date_str(s):
            s = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', s)

            s = s.replace("hrs", "")
            s = s.replace("January", "Jan")
            s = s.replace("February", "Feb")
            s = s.replace("March", "Mar")
            s = s.replace("April", "Apr")
            s = s.replace("May", "May")
            s = s.replace("June", "Jun")
            s = s.replace("July", "Jul")
            s = s.replace("August", "Aug")
            s = s.replace("September", "Sep")
            s = s.replace("October", "Oct")
            s = s.replace("November", "Nov")
            s = s.replace("December", "Dec")

            return s

        # Parse into YYYY-MM-DD HH:MM:SS e.g. 2027-03-02 23:59:00 
        fmt = "%d %b %Y %H%M"
        dt_start_sgt = datetime.strptime(clean_date_str(raw_start), fmt)
        dt_end_sgt = datetime.strptime(clean_date_str(raw_end), fmt)

        # Convert to Zulu
        dt_start_zulu = (dt_start_sgt - timedelta(hours=8)).replace(tzinfo=timezone.utc)
        dt_end_zulu = (dt_end_sgt - timedelta(hours=8)).replace(tzinfo=timezone.utc)
 
        # Calculate "Less than 2 months" flag
        now_zulu = datetime.now(timezone.utc)
        diff = dt_start_zulu - now_zulu
        start_in_less_than_2_months = dt_start_zulu < now_zulu + relativedelta(months=2)

        # Calculate duration
        duration = dt_end_sgt - dt_start_sgt
        days = duration.days

        return {
            #YYMMDDHHMM format e.g. 2607021600
            "start_dtg": dt_start_zulu.strftime("%y%m%d%H%M"), 
            "end_dtg": dt_end_zulu.strftime("%y%m%d%H%M"), 
            
            #DD MMM YYYY format e.g. 02 JUL 2026
            "start_v2": dt_start_zulu.strftime("%d %b %Y").upper(), 
            "end_v2": dt_end_zulu.strftime("%d %b %Y").upper(), 
            
            "month_year_end": dt_end_zulu.strftime("%b %Y").upper(), #Month of end date
            "year_end": dt_end_zulu.strftime("%Y"), #Year of end date

            "duration_days": days,
            "start_in_less_than_2_months": start_in_less_than_2_months,

            #true start date of crane
            "true_start(ddmmmyyyy)": dt_start_zulu.strftime("%d %b %Y").upper(), 
            "true_start(yymmddhhmm)": dt_start_zulu.strftime("%y%m%d%H%M")           
        }
    
    except Exception as e:
        return {
            "start_dtg": "Error",
            "end_dtg": "Error",

            "start_v2": "Error",
            "end_v2": "Error",
            
            "month_year_end": "Error", 
            "year_end": "Error", 

            "duration_days": "Error",
            "start_in_less_than_2_months": "Error",

            "true_start(ddmmmyyyy)": "Error", 
            "true_start(yymmddhhmm)": "Error"   
        }
    
def add_2_months(date_str):
    """
    Adds 2 months to date (yymmddhhmm format or ddmmmyyyy format). Used to add 2 mnths to AIP START when the add 2 mnths btn is pressed.

    Used in Upload_PDF.py
    
    """
    try:
        clean_str = date_str.strip()

        # For DDMMMYYYY format e.g. 03 JUL 2026
        if any(char.isalpha() for char in clean_str):
            parts = clean_str.split()

            if len(parts) == 3:
                day = parts[0]
                month = parts[1].capitalize() 
                year = parts[2]
                clean_std = f"{day} {month} {year}"
                
                # Add 2 months logic
                dt_obj = datetime.strptime(clean_std, "%d %b %Y")
                new_dt = dt_obj + relativedelta(months=2)

                # after adding 2 mnths, move date to end of the month (for ease of taking AIP/NOTAMs)
                return move_to_end_of_month(new_dt.strftime("%d %b %Y").upper())

        # For YYMMDDHHMM format e.g. 2607031600
        else:
            dt_obj = datetime.strptime(clean_str, "%y%m%d%H%M") 
            new_dt = dt_obj + relativedelta(months=2)
            return move_to_end_of_month(new_dt.strftime("%y%m%d%H%M"))

    except Exception as e:
        return f"Error: {str(e)}"

def move_to_end_of_month(date_str):
    """
    Moves date till end of the month (yymmddhhmm format or ddmmmyyyy format). For ease of taking AIP/NOTAMs.

    e.g. 15 JUL 2026 -> 31 JULY 2026

    Used by previous add_2_months function
    """

    if not date_str:
        return ""

    try:
        clean_str = date_str.strip()

        # DDMMMYYYY format e.g. 03 JUL 2026
        if any(char.isalpha() for char in clean_str):
            parts = clean_str.split()
            day, month, year = parts[0], parts[1].capitalize(), parts[2]
            dt_obj = datetime.strptime(f"{day} {month} {year}", "%d %b %Y")
            
            # Snap to last day
            last_day = dt_obj + relativedelta(day=31) 
            return last_day.strftime("%d %b %Y").upper()

        # YYMMDDHHMM format e.g. 2607031600
        else:
            dt_obj = datetime.strptime(clean_str, "%y%m%d%H%M")
            last_day_same_time = dt_obj + relativedelta(day=31)
            return last_day_same_time.strftime("%y%m%d%H%M")

    except Exception as e:
        return f"Error: {str(e)}"


def minus_1_min(zulu_str):
    """
    For NOTAM taking (NOTAM END DTG should be 1 min BEFORE start of AIP)

    Used in Upload_PDF.py when add 2 mnths btn is pressed. AIP Start date is added 2 mnths, then NOTAM END is calculated by minus-ing 1.

    e.g. 2606011600 -> 2606011559

    """
    try:
        dt_obj = datetime.strptime(zulu_str, "%y%m%d%H%M")
        minus_one_min_dt = dt_obj - timedelta(minutes=1)
        notam_end_time = minus_one_min_dt.strftime("%y%m%d%H%M")
        return notam_end_time
    
    except:
        return zulu_str
    
def plus_1_min(zulu_str):
    """
    For AIP taking (AIP START DTG should be 1 min AFTER start of AIP).

    Used in Upload_PDF.py when the Proceed btn is pressed. Ensures that the START DTG (start(yymmddhhmmz)) of AIP START is always 1 min ahead of NOTAM end.

    e.g. 2606011600 -> 2606011601
    
    """

    try:
        dt_obj = datetime.strptime(zulu_str, "%y%m%d%H%M")
        plus_one_min_dt = dt_obj + timedelta(minutes=1)
        aip_start_time = plus_one_min_dt.strftime("%y%m%d%H%M")
        return aip_start_time
    
    except:
        return zulu_str

# def validate_zulu_time(time_str):
#     """
#     Validates the yymmddhhmm format. Also ensures the year is within +/- 2 of the current year (to ensure the year of the crane start or and end isn't far from current year.)
#     Though, WIP to imrpove the logic eventually. 

#     The ddmmmyyyy format isn't validated (with no function to do so as well) because it's only after the user presses Proceed (and this date is validated), the ddmmmyyyy will generated.

#     Used in Upload_PDF.py and Manual_Entry.py when the Proceed btn is clicked.

#     """
#     # Basic length and digit check
#     if not time_str.isdigit() or len(time_str) != 10:
#         return False

#     try:
#         # Check the year 
#         current_year_short = int(datetime.now().strftime("%y")) 
#         input_year_short = int(time_str[:2])
        
#         # Check if input year is outside the [current-2, current+2] range
#         if abs(input_year_short - current_year_short) > 2:
#             return False

#         # Standard date validation
#         datetime.strptime(time_str, "%y%m%d%H%M")
#         return True
        
#     except ValueError:
#         return False

def convert_to_ddmmmyyyy(raw_date):
    """
    Converts yymmddhhmm format to ddmmmyyyy format. Used when AIP dates change and the ddmmmyyyy needs to be updated. This date format is specifically used for the AIP SUP word docs.

    Used in Upload_PDF.py and Manual_Entry.py
    
    """
    try:
        date_obj = datetime.strptime(raw_date, "%y%m%d%H%M")
        formatted_date = date_obj.strftime("%d %b %Y").upper()
        return formatted_date
    except:
        return "Error"

# def convert_end_to_mmyyyy(end_datetime):
#     """
#     Converts YYMMDDHHMM to MMYYYY (for tracking within Google Earth

#     Legacy code for naming the points for tracking within Google Earth.
    
#     """
#     try:
#         end_dt_obj = datetime.strptime(end_datetime.strip(), "%y%m%d%H%M").strftime("%b %Y").upper()
#         return end_dt_obj
#     except:
#         return "Error"

# period_str = "3rd Jul 2026 0000hrs to 2nd Mar 2027 2359hrs "
# process_period(period_str)