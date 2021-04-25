# API

from flask import Flask, request, make_response, jsonify
import configparser 
import os
import logging as log
import mysql.connector as mc 
import datetime


configFile = "/config.cfg"

config = configparser.ConfigParser()
path = os.path.dirname(os.path.realpath(__file__)) #current path
config.read(f'{path}'+configFile)

#variables
logFile = config['DEFAULT']['LOG_FILE']
logLevel = config['DEFAULT']['LOG_LEVEL']
db = config['MYSQL_DB']['DB']
dbUser = config['MYSQL_DB']['USER']
dbPasswd = config['MYSQL_DB']['PASSWORD']
dbTable = config['MYSQL_DB']['TABLE']
dbHost = config['MYSQL_DB']['HOST']
appHost = config['APP']['HOST']
appPort = config['APP']['PORT']

log.basicConfig(filename = logFile, level=logLevel)


def mysqlConn():
	try:
		return mc.connect(user=dbUser, password=dbPasswd, host=dbHost, database=db, auth_plugin="mysql_native_password")
	except Exception as e:
		log.info("Mysql database connection " + str(datetime.datetime.now()) + " --> " + str(e))


def createTable(db):
	try:
		query = "CREATE TABLE IF NOT EXISTS " + dbTable + " (id INT NOT NULL AUTO_INCREMENT, name VARCHAR(30), lastname VARCHAR(30), email VARCHAR(100), PRIMARY KEY (id));"
		cursor = db.cursor(buffered=True)
		cursor.execute(query)
	except Exception as e:
		log.error("Database Table Create " + str(datetime.datetime.now()) + " --> "+ str(e))



app = Flask(__name__)


@app.route('/select', methods=['GET'])
def selectEndpoint():
	mysqlDb = mysqlConn()
	if mysqlDb != None:
		try:
			andFlag = 0;
			q = "SELECT * FROM " + f"{db}.{dbTable}"
			
			name = request.args.get("name")
			if name != None:
				q += f" WHERE name = '{name}' "
				andFlag = 1
			lname = request.args.get("lastname")
			if lname != None:
				if andFlag:
					q += f"and lastname = '{lname}' "
				else:
					q += f" WHERE name = '{name}' "
				andFlag = 1
			email = request.args.get("email")
			if email != None:
				if andFlag:
					q += f"and email = '{email}' "
				else:
					q += f" WHERE email = '{email}' "

			cursor = mysqlDb.cursor(buffered=True)
			cursor.execute(q) #run query
			res = cursor.fetchall() # get result
			mysqlDb.close()
			return jsonify(res)

		except mc.Error as e: 
			log.error("Select Endpoint - Database " + str(datetime.datetime.now()) + " --> " + str(e))
		except Exception as e:
			log.error("Select Endpoint - Non-relation with Database " + str(datetime.datetime.now()) + " --> " + str(e))

	return make_response('', 404) 	


@app.route('/insert', methods=['PUT', 'POST'])
def insertEndpoint():
	mysqlDb = mysqlConn()
	if mysqlDb != None:
		try:
			name = request.get_json()["name"]
			lname = request.get_json()["lastname"]
			email = request.get_json()["email"]
			q = "INSERT INTO " + db + "." + dbTable + f" (name, lastname, email) VALUES ('{name}','{lname}','{email}');"

			cursor = mysqlDb.cursor(buffered=True)
			cursor.execute(q)
			mysqlDb.commit()
			mysqlDb.close()
			return "SUCCESS"

		except Exception as e: 
			log.info("Insert Endpoint " + str(datetime.datetime.now()) + " --> " + str(e));

	return make_response('', 404) # get 500 when no return value,
	

@app.route('/delete', methods=['DELETE'])
def deleteEndpoint():
	mysqlDb = mysqlConn()
	if mysqlDb != None:
		try:			
			name = request.get_json()["name"]
			lname = request.get_json()["lastname"]
			email = request.get_json()["email"]
			q = "DELETE FROM " + f"{db}.{dbTable} WHERE name = '{name}' and lastname = '{lname}' and email = '{email}'"

			cursor = mysqlDb.cursor(buffered=True)
			cursor.execute(q)
			mysqlDb.commit()
			mysqlDb.close()
			return "SUCCESS"

		except Exception as e:
			log.error("Delete Endpoint " + str(datetime.datetime.now()) + " --> " + str(e))

	return make_response('', 404) 


if __name__ =="__main__":
	mysqlDb = mysqlConn()
	if mysqlDb != None:
		createTable(mysqlDb)
		try:
			mysqlDb.close()
		except Exception as e:
			log.error("Mysql database close --> ", str(e))
	try:
		app.run(host=appHost, port=appPort, debug=True)
	except Exception as e:
		log.error("Application --> ",str(e))


































