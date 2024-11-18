import requests
import os
import random


API_KEY = os.getenv("API_KEY")
WIGLE_API_KEY = os.getenv("WIGLE_API_KEY")

MAPS_URL = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + API_KEY
WIGLE_URL = "https://api.wigle.net/api/v2/network/search"

CELL_TOWERS = [
            # Verizon 4G LTE
            {"cellId": 18713601, "locationAreaCode": 18688, "mobileCountryCode": 311, "mobileNetworkCode": 480, "signalStrength": -65},
            {"cellId": 18713612, "locationAreaCode": 18688, "mobileCountryCode": 311, "mobileNetworkCode": 480,"signalStrength": -68},
            # T-Mobile
            {"cellId": 11812099, "locationAreaCode": 22527, "mobileCountryCode": 310, "mobileNetworkCode": 260, "signalStrength": -72}
            ]

def log(data, accurate):
    filename = "logs/inaccurate_log.txt"
    if(accurate):
        filename = "logs/accurate_log.txt"
        
    file = open(filename, "a")
    file.write(str(data) + "\n")
    file.close()

def initial_location_estimation(target_mac):
    data = {
        "wifiAccessPoints": [{"macAddress":target_mac, "signalStrength":-57, "signalToNoiseRatio":40}],
        "cellTowers": CELL_TOWERS 
    }
    
    response = requests.post(MAPS_URL, json=data)

    received_location = response.json()['location']
    return (received_location['lat'], received_location['lng'])

def google_wps_triangulation(desired_mac, used_locations, desired_location):
    print(desired_location)
    accuracy_threshold = 150
    close_locations = []
    while len(close_locations) < 3:

        data = {
            "wifiAccessPoints": [{"macAddress":desired_mac, "signalStrength":-57, "signalToNoiseRatio":40}],
            "cellTowers": CELL_TOWERS
        }
        
        bssids = bssid_collection_via_wigle(desired_location[0], desired_location[1])
 
        for bssid in bssids:
            access_point = {"macAddress":bssid, "signalStrength":-90, "signalToNoiseRatio":15}
            data["wifiAccessPoints"].append(access_point)
            
        response = requests.post(MAPS_URL, json=data)

        received_location = response.json()

        log_accurate = False
        if received_location['accuracy'] < accuracy_threshold:
            str_loc_rep = str(received_location)
            if str_loc_rep in used_locations:
                continue
            coordinates = received_location['location']
            close_locations.append([coordinates['lat'],coordinates['lng']])
            log_accurate = True
            used_locations.add(str_loc_rep)
            print("Good Accuracy", received_location)
        else:
            print("Too High", received_location)
        log(received_location, log_accurate)

    central_lat = sum(location[0] for location in close_locations) / len(close_locations)
    central_long = sum(location[1] for location in close_locations) / len(close_locations)
    triangulated_location = [central_lat, central_long]
    return triangulated_location
    
def bssid_collection_via_wigle(lat, long):

    mod_range = [-.1, .1]
    lat_min_modifier = random.uniform(mod_range[0], mod_range[1])
    long_min_modifier = random.uniform(mod_range[0], mod_range[1])
    # Use min modifier as the range (therefore cant go lower than this)
    lat_max_modifier = random.uniform(lat_min_modifier, mod_range[1])
    long_max_modifier = random.uniform(long_min_modifier, mod_range[1])
    
    print(lat_min_modifier, long_min_modifier, lat_max_modifier, long_max_modifier)
    # Set headers with your API key
    headers = {
        "Authorization": "Basic " + WIGLE_API_KEY
    }
    
    min_lat = lat + lat_min_modifier
    min_long = long + long_min_modifier
    max_lat = lat + lat_max_modifier
    max_long = long + long_max_modifier
    
    # Establish query parameters
    params = {
        'latrange1': min_lat,
        'latrange2': max_lat,
        'longrange1': min_long,
        'longrange2': max_long,
        'lastupdtstart': '2018-01-01',
        'lastupdtend': '2024-12-31',
        'resultsPerPage': 100
    }
    
    # Make the request
    print("Query Request Sent")
    response = requests.get(WIGLE_URL, headers=headers, params=params)
    print("Answer Received")
    
    if response.status_code == 200:
        bssids = []
        response = response.json()
        # Parses json to check query success flag
        if response.get("success"):
            results = response.get("results")
            for network in results:
                bssid = network.get("netid")
                bssids.append(bssid)
            return bssids
        else:
            print("No Networks Found")
    else:
        print("Query Error:", response.status_code, response.reason, response.text)
    
def main():
    max_tries = 3
    target_mac = "80-78-71-c7-f4-96"
    triangulated_location = initial_location_estimation(target_mac)
    used_locations = set()
    for i in range(max_tries):
        print("Try", i+1)
        triangulated_location = google_wps_triangulation(target_mac, used_locations, triangulated_location)
    print("Final Est. Location:", triangulated_location)
if __name__ == "__main__":
    main()
