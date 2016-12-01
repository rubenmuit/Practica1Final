# -*- coding: utf-8 -*-
class muestra:

    def __init__(self, cotizacion, hora_cot, hora_muestra, fecha):
        self.cotizacion= cotizacion
        self.hora_cot = hora_cot
        self.hora_muestra = hora_muestra
        self.fecha = fecha
    

    def toDBCollection (self):
        return {
            "cotizacion":self.cotizacion,
            "hora_cot":self.hora_cot,
            "hora_muestra": self.hora_muestra,
            "fecha":self.fecha,
        }

    def __str__(self):
        return "cotizacion: %s - hora_cot: %s - hora_muestra: %s - fecha: %s " \
               %(self.cotizacion, self.hora_cot, self.hora_muestra, self.fecha)