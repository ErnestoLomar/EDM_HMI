import RPi.GPIO as GPIO
import time

iteracion = 0.015
pin_profundidad_1 = 29	#37
pin_profundidad_2 = 23	#35
pin_profundidad_3 = 21	#33
pin_profundidad_4 = 19	#31

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_profundidad_1, GPIO.OUT)
GPIO.setup(pin_profundidad_2, GPIO.OUT)
GPIO.setup(pin_profundidad_3, GPIO.OUT)
GPIO.setup(pin_profundidad_4, GPIO.OUT)
time.sleep(1.0)

def paso_1():
	GPIO.output(pin_profundidad_1, True)
	GPIO.output(pin_profundidad_2, False)
	GPIO.output(pin_profundidad_3, False)
	GPIO.output(pin_profundidad_4, False)
	time.sleep(iteracion)

def paso_2():
	GPIO.output(pin_profundidad_1, True)
	GPIO.output(pin_profundidad_2, False)
	GPIO.output(pin_profundidad_3, True)
	GPIO.output(pin_profundidad_4, False)
	time.sleep(iteracion)

def paso_3():
	GPIO.output(pin_profundidad_1, False)
	GPIO.output(pin_profundidad_2, False)
	GPIO.output(pin_profundidad_3, True)
	GPIO.output(pin_profundidad_4, False)
	time.sleep(iteracion)

def paso_4():
	GPIO.output(pin_profundidad_1, False)
	GPIO.output(pin_profundidad_2, True)
	GPIO.output(pin_profundidad_3, True)
	GPIO.output(pin_profundidad_4, False)
	time.sleep(iteracion)

def paso_5():
	GPIO.output(pin_profundidad_1, False)
	GPIO.output(pin_profundidad_2, True)
	GPIO.output(pin_profundidad_3, False)
	GPIO.output(pin_profundidad_4, False)
	time.sleep(iteracion)

def paso_6():
	GPIO.output(pin_profundidad_1, False)
	GPIO.output(pin_profundidad_2, True)
	GPIO.output(pin_profundidad_3, False)
	GPIO.output(pin_profundidad_4, True)
	time.sleep(iteracion)

def paso_7():
	GPIO.output(pin_profundidad_1, False)
	GPIO.output(pin_profundidad_2, False)
	GPIO.output(pin_profundidad_3, False)
	GPIO.output(pin_profundidad_4, True)
	time.sleep(iteracion)

def paso_8():
	GPIO.output(pin_profundidad_1, True)
	GPIO.output(pin_profundidad_2, False)
	GPIO.output(pin_profundidad_3, False)
	GPIO.output(pin_profundidad_4, True)
	time.sleep(iteracion)

def paso_adelante():
	paso_1();
	paso_2();
	paso_3();
	paso_4();
	paso_5();
	paso_6();
	paso_7();
	paso_8();

def paso_atras():
	paso_8();
	paso_7();
	paso_6();
	paso_5();
	paso_4();
	paso_3();
	paso_2();
	paso_1();

while True:
	for i in range(40):
		paso_adelante()

	for i in range(40):
		paso_atras()

	time.sleep(3.0)
 
 
 
 
 
 
import RPi.GPIO as GPIO
import time

zumbador = 7
relevador = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(relevador, GPIO.OUT)
GPIO.setup(zumbador, GPIO.OUT)
    
time.sleep(2)

print("Empezando prueba de relevador y zumbador")

while True:
	print("Se pasa el relevador a True")
	GPIO.output(relevador, True)
	time.sleep(5)
	print("Se pasa el relevador a False")
	GPIO.output(relevador, False)
	
	time.sleep(5)

	print("APROBADO")
	GPIO.output(zumbador, True)
	time.sleep(0.1)
	GPIO.output(zumbador, False)
	time.sleep(0.1)
	GPIO.output(zumbador, True)
	time.sleep(0.1)
	GPIO.output(zumbador, False)

	time.sleep(2)

	print("REPROBADO")

	for i in range(5):
		  GPIO.output(zumbador, True)
		  time.sleep(0.055)
		  GPIO.output(zumbador, False)
		  time.sleep(0.055)

	time.sleep(1)