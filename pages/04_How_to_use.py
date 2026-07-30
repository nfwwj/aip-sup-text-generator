import streamlit as st
from authenticate import remove_auth

remove_auth()

st.title("💡 How to Use")
st.set_page_config(page_title="How to Use", page_icon="💡")

st.sidebar.info("Made by Model. Model is super duper awesome.")

st.markdown("""
### A step by step user guide on how to use this web application. 

### 1. ⏬ Data Entry & Extraction

Copy all the text (CTRL + A, CTRL + C) from the crane PDF in Outlook and paste into the text box.
            
This web application may not be perfect, and you may encounter some errors during the data extraction process. Some common errors include:
""")

st.error(f"❌ Something went wrong with extracting the following fields: XXX, XXX, XXX. Please ensure the PDF is correctly formatted. Else, use manual data entry.")
st.markdown("This error is due to the formatting of the crane PDF has changed, or is formatted wrongly. Depending on which fields are affected, you may need to manaully edit the text you copied. A common mistake in the PDF includes:")

st.markdown("* Improperly formatted period information.")
st.warning("2nd **Ju1** 2026 0000hrs to **28nd** May 2026 2359hrs")


st.error("Something went wrong in extract_text_from_pdf.py")
st.markdown("This error is likely due to a bug in the code. Please let whoever's in charge of this web app know, with the PDF you used!")

st.markdown("---")

st.markdown("""
### 2. 🛠️ AIP & NOTAM Requirements
The app will automatically determine the AIP and NOTAM requirements based on the crane's start date and duration. Follow the instructions provided. Note that there is no longer a requirement to download and save the AIP SUP Word Document. Do continue to take the NOTAM if required. You will not be able to proceed to the next step if the NOTAM requirement is not met.
""")

st.success("✅ No requirement to take a NOTAM.")

st.markdown("No requirement to take a NOTAM. Save the crane record into the database.")

st.warning(f"⚠️ Duration is <= 2 months. Recommend taking 1x NOTAM instead.  **No requirement for AIP.**")

st.markdown("Take 1x NOTAM. Save the crane record into the database.")

st.warning(f"⚠️ NOTAM starts within 2 months and Duration is <= 4 months. Recommend taking 2x NOTAM instead. **No requirement for AIP.**")

st.markdown("Take 2x NOTAM (half-half). Save the crane record into the database.")

st.warning("⚠️ Crane starts within 2 months. Recommend taking 1x 2 month NOTAM first. **Add 2 months for the start date of AIP! Remember to download the AIP SUP word doc.**")

st.markdown("Take 1x **interim** NOTAM. Press the `Add 2 Months` button to automatically add 2 months to the start date of the AIP. Save the crane record into the database.")

st.markdown("Ensure every crane is tracked within the database!")
st.markdown("---")   

st.markdown("""              
### 3. 🔍 Data Validation
There are built in data validation and formatting checks. Ensure fields marked with an asterisk (*) are filled out correctly. Follow the instructions provided for any errors or warnings. Some examples include:
""")

st.error("⚠️ A NOTAM is required for this crane operation. Please take the NOTAM and provide the start and end datetimes for the NOTAM.")
st.markdown("The app has determined that a NOTAM is required based on the crane's start date and duration. Please take the NOTAM and provide the start and end datetimes for the NOTAM.")

st.markdown("---")

st.markdown("""
### 4. ✅ Remember to save the crane record into the database!
""")
