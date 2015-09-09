import os
import glob
import time
import MySQLdb
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)

db = MySQLdb.connect("localhost", "bucket", "bucket", "brewBucket")
curs = db.cursor()


os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")

#GIT COMMENT PLEASE IGNORE


baseDir = "/sys/bus/w1/devices/"
sensorPrefix = "28-00000"
sensorIds = [sensorPrefix + "5e9d352", sensorPrefix + "65c5e41"]

def readSensor(sensorId):
	tempFile = open(baseDir + sensorId + "/w1_slave")
	sensorData = tempFile.read();
	tempFile.close()
	sensorLines = sensorData.split("\n")
	tempReadingLine = sensorLines[1].split("t=")
	return ((float(tempReadingLine[1]) / 1000) * 9.0 / 5.0 +32.0)

#def read_temp_raw():
#	catdata = subprocess.Popen(['cat', device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#	out,err = catdata.communicate()
#	out_decode = out.decode('utf-8')
#	lines = out_decode.split('\n')
#	return lines

#def read_temp():
#	lines = read_temp_raw()
#	while lines[0].strip()[-3:] != 'YES' :
#		time.sleep(0.2)
#		lines = read_temp_raw()
#	equals_pos = lines[1].find('t=')
#	if equals_pos != -1:
#		temp_string = lines[1][equals_pos+2:]
#		temp_c = float(temp_string) / 1000.0
#		temp_f = temp_c * 9.0 /5.0 +32.0
#		return temp_f


#def write_to_db(sensorVal):
#	try:
#		params = ['0001',
#			sensorVal]
#	
#		curs.execute("INSERT INTO temp_data VALUES(%s,%s,NOW())", params)
#		db.commit()
#		print ('Write OK')
#	except:
#		print('Write Fail')


print('Welcome\nPress \'s\' to start!')
cmd=str(raw_input('Command: '))

if cmd in ['s']:

	while True:
		print (time.strftime("%I:%M:%S"))
		internal = readSensor(sensorIds[0])
		external = readSensor(sensorIds[1])
		heating = "noVal"
		
		if(internal < 68.0):
			GPIO.output(24,1)
			heating = "True"
		else:
			GPIO.output(24,0)
			heating = "False"
		
		try:
			if(heating == "True"):
				heatingBool = "T"
			else:
				heatingBool = "F"
				
			params = [2, external, internal, heatingBool]
			curs.execute("INSERT INTO batchData(batchId, externalTemp, internalTemp, heating, readTime) VALUES(%s, %s, %s, %s,NOW())", params)
			db.commit()
			print("Wrote to DB!")
		except MySQLdb.Error, e:
			print("DB write failed!")
			print("[ERROR] %d: %s\n" % (e.args[0], e.args[1]))
		
		print("Internal: " + str(round(internal,2)) + "\nExternal: " + str(round(external,2)) + "\nHeating: " + heating)
		
		print("==============================")
		time.sleep(60)
	
	
		
		
	#while True:
		#write_to_db(read_temp())
		#time.sleep(60)

