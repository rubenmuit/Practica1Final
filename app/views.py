#!/usr/bin/python
# -*- encoding: utf-8 -*-

__author__ = "Ruben Martin"
__version__ = "8.0"
__email__ = "ruben.martin.montano@gmail.com"
__status__ = "Production"

#********************************************************************************#
# views.py																		 #
#********************************************************************************#
#																				 #		
# Devuelve los valores de la aplicacion al cliente web							 #
#																				 #	
#********************************************************************************#

# -------------------------------------------------------------------------
# Imports necesarios
# -------------------------------------------------------------------------

from flask import render_template
from flask import request
from app import app
from funciones import calculo_media_mongo		# Calcular media MongoDB
from funciones import calculo_media_beebotte	# Calcular media Beebotte
from funciones import calculo_media_aleatoria	# Calcula media alternativa
from funciones import lectura_actual			# Lectura actual de cotizacion
from funciones import comprobar_umbral			# Comprueba cotizaciones fuera del umbral introducido
import time		# Librería para sacar fecha/hora sistema
import logging	# Librería para crear logs

# -------------------------------------------------------------------------
# Al cargar la pagina
# -------------------------------------------------------------------------
logging.basicConfig(filename='/home/ruben/MUIT/Practica1Final/logs/'+time.strftime("%Y%m%d")+'_web.log',level=logging.DEBUG)
@app.route('/')
def index():
	logging.info(time.strftime("%H:%M:%S:")+'AppInfo: New User.')	
	it = int(0)
	print it
	cot_actual, fecha_actual, hora_actual = lectura_actual() # Lectura cot actual
	Valor_media = ""
	mn = cot_actual
	mx = cot_actual
	try:
		posts
	except:	
		# Devolvemos al HTML:
		return render_template("index.html",
							   title='Cotizacion Vodafone',
							   valor_media=Valor_media,
							   cot_actual=cot_actual,
							   fecha_actual=fecha_actual,
							   hora_actual=hora_actual,
							   it=it,
							   post={},
							   mn=mn,
							   mx=mx)
	posts = request.posts
	# Devolvemos al HTML:
	return render_template("index.html",
						   title='Cotizacion Vodafone',
						   user=user,
						   valor_media=Valor_media,
						   cot_actual=cot_actual,
						   fecha_actual=fecha_actual,
						   hora_actual=hora_actual,
						   posts=posts, 
						   mn=mn, 
						   mx=mx)

# -------------------------------------------------------------------------
# Al pulsar un boton
# -------------------------------------------------------------------------

@app.route('/', methods=['POST'])
def pulso():
	cot_actual, fecha_actual, hora_actual = lectura_actual() # Lectura cot actual
	# -------------------------------------------------------------------------
	# Estado actual de las variables
	# -------------------------------------------------------------------------
	it = int(request.form['it']) 				# 1-> Mongo, 0-> Beebotte
	boton = request.form 						# Determina el boton pulsado
	text_media = request.form['text_media']		# Contenido campo de texto media
	text_umbral = request.form['text_umbral']	# Contenido campo de texto umbral

	# -------------------------------------------------------------------------
	# Boton media
	# -------------------------------------------------------------------------

	if 'boton_media' in boton:
		logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Mean requested.')

		if it:
			it = int(0) # Not it
		else:
			it = int(1) # Not it
		try:
			float(text_umbral)
		except:
			mn = cot_actual
			mx = cot_actual
			Valor_media, fuente_media = calculo_media_aleatoria(it) # Actualizamos valores
			# Devolvemos al HTML:
			return render_template("index.html",
					   title='Cotizacion Vodafone',
					   valor_media=Valor_media,
					   fuente_media = fuente_media,
					   text_umbral=text_umbral,
					   cot_actual=cot_actual,
					   fecha_actual=fecha_actual,
					   hora_actual=hora_actual,
					   it=it,
					   mn=mn,
					   mx=mx)
		else:

			mn = float(cot_actual.replace(',','.')) - float(text_umbral) * float(cot_actual.replace(',','.'))/100
			mx = float(cot_actual.replace(',','.')) + float(text_umbral) * float(cot_actual.replace(',','.'))/100
			Valor_media, fuente_media = calculo_media_aleatoria(it) # Actualizamos valores
			# Devolvemos al HTML:
			return render_template("index.html",
					   title='Cotizacion Vodafone',
					   valor_media=Valor_media,
					   fuente_media = fuente_media,
					   text_umbral=text_umbral,
					   cot_actual=cot_actual,
					   fecha_actual=fecha_actual,
					   hora_actual=hora_actual,
					   it=it,
					   mn=mn,
					   mx=mx)

	# -------------------------------------------------------------------------
	# Boton umbral
	# -------------------------------------------------------------------------

	if 'boton_umbral' in boton:
		logging.info(time.strftime("%H:%M:%S:")+'AppInfo: Umbral inserted.')
		Valor_media = text_media[0:6]
		fuente_media = text_media[7:len(text_media)]
		# Comprobar si el campo umbral es un numero del 1 al 100
		try:
			text_umbral = float(text_umbral)
		except:
			text_umbral = "Error"
			print text_umbral
			posts = {}
			mn = cot_actual
			mx = cot_actual
		else:
			if text_umbral >= 0:
				if text_umbral <= 100:
					posts, mx, mn = comprobar_umbral(cot_actual,text_umbral)
				else:
					text_umbral = "Error"
					posts = {}
					mn = cot_actual
					mx = cot_actual
			else:
				text_umbral = "Error"
				posts = {}	
				mn = cot_actual
				mx = cot_actual

		# Devolvemos al HTML:
		return render_template("index.html",
					   title='Cotizacion Vodafone',
					   valor_media=Valor_media,
					   fuente_media = fuente_media,
					   text_umbral=text_umbral,
					   cot_actual=cot_actual,
					   fecha_actual=fecha_actual,
					   hora_actual=hora_actual,
					   posts = posts,
					   it=it,
					   mx=mx, 
					   mn=mn)

	# -------------------------------------------------------------------------
	# Boton graficas
	# -------------------------------------------------------------------------

	if 'boton_graficas' in boton:
		logging.info(time.strftime("%H:%M:%S:")+'AppInfo: URL:Beebotte.')
		Valor_media = text_media[0:6]
		fuente_media = text_media[7:len(text_media)]


