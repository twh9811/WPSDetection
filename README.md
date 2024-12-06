Make sure the API keys for both WiGLE and Google are set as environment keys for your system.

Change the main in data_gathering.py to be the desired target MAC address.

Change the CELL_TOWERS global var in data_gathering.py to represent towers in the location of the target.

In data_gathering.py, change the random geofence modifiers found in bssid_collection_via_wigle() to the desirable range.


Run using "python3 data_gathering.py" the desired amount of times until the desired amount of data is retrieved.

To classify the results and get the final location estimate, run "python3 log_parser.py."

The final result may need wardriving as supplemental information to get a truly precise result.

The logs folder contains the logs gathered after the geofencing error was fixed. The pre-optimization folder shows the logs gathered before.
