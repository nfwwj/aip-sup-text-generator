import simplekml

def generate_crane_kml(data):
    """Generates a KML file"""

    lat = data.get("lat")
    long = data.get("long")
    
    kml = simplekml.Kml()
    pnt = kml.newpoint(name=f"{data.get('application_num')} EXPIRES {data.get('month_year_end')}")
    
    # Longitude FIRST in KML coordinates
    pnt.coords = [(long, lat)]

    pnt.description = (
        f"OFFICIAL (CLOSED) / SENSITIVE NORMAL"
        f"Application number: {data.get('application_num')}<br/>"
        f"Mref: {data.get('mref', 'N/A')}<br/>"
        f"Number of Cranes: {data.get('num_cranes', 'N/A')}<br/>"
        f"Height: {data.get('height(ft)', 'N/A')} ft<br/>"
        f"Start: {data.get('true_start(ddmmmyyyy)', 'N/A')}<br/>"
        f"End: {data.get('end(ddmmmyyyy)', 'N/A')}<br/>"
        f"Full Text: {data.get('full_text', 'N/A')}"
    )

    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png'
    filename = f"{data.get('application_num')} EXPIRES {data.get('month_year_end')}.kml"
    kml.save(filename)

    ## For copy and paste textbox
    ge_coords = format_coords_for_google_earth(data.get("raw_coordinates"))  #converts back to coordinates with symbols 
    text = f"""{data.get('application_num')} EXPIRES {data.get('month_year_end')}
        {ge_coords.get('formatted_lat')}
        {ge_coords.get('formatted_lon')}

        Application number: {data.get('application_num')}<br/>
        Mref: {data.get('mref', 'N/A')}<br/>
        Number of Cranes: {data.get('num_cranes', 'N/A')}<br/>
        Height: {data.get('height(ft)', 'N/A')} ft<br/>
        Start: {data.get('true_start(ddmmmyyyy)', 'N/A')}<br/>
        End: {data.get('end(ddmmmyyyy)', 'N/A')}<br/>
        Full Text: {data.get('full_text', 'N/A')}
    """

    return {"filename": filename, "text": text}

def format_coords_for_google_earth(raw_coords_str): 
    """ Converts '012124.2N 1035558.2E' into '1°21'24.2"N 103°55'58.2"E' for manual copy and paste into Google Earth."""
    try:
        # Clean up spacing and split into Lat and Long
        parts = raw_coords_str.strip().split()
        
        lat_raw, lon_raw = parts[0], parts[1]
       
        lat_deg = str(int(lat_raw[0:2]))  
        lat_min = lat_raw[2:4]
        lat_sec = lat_raw[4:-1]           
        lat_dir = lat_raw[-1]
        
        formatted_lat = f"{lat_deg}°{lat_min}'{lat_sec}\"{lat_dir}"
       
        lon_deg = str(int(lon_raw[0:3])) 
        lon_min = lon_raw[3:5]
        lon_sec = lon_raw[5:-1]
        lon_dir = lon_raw[-1]
        
        formatted_lon = f"{lon_deg}°{lon_min}'{lon_sec}\"{lon_dir}"
        # print(f"Formatted Lat: {formatted_lat}, Formatted Lon: {formatted_lon}")
        return {"formatted_lat": formatted_lat, "formatted_lon": formatted_lon}
        
    except Exception:  
        return {"formatted_lat": "Error", "formatted_lon": "Error"}
