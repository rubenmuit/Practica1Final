# coding=utf-8

#********************************************************************************#
# update.py 																	 #
#********************************************************************************#
#																				 #	
# - Este script es orquestado por un cron que se ejecuta entre las 8 - 18 cada   #
#   2 minutos de lunes a viernes.												 #
#																				 #
# - Obtiene los valores de la cotizacion, fecha y hora de la bolsa de VODAFONE,  #
#   y lo inserta en una bd local (MongoDB) y bd remota (Beebotte).				 #
#																				 #
#********************************************************************************#

__author__ = "Ruben Martin"
__version__ = "3.0"
__email__ = "ruben.martin.montano@gmail.com"
__status__ = "Production"

# -------------------------------------------------------------------------
# Imports necesarios
# -------------------------------------------------------------------------

import re 		# Librería expresiones regulares
import urllib	# Librería para interactuar con webs
import time		# Librería para sacar fecha/hora sistema
import logging	# Librería para crear logs
from beebotte import *	# Libreria para usar beebotte
from muestra import muestra 	# Estructura de datos para almacenar en bbdd
from pymongo import MongoClient # Librería de Mongo para python
from urllib2 import Request, urlopen, URLError	# Librería para test 

# --------------------------------------------------------------------------
# Comprobamos que la hora se encuentra entre las 8:30 y las 17:30. (Bolsa abierta)
# --------------------------------------------------------------------------

hora_actual= time.strftime("%H:%M:%S")
hora_flag = int(hora_actual[0:2])
minuto_flag = int(hora_actual[3:5])

if hora_flag == 8 and minuto_flag >= 30:
	flag = int(1)
else:
	if hora_flag > 8 and hora_flag < 17:
		flag = int(1)
	else:
		if hora_flag ==17 and minuto_flag <=30:
			flag = int(1)
		else:
			flag = int(0)

# --------------------------------------------------------------------------
# Si la hora se encuentra entre las 8:30 y las 17:30, flag = 1 y se ejecuta
# lo siguiente.
# --------------------------------------------------------------------------

if flag:

	logging.basicConfig(filename='/home/ruben/MUIT/Practica1Final/logs/'+time.strftime("%Y%m%d")+'_write.log',level=logging.DEBUG)

	var_empresa = "VODAFONE" # Empresa de la cotizacion
	url = "http://www.eleconomista.es/empresa/"+var_empresa # URL donde obtener los datos
	TRAZAS = 0 # Debug: 1-Activado, 0-Desactivado

	# --------------------------------------------------------------------------
	# Comprobamos que no hay problemas de conexion
	# --------------------------------------------------------------------------

	req = Request(url)
	try:
		response = urlopen(req)
	except URLError as e:
		if hasattr(e, 'reason'):
			logging.info(time.strftime("%H:%M:%S:")+'AppInfo: We failed to reach a server.')
			logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Reason: %s.', e.reason)
			print 'We failed to reach a server.'
			print 'Reason: ', e.reason
		elif hasattr(e, 'code'):
			logging.info(time.strftime("%H:%M:%S:")+'AppInfo: The server couldn\'t fulfill the request.')
			logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Error code: %s.', e.reason)
			print 'The server couldn\'t fulfill the request.'
			print 'Error code: ', e.code
	else: # En caso de que la web esté disponible se ejecuta lo siguiente.
		
		logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Starting query for new sample.')

		# --------------------------------------------------------------------------
		# Lectura de la Web
		# --------------------------------------------------------------------------

		f = urllib.urlopen(url)
		data = f.read()
		f.close()

		# --------------------------------------------------------------------------
		# Extraccion de parametros de la Web anterior
		# --------------------------------------------------------------------------

		patron_cotizacion = re.compile('[0-9],[0-9][0-9][0-9][0-9]')
		cotizacion = re.findall(patron_cotizacion,data)
		cotizacion = cotizacion[0] 						# Valor de la cotizacion leida
		patron_hora_cotizacion= re.compile('class="hora_1004">.*</span>')
		hora_cotizacion = re.findall(patron_hora_cotizacion,data)
		hora_cotizacion = hora_cotizacion[0]
		hora_cotizacion = hora_cotizacion[18:26] 		# Hora de la cotizacion
		fecha_cotizacion = time.strftime("%d/%m/%Y")	# Fecha de la cotizacion 
		hora_muestra = time.strftime("%H:%M:%S")		# Hora de la muestra

		if TRAZAS:
			print("Empresa: " + var_empresa)
			print("Cotizacion: "+ cotizacion)
			print("Hora de cotizacion: "+ hora_cotizacion)
			print("Fecha de cotizacion: " + fecha_cotizacion)
			print("Hora de muestra: " + hora_muestra)

		# --------------------------------------------------------------------------
		# MongoDB
		# --------------------------------------------------------------------------

		nueva_muestra = [muestra(cotizacion,hora_cotizacion,hora_muestra,fecha_cotizacion)] # Dato a insertar en la bbdd		
		mongoClient = MongoClient('localhost',27017) # Conexión al Server de MongoDB Pasandole el host y el puerto por defecto
		db = mongoClient.Empresa 			# Conexión a la base de datos Empresa
		collection = db.colecion_empresa 	# Obtenemos la coleccion "colecion_empresa" donde se almacenan los datos

		# Inserción del dato obtenido
		for nueva_muestra in nueva_muestra:
			collection.insert(nueva_muestra.toDBCollection())
		
		mongoClient.close() # Cerrar la conexion con MongoDB
		logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Insert in MongoDB done. Price: %s. Time: %s in Mongo', cotizacion, hora_cotizacion)

		# --------------------------------------------------------------------------
		# Beebotte
		# --------------------------------------------------------------------------	

		bclient = BBT("76a2c121dea5d551eb281ad572c9e7a0", "8127ace5f698e96720795107c4ce45cb77a8d333b46d68fb7646118cbe15589a") # API Key, Secret Key
		bclient.write('vodafone', 'Cotizacion', float(cotizacion.replace(',','.'))) # Inserta cotizacion
		bclient.write('vodafone', 'Hora_cotizacion', hora_cotizacion)		# Inserta la hora de la cotizacion
		bclient.write('vodafone', 'Hora_muestra', hora_muestra)				# Inserta la hora de la muestra
		bclient.write('vodafone', 'Fecha', fecha_cotizacion)				# Inserta la fecha de la cotizacion

		logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Insert in Beebotte done. Price: %s. Time: %s in Mongo', cotizacion, hora_cotizacion)
		logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Query for new sample ended.')	

# --------------------------------------------------------------------------EOF