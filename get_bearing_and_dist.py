import math
from shapely.geometry import Point, Polygon

def get_location_info(cord):
    '''Calculates bearing and distance info for AIP SUP. Formula retrieved from Excel.'''
    #cord = 012045.5N 1035324.7E
    try:
        N = cord.split(' ')[0]
        c5 = int(N[:2])
        d5 = int(N[2:4])
        e5 = float(N[4:].replace('N', '')) # "45.5" -> 45.5

        E = cord.split(' ')[1]
        c6 = int(E[:3])
        d6 = int(E[3:5])
        e6 = float(E[5:].replace('E', '')) # "24.7" -> 24.7

        c13 = c5 + d5/60 + e5/3600 #LAT
        c14 = c6 + d6/60 + e6/3600 #LONG

        #CORDS FOR PAYA LEBAR.
        m9 = 343333.3333
        m10 = 166666.6667
        j13 = 1.355722222
        j14 = 103.9027778


        c16 = j13-c13
        c17 = j14-c14

        i18 = calculate_complementary_angle(90,"-",c16,c17)
        j18 = calculate_complementary_angle(90,"+",c16,c17)
        k18 = calculate_complementary_angle(270,"-",c16,c17)
        l18 = calculate_complementary_angle(270,"+",c16,c17)

        distance = round(math.sqrt((c16)**2 + (c17)**2) * 60, 2)
        
        bearing = select_quadrant_value(c16, c17, i18, j18, k18, l18)
        lat = c13
        long = c14


        if distance is None or bearing is None:
            raise ValueError("Distance or bearing calculation resulted in None")
        else:
            return {
            "distance" : round(distance,2),
            "bearing" :round(bearing,1),
            "lat" : lat,
            "long" : long
            }
    
    except Exception as e:
        return {
            "distance" : "Error",
            "bearing" : "Error",
            "lat" : "Error",
            "long" : "Error"
            }

def calculate_complementary_angle(angle,op,c16,c17):
    '''Math logic for calculating bearing and distance information. Do not touch.'''
    ratio = abs(c16 / c17)

    angle_rad = math.atan(ratio)

    angle_deg = math.degrees(angle_rad)
    
    if op == "+":
        result = angle + angle_deg
    elif op == "-":
        result = angle - angle_deg

    # return round(result, 6)
    return result
    
def select_quadrant_value(c16, c17, i18, j18, k18, l18):
    '''Math logic for calculating bearing and distance information. Do not touch.'''
  
    if c16 <= 0 and c17 <= 0:
        result = i18
    
    elif c16 >= 0 and c17 <= 0:
        result = j18
    
    elif c16 >= 0 and c17 >= 0:
        result = k18
    
    elif c16 <= 0 and c17 >= 0:
        result = l18
    else:
        result = 0 

    # return round(result, 1)
    return result

# def round_for_cord(cord):


def within_5_km(lat,long):
    
    if not isinstance(lat, (int, float)) or not isinstance(long, (int, float)):
        return False
    
    #PLAB CTR
    plab_coords = [
        (103.8594,1.1833),
        (104.0302, 1.55),
        (103.8955, 1.5333),
        (103.915,1.4261 ),
        (103.8888, 1.4288),
        (103.8661,1.3741),
        (103.8377, 1.3755),
        (103.7816, 1.35),
        (103.7608,1.3402),
        (103.7497, 1.3097)
    ]

    restricted = Polygon(plab_coords)

    def check_if_inside_zone(crane_lat, crane_long, zone_polygon):
        try:
            crane_point = Point(crane_long, crane_lat) 
            return zone_polygon.contains(crane_point)
        except:
            return False
    
    return check_if_inside_zone(lat,long,restricted)

def get_upper_FL(height_ft):
    """
    Ceiling height to nearest 100 (FL)
    """
    try:
        height = float(height_ft)
        fl_value = math.ceil(height / 100)
        return f"{fl_value:03d}"
        
    except (ValueError, TypeError):
        return "000"