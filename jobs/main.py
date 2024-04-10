# simulate_vehicle_movement() takes 0 positional arguments but 1 was given
# .isoformat()

import os
import random
from datetime import datetime, timedelta
import uuid

from confluent_kafka import SerializingProducer
import simplejson as json 

LONDON_COORDINATES = {
    "latitude": 51.5074 ,
    "longitude":  -0.1278
}
BIRMINGHAM_COORDINATES = {
    "latitude": 52.4862 ,
    "longitude":  -1.8904
}

# movement increment calculation
LATITUDE_INCREMENTE =  (BIRMINGHAM_COORDINATES['latitude'] - LONDON_COORDINATES['latitude'])/100
LONGITUDE_INCREMENTE =  (BIRMINGHAM_COORDINATES['longitude'] - LONDON_COORDINATES['longitude'])/100

# environment variables
KAFKA_BOOSTRAP_SERVERS = os.getenv('KAFKA_BOOSTRAP_SERVERS', 'localhost:9092')
VEHICLE_TOPICS         = os.getenv('VEHICLE_TOPIC', 'vehicle_data')
GPS_TOPIC              = os.getenv('GPS_TOPIC', 'gps_data')
TRAFFIC_TOPIC          = os.getenv('TRAFFIC_TOPIC', 'traffic_data')
EMERGENY               = os.getenv('EMERGENCY_TOPIC', 'emergency_data')
WEATHER_TOPIC          = os.getenv('WEATHER_TOPIC', 'weather_data')

start_time = datetime.now()
start_location = LONDON_COORDINATES.copy()

def get_next_time():
    global start_time
    start_time += timedelta(seconds = random.randint(30, 60)) # update the frequency

def simulate_vehicle_movement(device_id):
    global start_location

    # then move towards birmingham
    start_location['latitude']  += LATITUDE_INCREMENTE
    start_location['longitude'] += LONGITUDE_INCREMENTE

    # add some randomness to the increase in increments
    start_location['latitude']  += random.uniform(.0005 , .0005) # giving limit so there are no up/down spikes
    start_location['longitude'] += random.uniform(.0005 , .0005)

    return start_location

def generate_vehicle_data(device_id):
    location = simulate_vehicle_movement(device_id)
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'timestamp': get_next_time(),#.isoformat(), # we want to keep increasing time as dirver moves from london to birmingham
        'location': (location['latitude'], location['longitude']),
        'speed': random.uniform(10, 40), # not too slow or fast
        'direction': 'North-East',
        'make': 'Toyota',
        'model': 'C500',
        'year': 2024,
        'fuelType': 'Hybrid'
    }

def generate_gps_data(device_id, timestamp, vehicle_type='private'):
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'timestamp': timestamp,
        'speed': random.uniform(0, 40),  # random speed: km/h
        'direction': 'North-East',
        'vehicleType': vehicle_type
    }

def generate_traffic_camera_data(device_id, timestamp, location, camera_id):
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'cameraId': camera_id,
        'location': location,
        'timestamp': timestamp,
        # we could not find snapshots online. So incase there are snapshots, use 'get' or 'request'
        # then code it in Base64EncodedString
        # or get the actual url and save in s3 bucket etc. and then stamp that in here
        'snapshot': 'Base64EncodedString'
    }

def generate_weather_data(device_id, timestamp, location):
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'location': location,
        'timestamp': timestamp,
        'temperature': random.uniform(-5, 26),
        'weatherCondition': random.choice(['Sunny', 'Cloudy', 'Rain', 'Snow']),
        'precipitation': random.uniform(0, 25),
        'windSpeed': random.uniform(0, 100),
        'humidity': random.randint(0, 100),  # percentage
        'airQualityIndex': random.uniform(0, 500)  # AQL Value goes here
    }

def generate_emergency_incident_data(device_id, timestamp, location):
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'incidentId': uuid.uuid4(),
        'type': random.choice(['Accident', 'Fire', 'Medical', 'Police', 'None']),
        'timestamp': timestamp,
        'location': location,
        'status': random.choice(['Active', 'Resolved']),
        'description': 'Description of the incident'
    }

def simulate_journey(producer, device_id):
    while True:
        # timestamp to be unique across all IoT
        vehicle_data            = generate_vehicle_data(device_id)
        gps_data                = generate_gps_data(device_id, vehicle_data['timestamp'])
        traffic_camera_data     = generate_traffic_camera_data(device_id, vehicle_data['timestamp'], vehicle_data['location'], camera_id='Nikon_Camera123')
        emergency_incident_data = generate_emergency_incident_data(device_id, vehicle_data['timestamp'], vehicle_data['location'])
        weather_data            = generate_weather_data(device_id, vehicle_data['timestamp'], vehicle_data['location'])
        print(vehicle_data)
        print(gps_data)
        print(traffic_camera_data)
        print(emergency_incident_data)
        print(weather_data)
        
        break

# def produce_data_to_kafka(producer, topic, data):
#     producer.produce(
#         topic,
#         key=str(data['id']),
#         value=json.dumps(data, default=json_serializer).encode('utf-8'),
#         on_delivery=delivery_report
#     )
#     producer.flush()

# produce_data_to_kafka(producer, VEHICLE_TOPIC, vehicle_data)
# produce_data_to_kafka(producer, GPS_TOPIC, gps_data)
# produce_data_to_kafka(producer, TRAFFIC_TOPIC, traffic_camera_data)
# produce_data_to_kafka(producer, WEATHER_TOPIC, weather_data)
# produce_data_to_kafka(producer, EMERGENCY_TOPIC, emergency_incident_data)

# entry point
if __name__ == "__main__" :
    producer_config = {
        'bootstrap.servers': KAFKA_BOOSTRAP_SERVERS, 
        'error_cb': lambda err: print(f'Kafka error: {err}')
    }
    producer = SerializingProducer(producer_config)

    try:
        simulate_journey(producer, 'vehicle_codingEx_123')
    except KeyboardInterrupt:
        print('Simulation ended by the user')
    except Exception as e:
        print(f'Unexpected error occured: {e}')
