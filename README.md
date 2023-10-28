# Stop-piramida ETL

## Description 
This project is a microservice written in python 3 that collects data on respectable and not respectable financial organizations. The collected data is not saved and is transmitted via the RabbitMQ message broker to the required consumer.

- Data markup matrix (формуляр): [link](https://docs.google.com/spreadsheets/d/1HoQMST3Zqn7sm4Scr4NeagTL6XeDFkxHM9nQWxcuZ-w/edit#gid=0)
- Google drive: [link](https://drive.google.com/drive/folders/1UPxVW1QRJuxgANFFt-LWFpXmPx8Q2XSP)

## Deploy Process
At the moment, the deployment is carried out manually via scm, followed by launching the daemon via ssh (as **root** user).
- Server on which the microservice is currently hosted: **178.170.221.13**
- Path to project on server: **/home/ETL-microservice/**
- Most actual version: **ETL_pipeline_v5**

## Usage
To run ETL on the server, you need to run the following commands.
```Console
root@SRV4XTE2GT4A8:~$ source home/ETL-microservice/venv/bin/activate
root@SRV4XTE2GT4A8:~$ cd home/ETL-microservice/ETL_pipeline_v5
root@SRV4XTE2GT4A8:~$ nohup python main.py &
```


## Logs
Logs by default are added to the UTIL.log file next to the file main.py , the logging system is implemented using python `logging`

Logs INFO example:
```Console
10/28/2023 03:08:10 PM - INFO - Created channel=1
10/28/2023 03:08:10 PM - INFO - Loop of scraping has been started 2023-10-28 15:08:10.422395
10/28/2023 03:08:10 PM - INFO - ETL process with source <Национальный банк РК> has been started
10/28/2023 03:09:13 PM - INFO - {"type":"white_list","name":"Акционерное общество ВТБ Регистратор","name_full":"">
10/28/2023 03:09:13 PM - INFO - {"type":"white_list","name":"Общество с ограниченной ответственностью \"Евроазиат>
10/28/2023 03:09:13 PM - INFO - {"type":"white_list","name":"Общество с ограниченной ответственностью \"Корпорати>
10/28/2023 03:09:13 PM - INFO - {"type":"white_list","name":"Общество с ограниченной ответственностью \"Оборонрег>
10/28/2023 03:09:13 PM - INFO - {"type":"white_list","name":"Общество с ограниченной ответственностью \"ПАРТНЁР\">
10/28/2023 03:09:13 PM - INFO - {"type":"white_list","name":"Общество с ограниченной ответственностью \"Регистрат>
...
```

Logs ERROR example:
```Console
10/28/2023 03:11:15 PM - ERROR - 6 validation errors for BaseDataUnit
legal_entity_address
  Input should be a valid string [type=string_type, input_value=nan, input_type=float]
    For further information visit https://errors.pydantic.dev/2.3/v/string_type
phones
  Input should be a valid string [type=string_type, input_value=nan, input_type=float]
    For further information visit https://errors.pydantic.dev/2.3/v/string_type
...
```