import socket
import json  # Puedes ajustar esto según el formato de tus datos
from PyQt5.QtCore import QObject, pyqtSignal
import time as tm
import os
import sys
import traceback

direccion_actual = os.getcwd().replace("\\", "/")
direccion_db = direccion_actual + "/HMI/db/"
direccion_utils = direccion_actual + "/HMI/utils/"

sys.path.insert(1, f'{direccion_db}')
sys.path.insert(1, f'{direccion_utils}')

from processes import getProcessesInNO, modifyCheckServidor
import global_variables as gv

class LeerAzureWorker(QObject):

    finished = pyqtSignal()
    progress = pyqtSignal(str)
    
    def __init__(self) -> None:
        
        super().__init__()
        
        try:
            # Definir las credenciales
            self.server = '20.106.77.209'
            self.port = 8170
            
        except Exception as e:
            print(f'Error en la conexión a Azure: ' + str(e))
            print(traceback.print_exc())
            
    def conectar_al_servidor(self, server, puerto):
        try:
            # Crear un objeto de socket
            cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Conectar al servidor
            cliente_socket.connect((server, puerto))

            # Si no se produce ninguna excepción, la conexión fue exitosa
            print("Conexión exitosa al servidor")
            return cliente_socket
        except Exception as e:
            print(f"Error al conectar al servidor: {str(e)}")
            print(traceback.print_exc())
            return None
        
    def verificar_conexion(self, cliente_socket):
        try:
            if cliente_socket is not None:
                mensaje_prueba = b"ping"
                cliente_socket.send(mensaje_prueba)
                
                gv.socket_connection = False

                # Esperar una pequeña respuesta
                respuesta = cliente_socket.recv(4)

                # Verificar si la respuesta es la esperada
                if respuesta == b"pong":
                    return True
                else:
                    raise Exception("Respuesta no válida")
            else:
                return False
        except Exception as e:
            print(f"Error al verificar conexión: {str(e)}")
            return False
        finally:
            # Restaurar el socket a su configuración original
            if cliente_socket is not None:
                cliente_socket.settimeout(None)
            else:
                return False
        
    def run(self):
        
        # Conectar al servidor
        self.cliente_socket = self.conectar_al_servidor(self.server, self.port)

        while True:
            
            try:
                
                if not self.verificar_conexion(self.cliente_socket):
                    
                    print("La conexión se ha perdido. Intentando reconectar...")
                    gv.socket_connection = False
                    
                    if self.cliente_socket is not None:
                        self.cliente_socket.close()
                    
                    self.cliente_socket = self.conectar_al_servidor(self.server, self.port)
                    
                else:
                    
                    gv.socket_connection = True
            
                    self.enviar_proceso()
                    
                tm.sleep(0.5)
                    
            except Exception as e:
                print(f'Error en la conexión a Azure: ' + str(e))
                print(traceback.print_exc())
                
    def calcular_checksum(self, trama):
        checksum = 0
        for char in trama:
            checksum += ord(char)
        return str(checksum)[-3:]
                
    def enviar_proceso(self):
        
        self.pending_processes = getProcessesInNO()
                    
        if len(self.pending_processes) > 0:
            
            for process in self.pending_processes:
                
                try:
                
                    id_process = str(process[0])
                    id_piece = str(process[1])
                    amount = str(process[2])
                    route = str(process[3])
                    date = str(process[4])
                    time = str(process[5])
                    status = str(process[6])
                    id_user = str(process[7])
                    folio_process = str(process[8])
                    check_servidor = str(process[9])
                    
                    # Construir los datos a enviar (puedes ajustar esto según tu formato)
                    trama_3 = "3,"+folio_process+","+id_piece+","+amount+","+route+","+date+time+","+status+","+id_user
                    checksum = self.calcular_checksum(trama_3)
                    trama_3 = "["+trama_3+","+str(checksum)+"]"
                    
                    print("\033[;34m"+f'Proceso {id_process} a enviar: ' + str(trama_3))
                    
                    # Enviar los datos al servidor
                    self.cliente_socket.sendall(trama_3.encode('utf-8'))
                    
                    print("\033[;32m"+f'Proceso {id_process} enviado a Azure')
                    
                    # Recibir la respuesta del servidor
                    respuesta_servidor = self.cliente_socket.recv(1024).decode('utf-8')

                    print(f'Respuesta del servidor para proceso {id_process}: {respuesta_servidor}')
                    
                    if respuesta_servidor == 'SKTOK':
                        
                        self.done = modifyCheckServidor(id_process)
                    
                        if self.done:
                            print("\033[;32m"+f'check_servidor de proceso {id_process} modificado a OK')
                        else:
                            print("\033[;31m"+f'check_servidor de proceso {id_process} no se pudo modificar')
                    else:
                        gv.socket_connection = False
                        print("\033[;31m"+f'Error en la respuesta del servidor para proceso {id_process}: {respuesta_servidor}')
                    
                except Exception as e:
                    print("\033[;31m"+f'Error enviando proceso {id_process} a Azure: ' + str(e))
                    print(traceback.print_exc())
                    gv.socket_connection = False
        else:
            print("No hay datos pendientes por enviar...")
        
        tm.sleep(0.5)