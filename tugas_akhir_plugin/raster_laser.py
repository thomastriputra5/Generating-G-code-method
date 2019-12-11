'''
# ----------------------------------------------------------------------------
# Copyright (C) 2014 305engineering <305engineering@gmail.com>
# Original concept by 305engineering.
#
# "THE MODIFIED BEER-WARE LICENSE" (Revision: my own :P):
# <305engineering@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff (except sell). If we meet some day, 
# and you think this stuff is worth it, you can buy me a beer in return.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------
'''


import sys
import os
import re

sys.path.append('/usr/share/inkscape/extensions')
sys.path.append('/Applications/Inkscape.app/Contents/Resources/extensions') 

import subprocess
import math

# import inkex
# import png
import array


class GcodeExport:
	def __init__(self):
        self.directory = "/home/"
        self.filename = -1.0
        self.add_numeric_suffix_to_filename = True
        self.bg_color = ""
		self.resolution = 5
		
		# How To Convert to Grayscale
		self.grayscale_type = 1

		# Conversion mode in Black and White
		self.conversion_type = 1

		# Mode Option
		self.BW_threshold = 128
		self.grayscale_resolution = 1

		# Black speed and shift
		self.speed_ON = 200

		# Mirror Y
		self.flip_y = False

		# Homing
		self.homing = 1

		# Commands
		self.laseron = "M03"
		self.laseroff = "M05"

		self.preview_only = False
		
		
	def effect(self):
		# Callback from __init__()
		# Everything takes place here
		

		current_file = self.args[-1]
		bg_color = self.bg_color
		
		
		##Implementare check_dir
		
		if (os.path.isdir(self.directory)) == True:					
			
			##CODICE SE ESISTE LA DIRECTORY
			#inkex.errormsg("OK") #DEBUG

			
			#Aggiungo un suffisso al nomefile per non sovrascrivere dei file
			if self.add_numeric_suffix_to_filename :
				dir_list = os.listdir(self.directory) #List di tutti i file nella directory di lavoro
				temp_name =  self.filename
				max_n = 0
				for s in dir_list :
					r = re.match(r"^%s_0*(\d+)%s$"%(re.escape(temp_name),'.png' ), s)
					if r :
						max_n = max(max_n,int(r.group(1)))	
				self.filename = temp_name + "_" + ( "0"*(4-len(str(max_n+1))) + str(max_n+1) )


			#genero i percorsi file da usare
			
			suffix = ""
			if self.conversion_type == 1:
				suffix = "_BWfix_"+str(self.BW_threshold)+"_"
			elif self.conversion_type == 2:
				suffix = "_BWrnd_"
			elif self.conversion_type == 3:
				suffix = "_H_"
			elif self.conversion_type == 4:
				suffix = "_Hrow_"
			elif self.conversion_type == 5:
				suffix = "_Hcol_"
			else:
				if self.grayscale_resolution == 1:
					suffix = "_Gray_256_"
				elif self.grayscale_resolution == 2:
					suffix = "_Gray_128_"
				elif self.grayscale_resolution == 4:
					suffix = "_Gray_64_"
				elif self.grayscale_resolution == 8:
					suffix = "_Gray_32_"
				elif self.grayscale_resolution == 16:
					suffix = "_Gray_16_"
				elif self.grayscale_resolution == 32:
					suffix = "_Gray_8_"
				else:
					suffix = "_Gray_"
				
			
			pos_file_png_exported = os.path.join(self.directory,self.filename+".png") 
			pos_file_png_BW = os.path.join(self.directory,self.filename+suffix+"preview.png") 
			pos_file_gcode = os.path.join(self.directory,self.filename+suffix+"gcode.txt") 
			

			#Esporto l'immagine in PNG
			self.exportPage(pos_file_png_exported,current_file,bg_color)


			
			#DA FARE
			#Manipolo l'immagine PNG per generare il file Gcode
			self.PNGtoGcode(pos_file_png_exported,pos_file_png_BW,pos_file_gcode)
						
			
		else:
			inkex.errormsg("Directory does not exist! Please specify existing directory!")
            

            
            
########	ESPORTA L IMMAGINE IN PNG		
######## 	Richiamata da effect()
		
	def exportPage(self,pos_file_png_exported,current_file,bg_color):		
		######## CREAZIONE DEL FILE PNG ########
		#Crea l'immagine dentro la cartella indicata  da "pos_file_png_exported"
		# -d 127 = risoluzione 127DPI  =>  5 pixel/mm  1pixel = 0.2mm
		###command="inkscape -C -e \"%s\" -b\"%s\" %s -d 127" % (pos_file_png_exported,bg_color,current_file) 

		if self.resolution == 1:
			DPI = 25.4
		elif self.resolution == 2:
			DPI = 50.8
		elif self.resolution == 5:
			DPI = 127
		else:
			DPI = 254

		command="inkscape -C -e \"%s\" -b\"%s\" %s -d %s" % (pos_file_png_exported,bg_color,current_file,DPI) #Comando da linea di comando per esportare in PNG
					
		p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return_code = p.wait()
		f = p.stdout
		err = p.stderr


########	CREA IMMAGINE IN B/N E POI GENERA GCODE
######## 	Richiamata da effect()

	def PNGtoGcode(self,pos_file_png_exported,pos_file_png_BW,pos_file_gcode):
		
		######## GENERO IMMAGINE IN SCALA DI GRIGI ########
		#Scorro l immagine e la faccio diventare una matrice composta da list


		reader = png.Reader(pos_file_png_exported)#File PNG generato
		
		w, h, pixels, metadata = reader.read_flat()
		
		
		matrice = [[255 for i in range(w)]for j in range(h)]  #List al posto di un array
		

		#Scrivo una nuova immagine in Scala di grigio 8bit
		#copia pixel per pixel 
		
		if self.grayscale_type == 1:
			#0.21R + 0.71G + 0.07B
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[pixel_position]*0.21 + pixels[(pixel_position+1)]*0.71 + pixels[(pixel_position+2)]*0.07)
		
		elif self.grayscale_type == 2:
			#(R+G+B)/3
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int((pixels[pixel_position] + pixels[(pixel_position+1)]+ pixels[(pixel_position+2)]) / 3 )		

		elif self.grayscale_type == 3:
			#R
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[pixel_position])			

		elif self.grayscale_type == 4:
			#G
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[(pixel_position+1)])	
		
		elif self.grayscale_type == 5:
			#B
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					matrice[y][x] = int(pixels[(pixel_position+2)])				
			
		elif self.grayscale_type == 6:
			#Max Color
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					list_RGB = pixels[pixel_position] , pixels[(pixel_position+1)] , pixels[(pixel_position+2)]
					matrice[y][x] = int(max(list_RGB))				

		else:
			#Min Color
			for y in range(h): # y varia da 0 a h-1
				for x in range(w): # x varia da 0 a w-1
					pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
					list_RGB = pixels[pixel_position] , pixels[(pixel_position+1)] , pixels[(pixel_position+2)]
					matrice[y][x] = int(min(list_RGB))	
		

		####Ora matrice contiene l'immagine in scala di grigi


		######## GENERO IMMAGINE IN BIANCO E NERO ########
		#Scorro matrice e genero matrice_BN
		B=255
		N=0 
		
		matrice_BN = [[255 for i in range(w)]for j in range(h)]
		
		
		if self.conversion_type == 1:
			#B/W fixed threshold
			soglia = self.BW_threshold
			for y in range(h): 
				for x in range(w):
					if matrice[y][x] >= soglia :
						matrice_BN[y][x] = B
					else:
						matrice_BN[y][x] = N
	
			
		elif self.conversion_type == 2:
			#B/W random threshold
			from random import randint
			for y in range(h): 
				for x in range(w): 
					soglia = randint(20,235)
					if matrice[y][x] >= soglia :
						matrice_BN[y][x] = B
					else:
						matrice_BN[y][x] = N
			
			
		elif self.conversion_type == 3:
			#Halftone
			Step1 = [[B,B,B,B,B],[B,B,B,B,B],[B,B,N,B,B],[B,B,B,B,B],[B,B,B,B,B]]
			Step2 = [[B,B,B,B,B],[B,B,N,B,B],[B,N,N,N,B],[B,B,N,B,B],[B,B,B,B,B]]
			Step3 = [[B,B,N,B,B],[B,N,N,N,B],[N,N,N,N,N],[B,N,N,N,B],[B,B,N,B,B]]
			Step4 = [[B,N,N,N,B],[N,N,N,N,N],[N,N,N,N,N],[N,N,N,N,N],[B,N,N,N,B]]
			
			for y in range(h/5): 
				for x in range(w/5): 
					media = 0
					for y2 in range(5):
						for x2 in range(5):
							media +=  matrice[y*5+y2][x*5+x2]
					media = media /25
					for y3 in range(5):
						for x3 in range(5):
							if media >= 250 and media <= 255:
								matrice_BN[y*5+y3][x*5+x3] = 	B	
							if media >= 190 and media < 250:
								matrice_BN[y*5+y3][x*5+x3] =	Step1[y3][x3]
							if media >= 130 and media < 190:
								matrice_BN[y*5+y3][x*5+x3] =	Step2[y3][x3]
							if media >= 70 and media < 130:
								matrice_BN[y*5+y3][x*5+x3] =	Step3[y3][x3]
							if media >= 10 and media < 70:
								matrice_BN[y*5+y3][x*5+x3] =	Step4[y3][x3]		
							if media >= 0 and media < 10:
								matrice_BN[y*5+y3][x*5+x3] = N


		elif self.conversion_type == 4:
			#Halftone row
			Step1r = [B,B,N,B,B]
			Step2r = [B,N,N,B,B]
			Step3r = [B,N,N,N,B]
			Step4r = [N,N,N,N,B]

			for y in range(h): 
				for x in range(w/5): 
					media = 0
					for x2 in range(5):
						media +=  matrice[y][x*5+x2]
					media = media /5
					for x3 in range(5):
						if media >= 250 and media <= 255:
							matrice_BN[y][x*5+x3] = 	B
						if media >= 190 and media < 250:
							matrice_BN[y][x*5+x3] =	Step1r[x3]
						if media >= 130 and media < 190:
							matrice_BN[y][x*5+x3] =	Step2r[x3]
						if media >= 70 and media < 130:
							matrice_BN[y][x*5+x3] =	Step3r[x3]
						if media >= 10 and media < 70:
							matrice_BN[y][x*5+x3] =	Step4r[x3]		
						if media >= 0 and media < 10:
							matrice_BN[y][x*5+x3] = N			


		elif self.conversion_type == 5:
			#Halftone column
			Step1c = [B,B,N,B,B]
			Step2c = [B,N,N,B,B]
			Step3c = [B,N,N,N,B]
			Step4c = [N,N,N,N,B]

			for y in range(h/5):
				for x in range(w):
					media = 0
					for y2 in range(5):
						media +=  matrice[y*5+y2][x]
					media = media /5
					for y3 in range(5):
						if media >= 250 and media <= 255:
							matrice_BN[y*5+y3][x] = 	B
						if media >= 190 and media < 250:
							matrice_BN[y*5+y3][x] =	Step1c[y3]
						if media >= 130 and media < 190:
							matrice_BN[y*5+y3][x] =	Step2c[y3]
						if media >= 70 and media < 130:
							matrice_BN[y*5+y3][x] =	Step3c[y3]
						if media >= 10 and media < 70:
							matrice_BN[y*5+y3][x] =	Step4c[y3]		
						if media >= 0 and media < 10:
							matrice_BN[y*5+y3][x] = N			
			
		else:
			#Grayscale
			if self.grayscale_resolution == 1:
				matrice_BN = matrice
			else:
				for y in range(h): 
					for x in range(w): 
						if matrice[y][x] <= 1:
							matrice_BN[y][x] == 0
							
						if matrice[y][x] >= 254:
							matrice_BN[y][x] == 255
						
						if matrice[y][x] > 1 and matrice[y][x] <254:
							matrice_BN[y][x] = ( matrice[y][x] // self.grayscale_resolution ) * self.grayscale_resolution
						
			
			
		####Ora matrice_BN contiene l'immagine in Bianco (255) e Nero (0)


		#### SALVO IMMAGINE IN BIANCO E NERO ####
		file_img_BN = open(pos_file_png_BW, 'wb') #Creo il file
		Costruttore_img = png.Writer(w, h, greyscale=True, bitdepth=8) #Impostazione del file immagine
		Costruttore_img.write(file_img_BN, matrice_BN) #Costruttore del file immagine
		file_img_BN.close()	#Chiudo il file


		#### GENERO IL FILE GCODE ####
		if self.preview_only == False: #Genero Gcode solo se devo
		
			if self.flip_y == False: #Inverto asse Y solo se flip_y = False     
				#-> coordinate Cartesiane (False) Coordinate "informatiche" (True)
				matrice_BN.reverse()				

			
			Laser_ON = False
			F_G01 = self.speed_ON
			Scala = self.resolution

			file_gcode = open(pos_file_gcode, 'w')  #Creo il file
			
			#Configurazioni iniziali standard Gcode
			file_gcode.write('; Generated with:\n; "Raster 2 Laser Gcode generator"\n; by 305 Engineering\n;\n;\n;\n')
			#HOMING
			if self.homing == 1:
				file_gcode.write('G28; home all axes\n')
			elif self.homing == 2:
				file_gcode.write('$H; home all axes\n')
			else:
				pass
			file_gcode.write('G21; Set units to millimeters\n')			
			file_gcode.write('G90; Use absolute coordinates\n')				
			file_gcode.write('G92; Coordinate Offset\n')	

			#Creazione del Gcode
			
			#allargo la matrice per lavorare su tutta l'immagine
			for y in range(h):
				matrice_BN[y].append(B)
			w = w+1
			
			if self.conversion_type != 6:
				for y in range(h):
					if y % 2 == 0 :
						for x in range(w):
							if matrice_BN[y][x] == N :
								if Laser_ON == False :
									#file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G00) + '\n')
									file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n') #tolto il Feed sul G00
									file_gcode.write(self.laseron + '\n')			
									Laser_ON = True
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == w-1 :
										file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
										file_gcode.write(self.laseroff + '\n')
										Laser_ON = False
									else: 
										if matrice_BN[y][x+1] != N :
											file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											file_gcode.write(self.laseroff + '\n')
											Laser_ON = False
					else:
						for x in reversed(range(w)):
							if matrice_BN[y][x] == N :
								if Laser_ON == False :
									#file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G00) + '\n')
									file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n') #tolto il Feed sul G00
									file_gcode.write(self.laseron + '\n')			
									Laser_ON = True
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == 0 :
										file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
										file_gcode.write(self.laseroff + '\n')
										Laser_ON = False
									else: 
										if matrice_BN[y][x-1] != N :
											file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											file_gcode.write(self.laseroff + '\n')
											Laser_ON = False				

			else: ##SCALA DI GRIGI
				for y in range(h):
					if y % 2 == 0 :
						for x in range(w):
							if matrice_BN[y][x] != B :
								if Laser_ON == False :
									file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
									file_gcode.write(self.laseron + ' '+ ' S' + str(255 - matrice_BN[y][x]) +'\n')
									Laser_ON = True
									
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == w-1 : #controllo fine riga
										file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
										file_gcode.write(self.laseroff + '\n')
										Laser_ON = False
										
									else: 
										if matrice_BN[y][x+1] == B :
											file_gcode.write('G01 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											file_gcode.write(self.laseroff + '\n')
											Laser_ON = False
											
										elif matrice_BN[y][x] != matrice_BN[y][x+1] :
											file_gcode.write('G01 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											file_gcode.write(self.laseron + ' '+ ' S' + str(255 - matrice_BN[y][x+1]) +'\n')												

					
					else:
						for x in reversed(range(w)):
							if matrice_BN[y][x] != B :
								if Laser_ON == False :
									file_gcode.write('G00 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
									file_gcode.write(self.laseron + ' '+ ' S' + str(255 - matrice_BN[y][x]) +'\n')
									Laser_ON = True
									
								if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
									if x == 0 : #controllo fine riga ritorno
										file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
										file_gcode.write(self.laseroff + '\n')
										Laser_ON = False
										
									else: 
										if matrice_BN[y][x-1] == B :
											file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											file_gcode.write(self.laseroff + '\n')
											Laser_ON = False
											
										elif  matrice_BN[y][x] != matrice_BN[y][x-1] :
											file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
											file_gcode.write(self.laseron + ' '+ ' S' + str(255 - matrice_BN[y][x-1]) +'\n')

			
			
			#Configurazioni finali standard Gcode
			file_gcode.write('G00 X0 Y0; home\n')
			#HOMING
			if self.homing == 1:
				file_gcode.write('G28; home all axes\n')
			elif self.homing == 2:
				file_gcode.write('$H; home all axes\n')
			else:
				pass
			
			file_gcode.close() #Chiudo il file




######## 	######## 	######## 	######## 	######## 	######## 	######## 	######## 	######## 	


def _main():
	e=GcodeExport()
	
	exit()

if __name__=="__main__":
	_main()




