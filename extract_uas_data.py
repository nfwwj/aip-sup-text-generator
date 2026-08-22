# import re


# def extract_uas_data(text):
#     """Calls individual functions that use regex patterns to extract UAS permit
#     data from the raw PDF text. Returns one dict per activity date/time listed
#     in Table 1, since a single permit can cover multiple activities.
#     """
#     try:
#         application_num = extract_application_num_from_pdf(text)
#         permit_no = extract_permit_no_from_pdf(text)
#         activities = extract_activities_from_pdf(text)

#         return [
#             {
#                 "application_num": application_num,
#                 "permit_no": permit_no,
#                 "activity_date": activity["activity_date"],
#                 "activity_time": activity["activity_time"],
#                 "altitude_ft": activity["altitude_ft"],
#                 "full_text": text.strip(),
#             }
#             for activity in activities
#         ]

#     except Exception as e:
#         return "Error"


# def extract_application_num_from_pdf(text):
#     try:
#         pattern = r"Application No\.\s*:\s*(.+)"
#         return re.search(pattern, text).group(1).strip()
#     except Exception:
#         return "Error"


# def extract_permit_no_from_pdf(text):
#     try:
#         pattern = r"Permit No\.\s*:\s*(.+)"
#         return re.search(pattern, text).group(1).strip()
#     except Exception:
#         return "Error"


# def extract_activities_from_pdf(text):
#     """Parses the Table 1 block into a list of {activity_date, activity_time,
#     altitude_ft} dicts. The altitude appears on its own line, once, and applies
#     to every date/time line preceding it (back to the last altitude line, or
#     the start of the table).
#     """
#     try:
#         lines = text.splitlines()

#         start_idx = None
#         end_idx = None
#         for i, line in enumerate(lines):
#             if start_idx is None and re.search(
#                 r"Activity Date\s+Activity Time\s+Operating Altitude", line
#             ):
#                 start_idx = i + 1
#             elif start_idx is not None and re.match(r"Table 1\.", line.strip()):
#                 end_idx = i
#                 break

#         if start_idx is None or end_idx is None:
#             raise ValueError("Could not locate Table 1 boundaries")

#         table_lines = [ln.strip() for ln in lines[start_idx:end_idx] if ln.strip()]

#         date_time_pattern = re.compile(
#             r"^(?P<date>.+?\d{4}(?:\s+to\s+.+?\d{4})?)\s+"
#             r"(?P<time>\d{4}LT\s+to\s+\d{4}LT)$"
#         )
#         altitude_pattern = re.compile(r"(\d+)\s*ft", re.IGNORECASE)

#         pending_rows = []  # rows waiting for the next altitude line
#         activities = []

#         for line in table_lines:
#             date_time_match = date_time_pattern.match(line)
#             if date_time_match:
#                 pending_rows.append(
#                     {
#                         "activity_date": date_time_match.group("date").strip(),
#                         "activity_time": date_time_match.group("time").strip(),
#                     }
#                 )
#                 continue

#             altitude_match = altitude_pattern.search(line)
#             if altitude_match and pending_rows:
#                 altitude_ft = int(altitude_match.group(1))
#                 for row in pending_rows:
#                     row["altitude_ft"] = altitude_ft
#                     activities.append(row)
#                 pending_rows = []

#         if pending_rows:
#             raise ValueError("Activity date/time line(s) found with no matching altitude")

#         if not activities:
#             raise ValueError("No activities parsed from Table 1")

#         return activities

#     except Exception as e:
#         return "Error"



