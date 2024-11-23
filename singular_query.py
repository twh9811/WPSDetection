import requests
import os
import random


API_KEY = os.getenv("API_KEY")
WIGLE_API_KEY = os.getenv("WIGLE_API_KEY")

MAPS_URL = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + API_KEY
WIGLE_URL = "https://api.wigle.net/api/v2/network/search"
    
def google_wps_triangulation(desired_mac):
    data = {
        "wifiAccessPoints": [{"macAddress":desired_mac, "signalStrength":-57, "signalToNoiseRatio":40}],
        "cellTowers": [
            # Verizon 4G LTE
            {"cellId": 18713601, "locationAreaCode": 18688, "mobileCountryCode": 311, "mobileNetworkCode": 480, "signalStrength": -65},
            {"cellId": 18713612, "locationAreaCode": 18688, "mobileCountryCode": 311, "mobileNetworkCode": 480,"signalStrength": -68},
            # T-Mobile
            {"cellId": 11812099, "locationAreaCode": 22527, "mobileCountryCode": 310, "mobileNetworkCode": 260, "signalStrength": -72}
            ]
    }
    
    #data["wifiAccessPoints"].append({"macAddress":"4c-19-5d-4f-62-21", "signalStrength":-57, "signalToNoiseRatio":40})
    data["wifiAccessPoints"].append({"macAddress":"f8-5b-3b-e0-05-fa", "signalStrength":-57, "signalToNoiseRatio":40})
    data["wifiAccessPoints"].append({"macAddress":"08-36-c9-95-ee-71", "signalStrength":-57, "signalToNoiseRatio":40})
    data["wifiAccessPoints"].append({"macAddress":"a0-55-1f-68-1d-39", "signalStrength":-57, "signalToNoiseRatio":40})
    response = requests.post(MAPS_URL, json=data)

    received_location = response.json()
    print(received_location)
    
def main():
    max_tries = 3
    test_mac = "80-78-71-c7-f4-96"
    for i in range(max_tries):
        print("Try", i+1)
        triangulated_location = google_wps_triangulation(test_mac)
    print("Final Est. Location:", triangulated_location)
if __name__ == "__main__":
    main()
