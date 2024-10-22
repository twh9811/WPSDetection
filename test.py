import requests
import os
import random


API_KEY = os.getenv("API_KEY")
WIGLE_API_KEY = os.getenv("WIGLE_API_KEY")

MAPS_URL = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + API_KEY
WIGLE_URL = "https://api.wigle.net/api/v2/network/search"

def google_wps_triangulation(desired_mac, desired_location=None):
    accuracy_threshold = 120
    close_locations = []
    while len(close_locations) < 3:

        data = {
            "wifiAccessPoints": []
        }
        
        prioritized_access_point = {"macAddress":desired_mac, "signalStrength":-57, "signalToNoiseRatio":40}
        # append it first for processing priority (?)
        data["wifiAccessPoints"].append(prioritized_access_point)
        # Neighbor WIFI...
        # data["wifiAccessPoints"].append({"macAddress":"4c-19-5d-4f-62-21", "signalStrength":-57, "signalToNoiseRatio":40})
        # data["wifiAccessPoints"].append({"macAddress":"f8-5b-3b-e0-05-fa", "signalStrength":-57, "signalToNoiseRatio":40})
        # data["wifiAccessPoints"].append({"macAddress":"08-36-c9-95-ee-71", "signalStrength":-57, "signalToNoiseRatio":40})
        # data["wifiAccessPoints"].append({"macAddress":"a0-55-1f-68-1d-39", "signalStrength":-57, "signalToNoiseRatio":40})
        if(desired_location is None):
            bssids = bssid_collection_via_wigle()
        else:
            bssids = bssid_collection_via_wigle(triangulated_location[0], triangulated_location[1])
            
        for bssid in bssids:
            access_point = {"macAddress":bssid, "signalStrength":-90, "signalToNoiseRatio":15}
            data["wifiAccessPoints"].append(access_point)
            
        response = requests.post(MAPS_URL, json=data)

        received_location = response.json()

        if received_location['accuracy'] < accuracy_threshold:
            print("Good Accuracy", received_location)
            coordinates = received_location['location']
            close_locations.append([coordinates['lat'],coordinates['long']])
        else:
            print("Too High", received_location)

    central_lat = sum(location[0] for location in close_locations)
    central_long = sum(location[1] for location in close_locations)
    triangulated_location = [central_lat, central_long]
    return triangulated_location
    
# Irondequoit (43.21313319463426, -77.5818301738431)
def bssid_collection_via_wigle(lat=43.21, long=-77.58):

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
    test_mac = "80-78-71-c7-f4-96"
    triangulated_location = None
    for i in range(max_tries):
        print("Try", i+1)
        if(triangulated_location is None):
            triangulated_location = google_wps_triangulation(test_mac)
        else:
            triangulated_location = google_wps_triangulation(test_mac, triangulated_location)
if __name__ == "__main__":
    main()
