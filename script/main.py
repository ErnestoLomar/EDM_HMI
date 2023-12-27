from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import sys
from PyQt5.QtWidgets import QWidget
import traceback
from datetime import datetime
import time as tm
from functools import partial
import RPi.GPIO as GPIO
import subprocess
import ntplib

direccion_actual = os.getcwd().replace("\\", "/")
direccion_design = direccion_actual + "/HMI/design/"
direccion_img = direccion_actual + "/HMI/img/"
direccion_db = direccion_actual + "/HMI/db/"
direccion_thread = direccion_actual + "/HMI/threads/"

sys.path.insert(1, f'{direccion_db}')
sys.path.insert(1, f'{direccion_thread}')

zumbador = 7
relevador = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(relevador, GPIO.OUT)
GPIO.setup(zumbador, GPIO.OUT)

iteracion = 0.03
pin_profundidad_1 = 29
pin_profundidad_2 = 23
pin_profundidad_3 = 21
pin_profundidad_4 = 19
pin_altura_1 = 37
pin_altura_2 = 35
pin_altura_3 = 33
pin_altura_4 = 31

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_profundidad_1, GPIO.OUT)
GPIO.setup(pin_profundidad_2, GPIO.OUT)
GPIO.setup(pin_profundidad_3, GPIO.OUT)
GPIO.setup(pin_profundidad_4, GPIO.OUT)
GPIO.setup(pin_altura_1, GPIO.OUT)
GPIO.setup(pin_altura_2, GPIO.OUT)
GPIO.setup(pin_altura_3, GPIO.OUT)
GPIO.setup(pin_altura_4, GPIO.OUT)

from pieces import getPieceByAlphabeticalOrder, getAllPiecesOrderByTypeMaterial, getPiecesWithClassificationSize, getPieceByName, getPieceByClient, getPieceByDistincMaterial
from clients import getAllClients, getClientByName
from processes import insertProcess, insertProcessHistory, getLastProcessHistory
from azure import LeerAzureWorker
from update_icons import UpdateIcons

class Main(QWidget):

    def __init__(self):
        
        super(Main, self).__init__()
        
        try:
            global direccion_design
            
            self.setGeometry(0, 0, 800, 480)
            self.setWindowFlags(Qt.FramelessWindowHint)
            uic.loadUi(f"{direccion_design}/main.ui", self)
            
            self.lbl_size1.mousePressEvent = self.loadWindowSize
            self.lbl_size2.mousePressEvent = self.loadWindowSize
            
            self.lbl_type1.mousePressEvent = self.loadWindowType
            self.lbl_type2.mousePressEvent = self.loadWindowType
            
            self.lbl_enterprises1.mousePressEvent = self.loadWindowEnterprises
            self.lbl_enterprises2.mousePressEvent = self.loadWindowEnterprises
            
            self.lbl_alphabet1.mousePressEvent = self.loadWindowAlphabet
            self.lbl_alphabet2.mousePressEvent = self.loadWindowAlphabet
            
            self.lbl_manual.mousePressEvent = self.loadWindowManual
            
            self.wifi_flag = False
            self.socket_flag = False
            
            self.runLeerAzure()
            self.runUpdateIcons()
            
        except Exception as e:
            print("Error en la clase Main: " + str(e))
            print(traceback.format_exc())
            
    def reportProgressIcons(self, res):
        try:
            date = res['date']
            time = res['time']
            self.lbl_date_time.setText(f"{date} {time}")
            
            socket_connection = res['socket_connection']
            if socket_connection:
                self.lbl_socket.show()
                self.lbl_socket.setPixmap(QPixmap(f"{direccion_img}/computacion-en-la-nube.png"))
            else:
                self.lbl_socket.setPixmap(QPixmap(f"{direccion_img}/sin-conexion.png"))
                if self.socket_flag:
                    self.lbl_socket.hide()
                else:
                    self.lbl_socket.show()
                self.socket_flag = not self.socket_flag
                
            if res['internet']:
                self.lbl_wifi.show()
                self.lbl_wifi.setPixmap(QPixmap(f"{direccion_img}/wifi.png"))
            else:
                self.lbl_wifi.setPixmap(QPixmap(f"{direccion_img}/no-wifi.png"))
                if self.wifi_flag:
                    self.lbl_wifi.hide()
                else:
                    self.lbl_wifi.show()
                self.wifi_flag = not self.wifi_flag
        except Exception as e:
            print("Error al actualizar los iconos: " + str(e))
            print(traceback.format_exc())

    def runUpdateIcons(self):
        try:
            self.iconosThread = QThread()
            self.iconosWorker = UpdateIcons()
            self.iconosWorker.moveToThread(self.iconosThread)
            self.iconosThread.started.connect(self.iconosWorker.run)
            self.iconosWorker.finished.connect(self.iconosThread.quit)
            self.iconosWorker.finished.connect(self.iconosWorker.deleteLater)
            self.iconosThread.finished.connect(self.iconosThread.deleteLater)
            self.iconosWorker.progress.connect(self.reportProgressIcons)
            self.iconosThread.start()
        except Exception as e:
            print("Error al iniciar el hilo de iconos: " + str(e))
            print(traceback.format_exc())
            
    def loadWindowManual(self, event):
        try:
            self.production_window = Production("", "", True)
            self.production_window.show()
        except Exception as e:
            print("Error en la clase Main cargando ventana manual: " + str(e))
            print(traceback.format_exc())
    
    def loadWindowSize(self, event):
        try:
            self.window_size = options("size")
            self.window_size.show()
        except Exception as e:
            print("Error en la clase Main cargando ventana size: " + str(e))
            print(traceback.format_exc())
        
    def loadWindowType(self, event):
        try:
            self.window_type = options("type")
            self.window_type.show()
        except Exception as e:
            print("Error en la clase Main cargando ventana type: " + str(e))
            print(traceback.format_exc())
            
    def loadWindowEnterprises(self, event):
        try:
            self.window_enterprises = options("enterprises")
            self.window_enterprises.show()
        except Exception as e:
            print("Error en la clase Main cargando ventana enterprises: " + str(e))
            print(traceback.format_exc())
            
    def loadWindowAlphabet(self, event):
        try:
            self.window_type = alphabet()
            self.window_type.show()
            self.window_type.obtener_dimensiones_bk_keyboard()
        except Exception as e:
            print("Error en la clase Main cargando ventana type: " + str(e))
            print(traceback.format_exc())
            
    def reportProgressAzure(self, res: str):
        try:
            print("Progreso de Azure: " + res)
        except Exception as e:
            print("Error en la clase Main reportando progreso de Azure: " + str(e))
            print(traceback.format_exc())

    def runLeerAzure(self):
        try:
            self.azureThread = QThread()
            self.azureWorker = LeerAzureWorker()
            self.azureWorker.moveToThread(self.azureThread)
            self.azureThread.started.connect(self.azureWorker.run)
            self.azureWorker.finished.connect(self.azureThread.quit)
            self.azureWorker.finished.connect(self.azureWorker.deleteLater)
            self.azureThread.finished.connect(self.azureThread.deleteLater)
            self.azureWorker.progress.connect(self.reportProgressAzure)
            self.azureThread.start()
        except Exception as e:
            print("Error en la clase Main ejecutando Azure: " + str(e))
            print(traceback.format_exc())
            
            
            
            
            
            
            
        
class ProductoWidget(QDialog):
    
    productoClicked = pyqtSignal(str)
    
    def __init__(self, nombre, ancho, alto, profundidad, imagen_path, parent=None):
        
        super(ProductoWidget, self).__init__(parent)

        try:
            # Configurar elementos del producto
            self.nombre = nombre
            nombre_label = QLabel(f"Nombre: {nombre}")
            nombre_label.setStyleSheet("font-size: 18px;")
            ancho_label = QLabel(f"Ancho: {ancho}")
            ancho_label.setStyleSheet("font-size: 18px;")
            alto_label = QLabel(f"Alto: {alto}")
            alto_label.setStyleSheet("font-size: 18px;")
            profundidad_label = QLabel(f"Profundidad: {profundidad}")
            profundidad_label.setStyleSheet("font-size: 18px;")
            imagen_label = QLabel(self)
            imagen_label.setPixmap(imagen_path.scaled(100, 100, aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation))

            # Configurar el diseño del widget
            layout = QVBoxLayout(self)
            layout.addWidget(nombre_label)
            layout.addWidget(ancho_label)
            layout.addWidget(alto_label)
            layout.addWidget(profundidad_label)
            layout.addWidget(imagen_label)
            
            self.setStyleSheet("background-color: #accc7b; color: #000; border-radius: 10px;")
            
            # Conectar la señal clicked a la función personalizada
            self.mousePressEvent = self.emitClickedSignal
            
        except Exception as e:
            print("Error en la clase ProductoWidget: " + str(e))
            print(traceback.format_exc())
            
    def emitClickedSignal(self, event):
        # Emitir la señal con información adicional (nombre del producto)
        self.productoClicked.emit(self.nombre)
        
        
        
        
        
        
        


class size_and_type(QWidget):
    
    def __init__(self,type_window, signal_close_window, option):
        
        super(size_and_type, self).__init__()
        
        try:
            global direccion_design, direccion_img
            
            self.setGeometry(0, 0, 800, 480)
            self.setWindowFlags(Qt.FramelessWindowHint)
            uic.loadUi(f"{direccion_design}/size_and_type.ui", self)
            # Bloquea la interacción con otras partes de la aplicación
            self.setWindowModality(Qt.ApplicationModal)
            
            self.type_window = type_window
            self.signal_close_window = signal_close_window
            self.option = option
            self.resultadoKB = ""
            
            self.setProducts(self.type_window)
            
            self.btn_regresar.mousePressEvent = self.regresar
            
        except Exception as e:
            print("Error en la clase size_and_type: " + str(e))
            print(traceback.format_exc())
        
    def setProducts(self, type_window):
        
        try:
            # Crear ventana principal
            main_layout = QVBoxLayout(self.products)

            # Crear área de desplazamiento
            scroll_area = QScrollArea(self.products)
            scroll_content = QWidget()
            scroll_content_layout = QGridLayout(scroll_content)
            
            if type_window == "size":
                
                self.lbl_orderby.setText("Ordenado por tamaño")
                
                self.all_pieces_by_size = getPiecesWithClassificationSize(self.option)
                
                #print("Piezas por tamaño: ", self.all_pieces_by_size)
                
                # Agregar widgets de productos al diseño de cuadrícula
                num_columnas = 2
                for i in range(len(self.all_pieces_by_size)):
                    producto_widget = ProductoWidget(
                        nombre=f"{self.all_pieces_by_size[i][1]}", # Nombre de la pieza
                        ancho=f"{self.all_pieces_by_size[i][3]}", # Ancho de la pieza
                        alto=f"{self.all_pieces_by_size[i][4]}", # Alto de la pieza
                        profundidad=f"{self.all_pieces_by_size[i][5]}", # Profundidad de la pieza
                        imagen_path=QPixmap(f"{direccion_img}/{str(self.all_pieces_by_size[i][1]).lower()}.png")  # Reemplaza con la ruta real de la imagen
                    )
                    fila = i // num_columnas
                    columna = i % num_columnas
                    scroll_content_layout.addWidget(producto_widget, fila, columna)
                    
                    # Conectar la señal clicked al método productoClickeado
                    producto_widget.productoClicked.connect(self.productoClickeado)
                    
            elif type_window == "type":
                
                self.lbl_orderby.setText("Ordenado por tipo de metal")
                
                self.all_pieces_by_type = getAllPiecesOrderByTypeMaterial(self.option)
                
                # Agregar widgets de productos al diseño de cuadrícula
                num_columnas = 2
                for i in range(len(self.all_pieces_by_type)):
                    producto_widget = ProductoWidget(
                        nombre=f"{self.all_pieces_by_type[i][1]}", # Nombre de la pieza
                        ancho=f"{self.all_pieces_by_type[i][3]}", # Ancho de la pieza
                        alto=f"{self.all_pieces_by_type[i][4]}", # Alto de la pieza
                        profundidad=f"{self.all_pieces_by_type[i][5]}", # Profundidad de la pieza
                        imagen_path=QPixmap(f"{direccion_img}/{str(self.all_pieces_by_type[i][1]).lower()}.png")  # Reemplaza con la ruta real de la imagen
                    )
                    fila = i // num_columnas
                    columna = i % num_columnas
                    scroll_content_layout.addWidget(producto_widget, fila, columna)
                    
                    # Conectar la señal clicked al método productoClickeado
                    producto_widget.productoClicked.connect(self.productoClickeado)
                    
            elif type_window == "enterprises":
                
                self.lbl_orderby.setText(f"Ordenado por cliente {self.option}")
                
                self.client = getClientByName(self.option)
                
                self.all_pieces_by_client = getPieceByClient(self.client[0])
                
                # Agregar widgets de productos al diseño de cuadrícula
                num_columnas = 2
                for i in range(len(self.all_pieces_by_client)):
                    producto_widget = ProductoWidget(
                        nombre=f"{self.all_pieces_by_client[i][1]}", # Nombre de la pieza
                        ancho=f"{self.all_pieces_by_client[i][3]}", # Ancho de la pieza
                        alto=f"{self.all_pieces_by_client[i][4]}", # Alto de la pieza
                        profundidad=f"{self.all_pieces_by_client[i][5]}", # Profundidad de la pieza
                        imagen_path=QPixmap(f"{direccion_img}/{str(self.all_pieces_by_client[i][1]).lower()}.png")  # Reemplaza con la ruta real de la imagen
                    )
                    fila = i // num_columnas
                    columna = i % num_columnas
                    scroll_content_layout.addWidget(producto_widget, fila, columna)
                    
                    # Conectar la señal clicked al método productoClickeado
                    producto_widget.productoClicked.connect(self.productoClickeado)

            scroll_area.setStyleSheet("QScrollArea { background-color: #fff; }"
                                    "QScrollBar:vertical { width: 35px; background-color: darkgray; }"
                                    "QScrollBar:horizontal { height: 15px; background-color: darkgray; }")
            # Configurar el área de desplazamiento
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(scroll_content)

            # Agregar el área de desplazamiento al diseño principal
            main_layout.addWidget(scroll_area)
            
        except Exception as e:
            print("Error en la clase size_and_type cargando productos: " + str(e))
            print(traceback.format_exc())
    
    def mostrar_teclado_numerico(self, piece):
        teclado = numeric_keyboard(piece)
        if teclado.exec_() == QDialog.Accepted:
            self.resultadoKB = teclado.resultado
    
    def productoClickeado(self, nombre_producto):
        # Función que se ejecutará cuando se haga clic en un producto
        #print(f"Producto {nombre_producto} clickeado")
        
        self.signal_close_window.emit()
        self.close()
        
        self.mostrar_teclado_numerico(nombre_producto)
        
        #print(self.resultadoKB)
        
        if self.resultadoKB != "cancelar":
            self.production_window = Production(nombre_producto, self.resultadoKB)
            self.production_window.show()
    
    def regresar(self, event):
        self.close()
        
        
        
        
        
        
        
        
class ClientWidget(QDialog):
    
    clientClicked = pyqtSignal(str)
    
    def __init__(self, nombre, imagen_path, parent=None):
        
        super(ClientWidget, self).__init__(parent)

        try:
            # Configurar elementos del producto
            self.nombre = nombre
            nombre_label = QLabel(nombre)
            nombre_label.setStyleSheet("font-size: 20px;")
            imagen_label = QLabel(self)
            imagen_label.setPixmap(imagen_path.scaled(100, 100, aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation))

            # Configurar el diseño del widget
            layout = QVBoxLayout(self)
            layout.addWidget(nombre_label)
            layout.addWidget(imagen_label)
            
            self.setStyleSheet("background-color: #accc7b; color: #000; border-radius: 10px;")
            
            # Conectar la señal clicked a la función personalizada
            self.mousePressEvent = self.emitClickedSignal
            
        except Exception as e:
            print("Error en la clase ClientWidget: " + str(e))
            print(traceback.format_exc())
            
    def emitClickedSignal(self, event):
        # Emitir la señal con información adicional (nombre del producto)
        self.clientClicked.emit(self.nombre)
        
        
        
        
        
        
        
        
        
class options(QWidget):
    
    close_window = pyqtSignal()
    
    def __init__(self, type_window):
        
        super(options, self).__init__()
        
        try:
            global direccion_design, direccion_img
            
            self.setGeometry(0, 0, 800, 480)
            self.setWindowFlags(Qt.FramelessWindowHint)
            uic.loadUi(f"{direccion_design}/size_and_type.ui", self)
            # Bloquea la interacción con otras partes de la aplicación
            self.setWindowModality(Qt.ApplicationModal)
            
            self.btn_regresar.mousePressEvent = self.regresar
            self.window_type = type_window
            self.close_window.connect(self.close)
            
            self.setOptions()
            
        except Exception as e:
            print("Error en la clase size_and_type: " + str(e))
            print(traceback.format_exc())
            
    def setOptions(self):
        
        try:
            
            if self.window_type == "enterprises":
                
                self.lbl_orderby.setText("Ordenado por empresas")
                
                # Crear ventana principal
                main_layout = QVBoxLayout(self.products)

                # Crear área de desplazamiento
                scroll_area = QScrollArea(self.products)
                scroll_content = QWidget()
                scroll_content_layout = QGridLayout(scroll_content)
                
                self.all_clients = getAllClients()
                
                # Agregar widgets de productos al diseño de cuadrícula
                num_columnas = 2
                
                for i in range(len(self.all_clients)):
                    
                    nombre = self.all_clients[i][1]
                    img = f"{direccion_img}/"+f"{nombre}".replace("/","-")+".png"
                    
                    client_widget = ClientWidget(
                        nombre= f"{self.all_clients[i][1]}", # Nombre de la pieza
                        imagen_path=QPixmap(img)  # Reemplaza con la ruta real de la imagen
                    )
                    fila = i // num_columnas
                    columna = i % num_columnas
                    scroll_content_layout.addWidget(client_widget, fila, columna)
                    
                    # Conectar la señal clicked al método productoClickeado
                    client_widget.clientClicked.connect(self.optionClickeado)
            
            elif self.window_type == "size":
                
                self.lbl_orderby.setText("Ordenado por tamaño")
                
                # Crear ventana principal
                main_layout = QVBoxLayout(self.products)

                # Crear área de desplazamiento
                scroll_area = QScrollArea(self.products)
                scroll_content = QWidget()
                scroll_content_layout = QGridLayout(scroll_content)
                
                # Agregar widgets de productos al diseño de cuadrícula
                num_columnas = 3
                nombre = ["Chico", "Mediano", "Grande"]
                
                for i in range(3):
                    
                    nomrbre = nombre[i]
                    img = f"{direccion_img}/"+f"{nomrbre}.png"
                    
                    size_widget = ClientWidget(
                        nombre= nomrbre, # Nombre de la pieza
                        imagen_path=QPixmap(img)  # Reemplaza con la ruta real de la imagen
                    )
                    fila = i // num_columnas
                    columna = i % num_columnas
                    scroll_content_layout.addWidget(size_widget, fila, columna)
                    
                    # Conectar la señal clicked al método productoClickeado
                    size_widget.clientClicked.connect(self.optionClickeado)
                    
            elif self.window_type == "type":
                
                self.lbl_orderby.setText("Ordenado por material")
                
                # Crear ventana principal
                main_layout = QVBoxLayout(self.products)

                # Crear área de desplazamiento
                scroll_area = QScrollArea(self.products)
                scroll_content = QWidget()
                scroll_content_layout = QGridLayout(scroll_content)
                
                self.all_material = getPieceByDistincMaterial()
                
                self.materials = [tupla[0] for tupla in self.all_material]
                
                #print("Materiales: ", self.materials)
                
                # Agregar widgets de productos al diseño de cuadrícula
                num_columnas = 2
                
                for i in range(len(self.materials)):
                    
                    nombre = self.materials[i]
                    img = f"{direccion_img}/"+f"{nombre}.png"
                    
                    client_widget = ClientWidget(
                        nombre= nombre, # Nombre de la pieza
                        imagen_path=QPixmap(img)  # Reemplaza con la ruta real de la imagen
                    )
                    fila = i // num_columnas
                    columna = i % num_columnas
                    scroll_content_layout.addWidget(client_widget, fila, columna)
                    
                    # Conectar la señal clicked al método productoClickeado
                    client_widget.clientClicked.connect(self.optionClickeado)

            scroll_area.setStyleSheet("QScrollArea { background-color: #fff; }"
                                    "QScrollBar:vertical { width: 35px; background-color: darkgray; }"
                                    "QScrollBar:horizontal { height: 15px; background-color: darkgray; }")
            # Configurar el área de desplazamiento
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(scroll_content)

            # Agregar el área de desplazamiento al diseño principal
            main_layout.addWidget(scroll_area)
            
        except Exception as e:
            print("Error en la clase enterprises cargando clientes: " + str(e))
            print(traceback.format_exc())
    
    def optionClickeado(self, name_option):
        # Función que se ejecutará cuando se haga clic en un producto
        
        self.window_options = size_and_type(self.window_type, self.close_window, name_option)
        self.window_options.show()
        #self.close()
    
    def regresar(self, event):
        self.close()
        
        
        
        
        
        
        
        
        
class alphabet(QWidget):
    
    def __init__(self):
        
        super(alphabet, self).__init__()
        
        try:
            global direccion_design, direccion_img
            
            self.setGeometry(0, 0, 800, 480)
            self.setWindowFlags(Qt.FramelessWindowHint)
            uic.loadUi(f"{direccion_design}/alphabet.ui", self)
            # Bloquea la interacción con otras partes de la aplicación
            self.setWindowModality(Qt.ApplicationModal)
            
            self.btn_regresar.mousePressEvent = self.regresar
            
            # Teclado simplificado (solo letras relevantes)
            self.keyboard = QWidget(self)
            self.keyboard_layout = QHBoxLayout()
            self.keyboard.setLayout(self.keyboard_layout)
            
            # Conexión del cuadro de búsqueda a la actualización de la lista de archivos
            self.search_edit.textChanged.connect(self.updateFileList)
            self.clear_button.mousePressEvent = self.clearLastLetter
            
            # Crear el diseño principal una vez en la inicialización
            self.main_layout = QVBoxLayout(self.products2)
            self.scroll_area = QScrollArea(self.products2)
            self.scroll_content = QWidget()
            self.scroll_content_layout = QGridLayout(self.scroll_content)

            # Configurar el área de desplazamiento
            self.scroll_area.setStyleSheet("QScrollArea { background-color: #fff; }"
                                    "QScrollBar:vertical { width: 35px; background-color: darkgray; }"
                                    "QScrollBar:horizontal { height: 15px; background-color: darkgray; }")
            
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setWidget(self.scroll_content)
            
            # Configuración del teclado simplificado (solo letras relevantes)
            self.setupKeyboard()
            
            # Configuración de la lista de archivo
            self.setAlphabet()
            
            # Almacenar la lista completa de archivos en memoria
            self.updateFileList()
            
        except Exception as e:
            print("Error en la clase Alphabet: " + str(e))
            print(traceback.format_exc())
            
    def obtener_dimensiones_bk_keyboard(self):
        
        x_keyboard = self.bk_keyboard.x()
        y_keyboard = self.bk_keyboard.y()
        ancho_keyboard = self.bk_keyboard.width()
        alto_keyboard = self.bk_keyboard.height()
        
        #print(x_keyboard, y_keyboard, ancho_keyboard, alto_keyboard)
        
        self.keyboard.setGeometry(int(x_keyboard), int(y_keyboard), ancho_keyboard, alto_keyboard)
        
            
    def setupKeyboard(self):
        # Limpia el teclado actual
        try:
            for i in reversed(range(self.keyboard_layout.count())):
                widget = self.keyboard_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
        except Exception as e:
            print("Error en la clase Alphabet limpiando teclado: " + str(e))
            print(traceback.format_exc())
                
    def loadFiles(self):
        
        try:
            # Almacenar la lista completa de archivos en memoria
            self.all_files = [f"{piece[1]}{piece[2]}" for piece in self.all_pieces_by_alphabet]
            self.all_files_names = [f"{piece[1]}" for piece in self.all_pieces_by_alphabet]
            
            # Agregar widgets de productos al diseño de cuadrícula
            num_columnas = 2
            
            for i in range(len(self.all_files)):
                
                nombre = self.all_files[i]
                img = f"{direccion_img}/{str(self.all_files_names[i]).lower()}.png"
                
                client_widget = ClientWidget(
                    nombre= nombre, # Nombre de la pieza
                    imagen_path=QPixmap(img)  # Reemplaza con la ruta real de la imagen
                )
                fila = i // num_columnas
                columna = i % num_columnas
                self.scroll_content_layout.addWidget(client_widget, fila, columna)
                
                # Conectar la señal clicked al método productoClickeado
                client_widget.clientClicked.connect(self.optionClickeado)

            # Agregar el área de desplazamiento al diseño principal
            self.main_layout.addWidget(self.scroll_area)

        except Exception as e:
            print("Error en la clase Alphabet cargando archivos: " + str(e))
            print(traceback.format_exc())
                
    def updateFileList(self):
        
        try:
            # Obtener la consulta de búsqueda y convertirla a minúsculas
            query = self.search_edit.text().strip().lower()
            
            # Si la consulta está vacía, mostrar todos los archivos
            if not query:
                self.loadFiles()
            else:
                #print("Se va a actualizar la lista de archivos")
                # Filtrar los archivos basados en la consulta
                matching_files = [file_name for file_name in self.all_files if file_name.lower().startswith(query)]
                matching_files_names = [file_name2 for file_name2 in self.all_files_names if file_name2.lower().startswith(query)]
                
                # Limpiar el contenido actual del diseño de cuadrícula
                for i in reversed(range(self.scroll_content_layout.count())):
                    widget = self.scroll_content_layout.itemAt(i).widget()
                    widget.setParent(None)
                
                self.all_material = matching_files
                
                #print("Materiales: ", self.all_material)
                #print("Alfabeto: ", self.materials)
                
                # Agregar widgets de productos al diseño de cuadrícula
                num_columnas = 2
                
                for i in range(len(self.all_material)):
                    
                    nombre = self.all_material[i]
                    img = f"{direccion_img}/{str(matching_files_names[i]).lower()}.png"
                    
                    client_widget = ClientWidget(
                        nombre= nombre, # Nombre de la pieza
                        imagen_path=QPixmap(img)  # Reemplaza con la ruta real de la imagen
                    )
                    fila = i // num_columnas
                    columna = i % num_columnas
                    self.scroll_content_layout.addWidget(client_widget, fila, columna)
                    
                    # Conectar la señal clicked al método productoClickeado
                    client_widget.clientClicked.connect(self.optionClickeado)

                # Agregar el área de desplazamiento al diseño principal
                self.main_layout.addWidget(self.scroll_area)

            # Actualizar el teclado simplificado según las letras relevantes
            self.updateKeyboard(query)
            
        except Exception as e:
            print("Error en la clase Alphabet actualizando lista de archivos: " + str(e))
            print(traceback.format_exc())
            
    def cortar_string(self, s):
        for i, char in enumerate(s):
            if char.isupper() and i > 0:
                return s[:i]
        return s
            
    def mostrar_teclado_numerico(self, piece):
        teclado = numeric_keyboard(piece)
        if teclado.exec_() == QDialog.Accepted:
            self.resultadoKB = teclado.resultado
            
    def optionClickeado(self, name_option):
        
        self.close()
        # Función que se ejecutará cuando se haga clic en un producto
        print(f"Alfabeto {name_option} clickeado")
        
        self.mostrar_teclado_numerico(str(self.cortar_string(name_option)))
        
        if self.resultadoKB != "cancelar":
            self.production_window = Production(str(self.cortar_string(name_option)), self.resultadoKB)
            self.production_window.show()
    
    def updateKeyboard(self, query):
        try:
            # Limpia el teclado actual
            self.setupKeyboard()

            # Filtra los nombres que coinciden con la consulta de búsqueda
            matching_files = [file_name for file_name in self.all_files if file_name.lower().startswith(query)]

            # Crea un conjunto de letras únicas siguientes en orden
            next_letters = set()
            for name in matching_files:
                if len(query) < len(name):
                    next_letter = name[len(query)].upper()
                    next_letters.add(next_letter)
                    
            # Si hay letras únicas siguientes en orden, agrega botones con ellas al teclado
            if next_letters:
                for letter in sorted(next_letters):
                    button = QPushButton(letter, self)
                    button.clicked.connect(lambda checked, l=letter: self.onLetterClicked(l))
                    button.setStyleSheet(f"background-color: rgb(65, 65, 65); color: rgb(255, 255, 255); font:75 14pt 'MS Shell Dlg 2';")
                    self.keyboard_layout.addWidget(button)
                    
        except Exception as e:
            print("Error en la clase Alphabet actualizando teclado: " + str(e))
            print(traceback.format_exc())
            
    def onLetterClicked(self, letter):
        try:
            current_text = self.search_edit.text()
            new_text = current_text + letter
            self.search_edit.setText(new_text.upper())
        except Exception as e:
            print("Error en la clase Alphabet al clickear letra: " + str(e))
            print(traceback.format_exc())
            
    def clearLastLetter(self, event):
        try:
            current_text = self.search_edit.text()
            if current_text:
                new_text = current_text[:-1]  # Elimina la última letra
                self.search_edit.setText(new_text)
        except Exception as e:
            print("Error al eliminar la última letra", e)
            print(traceback.format_exc())
            
    def setAlphabet(self):
        
        try:
            # Crear ventana principal
            main_layout = QVBoxLayout(self.products)

            # Crear área de desplazamiento
            scroll_area = QScrollArea(self.products)
            scroll_content = QWidget()
            scroll_content_layout = QGridLayout(scroll_content)
            
            self.lbl_orderby.setText("Ordenado por alfabeto")
            
            # Obtén las piezas ordenadas por el nombre
            self.all_pieces_by_alphabet = getPieceByAlphabeticalOrder()
            
            # Agrupa las piezas por la primera letra del nombre
            pieces_by_letter = {}
            for piece in self.all_pieces_by_alphabet:
                first_letter = piece[1][0].upper()  # Obtén la primera letra y conviértela a mayúscula
                if first_letter not in pieces_by_letter:
                    pieces_by_letter[first_letter] = []
                pieces_by_letter[first_letter].append(piece)
            
            # Agregar widgets de productos al diseño de cuadrícula con secciones
            for letter, pieces in pieces_by_letter.items():
                # Agregar una etiqueta de sección para la letra actual
                section_label = QLabel(letter)
                scroll_content_layout.addWidget(section_label)
                
                # Agregar widgets de productos para cada pieza en la sección
                for i, piece in enumerate(pieces):
                    producto_widget = ProductoWidget(
                        nombre=f"{piece[1]}",  # Nombre de la pieza
                        ancho=f"{piece[3]}",  # Ancho de la pieza
                        alto=f"{piece[4]}",   # Alto de la pieza
                        profundidad=f"{piece[5]}",  # Profundidad de la pieza
                        imagen_path=QPixmap(f"{direccion_img}/{str(piece[1]).lower()}.png")  # Reemplaza con la ruta real de la imagen
                    )
                    scroll_content_layout.addWidget(producto_widget)
                    
                    # Conectar la señal clicked al método productoClickeado
                    producto_widget.productoClicked.connect(self.productoClickeado)

            scroll_area.setStyleSheet("QScrollArea { background-color: #fff; }"
                                    "QScrollBar:vertical { width: 35px; background-color: darkgray; }"
                                    "QScrollBar:horizontal { height: 15px; background-color: darkgray; }")
            
            # Configurar el área de desplazamiento
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(scroll_content)

            # Agregar el área de desplazamiento al diseño principal
            main_layout.addWidget(scroll_area)
            
        except Exception as e:
            print("Error en la clase enterprises cargando alfabeticamente: " + str(e))
            print(traceback.format_exc())
            
    def mostrar_teclado_numerico(self, piece):
        teclado = numeric_keyboard(piece)
        if teclado.exec_() == QDialog.Accepted:
            self.resultadoKB = teclado.resultado
    
    def productoClickeado(self, nombre_producto):
        # Función que se ejecutará cuando se haga clic en un producto
        
        self.close()
        
        self.mostrar_teclado_numerico(nombre_producto)
        
        if self.resultadoKB != "cancelar":
            self.production_window = Production(nombre_producto, self.resultadoKB)
            self.production_window.show()
    
    def regresar(self, event):
        self.close()
        
        
        
        
        
        
        
        
        
        
class Production(QWidget):

    def __init__(self, piece, result_kb, Manual = False):
        
        super(Production, self).__init__()
        
        global direccion_design, direccion_img
            
        self.setGeometry(0, 0, 800, 480)
        self.setWindowFlags(Qt.FramelessWindowHint)
        uic.loadUi(f"{direccion_design}/production.ui", self)
        # Bloquea la interacción con otras partes de la aplicación
        self.setWindowModality(Qt.ApplicationModal)
        
        self.chosen_piece = piece
        self.result_amount = result_kb
        self.manual = Manual
        self.move_in_x = False
        self.draining = True
        self.in_process = False
        self.going = False
        self.wait_time = 0
        self.tiempo_transcurrido = 0
        
        self.timer_progress = QTimer(self)
        self.timer_progress.timeout.connect(self.update_progress)
        
        self.cronometro = QTime()
        self.cronometro.setHMS(0, 0, 0)  # Establecer el cronómetro a 00:00:00
        
        self.container_time_list = []
        self.container_time_list_editable = [
            {'time': 0, 'container': 'btn_container1'},
            {'time': 0, 'container': 'btn_drying1'},
            {'time': 0, 'container': 'btn_container2'},
            {'time': 0, 'container': 'btn_drying2'},
            {'time': 0, 'container': 'btn_container3'},
            {'time': 0, 'container': 'btn_drying3'}
        ]
        
        self.btn_container1.mousePressEvent = lambda event: self.loadWindowOnlyKeyboard(self.btn_container1)
        self.btn_container2.mousePressEvent = lambda event: self.loadWindowOnlyKeyboard(self.btn_container2)
        self.btn_container3.mousePressEvent = lambda event: self.loadWindowOnlyKeyboard(self.btn_container3)

        self.btn_drying1.mousePressEvent = lambda event: self.loadWindowOnlyKeyboard(self.btn_drying1)
        self.btn_drying2.mousePressEvent = lambda event: self.loadWindowOnlyKeyboard(self.btn_drying2)
        self.btn_drying3.mousePressEvent = lambda event: self.loadWindowOnlyKeyboard(self.btn_drying3)
        
        self.btn_cancelar.mousePressEvent = self.close_windows
        self.btn_salir.mousePressEvent = self.close_window

        self.progress_bar.hide()
        self.btn_salir.hide()
        self.lbl_seconds.hide()
        
        # Obtener la fecha actual
        fecha_actual = datetime.now()

        # Formatear la fecha en el formato deseado
        fecha_formateada = fecha_actual.strftime("%Y%m%d")
        
        # Obtener la hora actual
        hora_actual = datetime.now().time()

        # Formatear la hora en el formato deseado
        hora_formateada = hora_actual.strftime("%H%M%S")
        
        if len(self.chosen_piece) > 2:
        
            self.all_pieces = getPieceByName(self.chosen_piece)
            
            self.id_piece = self.all_pieces[0]
            name_piece = self.all_pieces[1]
            material_piece = self.all_pieces[2]
            width_piece = self.all_pieces[3]
            height_piece = self.all_pieces[4]
            length_piece = self.all_pieces[5]
            time1_piece = self.all_pieces[6]
            time2_piece = self.all_pieces[7]
            time3_piece = self.all_pieces[8]
            time4_piece = self.all_pieces[9]
            time5_piece = self.all_pieces[10]
            time6_piece = self.all_pieces[11]
            id_client = self.all_pieces[12]
            
            self.times = self.all_pieces[6:12]
        else:
            self.id_piece = 9
            self.result_amount = 0
        
        # Creamos el nuevo folio único del proceso
        
        self.process_history = 99
        
        done_process_history = insertProcessHistory(self.id_piece, self.result_amount, fecha_formateada, hora_formateada, "1")
        
        if done_process_history:
            
            last_process = getLastProcessHistory()
        
            self.process_history = last_process[0]
            
        else:
            attempts = 0
            while (not insert and attempts < 3):
                insert = insertProcessHistory(self.id_piece, self.result_amount, fecha_formateada, hora_formateada, "1")
                attempts += 1
            if insert:
                print("Se inserto la trama de historial de procesos")
            else:
                print("No se pudo insertar el historial de proceso en la base de datos")
                self.window_message = message("No se han cargado el proceso correctamente", "sin_tiempos", "error")
                self.window_message.show()
                self.close()
            
            
        
        if self.manual:
            
            self.btn_container1.show()
            self.btn_drying1.show()
            
            self.btn_container2.show()
            self.btn_drying2.show()
            
            self.btn_container3.show()
            self.btn_drying3.show()
            
            self.btn_iniciar.mousePressEvent = self.iniciar_manual
            
            #print("Iniciando proceso manual")
            
            #print("Se han cargado los tiempos correctamente")
            insert = insertProcess(self.id_piece, self.result_amount, "1", fecha_formateada, hora_formateada, "1", "1", self.process_history)
        
            if insert:                
                print("Se inserto la trama de espera de piezas")
            else:
                attempts = 0
                while (not insert and attempts < 3):
                    insert = insertProcess(self.id_piece, self.result_amount, "1", fecha_formateada, hora_formateada, "1", "1", self.process_history)
                    attempts += 1
                if insert:
                    print("Se inserto la trama de espera de piezas")
                else:
                    print("No se pudo insertar el proceso en la base de datos")
                    self.window_message = message("No se han cargado el proceso correctamente", "sin_tiempos", "error")
                    self.window_message.show()
                    self.close()
            
            
        else:
            
            self.btn_container1.hide()
            self.btn_drying1.hide()
            
            self.btn_container2.hide()
            self.btn_drying2.hide()
            
            self.btn_container3.hide()
            self.btn_drying3.hide()
            
            self.btn_iniciar.mousePressEvent = self.iniciar
            
            insert = insertProcess(self.id_piece, self.result_amount, "1", fecha_formateada, hora_formateada, "1", "1", self.process_history)
            
            if insert:
                print("Se inserto la trama de espera de piezas")
            else:
                attempts = 0
                while (not insert and attempts < 3):
                    insert = insertProcess(self.id_piece, self.result_amount, "1", fecha_formateada, hora_formateada, "1", "1", self.process_history)
                    attempts += 1
                if insert:
                    print("Se inserto la trama de espera de piezas")
                else:
                    print("No se pudo insertar el proceso en la base de datos")
                    self.window_message = message("No se han cargado el proceso correctamente", "sin_tiempos", "error")
                    self.window_message.show()
                    self.close()
                    
            
    def close_window(self, event):
        
        # Obtener la fecha actual
        fecha_actual = datetime.now()

        # Formatear la fecha en el formato deseado
        fecha_formateada = fecha_actual.strftime("%Y%m%d")
        
        # Obtener la hora actual
        hora_actual = datetime.now().time()

        # Formatear la hora en el formato deseado
        hora_formateada = hora_actual.strftime("%H%M%S")
        
        insert = insertProcess(self.id_piece, self.result_amount, "16", fecha_formateada, hora_formateada, "5", "1", self.process_history)
        
        self.btn_salir.hide()
        self.lbl_executed_process.setText("Restaurando posición inicial")
        self.restart_motor = QTimer(self)
        self.restart_motor.timeout.connect(self.process_end_to_start)
        self.restart_motor.start(50)
        
    def close_windows(self, event):
        
        # Obtener la fecha actual
        fecha_actual = datetime.now()

        # Formatear la fecha en el formato deseado
        fecha_formateada = fecha_actual.strftime("%Y%m%d")
        
        # Obtener la hora actual
        hora_actual = datetime.now().time()

        # Formatear la hora en el formato deseado
        hora_formateada = hora_actual.strftime("%H%M%S")
        
        insert = insertProcess(self.id_piece, self.result_amount, "0", fecha_formateada, hora_formateada, "4", "1", self.process_history)
        
        self.close()
        
    def iniciar(self, event):
        
        self.btn_cancelar.hide()
        self.btn_iniciar.hide()
        
        self.progress_bar.show()
        
        #######################################################
        #Aquí es donde empieza todo el proceso de la simulación
        #######################################################
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(partial(self.process_1_to_2, self.times))
        self.timer.start(5)
                
    def iniciar_manual(self, event):
        
        if self.check_container_time():
            
            print("La lista de tiempos editable es: ", self.container_time_list_editable)
            
            # Crear una lista de todos los tiempos
            self.todos_los_tiempos_manuales = [elemento['time'] for elemento in self.container_time_list_editable]
            
            self.btn_cancelar.hide()
            self.btn_iniciar.hide()

            self.progress_bar.show()
        
            self.btn_container1.hide()
            self.btn_drying1.hide()
            
            self.btn_container2.hide()
            self.btn_drying2.hide()
            
            self.btn_container3.hide()
            self.btn_drying3.hide()
            
            #######################################################
            #Aquí es donde empieza todo el proceso de la simulación
            #######################################################
            
            self.timer = QTimer(self)
            self.timer.timeout.connect(partial(self.process_1_to_2, self.todos_los_tiempos_manuales))
            self.timer.start(5)
            
        else:
            print("No se han cargado los tiempos correctamente")
            self.window_message = message("No se han cargado los tiempos correctamente", "sin_tiempos", "warning")
            self.window_message.show()
            
    def check_container_time(self):
        
        # Verificar si hay al menos un par de 'container' y 'drying'
        containers = set()
        dryings = set()
        
        for resultado in self.container_time_list:
            if 'container' in resultado['container']:
                containers.add(resultado['container'])
            elif 'drying' in resultado['container']:
                dryings.add(resultado['container'])
        
        # Verificar que cada 'container' tenga un par 'drying'
        for container in containers:
            drying_pair = container.replace('container', 'drying')
            if drying_pair not in dryings:
                return False
            
        # Verificar que cada 'drying' tenga su par 'container'
        for drying in dryings:
            container_pair = drying.replace('drying', 'container')
            if container_pair not in containers:
                return False

        return len(containers) >= 1 and len(dryings) >= 1
            
    
    def loadWindowOnlyKeyboard(self, source_button):
        
        source_button_name = source_button.objectName()
        self.window_keyboard = only_keyboard(source_button_name)
        
        if self.window_keyboard.exec_() == QDialog.Accepted:
            
            self.result_time = self.window_keyboard.resultado
            source_button_name = self.window_keyboard.source_button
            source_button.setText(self.result_time)
            
            encontrado = False
            
            for resultado in self.container_time_list:
                if resultado['container'] == source_button_name:
                    resultado['time'] = self.result_time
                    encontrado = True
                    for elemento in self.container_time_list_editable:
                        if elemento['container'] == source_button_name:
                            elemento['time'] = self.result_time
                    break

            if not encontrado:
                self.container_time_list.append({'time': self.result_time, 'container': source_button_name})
                for elemento in self.container_time_list_editable:
                    if elemento['container'] == source_button_name:
                        elemento['time'] = self.result_time
                
            self.setWindowModality(Qt.ApplicationModal)
            
    def move_x(self, label_to_move):
        try:
            label_to_move.move(label_to_move.x() + 11, label_to_move.y())
            return True
        except Exception as e:
            print(f"Error al mover el label: {str(e)}")
            print(traceback.print_exc())
            return False

    def move_minus_x(self, label_to_move):
        try:
            label_to_move.move(label_to_move.x() - 11, label_to_move.y())
            return True
        except Exception as e:
            print(f"Error al mover el label: {str(e)}")
            print(traceback.print_exc())
            return False

    def move_y(self, label_to_move):
        try:
            label_to_move.move(label_to_move.x(), label_to_move.y() + 6)
            return True
        except Exception as e:
            print(f"Error al mover el label: {str(e)}")
            print(traceback.print_exc())
            return False

    def move_minus_y(self, label_to_move):
        try:
            label_to_move.move(label_to_move.x(), label_to_move.y() - 6)
            return True
        except Exception as e:
            print(f"Error al mover el label: {str(e)}")
            print(traceback.print_exc())
            return False
        
    def process_1_to_2(self, times):
        
        if not self.in_process:
        
            if self.horizontal_bar.y() <= 130 or self.move_in_x:
                
                self.move_in_x = True
                
                if self.pinza.x() >= 180:
                    
                    # TERCERA ANIMACIÓN
                    # SE MUEVE DE ARRIBA PARA ABAJO
                    self.paso_altura_abajo()
                    GPIO.output(relevador, False)
                    
                    done_piece = self.move_y(self.piece_select)
                    done_pinza = self.move_y(self.pinza)
                    done_horizontal_bar = self.move_y(self.horizontal_bar)
                    
                    if self.piece_select.y() >= 270:
                        
                        print("Llego al 1er deposito (stage 2), va a esperar ", times[0], " segundos")
                        self.in_process = True
                        self.move_in_x = False
                        self.wait_time = int(times[0])
                        self.going = False
                        
                        # Obtener la fecha actual
                        fecha_actual = datetime.now()

                        # Formatear la fecha en el formato deseado
                        fecha_formateada = fecha_actual.strftime("%Y%m%d")
                        
                        # Obtener la hora actual
                        hora_actual = datetime.now().time()

                        # Formatear la hora en el formato deseado
                        hora_formateada = hora_actual.strftime("%H%M%S")
                        
                        insert = insertProcess(self.id_piece, self.result_amount, "3", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("Sumergido en deposito 1.")
                        
                        self.timer_progress.start(1000)
                        
                else:
                    
                    # SEGUNDA ANIMACIÓN
                    # SE MUEVE DE IZQUIERDA A DERECHA
                    self.paso_profundidad_adelante()
                    GPIO.output(relevador, True)
                    
                    done_piece = self.move_x(self.piece_select)
                    done_pinza = self.move_x(self.pinza)
                    
            elif self.horizontal_bar.y() >= 130 and not self.move_in_x:
                
                # PRIMERA ANIMACIÓN
                # SE MUEVE DE ABAJO PARA ARRIBA
                self.paso_altura_arriba()
                GPIO.output(relevador, False)
                
                done_piece = self.move_minus_y(self.piece_select)
                done_pinza = self.move_minus_y(self.pinza)
                done_horizontal_bar = self.move_minus_y(self.horizontal_bar)
                
                if not self.going:
                
                    # Obtener la fecha actual
                    fecha_actual = datetime.now()

                    # Formatear la fecha en el formato deseado
                    fecha_formateada = fecha_actual.strftime("%Y%m%d")
                    
                    # Obtener la hora actual
                    hora_actual = datetime.now().time()

                    # Formatear la hora en el formato deseado
                    hora_formateada = hora_actual.strftime("%H%M%S")
                    
                    insert = insertProcess(self.id_piece, self.result_amount, "2", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                    
                    self.going = True
                
                    self.lbl_executed_process.setText("Yendo a sumergirse en deposito 1.")
                    self.lbl_seconds.hide()
        else:
            
            if self.tiempo_transcurrido >= self.wait_time:
                print("Saliendo del 1er deposito: ", self.tiempo_transcurrido)
                self.timer.stop()
                self.in_process = False
                self.timer_progress.stop()
                self.progress_bar.setValue(self.tiempo_transcurrido)
                self.tiempo_transcurrido = 0
                self.cronometro.setHMS(0, 0, 0)
                
                self.timer2 = QTimer(self)
                self.timer2.timeout.connect(partial(self.process_2_to_4, times))
                self.timer2.start(5)
            else:
                self.progress_bar.setValue(self.tiempo_transcurrido)
                self.lbl_seconds.show()
                self.lbl_seconds.setText(str(self.wait_time)+"s")
                
                
                
                
            
    def process_2_to_4(self, times):
        
        if not self.in_process:
        
            if self.horizontal_bar.y() <= 130 or self.move_in_x:
                
                self.move_in_x = True
                
                if self.pinza.x() >= 360:
                    
                    # TERCERA ANIMACIÓN
                    # SE MUEVE DE ARRIBA PARA ABAJO
                    self.paso_altura_abajo()
                    GPIO.output(relevador, False)
                    
                    done_piece = self.move_y(self.piece_select)
                    done_pinza = self.move_y(self.pinza)
                    done_horizontal_bar = self.move_y(self.horizontal_bar)
                    
                    if self.piece_select.y() >= 270:
                        
                        print("Llego al 2do deposito (stage 4), va a esperar ", times[2], " segundos")
                        self.in_process = True
                        self.move_in_x = False
                        self.wait_time = int(times[2])
                        self.going = False
                        
                        # Obtener la fecha actual
                        fecha_actual = datetime.now()

                        # Formatear la fecha en el formato deseado
                        fecha_formateada = fecha_actual.strftime("%Y%m%d")
                        
                        # Obtener la hora actual
                        hora_actual = datetime.now().time()

                        # Formatear la hora en el formato deseado
                        hora_formateada = hora_actual.strftime("%H%M%S")
                        
                        insert = insertProcess(self.id_piece, self.result_amount, "7", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("Sumergido en deposito 2.")
                        
                        self.timer_progress.start(1000)
                        
                else:
                    
                    if self.draining:
                        
                        print("Llego al 1er escurrimiento (stage 3), va a esperar ", times[1], " segundos")
                        
                        self.in_process = True
                        self.wait_time = int(times[1])
                        self.going = False
                        
                        # Obtener la fecha actual
                        fecha_actual = datetime.now()

                        # Formatear la fecha en el formato deseado
                        fecha_formateada = fecha_actual.strftime("%Y%m%d")
                        
                        # Obtener la hora actual
                        hora_actual = datetime.now().time()

                        # Formatear la hora en el formato deseado
                        hora_formateada = hora_actual.strftime("%H%M%S")
                        
                        insert = insertProcess(self.id_piece, self.result_amount, "5", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("Escurriendo en deposito 1.")
                        
                        self.timer_progress.start(1000)
                        
                    else:
                        # SEGUNDA ANIMACIÓN
                        # SE MUEVE DE IZQUIERDA A DERECHA
                        self.paso_profundidad_adelante()
                        GPIO.output(relevador, True)
                        
                        done_piece = self.move_x(self.piece_select)
                        done_pinza = self.move_x(self.pinza)
                    
            elif self.horizontal_bar.y() >= 130 and not self.move_in_x:
                
                # PRIMERA ANIMACIÓN
                # SE MUEVE DE ABAJO PARA ARRIBA
                self.paso_altura_arriba()
                GPIO.output(relevador, False)
                
                done_piece = self.move_minus_y(self.piece_select)
                done_pinza = self.move_minus_y(self.pinza)
                done_horizontal_bar = self.move_minus_y(self.horizontal_bar)
                
                if not self.going:
                    
                    # Obtener la fecha actual
                    fecha_actual = datetime.now()

                    # Formatear la fecha en el formato deseado
                    fecha_formateada = fecha_actual.strftime("%Y%m%d")
                    
                    # Obtener la hora actual
                    hora_actual = datetime.now().time()

                    # Formatear la hora en el formato deseado
                    hora_formateada = hora_actual.strftime("%H%M%S")
                    
                    insert = insertProcess(self.id_piece, self.result_amount, "4", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                    
                    self.going = True
                    
                    self.lbl_executed_process.setText("Yendo a escurrirse en deposito 1.")
                    self.lbl_seconds.hide()
        else:
            
            if self.draining:
                
                GPIO.output(relevador, False)
                
                if self.tiempo_transcurrido >= self.wait_time:
                    
                    print("Saliendo del 1er escurrimiento: ", self.tiempo_transcurrido)
                    self.in_process = False
                    self.draining = False
                    self.timer_progress.stop()
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.tiempo_transcurrido = 0
                    self.cronometro.setHMS(0, 0, 0)  # Establecer el cronómetro a 00:00:00
                    
                    if not self.going:
                    
                        # Obtener la fecha actual
                        fecha_actual = datetime.now()

                        # Formatear la fecha en el formato deseado
                        fecha_formateada = fecha_actual.strftime("%Y%m%d")
                        
                        # Obtener la hora actual
                        hora_actual = datetime.now().time()

                        # Formatear la hora en el formato deseado
                        hora_formateada = hora_actual.strftime("%H%M%S")
                        
                        insert = insertProcess(self.id_piece, self.result_amount, "6", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                        
                        self.going = True
                        
                        self.lbl_executed_process.setText("Yendo a sumergirse en deposito 2.")
                        self.lbl_seconds.hide()
                else:
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.lbl_seconds.show()
                    self.lbl_seconds.setText(str(self.wait_time)+"s")
                    
            else:
                
                if self.tiempo_transcurrido >= self.wait_time:
                    
                    print("Saliendo del 1er deposito: ", self.tiempo_transcurrido)
                    self.timer2.stop()
                    self.in_process = False
                    self.timer_progress.stop()
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.tiempo_transcurrido = 0
                    self.cronometro.setHMS(0, 0, 0)  # Establecer el cronómetro a 00:00:00
                    self.draining = True
                    
                    self.timer3 = QTimer(self)
                    self.timer3.timeout.connect(partial(self.process_4_to_6, times))
                    self.timer3.start(5)
                else:
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.lbl_seconds.show()
                    self.lbl_seconds.setText(str(self.wait_time)+"s")
            
            
            
            
            
    def process_4_to_6(self, times):
        
        if not self.in_process:
        
            if self.horizontal_bar.y() <= 130 or self.move_in_x:
                
                self.move_in_x = True
                
                if self.pinza.x() >= 530:
                    
                    # TERCERA ANIMACIÓN
                    # SE MUEVE DE ARRIBA PARA ABAJO
                    self.paso_altura_abajo()
                    GPIO.output(relevador, False)
                    
                    done_piece = self.move_y(self.piece_select)
                    done_pinza = self.move_y(self.pinza)
                    done_horizontal_bar = self.move_y(self.horizontal_bar)
                    
                    if self.piece_select.y() >= 270:
                        
                        print("Llego al 3er deposito (stage 6), va a esperar ", times[4], " segundos")
                        self.in_process = True
                        self.move_in_x = False
                        self.wait_time = int(times[4])
                        self.going = False
                        
                        # Obtener la fecha actual
                        fecha_actual = datetime.now()

                        # Formatear la fecha en el formato deseado
                        fecha_formateada = fecha_actual.strftime("%Y%m%d")
                        
                        # Obtener la hora actual
                        hora_actual = datetime.now().time()

                        # Formatear la hora en el formato deseado
                        hora_formateada = hora_actual.strftime("%H%M%S")
                        
                        insert = insertProcess(self.id_piece, self.result_amount, "11", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("Sumergido en deposito 3.")
                        
                        self.timer_progress.start(1000)
                        
                else:
                        
                    if self.draining:
                        
                        print("Llego al 2do escurrimiento (stage 5), va a esperar ", times[3], " segundos")
                        
                        self.in_process = True
                        self.wait_time = int(times[3])
                        self.going = False
                        
                        # Obtener la fecha actual
                        fecha_actual = datetime.now()

                        # Formatear la fecha en el formato deseado
                        fecha_formateada = fecha_actual.strftime("%Y%m%d")
                        
                        # Obtener la hora actual
                        hora_actual = datetime.now().time()

                        # Formatear la hora en el formato deseado
                        hora_formateada = hora_actual.strftime("%H%M%S")
                        
                        insert = insertProcess(self.id_piece, self.result_amount, "9", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("Escurriendo en deposito 2.")
                        
                        self.timer_progress.start(1000)
                    
                    else:
                        
                        # SEGUNDA ANIMACIÓN
                        # SE MUEVE DE IZQUIERDA A DERECHA
                        self.paso_profundidad_adelante()
                        GPIO.output(relevador, True)
                        
                        done_piece = self.move_x(self.piece_select)
                        done_pinza = self.move_x(self.pinza)
                    
            elif self.horizontal_bar.y() >= 130 and not self.move_in_x:
                
                # PRIMERA ANIMACIÓN
                # SE MUEVE DE ABAJO PARA ARRIBA
                self.paso_altura_arriba()
                GPIO.output(relevador, False)
                
                done_piece = self.move_minus_y(self.piece_select)
                done_pinza = self.move_minus_y(self.pinza)
                done_horizontal_bar = self.move_minus_y(self.horizontal_bar)
                
                if not self.going:
                
                    # Obtener la fecha actual
                    fecha_actual = datetime.now()

                    # Formatear la fecha en el formato deseado
                    fecha_formateada = fecha_actual.strftime("%Y%m%d")
                    
                    # Obtener la hora actual
                    hora_actual = datetime.now().time()

                    # Formatear la hora en el formato deseado
                    hora_formateada = hora_actual.strftime("%H%M%S")
                    
                    insert = insertProcess(self.id_piece, self.result_amount, "8", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                    
                    self.going = True
                    
                    self.lbl_executed_process.setText("Yendo a escurrirse en deposito 2.")
                    self.lbl_seconds.hide()
        else:
            
            if self.draining:
                
                GPIO.output(relevador, False)
                
                if self.tiempo_transcurrido >= self.wait_time:
                    
                    print("Saliendo del 2do escurrimiento: ", self.tiempo_transcurrido)
                    self.in_process = False
                    self.draining = False
                    self.timer_progress.stop()
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.tiempo_transcurrido = 0
                    self.cronometro.setHMS(0, 0, 0)  # Establecer el cronómetro a 00:00:00
                    
                    if not self.going:
                    
                        # Obtener la fecha actual
                        fecha_actual = datetime.now()

                        # Formatear la fecha en el formato deseado
                        fecha_formateada = fecha_actual.strftime("%Y%m%d")
                        
                        # Obtener la hora actual
                        hora_actual = datetime.now().time()

                        # Formatear la hora en el formato deseado
                        hora_formateada = hora_actual.strftime("%H%M%S")
                        
                        insert = insertProcess(self.id_piece, self.result_amount, "10", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                        
                        self.going = True
                        
                        self.lbl_executed_process.setText("Yendo a sumergirse en deposito 3.")
                        self.lbl_seconds.hide()
                else:
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.lbl_seconds.show()
                    self.lbl_seconds.setText(str(self.wait_time)+"s")
                    
            else:
                
                if self.tiempo_transcurrido >= self.wait_time:
                    
                    print("Saliendo del 2do deposito: ", self.tiempo_transcurrido)
                    self.timer3.stop()
                    self.in_process = False
                    self.timer_progress.stop()
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.tiempo_transcurrido = 0
                    self.cronometro.setHMS(0, 0, 0)  # Establecer el cronómetro a 00:00:00
                    self.draining = True
                    
                    self.timer4 = QTimer(self)
                    self.timer4.timeout.connect(partial(self.process_6_to_8, times))
                    self.timer4.start(5)
                else:
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.lbl_seconds.show()
                    self.lbl_seconds.setText(str(self.wait_time)+"s")
            
            
            
            
    def process_6_to_8(self, times):
        
        if not self.in_process:
        
            if self.horizontal_bar.y() <= 130 or self.move_in_x:
                
                self.move_in_x = True
                
                if self.pinza.x() >= 700:
                    
                    # TERCERA ANIMACIÓN
                    # SE MUEVE DE ARRIBA PARA ABAJO
                    self.paso_altura_abajo()
                    GPIO.output(relevador, False)
                    
                    done_piece = self.move_y(self.piece_select)
                    done_pinza = self.move_y(self.pinza)
                    done_horizontal_bar = self.move_y(self.horizontal_bar)
                    
                    if self.piece_select.y() >= 270:
                        
                        self.timer4.stop()
                        
                        print("Llego al final del proceso (stage 8)")
                        self.move_in_x = False
                        self.draining = True
                        self.going = False
                        
                        # Obtener la fecha actual
                        fecha_actual = datetime.now()

                        # Formatear la fecha en el formato deseado
                        fecha_formateada = fecha_actual.strftime("%Y%m%d")
                        
                        # Obtener la hora actual
                        hora_actual = datetime.now().time()

                        # Formatear la hora en el formato deseado
                        hora_formateada = hora_actual.strftime("%H%M%S")
                        
                        insert = insertProcess(self.id_piece, self.result_amount, "15", fecha_formateada, hora_formateada, "3", "1", self.process_history)
                        
                        self.lbl_executed_process.setText("Terminó el proceso.")
                        self.progress_bar.hide()
                        self.btn_salir.show()
                        self.lbl_seconds.hide()
                        self.approved_sound()
                        
                else:
                        
                    if self.draining:
                        
                        print("Llego al 3er escurrimiento (stage 7), va a esperar ", times[5], " segundos")
                        
                        self.in_process = True
                        self.wait_time = int(times[5])
                        self.going = False
                        
                        # Obtener la fecha actual
                        fecha_actual = datetime.now()

                        # Formatear la fecha en el formato deseado
                        fecha_formateada = fecha_actual.strftime("%Y%m%d")
                        
                        # Obtener la hora actual
                        hora_actual = datetime.now().time()

                        # Formatear la hora en el formato deseado
                        hora_formateada = hora_actual.strftime("%H%M%S")
                        
                        insert = insertProcess(self.id_piece, self.result_amount, "13", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("Escurriendo en deposito 3.")
                        
                        self.timer_progress.start(1000)
                    
                    else:
                        
                        # SEGUNDA ANIMACIÓN
                        # SE MUEVE DE IZQUIERDA A DERECHA
                        self.paso_profundidad_adelante()
                        GPIO.output(relevador, True)
                        
                        done_piece = self.move_x(self.piece_select)
                        done_pinza = self.move_x(self.pinza)
                    
            elif self.horizontal_bar.y() >= 130 and not self.move_in_x:
                
                # PRIMERA ANIMACIÓN
                # SE MUEVE DE ABAJO PARA ARRIBA
                self.paso_altura_arriba()
                GPIO.output(relevador, False)
                
                done_piece = self.move_minus_y(self.piece_select)
                done_pinza = self.move_minus_y(self.pinza)
                done_horizontal_bar = self.move_minus_y(self.horizontal_bar)
                
                if not self.going:
                
                    # Obtener la fecha actual
                    fecha_actual = datetime.now()

                    # Formatear la fecha en el formato deseado
                    fecha_formateada = fecha_actual.strftime("%Y%m%d")
                    
                    # Obtener la hora actual
                    hora_actual = datetime.now().time()

                    # Formatear la hora en el formato deseado
                    hora_formateada = hora_actual.strftime("%H%M%S")
                    
                    insert = insertProcess(self.id_piece, self.result_amount, "12", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                    
                    self.going = True
                    
                    self.lbl_executed_process.setText("Yendo a escurrirse en deposito 3.")
                    self.lbl_seconds.hide()
        else:
            
            if self.draining:
                
                GPIO.output(relevador, False)
                
                if self.tiempo_transcurrido >= self.wait_time:
                    
                    print("Saliendo del 3er escurrimiento: ", self.tiempo_transcurrido)
                    self.in_process = False
                    self.draining = False
                    self.timer_progress.stop()
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.tiempo_transcurrido = 0
                    self.cronometro.setHMS(0, 0, 0)  # Establecer el cronómetro a 00:00:00
                    
                    if not self.going:
                    
                        # Obtener la fecha actual
                        fecha_actual = datetime.now()

                        # Formatear la fecha en el formato deseado
                        fecha_formateada = fecha_actual.strftime("%Y%m%d")
                        
                        # Obtener la hora actual
                        hora_actual = datetime.now().time()

                        # Formatear la hora en el formato deseado
                        hora_formateada = hora_actual.strftime("%H%M%S")
                        
                        insert = insertProcess(self.id_piece, self.result_amount, "14", fecha_formateada, hora_formateada, "2", "1", self.process_history)
                        
                        self.going = True
                        
                        self.lbl_executed_process.setText("Terminando proceso")
                    
                else:
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.lbl_seconds.show()
                    self.lbl_seconds.setText(str(self.wait_time)+"s")
            
            
            
            
    def update_progress(self):
        
        self.cronometro = self.cronometro.addSecs(1)  # Aumentar en 1 segundo

        # Actualizar la QProgressBar
        self.tiempo_transcurrido = self.cronometro.second() + self.cronometro.minute() * 60



    def process_1_to_2_manual(self, times):
        
        if not self.in_process:
        
            if self.horizontal_bar.y() <= 130 or self.move_in_x:
                
                self.move_in_x = True
                
                if self.pinza.x() >= 180:
                    
                    # TERCERA ANIMACIÓN
                    # SE MUEVE DE ARRIBA PARA ABAJO
                    self.paso_altura_abajo()
                    GPIO.output(relevador, False)
                    
                    done_piece = self.move_y(self.piece_select)
                    done_pinza = self.move_y(self.pinza)
                    done_horizontal_bar = self.move_y(self.horizontal_bar)
                    
                    if self.piece_select.y() >= 270:
                        
                        print("Llego al 1er deposito (stage 2), va a esperar ", times[0], " segundos")
                        self.in_process = True
                        self.move_in_x = False
                        self.wait_time = int(times[0])
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("En 1er deposito")
                        
                        self.timer_progress.start(1000)
                        
                else:
                    
                    # SEGUNDA ANIMACIÓN
                    # SE MUEVE DE IZQUIERDA A DERECHA
                    self.paso_profundidad_adelante()
                    GPIO.output(relevador, True)
                    
                    done_piece = self.move_x(self.piece_select)
                    done_pinza = self.move_x(self.pinza)
                    
            elif self.horizontal_bar.y() >= 130 and not self.move_in_x:
                
                # PRIMERA ANIMACIÓN
                # SE MUEVE DE ABAJO PARA ARRIBA
                self.paso_altura_arriba()
                GPIO.output(relevador, False)
                
                done_piece = self.move_minus_y(self.piece_select)
                done_pinza = self.move_minus_y(self.pinza)
                done_horizontal_bar = self.move_minus_y(self.horizontal_bar)
                self.lbl_executed_process.setText("Yendo al 1er deposito")
                self.lbl_seconds.hide()
        else:
            
            if self.tiempo_transcurrido >= self.wait_time:
                print("Saliendo del 1er deposito: ", self.tiempo_transcurrido)
                self.timer.stop()
                self.in_process = False
                self.timer_progress.stop()
                self.progress_bar.setValue(self.tiempo_transcurrido)
                self.tiempo_transcurrido = 0
                self.cronometro.setHMS(0, 0, 0)
                
                self.timer2 = QTimer(self)
                self.timer2.timeout.connect(partial(self.process_2_to_4_manual, times))
                self.timer2.start(5)
            else:
                self.progress_bar.setValue(self.tiempo_transcurrido)
                self.lbl_seconds.show()
                self.lbl_seconds.setText(str(self.wait_time)+"s")
                
                
                
                
            
    def process_2_to_4_manual(self, times):
        
        if not self.in_process:
        
            if self.horizontal_bar.y() <= 130 or self.move_in_x:
                
                self.move_in_x = True
                
                if self.pinza.x() >= 360:
                    
                    # TERCERA ANIMACIÓN
                    # SE MUEVE DE ARRIBA PARA ABAJO
                    self.paso_altura_abajo()
                    GPIO.output(relevador, False)
                    
                    done_piece = self.move_y(self.piece_select)
                    done_pinza = self.move_y(self.pinza)
                    done_horizontal_bar = self.move_y(self.horizontal_bar)
                    
                    if self.piece_select.y() >= 270:
                        
                        """self.timer2.stop()
                        
                        print("Llego al 2do deposito (stage 4), va a esperar ", times[2], " segundos")
                        self.move_in_x = False
                        self.draining = True
                        tm.sleep(int(times[2]))
                        print("Saliendo del 2do deposito")
                        
                        self.timer3 = QTimer(self)
                        self.timer3.timeout.connect(partial(self.process_4_to_6, self.times))
                        self.timer3.start(5)"""
                        
                        print("Llego al 2do deposito (stage 4), va a esperar ", times[2], " segundos")
                        self.in_process = True
                        self.move_in_x = False
                        self.wait_time = int(times[2])
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("En 2do deposito")
                        
                        self.timer_progress.start(1000)
                        
                else:
                    
                    if self.draining:
                        
                        print("Llego al 1er escurrimiento (stage 3), va a esperar ", times[1], " segundos")
                        
                        self.in_process = True
                        self.wait_time = int(times[1])
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("En 1er escurrimiento")
                        
                        self.timer_progress.start(1000)
                        
                    else:
                        
                        # SEGUNDA ANIMACIÓN
                        # SE MUEVE DE IZQUIERDA A DERECHA
                        self.paso_profundidad_adelante()
                        GPIO.output(relevador, True)
                        
                        done_piece = self.move_x(self.piece_select)
                        done_pinza = self.move_x(self.pinza)
                    
            elif self.horizontal_bar.y() >= 130 and not self.move_in_x:
                
                # PRIMERA ANIMACIÓN
                # SE MUEVE DE ABAJO PARA ARRIBA
                self.paso_altura_arriba()
                GPIO.output(relevador, False)
                
                done_piece = self.move_minus_y(self.piece_select)
                done_pinza = self.move_minus_y(self.pinza)
                done_horizontal_bar = self.move_minus_y(self.horizontal_bar)
                self.lbl_executed_process.setText("Yendo al 1er escurrimiento")
                self.lbl_seconds.hide()
        else:
            
            if self.draining:
                
                GPIO.output(relevador, False)
                
                if self.tiempo_transcurrido >= self.wait_time:
                    
                    print("Saliendo del 1er escurrimiento: ", self.tiempo_transcurrido)
                    self.in_process = False
                    self.draining = False
                    self.timer_progress.stop()
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.tiempo_transcurrido = 0
                    self.cronometro.setHMS(0, 0, 0)  # Establecer el cronómetro a 00:00:00
                    self.lbl_executed_process.setText("Yendo al 2do deposito")
                    self.lbl_seconds.hide()
                else:
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.lbl_seconds.show()
                    self.lbl_seconds.setText(str(self.wait_time)+"s")
                    
            else:
                
                if self.tiempo_transcurrido >= self.wait_time:
                    
                    print("Saliendo del 1er deposito: ", self.tiempo_transcurrido)
                    self.timer2.stop()
                    self.in_process = False
                    self.timer_progress.stop()
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.tiempo_transcurrido = 0
                    self.cronometro.setHMS(0, 0, 0)  # Establecer el cronómetro a 00:00:00
                    self.draining = True
                    
                    self.timer3 = QTimer(self)
                    self.timer3.timeout.connect(partial(self.process_4_to_6_manual, times))
                    self.timer3.start(5)
                else:
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.lbl_seconds.show()
                    self.lbl_seconds.setText(str(self.wait_time)+"s")
            
            
            
            
            
    def process_4_to_6_manual(self, times):
        
        if not self.in_process:
        
            if self.horizontal_bar.y() <= 130 or self.move_in_x:
                
                self.move_in_x = True
                
                if self.pinza.x() >= 530:
                    
                    # TERCERA ANIMACIÓN
                    # SE MUEVE DE ARRIBA PARA ABAJO
                    self.paso_altura_abajo()
                    GPIO.output(relevador, False)
                    
                    done_piece = self.move_y(self.piece_select)
                    done_pinza = self.move_y(self.pinza)
                    done_horizontal_bar = self.move_y(self.horizontal_bar)
                    
                    if self.piece_select.y() >= 270:
                        
                        """self.timer3.stop()
                        
                        print("Llego al 3er deposito (stage 6), va a esperar ", times[4], " segundos")
                        self.move_in_x = False
                        self.draining = True
                        tm.sleep(int(times[4]))
                        print("Saliendo del 3er deposito")
                        
                        self.timer4 = QTimer(self)
                        self.timer4.timeout.connect(partial(self.process_6_to_8, self.times))
                        self.timer4.start(5)"""
                        
                        self.in_process = True
                        self.move_in_x = False
                        self.wait_time = int(times[4])
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("En 3er deposito")
                        
                        self.timer_progress.start(1000)
                        
                else:
                        
                    if self.draining:
                        
                        print("Llego al 2do escurrimiento (stage 5), va a esperar ", times[3], " segundos")
                        
                        self.in_process = True
                        self.wait_time = int(times[3])
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("En 2do escurrimiento")
                        
                        self.timer_progress.start(1000)
                        
                    else:
                        
                        # SEGUNDA ANIMACIÓN
                        # SE MUEVE DE IZQUIERDA A DERECHA
                        self.paso_profundidad_adelante()
                        GPIO.output(relevador, True)
                        
                        done_piece = self.move_x(self.piece_select)
                        done_pinza = self.move_x(self.pinza)
                    
            elif self.horizontal_bar.y() >= 130 and not self.move_in_x:
                
                # PRIMERA ANIMACIÓN
                # SE MUEVE DE ABAJO PARA ARRIBA
                self.paso_altura_arriba()
                GPIO.output(relevador, False)
                
                done_piece = self.move_minus_y(self.piece_select)
                done_pinza = self.move_minus_y(self.pinza)
                done_horizontal_bar = self.move_minus_y(self.horizontal_bar)
                self.lbl_executed_process.setText("Yendo al 2do escurrimiento")
                self.lbl_seconds.hide()
        else:
            
            if self.draining:
                
                GPIO.output(relevador, False)
                
                if self.tiempo_transcurrido >= self.wait_time:
                    
                    print("Saliendo del 2do escurrimiento: ", self.tiempo_transcurrido)
                    self.in_process = False
                    self.draining = False
                    self.timer_progress.stop()
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.tiempo_transcurrido = 0
                    self.cronometro.setHMS(0, 0, 0)  # Establecer el cronómetro a 00:00:00
                    self.lbl_executed_process.setText("Yendo al 3er deposito")
                    self.lbl_seconds.hide()
                else:
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.lbl_seconds.show()
                    self.lbl_seconds.setText(str(self.wait_time)+"s")
                    
            else:
                
                if self.tiempo_transcurrido >= self.wait_time:
                    
                    print("Saliendo del 2do deposito: ", self.tiempo_transcurrido)
                    self.timer3.stop()
                    self.in_process = False
                    self.timer_progress.stop()
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.tiempo_transcurrido = 0
                    self.cronometro.setHMS(0, 0, 0)  # Establecer el cronómetro a 00:00:00
                    self.draining = True
                    
                    self.timer4 = QTimer(self)
                    self.timer4.timeout.connect(partial(self.process_6_to_8_manual, times))
                    self.timer4.start(5)
                else:
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.lbl_seconds.show()
                    self.lbl_seconds.setText(str(self.wait_time)+"s")
            
            
            
            
    def process_6_to_8_manual(self, times):
        
        if not self.in_process:
        
            if self.horizontal_bar.y() <= 130 or self.move_in_x:
                
                self.move_in_x = True
                
                if self.pinza.x() >= 700:
                    
                    # TERCERA ANIMACIÓN
                    # SE MUEVE DE ARRIBA PARA ABAJO
                    self.paso_altura_abajo()
                    GPIO.output(relevador, False)
                    
                    done_piece = self.move_y(self.piece_select)
                    done_pinza = self.move_y(self.pinza)
                    done_horizontal_bar = self.move_y(self.horizontal_bar)
                    
                    if self.piece_select.y() >= 270:
                        
                        self.timer4.stop()
                        
                        print("Llego al final del proceso (stage 8)")
                        self.move_in_x = False
                        self.draining = True
                        self.lbl_executed_process.setText("Proceso terminado")
                        self.progress_bar.hide()
                        self.btn_salir.show()
                        self.lbl_seconds.hide()
                        self.approved_sound()
                        
                else:
                        
                    if self.draining:
                        
                        print("Llego al 3er escurrimiento (stage 7), va a esperar ", times[5], " segundos")
                        
                        self.in_process = True
                        self.wait_time = int(times[5])
                        
                        self.progress_bar.setMaximum(self.wait_time)
                        self.lbl_executed_process.setText("En 3er escurrimiento")
                        
                        self.timer_progress.start(1000)
                        
                    else:
                        
                        # SEGUNDA ANIMACIÓN
                        # SE MUEVE DE IZQUIERDA A DERECHA
                        self.paso_profundidad_adelante()
                        GPIO.output(relevador, True)
                        
                        done_piece = self.move_x(self.piece_select)
                        done_pinza = self.move_x(self.pinza)
                    
            elif self.horizontal_bar.y() >= 130 and not self.move_in_x:
                
                # PRIMERA ANIMACIÓN
                # SE MUEVE DE ABAJO PARA ARRIBA
                self.paso_altura_arriba()
                GPIO.output(relevador, False)
                
                done_piece = self.move_minus_y(self.piece_select)
                done_pinza = self.move_minus_y(self.pinza)
                done_horizontal_bar = self.move_minus_y(self.horizontal_bar)
                self.lbl_executed_process.setText("Yendo al 3er escurrimiento")
                self.lbl_seconds.hide()
        else:
            
            if self.draining:
                
                GPIO.output(relevador, False)
                
                if self.tiempo_transcurrido >= self.wait_time:
                    
                    print("Saliendo del 3er escurrimiento: ", self.tiempo_transcurrido)
                    self.in_process = False
                    self.draining = False
                    self.timer_progress.stop()
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.tiempo_transcurrido = 0
                    self.cronometro.setHMS(0, 0, 0)  # Establecer el cronómetro a 00:00:00
                    self.lbl_executed_process.setText("Terminando proceso")
                    
                else:
                    self.progress_bar.setValue(self.tiempo_transcurrido)
                    self.lbl_seconds.show()
                    self.lbl_seconds.setText(str(self.wait_time)+"s")
                    
                    
                    
    def process_end_to_start(self):
        
        if self.horizontal_bar.y() <= 130 or self.move_in_x:
            
            self.move_in_x = True
            
            if self.pinza.x() <= 20:
                
                # TERCERA ANIMACIÓN
                # SE MUEVE DE ARRIBA PARA ABAJO
                self.paso_altura_abajo()
                print("Se mueve de arriba a abajo: ", self.pinza.x())
                done_piece = self.move_y(self.piece_select)
                done_pinza = self.move_y(self.pinza)
                done_horizontal_bar = self.move_y(self.horizontal_bar)
                
                if self.piece_select.y() >= 360:
                        
                    self.restart_motor.stop()
                    
                    print("Llego al inicio")
                    self.approved_sound()
                    self.close()
                    
            else:
                    
                # SEGUNDA ANIMACIÓN
                # SE MUEVE DE DERECHA A IZQUIERDA
                self.paso_profundidad_atras()
                print("Se mueve de derecha a izquierda: ", self.pinza.x())
                done_piece = self.move_minus_x(self.piece_select)
                done_pinza = self.move_minus_x(self.pinza)
                
        elif self.horizontal_bar.y() >= 130 and not self.move_in_x:
            
            # PRIMERA ANIMACIÓN
            # SE MUEVE DE ABAJO PARA ARRIBA
            self.paso_altura_arriba()
            print("Se mueve de abajo para arriba: ", self.horizontal_bar.y())
            done_piece = self.move_minus_y(self.piece_select)
            done_pinza = self.move_minus_y(self.pinza)
            done_horizontal_bar = self.move_minus_y(self.horizontal_bar)
                    
                    
                    
    def approved_sound(self):
        GPIO.output(zumbador, True)
        tm.sleep(0.1)
        GPIO.output(zumbador, False)
        tm.sleep(0.1)
        GPIO.output(zumbador, True)
        tm.sleep(0.1)
        GPIO.output(zumbador, False)
        
    def failed_sound(self):
        for i in range(5):
            GPIO.output(zumbador, True)
            tm.sleep(0.055)
            GPIO.output(zumbador, False)
            tm.sleep(0.055)
    
    def paso_profundidad_1(self):
        GPIO.output(pin_profundidad_1, True)
        GPIO.output(pin_profundidad_2, False)
        GPIO.output(pin_profundidad_3, False)
        GPIO.output(pin_profundidad_4, False)
        tm.sleep(iteracion)

    def paso_profundidad_2(self):
        GPIO.output(pin_profundidad_1, True)
        GPIO.output(pin_profundidad_2, False)
        GPIO.output(pin_profundidad_3, True)
        GPIO.output(pin_profundidad_4, False)
        tm.sleep(iteracion)

    def paso_profundidad_3(self):
        GPIO.output(pin_profundidad_1, False)
        GPIO.output(pin_profundidad_2, False)
        GPIO.output(pin_profundidad_3, True)
        GPIO.output(pin_profundidad_4, False)
        tm.sleep(iteracion)

    def paso_profundidad_4(self):
        GPIO.output(pin_profundidad_1, False)
        GPIO.output(pin_profundidad_2, True)
        GPIO.output(pin_profundidad_3, True)
        GPIO.output(pin_profundidad_4, False)
        tm.sleep(iteracion)

    def paso_profundidad_5(self):
        GPIO.output(pin_profundidad_1, False)
        GPIO.output(pin_profundidad_2, True)
        GPIO.output(pin_profundidad_3, False)
        GPIO.output(pin_profundidad_4, False)
        tm.sleep(iteracion)

    def paso_profundidad_6(self):
        GPIO.output(pin_profundidad_1, False)
        GPIO.output(pin_profundidad_2, True)
        GPIO.output(pin_profundidad_3, False)
        GPIO.output(pin_profundidad_4, True)
        tm.sleep(iteracion)

    def paso_profundidad_7(self):
        GPIO.output(pin_profundidad_1, False)
        GPIO.output(pin_profundidad_2, False)
        GPIO.output(pin_profundidad_3, False)
        GPIO.output(pin_profundidad_4, True)
        tm.sleep(iteracion)

    def paso_profundidad_8(self):
        GPIO.output(pin_profundidad_1, True)
        GPIO.output(pin_profundidad_2, False)
        GPIO.output(pin_profundidad_3, False)
        GPIO.output(pin_profundidad_4, True)
        tm.sleep(iteracion)

    def paso_altura_1(self):
        GPIO.output(pin_altura_1, True)
        GPIO.output(pin_altura_2, False)
        GPIO.output(pin_altura_3, False)
        GPIO.output(pin_altura_4, False)
        tm.sleep(iteracion)

    def paso_altura_2(self):
        GPIO.output(pin_altura_1, True)
        GPIO.output(pin_altura_2, False)
        GPIO.output(pin_altura_3, True)
        GPIO.output(pin_altura_4, False)
        tm.sleep(iteracion)

    def paso_altura_3(self):
        GPIO.output(pin_altura_1, False)
        GPIO.output(pin_altura_2, False)
        GPIO.output(pin_altura_3, True)
        GPIO.output(pin_altura_4, False)
        tm.sleep(iteracion)

    def paso_altura_4(self):
        GPIO.output(pin_altura_1, False)
        GPIO.output(pin_altura_2, True)
        GPIO.output(pin_altura_3, True)
        GPIO.output(pin_altura_4, False)
        tm.sleep(iteracion)

    def paso_altura_5(self):
        GPIO.output(pin_altura_1, False)
        GPIO.output(pin_altura_2, True)
        GPIO.output(pin_altura_3, False)
        GPIO.output(pin_altura_4, False)
        tm.sleep(iteracion)

    def paso_altura_6(self):
        GPIO.output(pin_altura_1, False)
        GPIO.output(pin_altura_2, True)
        GPIO.output(pin_altura_3, False)
        GPIO.output(pin_altura_4, True)
        tm.sleep(iteracion)

    def paso_altura_7(self):
        GPIO.output(pin_altura_1, False)
        GPIO.output(pin_altura_2, False)
        GPIO.output(pin_altura_3, False)
        GPIO.output(pin_altura_4, True)
        tm.sleep(iteracion)

    def paso_altura_8(self):
        GPIO.output(pin_altura_1, True)
        GPIO.output(pin_altura_2, False)
        GPIO.output(pin_altura_3, False)
        GPIO.output(pin_altura_4, True)
        tm.sleep(iteracion)

    def paso_profundidad_adelante(self):
        self.paso_profundidad_1();
        self.paso_profundidad_2();
        self.paso_profundidad_3();
        self.paso_profundidad_4();
        self.paso_profundidad_5();
        self.paso_profundidad_6();
        self.paso_profundidad_7();
        self.paso_profundidad_8();

    def paso_profundidad_atras(self):
        self.paso_profundidad_8();
        self.paso_profundidad_7();
        self.paso_profundidad_6();
        self.paso_profundidad_5();
        self.paso_profundidad_4();
        self.paso_profundidad_3();
        self.paso_profundidad_2();
        self.paso_profundidad_1();

    def paso_altura_abajo(self):
        self.paso_altura_1();
        self.paso_altura_2();
        self.paso_altura_3();
        self.paso_altura_4();
        self.paso_altura_5();
        self.paso_altura_6();
        self.paso_altura_7();
        self.paso_altura_8();

    def paso_altura_arriba(self):
        self.paso_altura_8();
        self.paso_altura_7();
        self.paso_altura_6();
        self.paso_altura_5();
        self.paso_altura_4();
        self.paso_altura_3();
        self.paso_altura_2();
        self.paso_altura_1();








class numeric_keyboard(QDialog):
    
    def __init__(self, piece):
        super().__init__()
        
        self.setGeometry(0, 0, 800, 480)
        self.setWindowFlags(Qt.FramelessWindowHint)
        uic.loadUi(f"{direccion_design}/numeric_keyboard.ui", self)
        # Bloquea la interacción con otras partes de la aplicación
        self.setWindowModality(Qt.ApplicationModal)

        self.resultado = ""
        self.piece = piece
        
        #print("Pieza seleccionada: ", piece)
        self.lbl_name.setText(piece)
        self.lbl_img.setPixmap(QPixmap(f"{direccion_img}/{piece.lower()}.png"))
        self.btn_cancel.mousePressEvent = self.close_window
        

        # Diseño del teclado numérico
        layout = QGridLayout()
        self.botones = {
            "one": [], "two": [], "three": [], "four": [], "five": [], "six": [], "seven": [], "eight": [], "nine": [], "zero": [], "del": [], "enter": []
        }

        # Configura los eventos de clic en los botones del teclado
        for name, val in self.botones.items():
            for i in range(1):
                label_teclado = getattr(self, f"btn_{name}{i+1}")
                label_teclado.mousePressEvent = self.get_mouse_press_event_handler(name)

        self.btn_enter1.mousePressEvent = self.aceptar
        
    def close_window(self, event):
        self.resultado = "cancelar"
        self.accept()
        
    
    def get_mouse_press_event_handler(self, function_name):
        return lambda event, name=function_name: self.on_mouse_press(event, name)

    def on_mouse_press(self, event, name):
        
        self.click_sound()
        
        teclas_numericas = {
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "zero": "0",
        }

        if name == "del":
            # Elimina el último carácter ingresado
            self.delete_last_character()
        elif name in teclas_numericas:
            # Procesa la presión de una tecla numérica y actualiza la variable y la interfaz
            self.handle_numeric_key_press(name, teclas_numericas[name])
        
        self.txed_response.setText("".join(self.resultado))
        
    def delete_last_character(self):
        # Elimina el último carácter ingresado
        self.resultado = self.resultado[:-1]

        self.txed_response.setText("".join(self.resultado))

        # Mueve el cursor al final del texto
        cursor = self.txed_response.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.txed_response.setTextCursor(cursor)
        
    
    def handle_numeric_key_press(self, name, value):
        # Maneja la presión de una tecla numérica y actualiza la variable y la interfaz
        self.resultado = self.resultado + value
        self.txed_response.setPlainText("".join(self.resultado))

        cursor = self.txed_response.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.txed_response.setTextCursor(cursor)

    def aceptar(self, event):
        
        if len(self.resultado) == 0:
            self.window_message = message("Ingrese un numero de piezas", "sin_tiempos", "warning")
            self.window_message.show()
        else:
            if int(self.resultado) == 0:
                self.window_message = message("Ingrese un numero de piezas mayor a 0", "sin_tiempos", "warning")
                self.window_message.show()
            else:
                self.accept()
                
                
    def click_sound(self):
        GPIO.output(zumbador, True)
        tm.sleep(0.1)
        GPIO.output(zumbador, False)










class only_keyboard(QDialog):

    def __init__(self, source_button):
        super().__init__()
        
        self.setGeometry(0, 0, 800, 480)
        self.setWindowFlags(Qt.FramelessWindowHint)
        uic.loadUi(f"{direccion_design}/only_keyboard.ui", self)
        # Bloquea la interacción con otras partes de la aplicación
        self.setWindowModality(Qt.ApplicationModal)

        self.resultado = ""
        self.source_button = source_button
        

        # Diseño del teclado numérico
        layout = QGridLayout()
        self.botones = {
            "one": [], "two": [], "three": [], "four": [], "five": [], "six": [], "seven": [], "eight": [], "nine": [], "zero": [],
            "del": [], "enter": []
        }

        # Configura los eventos de clic en los botones del teclado
        for name, val in self.botones.items():
            for i in range(1):
                label_teclado = getattr(self, f"btn_{name}{i+1}")
                label_teclado.mousePressEvent = self.get_mouse_press_event_handler(name)

        self.btn_enter1.mousePressEvent = self.aceptar
        
        self.center_on_screen()
        
    def center_on_screen(self):
        # Obtiene el tamaño de la pantalla disponible
        screen_geometry = QDesktopWidget().availableGeometry()

        # Calcula la posición para centrar la ventana emergente
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2

        # Establece la posición centrada
        self.move(x, y)
    
    def get_mouse_press_event_handler(self, function_name):
        return lambda event, name=function_name: self.on_mouse_press(event, name)

    def on_mouse_press(self, event, name):
        
        self.click_sound()
        
        teclas_numericas = {
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "zero": "0",
        }

        if name == "del":
            # Elimina el último carácter ingresado
            self.delete_last_character()
        elif name in teclas_numericas:
            # Procesa la presión de una tecla numérica y actualiza la variable y la interfaz
            self.handle_numeric_key_press(name, teclas_numericas[name])
        
        self.txed_response.setText("".join(self.resultado))
        
    def delete_last_character(self):
        # Elimina el último carácter ingresado
        self.resultado = self.resultado[:-1]

        self.txed_response.setText("".join(self.resultado))

        # Mueve el cursor al final del texto
        cursor = self.txed_response.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.txed_response.setTextCursor(cursor)
        
    
    def handle_numeric_key_press(self, name, value):
        # Maneja la presión de una tecla numérica y actualiza la variable y la interfaz
        self.resultado = self.resultado + value
        self.txed_response.setPlainText("".join(self.resultado))

        cursor = self.txed_response.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.txed_response.setTextCursor(cursor)

    def aceptar(self, event):
        self.accept(source_button=self.source_button)
        
    def accept(self, source_button):
        self.source_button = source_button
        super().accept()
    
    def click_sound(self):
        GPIO.output(zumbador, True)
        tm.sleep(0.1)
        GPIO.output(zumbador, False)










class message(QDialog):

    def __init__(self, message, img, icon):
        super().__init__()
        
        self.setGeometry(0, 0, 800, 480)
        self.setWindowFlags(Qt.FramelessWindowHint)
        uic.loadUi(f"{direccion_design}/message.ui", self)
        # Bloquea la interacción con otras partes de la aplicación
        self.setWindowModality(Qt.ApplicationModal)

        self.message = message
        self.img = img
        self.icon = icon
        
        self.lbl_message.setText(message)
        self.lbl_img.setPixmap(QPixmap(f"{direccion_img}/{img}.png"))
        self.lbl_icon.setPixmap(QPixmap(f"{direccion_img}/{icon}.png"))
        
        self.btn_ok.mousePressEvent = self.ok
        self.center_on_screen()
        
    def center_on_screen(self):
        # Obtiene el tamaño de la pantalla disponible
        screen_geometry = QDesktopWidget().availableGeometry()

        # Calcula la posición para centrar la ventana emergente
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2

        # Establece la posición centrada
        self.move(x, y)
        
    def ok(self, event):
        self.close()
        
def actualizar_fecha_hora():
    
    try:
        # Especifica el servidor NTP al que te quieres conectar
        ntp_server = 'pool.ntp.org'

        # Conecta con el servidor NTP
        cliente_ntp = ntplib.NTPClient()
        respuesta_ntp = cliente_ntp.request(ntp_server)

        # Obtiene la fecha y hora del servidor NTP
        fecha_hora_servidor = datetime.fromtimestamp(respuesta_ntp.tx_time)

        # Formatea la fecha y hora
        formatted_date_time = fecha_hora_servidor.strftime("%Y-%m-%d %H:%M:%S")

        # Ejecuta el comando para actualizar la fecha y hora del sistema
        command = f"sudo date -s '{formatted_date_time}'"
        subprocess.call(command, shell=True)

        print(f"Fecha y hora actualizadas a: {formatted_date_time}")
        return True
    except Exception as e:
        print("No se pudo actualizar la hora del sistema")
        print(traceback.format_exc())
        return False
        
if __name__ == '__main__':
    
    while True:
        done_date_hour = actualizar_fecha_hora()
        if done_date_hour:
            break
    
    app = QApplication(['a'])
    GUI = Main()
    GUI.show()
    sys.exit(app.exec())