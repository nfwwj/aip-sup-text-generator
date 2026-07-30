import pypdf
from extract_text_from_pdf import extract_pdf_data, mask_phone_numbers
from get_bearing_and_dist import get_location_info, get_upper_FL
from get_time_info import process_period
from get_bearing_and_dist import within_5_km

num2words1 = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', \
            6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten', \
            11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', \
            15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen', 19: 'Nineteen'}

# def main(file_path):

def main(full_text):
    """First file that gets run by Upload_PDF.py to 
    1. Call extract_pdf_data() to extract the raw text from the PDF
    2. Call individual functions to processes the raw text into new calculated and formatted fields
    
    
    """
    try:
        # file = pypdf.PdfReader(file_path)
        # page = file.pages[0].extract_text()

        # full_text = ""
        # for p in file.pages:
        #     extracted = p.extract_text()
        #     if extracted:
        #         full_text += extracted + "\n"

        data = extract_pdf_data(full_text)

        if data == "Error": #if smth within the function itself goes wrong
            raise Exception("Something went wrong in extract_text_from_pdf.py")

        location_information = get_location_info(data.get("raw_coordinates")) # Gets bearing and distance information
        
        period_information = process_period(data.get("period")) # Gets start and end dates, along with duration  

        num_cranes_value = data.get("num_cranes")
        num_temp = num2words1.get(num_cranes_value)

        if num_temp is None:
            num_temp = str(num_cranes_value)
        else:
            num_temp = num_temp.upper()

        if isinstance(num_cranes_value, int) and num_cranes_value > 1:
            crane_plural_temp = "CRANES"
        else:
            crane_plural_temp = "CRANE"

        upper_FL = get_upper_FL(data.get("height(ft)"))

        full_text = mask_phone_numbers(full_text)
        
        return {
            "application_num": data.get("application_num"),
            "num_cranes": data.get("num_cranes"),
            "raw_coordinates": data.get("raw_coordinates"),
            "rounded_coordinates": data.get("rounded_coordinates"),
            "rounded_coord_for_notam": data.get("rounded_coord_for_notam"),
            "height(ft)": data.get("height(ft)"),
            "period": data.get("period"),

            "distance": location_information.get("distance"),
            "bearing": location_information.get("bearing"),
            "lat": location_information.get("lat"),
            "long": location_information.get("long"),
            "upper_FL": upper_FL,

            "start(yyyymmddhhmmz)": period_information.get("start_dtg", ""),
            "end(yyyymmddhhmmz)": period_information.get("end_dtg", ""),
            "start(ddmmmyyyy)": period_information.get("start_v2", ""),
            "end(ddmmmyyyy)": period_information.get("end_v2", ""),
            "duration_days": period_information.get("duration_days", ""),
            "start_in_less_than_2_months": period_information.get("start_in_less_than_2_months", ""),
            "month_year_end": period_information.get("month_year_end"),
            "true_start(ddmmmyyyy)": period_information.get("true_start(ddmmmyyyy)"),
            "true_start(yymmddhhmm)": period_information.get("true_start(yymmddhhmm)"),

            "full_text": full_text.strip(),
            "ref_raw_coords": data.get("ref_raw_coords", ""),
            "ref_height(m)": data.get("ref_height(m)", ""),
            "ref_period": data.get("ref_period", ""),
            "ref_application_num": data.get("ref_application_num", ""),
            "ref_num_cranes": data.get("ref_num_cranes", ""),

            "num_temp": num_temp,
            "crane_plural_temp": crane_plural_temp
        }
    except Exception as e:
        return {"Error": f"{e}"}



# print(main("test.pdf"))