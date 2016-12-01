# coding=utf-8

__author__ = "Ruben Martin"
__version__ = "2.5"
__email__ = "ruben.martin.montano@gmail.com"
__status__ = "Production"

#********************************************************************************#
# funciones.py 																	 #
#********************************************************************************#
#																				 #	
# - calculo_media_mongo(): devuelve la media de las cotizaciones de MongoDB  	 #
#																				 #	
# - calculo_media_beebotte(): devuelve la media de las cotizaciones de Beebotte	 #		
#																				 #	
# - calculo_media_aleatoria(it): devuelve la media de las cotizaciones de Mongo y#
#   beebotte alternativamente.												  	 #
#																				 #	
# - lectura_actual(): devuelve los valores de cotizacion, fecha y hora actuales	 #		
#																				 #	
# - comprobar_umbral(cotizacion, umbral): devuelve los valores que se encuentren #		
#	fuera del umbral introducido												 #	
#																				 #
#********************************************************************************#

# -------------------------------------------------------------------------
# Imports necesarios
# -------------------------------------------------------------------------

import re 		# Librería expresiones regulares
import urllib	# Librería para interactuar con webs
import time		# Librería para sacar fecha/hora sistema
import logging	# Librería para crear logs
from random import getrandbits 	# Librería para números aleatorios
from beebotte import *	# Libreria para usar beebotte
from muestra import muestra 	# Estructura de datos para almacenar en bbdd
from pymongo import MongoClient # Librería de Mongo para python
from urllib2 import Request, urlopen, URLError	# Librería para test 

TRAZAS = 0 # Variable de control de trazas: 1->Sí, 0->No

####################################################################################################################################

def calculo_media_mongo(): 

	mongoClient = MongoClient('localhost',27017) 	# Conexión al Server de MongoDB Pasandole el host y el puerto por defecto
	db = mongoClient.Empresa 						# Conexión a la base de datos
	collection = db.colecion_empresa 				# Obtenemos una coleccion para trabajar con ella	

	media = float(0) 						# Variable donde se almacena la media
	n_muestras = collection.find().count()  # Cuenta el número de documentos en la colección			
	
	if TRAZAS:
		print "Número de muestras en bbdd: %d\n" %(n_muestras)
	
	cursor = collection.find()	# Array con los elementos de la colección
	for fut in cursor:
		media = media + float(fut['cotizacion'].replace(',','.')) # Sumatorio de las cotizaciones
		if TRAZAS:
			print "Acumulativo local: %f\n" %(media)
	
	media = media / n_muestras	# Cálculo de la media
	if TRAZAS:
		print "Media: %f\n" %(media)
		
	mongoClient.close() # Cerrar la conexion de la bbdd
	media = round(media,4)
	return media # Devuelve la media de todos los elementos de MongoDB

####################################################################################################################################

def calculo_media_beebotte():
	
	bclient = BBT("76a2c121dea5d551eb281ad572c9e7a0", "8127ace5f698e96720795107c4ce45cb77a8d333b46d68fb7646118cbe15589a")
	records = bclient.read("vodafone", "Cotizacion", limit = 10)
	n_muestras = 10  # Últimas muestras
	media = float(0) # Variable donde se almacena la media
	for i in range(int(n_muestras)):
		dato = records[i]
		media = media + float(dato ['data']) # Sumatorio de las cotizaciones
		if TRAZAS:
			print "Acumulativo remota: %f\n" %(media)
	media = media / n_muestras	# Cálculo de la media
	if TRAZAS:
		print "Media: %f\n" %(media)
	media = round(media,4)
	return media # Devuelve la media de todos los elementos de Beebotte

####################################################################################################################################

def calculo_media_aleatoria(it):

	if it:
		if TRAZAS:
			print "MongoDB"
		media = calculo_media_mongo()
		fuente = "(Mongo)"

	else:
		if TRAZAS:
			print "Beebotte"
		media = calculo_media_beebotte()
		fuente = "(Beebotte)"

	return media, fuente # Devuelve la media, y si es de MongoDB o Beebotte

####################################################################################################################################

def lectura_actual():
	var_empresa = "VODAFONE"
	url = "http://www.eleconomista.es/empresa/"+var_empresa
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
	else:
		

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

		# PRINT de CONTROL
		if TRAZAS:
			print("Cotizacion: "+ cotizacion)
	return	cotizacion, fecha_cotizacion, hora_cotizacion # Devuelve los valores actuales

####################################################################################################################################

def comprobar_umbral(cotizacion, umbral):

	umbral = float(umbral)

	cotizacion = float(cotizacion.replace(',','.'))

	cot_max = cotizacion + cotizacion*umbral/100
	cot_min = cotizacion - cotizacion*umbral/100

	# Conexión al Server de MongoDB Pasandole el host y el puerto por defecto
	mongoClient = MongoClient('localhost',27017)

	# Conexión a la base de datos
	db = mongoClient.Empresa

	# Obtenemos una coleccion para trabajar con ella
	collection = db.colecion_empresa

	cursor = collection.find() # Lectura todos datos

	fuera_i = 0
	posts = []

	for fut in cursor:

		cot = float(fut['cotizacion'].replace(',','.'))

		fecha = fut['fecha']
		hora = fut['hora_cot']

		if cot >= cot_max:
			posts = posts + [
			{
				'cot' : cot,
				'fecha' : fecha,
				'hora'  : hora
			}]
		if cot <= cot_min:
			posts = posts + [
			{
				'cot' : cot,
				'fecha' : fecha,
				'hora'  : hora
			}]
		fuera_i = fuera_i+1
	return posts, cot_max, cot_min

####################################################################################################################################