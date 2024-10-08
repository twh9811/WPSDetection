import requests
import os
import random


API_KEY = os.getenv("API_KEY")
WIGLE_API_KEY = os.getenv("WIGLE_API_KEY")

MAPS_URL = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + API_KEY
WIGLE_URL = "https://api.wigle.net/api/v2/network/search"

def google_wps_triangulation(desired_mac):
    """
    Provides Google Maps WPS a list of BSSIDs in a specific r egion and attempts to locate a priority BSSID in that region.
    Loops until accuracy is improved to threshold.
    """
    attempt = 0
    accuracy_threshold = 200
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
        
        bssids = bssid_collection_via_wigle()
        select_amount = 25
        random_bssids = random.sample(bssids, select_amount)
        for bssid in random_bssids:
            access_point = {"macAddress":bssid, "signalStrength":-90, "signalToNoiseRatio":15}
            data["wifiAccessPoints"].append(access_point)
        
        response = requests.post(MAPS_URL, json=data)

        received_location = response.json()
        
        if received_location['accuracy'] < accuracy_threshold:
            print("Good Accuracy", received_location)
            break
        print("Too High", received_location)
        attempt += 1

def bssid_collection_via_wigle():
    """
    Creates a box outlining a specific geographic region, returns bssids in that location.
    """
    mod_range = [-.1, 1]
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
                #print(network)
                bssid = network.get("netid")
                lat = network.get("trilat")
                long = network.get("trilong")
                # Extra check because the query parameters dont seem to work consistently....
                if min_lat <= lat <= max_lat and min_long <= long <= max_long:
                    bssids.append(bssid)
            return bssids
        else:
            print("No Networks Found")
    else:
        print("Query Error:", response.status_code, response.reason, response.text)
    
def main():
    #test_mac = "E8-65-38-02-4A-6F"
    test_mac = "80-78-71-c7-f4-96"
    google_wps_triangulation(test_mac)
    
if __name__ == "__main__":
    main()