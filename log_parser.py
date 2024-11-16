import json
from geopy import distance
classified_logs = "logs/classified_accurate_log.txt"
normal_logs = "logs/accurate_log.txt"
# How can we update this to reflect the actual location better? This determines the classification math...
# STARTING_CENTER_POINT = (43.234806262034226, -77.62164262024581)
STARTING_CENTER_POINT = (43.214017478656366, -77.57894640208245)

def check_radius(given_point):
    # Kilometers 
    radius = 5
    calc_distance = distance.distance(STARTING_CENTER_POINT, given_point)
    return calc_distance <= radius
    
def classify_log(classified_logs, normal_logs):
    lat_sum = 0
    lng_sum = 0
    total_accurate = 0
    
    with open(classified_logs, 'w') as classified_file:
        with open(normal_logs) as normal_file:
            for line in normal_file:
                # Json module is stupid and doesnt accept single quotes...
                line = line.replace("'", '\"')
                json_data = json.loads(line)
                location_data = json_data['location']
                est_point = (location_data['lat'], location_data['lng'])
                
                # Classifies the point based on the distance from the center starting point
                if 'tag' not in json_data:
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

if __name__ == "__main__":
    main()