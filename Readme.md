## Introduction
Project aims to collect data from IoT (Internet of Things) simulated devices. Data will be handled in Kafka (becuase its realtime) managed by zookeeper and then moved in Spark (so batches can be created to align the time, since there might be latency in all of the IoT devices streaming data). Zookeeper, Kafka and Spark will installed/configured upon in a Docker Container. <br>

This data will then be moved into S3 bucket, from where using Data Catalog we will do transformations and using AWS Glue we will move the data into Amazon Redshift (our datawarehouse) and Amazon Athena (backup warehouse). From there we can gather insights on the data in a data vizualisation tool.

## Pre-reqs for this project
1. Use python < 3.12 (latest version is finicky) is finicky 
2. Create folder `smartcity`
3. Create git repo `git init`
4. Create virtual environment: `py -3.10 -m virtualenv smartcity_env`
5. Activate virtual environment     
    5.1 In Linux `.` <br>
    5.2 In Powershell `set-executionpolicy RemoteSigned -Scope CurrentUser` <br>
                       `Main_project_folder/smartcity_env/Scripts/activate.ps1 ` <br>
    5.3 In Command Promp `call .\smartcity_env\Scripts\activate`
    5.4 If you are using existing code: Create new environemtn and download the requirements `pip install -r /SmartCity/requirements.txt`
6. Create docker-compose file with zookeeper, kafka, spark (master and workers). Keep them all on the same network so that they can interact with each other.
7. Create `main.py` file where data is simulated for the journey.
8. When the data is ready to be ingested in Kafka. Create Kafka functions nad after running main.py check in Kafka using Docker's `broker` image -> `exec` -> command `kafka-topic --list bootsrap-server broker:2902`
9. Check for one of the topics `kafka-console-consumer --topic vehicle_data --boostrap-server broker:9092 --from-beginning`. Production of data and ingestion into KAFKA is now complete
10. Create AWS account and create S3 bucket (diasble block all public access). Download AWS CLI. We can now start working on consuming the stream from Kafka into Spark.
11. Create `config.py` in jobs to configure AWS access. Use powershell `New-Item jobs/config.py` (subsitute of linux command `touch`)
12. Use command in cmd to run the spark master 
```
docker exec -it smartcity-spark-master-1 spark-submit \
--master spark://spark-master:7077 \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk:1.11.469 \
jobs/spark-city.py
```
13. When the above commands runs `localhost:9090` can be used to access the UI. Run `main.py` to create the data that needs to be ingested.
14. Data is not going to be consumed and pusehd to S3 bucket that is being used as a lakehouse. There will be checkpoints created
15. Now we will use Amazon Glue Crawler to crawl the data and 

. Keep pushing code to git/github on interval
```
git remote -v
git remote add origin https://github.com/<user>/<user_repository>
git add .
git commit -m "updates to schema and sql files"
git push origin main
```


## Source 
[SmartCity Real time Streaming data pipeline | CodeWithYu](https://www.youtube.com/watch?v=Vv_fvwF41_0&ab_channel=CodeWithYu)
