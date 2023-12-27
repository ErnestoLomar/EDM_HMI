#Librerías externas
from PyQt5.QtCore import QObject, pyqtSignal
import time
import traceback
from datetime import datetime
import os
import sys
import socket

direccion_actual = os.getcwd().replace("\\", "/")
direccion_utils = direccion_actual.replace("script", "utils")

sys.path.insert(1, f'{direccion_utils}')

#Es un QObject que emite una señal cuando está hecho.
class UpdateIcons(QObject):
    try:
        finished = pyqtSignal()
        progress = pyqtSignal(dict)
    except Exception as e:
        print("Error en la clase UpdateIcons: " + str(e))
        print(traceback.format_exc())
    
    #Crea un nuevo hilo, y en ese hilo ejecuta una función que emite una señal cada segundo
    def run(self):
        try:
            while True:
                res = {}
                from global_variables import socket_connection
                
                # Obtener la fecha actual
                fecha_actual = datetime.now()

                # Formatear la fecha en el formato deseado
                fecha_formateada = fecha_actual.strftime("%Y-%m-%d")
                
                # Obtener la hora actual
                hora_actual = datetime.now().time()

                # Formatear la hora en el formato deseado
                hora_formateada = hora_actual.strftime("%H:%M:%S")
                
                res['date'] = fecha_formateada
                res['time'] = hora_formateada
                if self.check_internet_connection():
                    res['internet'] = True
                else:
                    res['internet'] = False
                res['socket_connection'] = socket_connection
                
                self.progress.emit(res)
                
                time.sleep(1)
        except Exception as e:
            print("Error en la clase UpdateIcons ejecutando: " + str(e))
            print(traceback.format_exc())
            
    def check_internet_connection(self):
        try:
            # Intentar establecer una conexión con un servidor (en este caso, Google)
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            return False
