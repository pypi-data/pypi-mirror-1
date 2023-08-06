#!/usr/bin/env python
'''
Created on 18/12/2009
Programa que permite colgar llamadas de un Asterisk
con mas de X tiempo.

@version: 0.0.1
@organization: Sapian SA
@author: Sebastian Rojo
'''
from Asterisk.Manager import Manager
from AsteriskChannelHangup.Config import Config

if not Config().get_max_time_for_calls():
    _tiempo_max_de_llamada = 3600
else:
    _tiempo_max_de_llamada = Config().get_max_time_for_calls()
     
def ColgarCanalesPegados(_tiempo_max_de_llamada=3600):
    ''' Esta Funcion cuelga los canales colagados en un servidor asterisk'''
    datos_de_configuracion = Config().get_connection()
    pbx = Manager(*datos_de_configuracion)
    print "se conctara conel servidor asterisk" , datos_de_configuracion[0]
    result = pbx.Status()
    uno = " ";
    contador = 0;
    for canales in result:
        status = canales.Status()
        tiempo_de_llamada = status.get("Seconds")
        if type(tiempo_de_llamada) == type(uno):
            if int(tiempo_de_llamada) > int(_tiempo_max_de_llamada):
                if contador == 0:
                    contador = 1
                    print "hay canales con mas de ", _tiempo_max_de_llamada \
                    , "Segundos"
                print "el canal", canales.id, "tiene ", tiempo_de_llamada, \
                 "segundos. sera colgada en este instante";    
                #canales.Hangup()
            else:
                print "el canal ", canales.id, "tiene", tiempo_de_llamada
        else:
            print "el canal ", canales.id, "no tiene tiempo"

if __name__ == '__main__':
    ColgarCanalesPegados(_tiempo_max_de_llamada)
    pass
