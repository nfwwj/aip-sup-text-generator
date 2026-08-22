import streamlit as st
from authenticate import remove_auth

remove_auth()

st.title("💻 Dev Notes")
st.set_page_config(page_title="Dev Notes", page_icon="💻")

st.sidebar.info("Made by Model. Model is super duper awesome.")

st.markdown("""
### THIS WEB APPLICATION IS STILL A WORK IN PROGRESS! ANY BUGS, FEEDBACK PLS LET ME KNOW.
### v1.2 patch notes 
**FIXED:**
1. Bold tag bug + no spacing bug in google earth 

**ADDED:**
1. Mandatory Crane application number
2. Amended warning to tell user to track crane in Excel now. (AIP not required still)
3. AIP required (Yes/No) for Excel tracking ("Yes" if crane starts after 2 months, "No" if crane <= 2 months, or <= 4 months but start within 2 months (as per flowchart, but KIV. Maybe just allow to take the AIP?) )
4. Add NOTAM Mref into google earth descriptions
5. If NOTAM is required for uploaded PDF, NOTAM Mref, NOTAM start and end input is mandatory.
6. NOTAM required (Yes/No) for Excel tracking ("Yes" if crane starts within 2 months, or duration <= 2 months or duration <= 4 months but start within 2 months)

---

### v1.3 patch notes 
**FIXED:**
1. Raw coordinates now mandatory for manual entry/uploaded PDF. Using rounded coordinates caused too much inaccuracy for range and bearing calculation.
            
---
            
### v1.4 patch notes 
**ADDED:**
1. "NOTAM taken by" field for both manual entry and uploaded PDF. Mandatory if NOTAM is required.
2. "Bearing/ Range" field for both manual entry and uploaded PDF. For easy reference when making the NOTAM. 
3. Manual copy and paste field for Google Earth KML data, due to some current limitations. 
4. Some code refactoring and cleaning up for better readability.
            
---
            
### v1.5 patch notes 
**FIXED:**
1. Fixed a bug where number of cranes were extracted incorrectly. "Application for 2x Mobile Cranes and 2x Luffer Cranes" would only extract 2 cranes instead of 4 cranes due to the "and" in between. Regex pattern has been updated.
2. Amended AIP SUP word doc template. Now it should only contain 2 pages, instead of the previous 3 pages.
3. Fixed a bug where the AIP start date/ datetime would not update when user manually adds the NOTAM end date into the upload PDF page.

**ADDED:**
1. App will now display which specific fields had errors during extraction. The app will still stop running when an error is encountered.
            
---
            
### v1.6 patch notes
**ADDED:**
1. NOTAM start/end datetime is now automatically populated if the crane duration is <= 2 months as AIP is not required. 
2. The app will now warn if the crane is outside of PLAB CTR.
            
---
            
### v1.7 patch notes 
**ADDED:**
1. There is now an option to download a ZIP file containing both the AIP SUP Word Document and the KML file together.
2. Added a helpful tutorial page
3. Download buttons now automatically disabled if they're not required e.g. If there isn't a requirement for an AIP, the download button will be disabled.
4. Added a section that shows NOTAM Text, Cord, and Upper Limit for easy reference.
5. Button to refresh website (as INet blocks more than 1 download on a webpage, unless the page is refreshed)
                                
**FIXED:**
1. Regex patterns have been updated to accept full month names as well e.g. "April" instead of just "Apr", though the crane PDF should've come with the 3 letter month format by default.
2. Formulas to calculate Bearing and Range has been updated. Previously, 23.4 was interpreted as 4 instead of 40, resulting in some deviation. Verified with 3rd party website, but there is still a variation of 0.01 (WIP).      
            
---
            
### v1.8 patch notes 
            
**ADDED:**
1. Established a connection to an external database. There is now an option to add the crane record into the external database. Excel is no longer required.
2. There is now a built-in map showing the location of the cranes. The data is retrieved from the database. Google Earth is no longer required.
3. No longer a requirement to download the crane PDF. The app now accepts copied and pasted text from the crane PDF.
4. No longer a requirement to download the AIP SUP Word Document. The app now generates the AIP SUP Word Document in the backend automatically.
            
**FIXED:**
1. Fixed a bug where manually inputting NOTAM start/end dates into Upload PDF didn't update the field, and info box when the Proceed button is clicked.
2. Fixed a bug where web page would crash when Period within the crane PDF included an asterisk.             
---
            
### v1.9 patch notes
            
**ADDED:**
1. Added search bar in Map to search for crane records by application number.
2. Extended delete feature into the Map page.
3. Added edit feature for crane records.
4. Added a button to apply the "AIP required" checkbox to all crane records that require it (for AIP IC usage).
5. Some code refactoring.

---

### v2.0 patch notes
            
**FIXED:**
1. Edit crane feature now checks whether date values are valid (Good job to Shawn for breaking it)
2. Cranes, and the generated AIP SUP word docs, are now sorted by AIP start date, earliest first (for AIP IC usage).

---

### v2.1 patch notes
            
**ADDED:**
1. Some optimization relating to fetching of data. Loading times for most pages should be decreased.
""")



st.info("""
### WIP FEATURES
        
1. Add a way to track cranes of interest
2. Streamline NOTAM taking process (e.g. Not required to immediately take the NOTAM. NOTAM can be taken later, stored in the database.)
""")
