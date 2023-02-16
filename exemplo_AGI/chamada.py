#!/usr/bin/env python
import sys
from asterisk.agi import *
import mysql.connector

class Projeto_agi(AGI):
	def __init__(self):
		self.agi = AGI()
		self.container = ""
		self.container_password = ""
		self.agi.verbose("python agi started")
		self.agi.stream_file("menu_boas_vindas")	

	def sql_call_procedure(self,container_number,container_password,operation):
		"""	 	funciotions
		0 - autentication / 1 - check in  / 2- check out , 3- absence """
		# bind mysql date base 
		self.agi.verbose("try conect to DB")
		# DB TESTE NÂO FUNCIONA MAIS
		mydb = mysql.connector.connect(
			host="192.168.102.100",
			user="asterisk",
			password="ifrnaula",
			database="SUAP",
			collation="utf8_general_ci")
		# create a cursor 
		mycursor = mydb.cursor()
		# call procedure
		self.agi.verbose("send number of container and password to make auth")
		mycursor.callproc("Chamada_AGI",[container_number,container_password,operation])
		for result in mycursor.stored_results():
			result_proc = result.fetchall()[0][0]
		self.agi.verbose("procedure return %s" %result_proc)
		return result_proc
	def autentication(self):
		# to get container number
		self.agi.stream_file("autenticacaoNContainer")	
		for digits in range(2):
			new_num = self.agi.wait_for_digit(-1)
			self.container = self.container + str(new_num)
		self.agi.verbose("container number is %s" % self.container)
		# to get password
		self.agi.stream_file("autenticacaoNsenha")
		for digits in range(6):
			new_num = self.agi.wait_for_digit(-1)
			self.container_password = str(self.container_password) + str(new_num)
		self.agi.verbose("container password is %s" % self.container_password)
		#to say container number and password to client
		self.agi.stream_file("numero_de_seu_container")
		self.agi.say_number(self.container)
		self.agi.stream_file("a_senha_digitada_foi")
		self.agi.say_digits(self.container_password)
		autentication_is = self.sql_call_procedure(self.container,self.container_password,0)
		self.agi.verbose("autenticaca %s" %autentication_is)

		return True if autentication_is == 0 else False 
	def checkIn(self):
		num_procedure_return = self.sql_call_procedure(self.container,self.container_password,1)
		self.agi.verbose("make check-in") if num_procedure_return == 0 else self.agi.verbose("error in make check-in")
		self.agi.stream_file("presenca_marcada_com_sucesso") if num_procedure_return == 0 else self.agi.stream_file("entrada_falhas")
	def checkOut(self):
		num_procedure_return = self.sql_call_procedure(self.container,self.container_password,2)
		self.agi.verbose("make check-out") if num_procedure_return == 0 else self.agi.verbose("error in make check-out")
		self.agi.stream_file("saida_marcada_com_sucesso") if num_procedure_return == 0 else self.agi.stream_file("saida_falhas")
	def absence(self):
		absenc  = str(self.sql_call_procedure(self.container,self.container_password,3))
		self.agi.verbose("speak the absense")
		if absenc.isdigit():
			self.agi.stream_file("Voce_possui")
			self.agi.say_number(int(absenc))
			self.agi.stream_file("Faltas")
		else:
			self.agi.verbose("error in the query, return value %s" % absenc)
			self.agi.stream_file("faltas_falhas")

	def end_call(self):
		self.agi.stream_file("obrigado_por_ligar_ate_logo")
		self.agi.verbose("end of call")
		agi.hungup()
		sys.exit()
	def routine(self):
		stats = self.autentication()
		if stats == True:
			self.agi.verbose("sucess return 0")
			self.agi.stream_file("autenticacao_com_sucesso")
		elif stats == False:
			self.agi.verbose("faill to autentication -1")
			self.agi.stream_file("erro_de_autenticacao")
			self.end_call()
			
		while True:
			self.agi.verbose("speak selec menu")
			self.agi.stream_file("menu_selecao_1_2_3")
			option = self.agi.wait_for_digit(-1)
			self.agi.verbose("selected option %s" %option)
			if option == "1":
				self.checkIn()
			elif option == "2":
				self.checkOut()
			elif option == "3":
				self.absence()
			elif option == "0":
				break		
		self.end_call()
							

# para executar 
agi = Projeto_agi()
agi.routine()

		
