import requests
import os
import geopy.distance


API_KEY = os.getenv("API_KEY")
WIGLE_API_KEY = os.getenv("WIGLE_API_KEY")

MAPS_URL = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + API_KEY
WIGLE_URL = "https://api.wigle.net/api/v2/network/search"

def google_wps_triangulation(bssids, desired_mac):
    """
    Provides Google Maps WPS a list of BSSIDs in a specific r egion and attempts to locate a priority BSSID in that region
    """
    
    data = {
        "wifiAccessPoints": []
    }
    
    prioritized_access_point = {"macAddress":desired_mac, "signalStrength":-45, "signalToNoiseRatio":40}
    # append it first for processing priority (?)
    data["wifiAccessPoints"].append(prioritized_access_point)
    
    for bssid in bssids:
        access_point = {"macAddress":bssid, "signalStrength":-75, "signalToNoiseRatio":15}

        data["wifiAccessPoints"].append(access_point)
    
    response = requests.post(MAPS_URL, json=data)

    received_location = response.json()

    print(received_location)

def bssid_collection_via_wigle():
    """
    Creates a box outlining a specific geographic region, returns bssids in that location.
    """
    
    # Set headers with your API key
    headers = {
        "Authorization": "Basic " + WIGLE_API_KEY
    }
    
    # North Greece 
    max_lat = 43.254727440238206
    max_long = -77.73275248513913
    # West Irondequoit
    min_lat = 43.22439607883378
    min_long = -77.59918017155313
    
    # Establish query parameters
    params = {
        'latrange1': min_lat,
        'latrange2': max_lat,
        'longrange1': min_long,
        'longrange2': max_long,
        'lastupdtstart': '2024-01-01',
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
                coordinates = (network.get("trilat"), network.get("trilong"))
                bssids.append(bssid)
            return bssids
        else:
            print("No Networks Found")
    else:
        print("Query Error:", response.status_code, response.reason, response.text)

def main():
    test_mac = "E8-65-38-02-4A-6F"
    bssids = bssid_collection_via_wigle()
    google_wps_triangulation(bssids, test_mac)
    
if __name__ == "__main__":
    main()