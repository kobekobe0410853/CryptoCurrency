from influxdb import InfluxDBClient

#hostStr = '127.0.0.1'
hostStr = '140.113.122.202'
portInt = 8086
usrStr = 'root'
pwdStr = '1234567890' 
DB = 'test'

try:
    client = InfluxDBClient(host=hostStr, port=portInt, username=usrStr, password=pwdStr, database=DB)
except Exception:
    print Exception
