# coding=utf-8
import re 		# Librería expresiones regulares
import urllib	# Librería para interactuar con webs
import time		# Librería para sacar fecha/hora sistema
import logging	# Librería para crear logs
from beebotte import *	# Libreria para usar beebotte
from muestra import muestra 	# Estructura de datos para almacenar en bbdd
from pymongo import MongoClient # Librería de Mongo para python
from urllib2 import Request, urlopen, URLError	# Librería para test 

#logging.basicConfig(filename='./logs/'+time.strftime("%Y%m%d")+'_write.log',level=logging.DEBUG)

var_empresa = "VODAFONE"
url = "http://www.eleconomista.es/empresa/"+var_empresa
TRAZAS = 0

req = Request(url)
try:
	response = urlopen(req)
except URLError as e:
	if hasattr(e, 'reason'):
		#logging.info(time.strftime("%H:%M:%S:")+'AppInfo: We failed to reach a server.')
		#logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Reason: %s.', e.reason)
		print 'We failed to reach a server.'
		print 'Reason: ', e.reason
	elif hasattr(e, 'code'):
		#logging.info(time.strftime("%H:%M:%S:")+'AppInfo: The server couldn\'t fulfill the request.')
		#logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Error code: %s.', e.reason)
		print 'The server couldn\'t fulfill the request.'
		print 'Error code: ', e.code
else:
	#logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Starting query for new sample.')

	# --- LECTURA DE LA WEB-------------------------------------------

	f = urllib.urlopen(url)
	data = f.read()
	f.close()

	# --- EXTRACCIÓN PARÁMETROS --------------------------------------

	patron_cotizacion = re.compile('[0-9],[0-9][0-9][0-9][0-9]')
	cotizacion = re.findall(patron_cotizacion,data)
	cotizacion=cotizacion[0]

	patron_hora_cotizacion= re.compile('class="hora_1004">.*</span>')
	hora_cotizacion = re.findall(patron_hora_cotizacion,data)
	hora_cotizacion=hora_cotizacion[0]
	hora_cotizacion=hora_cotizacion[18:26]

	fecha_cotizacion=time.strftime("%d/%m/%Y")
	hora_muestra = time.strftime("%H:%M:%S")

	# PRINT de CONTROL
	if TRAZAS:
		print("Empresa: " + var_empresa)
		print("Cotizacion: "+ cotizacion)
		print("Hora de cotizacion: "+ hora_cotizacion)
		print("Fecha de cotizacion: " + fecha_cotizacion)
		print("Hora de muestra: " + hora_muestra)


	# Dato a insertar en la bbdd
	nueva_muestra = [muestra(cotizacion,hora_cotizacion,hora_muestra,fecha_cotizacion)]


	# Conexión al Server de MongoDB Pasandole el host y el puerto por defecto
	mongoClient = MongoClient('localhost',27017)

	# Conexión a la base de datos
	db = mongoClient.Empresa

	# Obtenemos una coleccion para trabajar con ella
	collection = db.colecion_empresa

	# Inserción muestra
	for nueva_muestra in nueva_muestra:
		collection.insert(nueva_muestra.toDBCollection())

	# Cerrar la conexion
	mongoClient.close()
	#logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Insert in MongoDB done. Price: %s. Time: %s in Mongo', cotizacion, hora_cotizacion)
	# beebotte
	bclient = BBT("76a2c121dea5d551eb281ad572c9e7a0", "8127ace5f698e96720795107c4ce45cb77a8d333b46d68fb7646118cbe15589a")
	bclient.write('vodafone', 'Cotizacion', float(cotizacion.replace(',','.')))
	bclient.write('vodafone', 'Hora_cotizacion', hora_cotizacion)
	bclient.write('vodafone', 'Hora_muestra', hora_muestra)
	bclient.write('vodafone', 'Fecha', fecha_cotizacion)

	#logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Insert in Beebotte done. Price: %s. Time: %s in Mongo', cotizacion, hora_cotizacion)
	#logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Query for new sample ended.')			