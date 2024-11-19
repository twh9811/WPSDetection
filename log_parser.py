import json
from geopy import distance
classified_logs = "logs/classified_accurate_log.txt"
cheating_logs = "logs/manual_accurate_log.txt"
normal_logs = "logs/accurate_log.txt"

STARTING_CENTER_POINT = (43.2260006, -77.6435763)
TARGET_LOC = (43.235023195950276, -77.6273781379702)

# Radius in kilometers
def check_radius(given_point, starting_point=STARTING_CENTER_POINT, radius=2):
    calc_distance = distance.distance(starting_point, given_point)
    return calc_distance <= radius

def classify_log(classification_type, normal_logs, cheating=False):
    lat_sum = 0
    lng_sum = 0
    total_accurate = 0
        
    with open(classification_type, 'w') as classified_file:
        with open(normal_logs) as normal_file:
            for line in normal_file:
                # Json module is stupid and doesnt accept single quotes...
                line = line.replace("'", '\"')
                json_data = json.loads(line)
                location_data = json_data['location']
                est_point = (location_data['lat'], location_data['lng'])
                
                # Classifies the point based on the distance from the center starting point
                if 'tag' not in json_data:
                    if(cheating):
                        result = check_radius(est_point,TARGET_LOC,1)
                    else:
                        result = check_radius(est_point)
                    if(result):
                        json_data['tag'] = "Y"
                        lat_sum += est_point[0]
                        lng_sum += est_point[1]
                        total_accurate += 1
                    else:
                        json_data['tag'] = "N"                
                json_string = json.dumps(json_data) + "\n"
                classified_file.write(json_string)        
        normal_file.close()
    classified_file.close()
    return lat_sum/total_accurate, lng_sum/total_accurate

def main():
    est_lat, est_lng = classify_log(classified_logs,normal_logs)
    print("Estimated Location: " + str(est_lat) + "," + str(est_lng))
    
    est_lat, est_lng = classify_log(cheating_logs,normal_logs,True)
    print("Cheating Est Location: " + str(est_lat) + "," + str(est_lng))
    

if __name__ == "__main__":
    main()