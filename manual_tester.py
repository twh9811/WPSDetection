import json
    
def classify_log(normal_logs):
    lat_sum = 0
    lng_sum = 0
    total_accurate = 0
    
    with open(normal_logs) as normal_file:
        for line in normal_file:
            # Json module is stupid and doesnt accept single quotes...
            line = line.replace("'", '\"')
            json_data = json.loads(line)
            location_data = json_data['location']
            est_point = (location_data['lat'], location_data['lng'])
            tag_status = json_data['tag']
            if(tag_status == "Y"):
                lat_sum += est_point[0]
                lng_sum += est_point[1]
                total_accurate += 1        
    normal_file.close()
    return lat_sum/total_accurate, lng_sum/total_accurate

def main():
    est_lat, est_lng = classify_log("manual_accurate_log.txt")
    print("Estimated Location: " + str(est_lat) + "," + str(est_lng))

if __name__ == "__main__":
    main()