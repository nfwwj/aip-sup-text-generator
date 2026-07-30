import re
import math

def format_coords_custom(raw_coords):
    '''Removes all symbols for AIP SUP text e.g. 1°20'43.3"N 103°53'18.1"E -> 012043.3N 1035318.1E'''
    try:
        dms_parse = r"(\d+)°(\d+)'([\d.]+)\"([NSEW])"

        # returns [('1', '20', '43.3', 'N'), ('103', '53', '18.1', 'E')]
        matches = re.findall(dms_parse, raw_coords) 
        
        # If doesn't return 2 matches (lat and long), raise an error
        if len(matches) >= 2:
            raw_results = []

            for i, match in enumerate(matches):
                deg, mnt, sec, direction = match
                deg, mnt = int(deg), int(mnt)

                # Formatting logic
                pad = 3 if i == 1 else 2
                raw_results.append(f"{deg:0{pad}d}{mnt:02d}{sec}{direction}")

            raw_coordinates = f"{raw_results[0]} {raw_results[1]}" #012043.3N 1035318.7E
            rounded_coordinates = round_coords(raw_coordinates) #012044N 1035319E
            rounded_coord_for_notam = round_further_for_notam(rounded_coordinates)
            return {
                "raw_coordinates": raw_coordinates,
                "rounded_coordinates": rounded_coordinates,
                "rounded_coord_for_notam" : rounded_coord_for_notam
            }

        raise ValueError("Unable to parse coordinates.")
    
    except Exception as e:
        return {
            "raw_coordinates": "Error",
            "rounded_coordinates": "Error",
            "rounded_coord_for_notam": "Error",
            "error": f"Something went wrong when formatting the coordinates: {e}"
        }


# def validate_coord(coords_str):
#     pattern = r"^\d{4}\d+\.\d+N\s\d{5}\d+\.\d+E$"
#     return bool(re.match(pattern, coords_str))


def round_coords(raw_coords):
    '''Rounds the decimal seconds'''
    try:
        parts = raw_coords.strip().split(" ")
        results = []

        for i, text in enumerate(parts):
            if i == 0:
                pattern = r"(\d{2})(\d{2})(\d+\.\d+|\d+)([NS])"
            else:
                pattern = r"(\d{3})(\d{2})(\d+\.\d+|\d+)([EW])"

            match = re.match(pattern, text)
            if not match:
                continue

            deg, mnt, sec, direction = match.groups()
            deg, mnt = int(deg), int(mnt)
            sec_float = float(sec)

            sec_rounded = math.floor(sec_float + 0.5)
            if sec_rounded == 60:
                sec_rounded = 0
                mnt += 1
                if mnt == 60:
                    mnt = 0
                    deg += 1

            pad = 3 if i == 1 else 2
            results.append(f"{deg:0{pad}d}{mnt:02d}{sec_rounded:02d}{direction}")

        return " ".join(results)

    except Exception:
        return raw_coords

def round_further_for_notam(rounded_coords):
    ''' Takes rounded_coordinates (e.g., "012044N 1035319E") and 
    rounds to the nearest minute (e.g. 0121N10353E) '''

    try:
        parts = rounded_coords.strip().split(" ")
        notam_parts = []

        for i, text in enumerate(parts):

            if i == 0:
                pattern = r"(\d{2})(\d{2})(\d{2})([NS])"
            else:
                pattern = r"(\d{3})(\d{2})(\d{2})([EW])"

            match = re.match(pattern, text)
            if not match:
                continue

            deg, mnt, sec, direction = match.groups()
            deg, mnt, sec = int(deg), int(mnt), int(sec)


            if sec >= 30:
                mnt += 1
                if mnt == 60:
                    mnt = 0
                    deg += 1


            pad = 3 if i == 1 else 2
            notam_parts.append(f"{deg:0{pad}d}{mnt:02d}{direction}")


        return "".join(notam_parts)

    except Exception:

        return rounded_coords



# DEBUG
# raw_coords = "1°20'43.3\"N 103°53'18.7\"E"
# format_coords_custom(raw_coords)

# coord = '012124.N 1035558.E'
# print(validate_coord(coord))