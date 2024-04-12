from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *
from config import configuration

def main():
    spark = SparkSession.builder.appName("SmartCityStreaming")\
    .config("spark.jars.packages",
             "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0", # this is to connect spark and kafa
             "org.apache.hadoop:hadoop-aws:3.3.1",               # this is to connect spark to aws
             "com.amazonaws:aws-java-sdk:1.11.469")\
    .config("spark.hadoop.fs.s3.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")\
    .config("spark.hadoop.fs.s3.access.key", configuration.get('AWS_ACCESS_KEY'))\
    .config("spark.hadoop.fs.s3.secret.key", configuration.get('AWS_SECRET_KEY'))\
    .config("spark.hadoop.fs.s3.aws.credentials.provider", 
            "org.apache.hadoop.fx.s3a.impl.SimpleAWSCredentialsProvider")\
    .getOrCreate()
    # these can found on maven repository
    # https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10_2.13/3.5.0
    # https://mvnrepository.com/artifact/org.apache.hadoop/hadoop-aws/3.3.1

    # Adjust the log level to minimize the console output on executors
    spark.sparkContext.setLogLevel('WARN')

# The structure of the data coming in from the consumer is structured with StructType to give the data a sense of meaning before, during and after consummation.

# vehicle schema schema from main.py "generate_vehicle_data"
    vehicleSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("make", StringType(), True),
        StructField("model", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("fuelType", StringType(), True),
    ])
    # gpsSchema from main.py "generate_gps_data"
    gpsSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("vehicleType", StringType(), True)
    ])
    # trafficSchema "generate_traffic_camera_data"
    trafficSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("cameraId", StringType(), True),
        StructField("location", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("snapshot", StringType(), True)
    ])
    # weatherSchema "generate_weather_data"
    weatherSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("location", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("temperature", DoubleType(), True),
        StructField("weatherCondition", StringType(), True),
        StructField("precipitation", DoubleType(), True),
        StructField("windSpeed", DoubleType(), True),
        StructField("humidity", IntegerType(), True),
        StructField("airQualityIndex", DoubleType(), True),
    ])
    # emergencySchema "generate_weather_data"
    emergencySchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("incidentId", StringType(), True),
        StructField("type", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("status", StringType(), True),
        StructField("description", StringType(), True),
    ])

# subscribe to Kafka topic
def read_kafka_topic(topic, schema):
    return (main.spark.readStream  # from main func
            .format('kafka')
            .option('kafka.bootstrap.servers', 'broker:29092')
            .option('subscribe', topic)
            .option('startingOffsets', 'earliest')
            .load()
            .selectExpr('CAST(value AS STRING)')
            .select(from_json(col('value'), schema).alias('data'))
            .select('data.*')
            .withWatermark('timestamp', '2 minutes') # this is in case data is delayed, so there is a stamp to know where to start from
            )

# subscribe to any topic and serializing them to the schema we want. To utilize this function we call it as:
vehicleDF = read_kafka_topic('vehicle_data', main.vehicleSchema).alias('vehicle') #from main fucn
gpsDF = read_kafka_topic('gps_data', gpsSchema).alias('gps')
trafficDF = read_kafka_topic('traffic_data', trafficSchema).alias('traffic')
weatherDF = read_kafka_topic('weather_data', weatherSchema).alias('weather')
emergencyDF = read_kafka_topic('emergency_data', emergencySchema).alias('emergency')

# Eventually, we need to write the data to AWS S3 Bucket but we have a challenge here, and that is 5 data streams! We need to be able to write them in parallel to S3 bucket without fail. To achieve this, a function comes in handy:
def streamWriter(input: DataFrame, checkpointFolder, output):
    return (input.writeStream
            .format('parquet')
            .option('checkpointLocation', checkpointFolder)
            .option('path', output)
            .outputMode('append')
            .start())
# This function allows us to start each of the streams in parallel and they all run concurrently writing data to S3. In our case, the function is invoked as thus:


query1 = streamWriter(vehicleDF, 's3a://spark-streaming-data/checkpoints/vehicle_data',
             's3a://spark-streaming-data/data/vehicle_data')
query2 = streamWriter(gpsDF, 's3a://spark-streaming-data/checkpoints/gps_data',
             's3a://spark-streaming-data/data/gps_data')
query3 = streamWriter(trafficDF, 's3a://spark-streaming-data/checkpoints/traffic_data',
             's3a://spark-streaming-data/data/traffic_data')
query4 = streamWriter(weatherDF, 's3a://spark-streaming-data/checkpoints/weather_data',
             's3a://spark-streaming-data/data/weather_data')
query5 = streamWriter(emergencyDF, 's3a://spark-streaming-data/checkpoints/emergency_data',
             's3a://spark-streaming-data/data/emergency_data')
query5.awaitTermination()
# The awaitTermination function at the end of that blocks sends all the started streams on their journey to heavenly race without interference!

# The next thing to do is to submit out spark job to our spark master-worker cluster.


# docker exec -it smartcity-spark-master-1 spark-submit \
# --master spark://spark-master:7077 \
# --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk:1.11.469 \
# jobs/spark-city.py

if __name__ == "__main__":
    main()