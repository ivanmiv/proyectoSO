#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# Librerias requeridas para correr aplicaciones basadas en Flask
from flask import Flask, jsonify, make_response, request
import subprocess
 
app = Flask(__name__)

# Web service que se invoca al momento de ejecutar el comando
# curl http://localhost:5000
@app.route('/',methods = ['GET'])
def index():
	
	texto = ">>>Raiz del web service \n"
	texto+= "/vms/ostypes para ver los sitemas soportados \n"
	texto+= "/vms para ver la lsita de maquinas asociadas al usuario \n"
	texto+= "/vms/running para ver las maquinas que se encuentran en ejecucion \n"
	texto+= "/vms/info/<vmname> para ver las caracteristicas de la maquina con vmname <vname> \n"
	texto+= "/vms/make para crear una maquina virtual con los parametros enviados atraves de POST \n"
	texto+= "/vms/delete/<vmname> para borrar la maquina con nombre <vname> \n"
	texto+= "<<<Extras>>>\n"
	texto+= "/vms/start/<vmname> para iniciar la maquina con nombre <vname> \n"
	texto+= "/vms/stop/<vmname> para detener la maquina con nombre <vname> \n"
	return texto

# Este metodo retorna la lista de sistemas operativos soportados por VirtualBox
# Los tipos de sistemas operativos soportados deben ser mostrados al ejecutar 
# el comando
# curl http://localhost:5000/vms/ostypes
@app.route('/vms/ostypes',methods = ['GET'])
def ostypes():
	output = "Os Types\n"	
	output+= subprocess.check_output("VBoxManage list ostypes",shell=True)
	return output

# Este metodo retorna la lista de maquinas asociadas con un usuario al ejecutar
# el comando
# curl http://localhost:5000/vms
@app.route('/vms',methods = ['GET'])
def listvms():
	output = "Maquinas asociadas al usuario \n"
	
	output+= subprocess.check_output("VBoxManage list vms",shell=True)	
	 
	return output
	

# Este metodo retorna aquellas maquinas que se encuentran en ejecucion al 
# ejecutar el comando
# curl http://localhost:5000/vms/running
@app.route('/vms/running',methods = ['GET'])
def runninglistvms():

	
	funcionando = int(subprocess.check_output("echo $((`VBoxManage list runningvms | grep -c \"\"`))",shell=True))
	
	output = "Maquinas ejecutandose: "+str(funcionando)+" \n"
	
	
	if funcionando>0:
		output+= subprocess.check_output(['VBoxManage','list','runningvms'])+"\n"
				
	else:
		output+= "No hay maquinas funcionando en el equipo\n"
		
	return output


# Este metodo retorna las caracteristica de una maquina virtual cuyo nombre es vname
# curl http://localhost:5000/vms/info/<vmname>

@app.route('/vms/info/<vmname>', methods = ['GET'])
def vminfo(vmname=None):
	output = "Info: "+vmname+"\n"
	
	existe = int(subprocess.check_output("echo $((`VBoxManage list vms | grep -c \""+vmname+"\"`))",shell=True))
	
	if existe != 0:	
		
		#Informacion de numero de cpu y memoria
		comando = "bash VBoxManage showvminfo \"" + vmname + "\" | grep  -e 'Number of CPUs' -e Memory"		
		output += subprocess.check_output(comando,shell=True)	
		
		
		interfacesRed = "VBoxManage showvminfo \""+vmname+"\" | grep 'NIC' | grep -v 'disabled' | grep -v 'Settings' | cut -d ',' -f2 | cut -d ':' -f2" 
		numinterfacesRed = interfacesRed+" | grep -c '' "
		
		output += "Numero de interfaces de red : "+subprocess.check_output(numinterfacesRed,shell=True)
		output += "Detalle interfaces de red: \n"
		output += subprocess.check_output(interfacesRed,shell=True)
		
		
	else:
		output+= "Ha ocurrido un error, no existe una maquina con nombre "+vmname+"\n"
		output+= "Imposible mostrar informacion de una maquina inexistente \n"	
		
		
	return output
	
	
# Este metodo crea una maquina virtual con los parametros enviados en POST
@app.route('/vms/make', methods = ['POST'])
def vmmake():
	output = "Creando: \n"	
	nombre = request.form['nombre']
	cantidadCPU = request.form['cantidadNucleos']
	capacidadRam = request.form['capacidadRam']
	output+="Datos: Nombre = "+nombre+" Cantidad de CPU = "+cantidadCPU+" Capacidad de ram = "+capacidadRam+"\n"
	
	#Ejecucion del script de crear maquina	
	
	existe = int(subprocess.check_output("echo $((`VBoxManage list vms | grep -c \""+nombre+"\"`))",shell=True))
	 
	if existe == 1:		
		output+= "Ha ocurrido un error, ya existe una maquina con nombre "+nombre+"\n"
		output+= "no es posible crear dos maquinas con el mismo nombre, por favor seleccione otro \n"
	else:
		
		#Comandos necesarios para crear una maquina virtual		

		subprocess.check_output("VBoxManage  createhd --filename \""+nombre+"\".vdi --size 100",shell=True)
		subprocess.check_output("VBoxManage createvm --name \""+nombre+"\" --ostype \"Ubuntu\" --register",shell=True)
		subprocess.check_output("VBoxManage storagectl \""+nombre+"\" --name \"SATA Controller\" --add sata --controller IntelAHCI",shell=True)
		subprocess.check_output("VBoxManage storageattach \""+nombre+"\" --storagectl \"SATA Controller\" --port 0 --device 0 --type hdd --medium \""+nombre+"\".vdi",shell=True)
		subprocess.check_output("VBoxManage storagectl \""+nombre+"\" --name \"IDE Controller\" --add ide",shell=True)
		subprocess.check_output("VBoxManage modifyvm \""+nombre+"\" --ioapic on",shell=True)
		subprocess.check_output("VBoxManage modifyvm \""+nombre+"\" --boot1 dvd --boot2 disk --boot3 none --boot4 none",shell=True)
		subprocess.check_output("VBoxManage modifyvm \""+nombre+"\" --memory \""+capacidadRam+"\" --vram 128",shell=True)
		subprocess.check_output("VBoxManage modifyvm \""+nombre+"\" --cpus "+cantidadCPU+"",shell=True)
		
		output+= "Maquina creada \n"
		
		

	return output	

	
# Este metodo borra la maquina virtual llamada <vmname>
@app.route('/vms/delete/<vmname>', methods = ['DELETE'])
def vmdelete(vmname=None):
	output = "Borrar: "+vmname+"\n"
	
	
	existe = int(subprocess.check_output("echo $((`VBoxManage list vms | grep -c \""+vmname+"\"`))",shell=True))
	 
	if existe == 1:		
		output += "Resultado de borrar ="+subprocess.check_output("VBoxManage unregistervm \""+vmname+"\" --delete",shell=True)+" ok \n"	
	else:	
		output+= "Ha ocurrido un error, no existe una maquina con nombre "+vmname+"\n"
		output+= "No es posible eliminar una maquina inexistente\n"
		
	return output
	


	
######################################################################	
# 	Metodo adicional paara iniciar una maquina y comprobar el funcionamiento de /vms/running
# curl http://localhost:5000/vms/start/<vmname>

@app.route('/vms/start/<vmname>', methods = ['GET'])
def vmstart(vmname=None):
	output = "Iniciando: "+vmname+"\n"
	
	existe = int(subprocess.check_output("echo $((`VBoxManage list vms | grep -c \""+vmname+"\"`))",shell=True))
	if existe != 1:
		return "No existe la maquina llamada "+vmname
		
	
	funcionando = int(subprocess.check_output("echo $((`VBoxManage list runningvms | grep -c \""+vmname+"\"`))",shell=True))
	
	if funcionando == 1:
		output+= "La maquina \""+vmname+"\" ya se encuentra Funcionando\n"		
	else:
		output+= subprocess.check_output("VBoxManage startvm \""+vmname+"\" --type headless",shell=True)+"\n"	
		
	return output

# 	Metodo adicional paara detener maquinas y comprobar el funcionamiento de /vms/running
# curl http://localhost:5000/vms/stop/<vmname>
@app.route('/vms/stop/<vmname>', methods = ['GET'])
def vmstop(vmname=None):
	output = "Deteniendo: "+vmname+"\n"

	existe = int(subprocess.check_output("echo $((`VBoxManage list vms | grep -c \""+vmname+"\"`))",shell=True))
	if existe != 1:
		return "No existe la maquina llamada "+vmname+"\n"	
	
	funcionando = int(subprocess.check_output("echo $((`VBoxManage list runningvms | grep -c \""+vmname+"\"`))",shell=True))
	
	if funcionando == 1:
		output+= subprocess.check_output("VBoxManage controlvm \""+vmname+"\" poweroff soft",shell=True)+"\n"
		output+= "Maquina detenida correctamente\n"
		
	else:
		output+= "La maquina \""+vmname+"\" no ha sido iniciada\n"	
		
		
	return output	
	
	
######################################################################

if __name__ == '__main__':
        app.run(debug = True, host='0.0.0.0')