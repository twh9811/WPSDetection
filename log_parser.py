import json

def parse_log(filename):
    with open(filename) as file:
        lat_sum = 0
        lng_sum = 0
        total_accurate = 0
        for line in file:
            # Json module is stupid and doesnt accept single quotes...
            line = line.replace("'", '\"')
            json_data = json.loads(line)
            
            accuracy_tag = json_data['tag']
            location_data = json_data['location']
            if(accuracy_tag == "Y"):
                lat_sum += location_data['lat']
                lng_sum += location_data['lng']
                total_accurate += 1
    return lat_sum/total_accurate, lng_sum/total_accurate
        
def main():
    filename = "logs/accurate_log.txt"
    est_lat, est_lng = parse_log(filename)
    print("Estimated Location: " + str(est_lat) + "," + str(est_lng))

if __name__ == "__main__":
    main()