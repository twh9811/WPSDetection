import requests
import os
import random


API_KEY = os.getenv("API_KEY")
WIGLE_API_KEY = os.getenv("WIGLE_API_KEY")

MAPS_URL = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + API_KEY
WIGLE_URL = "https://api.wigle.net/api/v2/network/search"

def google_wps_triangulation(desired_mac, close_bssids=None):
    """
    Provides Google Maps WPS a list of BSSIDs in a specific r egion and attempts to locate a priority BSSID in that region.
    Loops until accuracy is improved to threshold.
    """
    attempt = 0
    accuracy_threshold = 120
    accurate_bssids =  set()
    while attempt < 10:

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
        if(close_bssids is not None):
            for bssid in close_bssids:
                access_point = {"macAddress":bssid, "signalStrength":-75, "signalToNoiseRatio":25}
                data["wifiAccessPoints"].append(access_point)
        else:
            bssids = bssid_collection_via_wigle()
            for bssid in bssids:
                access_point = {"macAddress":bssid, "signalStrength":-90, "signalToNoiseRatio":15}
                data["wifiAccessPoints"].append(access_point)
            
        response = requests.post(MAPS_URL, json=data)

        received_location = response.json()
        
        # Check accuracy. If its good, add these to a list with a better signal strength to signify these should be closer to the desired location.
        if received_location['accuracy'] < accuracy_threshold:
            print("Good Accuracy", received_location)
            for bssid in bssids:
                accurate_bssids.add(bssid)
        else:
            # Otherwise ignore bssids, try again.
            print("Too High", received_location)
        attempt += 1
        
    data = {
        "wifiAccessPoints": []
    }
        
    prioritized_access_point = {"macAddress":desired_mac, "signalStrength":-57, "signalToNoiseRatio":40}
    data["wifiAccessPoints"].append(prioritized_access_point)
    for bssid in accurate_bssids:
        access_point = {"macAddress":bssid, "signalStrength":-85, "signalToNoiseRatio":20}
        data["wifiAccessPoints"].append(access_point)
    response = requests.post(MAPS_URL, json=data)

    received_location = response.json()
    print(received_location)
    return accurate_bssids

def bssid_collection_via_wigle():
    """
    Creates a box outlining a specific geographic region, returns bssids in that location.
    """
    mod_range = [-.1, .1]
    lat_min_modifier = random.uniform(mod_range[0], mod_range[1])
    long_min_modifier = random.uniform(mod_range[0], mod_range[1])
    lat_max_modifier = random.uniform(mod_range[0], mod_range[1])
    long_max_modifier = random.uniform(mod_range[0], mod_range[1])
    
    print(lat_min_modifier, long_min_modifier, lat_max_modifier, long_max_modifier)
    # Set headers with your API key
    headers = {
        "Authorization": "Basic " + WIGLE_API_KEY
    }
    
    # Irondequoit (43.21313319463426, -77.5818301738431)
    min_lat = 43.21 + lat_min_modifier
    min_long = -77.58 + long_min_modifier
    max_lat = 43.21 + lat_max_modifier
    max_long = -77.58 + long_max_modifier
    
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
    response = requests.get(WIGLE_URL, headers=headers, params=params)
    
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
    close_bssids = set()
    for i in range(max_tries):
        print("Try 1")
        if(i == 0):
            curr_set = google_wps_triangulation(test_mac)
        else:
            curr_set = google_wps_triangulation(test_mac, close_bssids)
        close_bssids.update(curr_set)
if __name__ == "__main__":
    main()