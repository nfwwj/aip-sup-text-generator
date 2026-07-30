import re
import math
from format_coords import format_coords_custom
import streamlit as st

def extract_pdf_data(text):
    """Calls individual functions that uses regex pattern to extract the text from the PDF.
    Some fields are returned raw, and some are sent into other functions to get formatted.
    """
    try:
        return {
            "ref_raw_coords": extract_coord_from_pdf(text).get("raw_coords"),
            "ref_height(m)": extract_height_from_pdf(text).get("ref_height(m)"),
            "ref_period": extract_period_from_pdf(text),
            "ref_application_num": extract_application_num_from_pdf(text),
            "ref_num_cranes": extract_num_cranes_from_pdf(text).get("ref_num_cranes"),

            "raw_coordinates": extract_coord_from_pdf(text).get("raw_coordinates"),
            "rounded_coordinates": extract_coord_from_pdf(text).get("rounded_coordinates"),
            "rounded_coord_for_notam": extract_coord_from_pdf(text).get("rounded_coord_for_notam"),
            "height(ft)": extract_height_from_pdf(text).get("height(ft)"),
            "period": extract_period_from_pdf(text),
            "application_num" : extract_application_num_from_pdf(text),
            "num_cranes" : extract_num_cranes_from_pdf(text).get("num_cranes")
            }
    
    except Exception as e:
        return "Error"
        
        
def extract_coord_from_pdf(text):
    try:
        coord_pattern = r"(\d+°\d+'[\d.]+\"[NSEW])\s+(\d+°\d+'[\d.]+\"[NSEW])"
        raw_coords = re.search(coord_pattern, text).group(0)
        formatted_coords = format_coords_custom(raw_coords) #from format_coords.py
        return {"raw_coords": raw_coords,
            "raw_coordinates": formatted_coords.get("raw_coordinates", "Error"),
            "rounded_coordinates": formatted_coords.get("rounded_coordinates", "Error"),
            "rounded_coord_for_notam": formatted_coords.get("rounded_coord_for_notam", "Error")}
    
    except Exception as e:
        return {"raw_coords": "Error",
                "raw_coordinates": "Error",
                "rounded_coordinates": "Error",
                "rounded_coord_for_notam": "Error"}
    
def extract_height_from_pdf(text):
    try:
        height_pattern = r"Max Height\s*:\s*(\d+)m\s*AMSL"
        ref_height = re.search(height_pattern, text).group(1)
        height_ft = math.ceil(int(ref_height) * 3.28084)
        return {"height(ft)": height_ft, "ref_height(m)": ref_height}
    except Exception as e:
        return {"height(ft)": "Error", "ref_height(m)": "Error"}

def extract_period_from_pdf(text):
    try:
        period_pattern = r"Period\s*:\s*(.*)"
        period = re.search(period_pattern, text).group(1)
        period = period.strip().rstrip("*").strip()
        return period
    except Exception as e:
        return "Error"

def extract_application_num_from_pdf(text):
    try:
        application_num_pattern = r"Ref No\.:\s*([^/]+)" 
        application_num = re.search(application_num_pattern, text).group(1).strip()
        return application_num
    except Exception as e:
        return "Error"
    
def extract_num_cranes_from_pdf(text):
    try:
        num_cranes_pattern = r"Application for.*?(?=\.|\n|$)"
        num_cranes_text = re.search(num_cranes_pattern, text, re.IGNORECASE | re.DOTALL).group(0)
        crane_counts = re.findall(r"(\d+)\s*x", num_cranes_text)
        num_cranes = sum(int(c) for c in crane_counts)
        return {"num_cranes": num_cranes, "ref_num_cranes": num_cranes_text}
    except Exception as e:
        return {"num_cranes": "Error", "ref_num_cranes": "Error"}

def mask_phone_numbers(text):
    phone_pattern = r"\b([689]\d{3})-?(\d{4})\b"

    def mask(match):
        try:
            first_half = match.group(1)
            second_half = match.group(2)

            # Fetch the mask value from st.secrets (cast to int just in case it's read as a string)
            secret_mask = int(st.secrets.mask)

            # Convert second half to integer, add the secret, and wrap around 10000
            new_second_half = (int(second_half) + secret_mask) % 10000

            # Check if original match had a hyphen to preserve the exact style
            if "-" in match.group(0):
                return f"{first_half}-{new_second_half:04d}"
            else:
                return f"{first_half}{new_second_half:04d}"

        except Exception:
            # If an individual number calculation breaks, return N/A for that match
            return "N/A"

    try:
        # Check if text is a valid string before running regex
        if not isinstance(text, str) or text.strip() == "":
            return "N/A"

        return re.sub(phone_pattern, mask, text)

    except Exception:
        # Global fallback if the regex engine crashes
        return "N/A"