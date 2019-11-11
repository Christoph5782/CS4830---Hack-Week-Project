#----------Christopher Foeller-----Lab 3-----5/1/19----------#
# Description: 	This is a simple chat room using a server and client
#				made using socket. It supports login/logout, making a
#				new account, and sending messages to all users in the
#				chat room. You can also look up all of the commands by
#				typing help and exit the client by typing exit
#
# File: This is the code that runs the Echo Server the clients connect to

import socket
import select
import errno
import sys
import time

#-------------------------Establish Variables-------------------------#
HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 14745
FILE = "users.txt"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

socket_list = [server_socket]
clients = {}
users = {}

#--------------------------Get User From File--------------------------#
def getusers():
	f = open(FILE, "r")
	rawinput = f.read()
	splitinput = rawinput.split(" | ")
	for x in splitinput:
		y = x.split(" ")
		if len(y) < 2:
			print("May want to check the users.txt")
			print("Possible issue here")
			continue
		else:
			users[y[0]] = y[1]

	f.close()
	return





#----------------------------Client Commands----------------------------#
def login(inputinfo):
	teal = inputinfo.decode("utf-8")
	splitmsg = teal.split(" ")
	if len(splitmsg) < 2:
		return False
	if splitmsg[0] in users:
		if users[splitmsg[0]] == splitmsg[1]:
			return True
	return False


def newuser(inputinfo):
	teal = inputinfo.decode("utf-8")
	splitmsg = teal.split(" ")
	if splitmsg[0] in users:
		return "E"#User Exists
	elif len(splitmsg) < 2:
		return "N"#Invalid Password
	elif ((len(splitmsg[1]) < 4) or (len(splitmsg[1]) > 8)):
		return "N"#Invalid Password
	else:
		users[splitmsg[0]] = splitmsg[1]
		f = open(FILE, "a")
		f.write(" | " + splitmsg[0] + " " + splitmsg[1])
		f.close()
		return "T"#Success!


def receivemsg(client_socket):
	try:

		message_header = client_socket.recv(HEADER_LENGTH)

		if not len(message_header):
			return False

		message_length = int(message_header.decode("utf-8").strip())
		return {"header": message_header, "data": client_socket.recv(message_length)}


	except:
		return False

#-------------------------------Main Code-------------------------------#
getusers()#Fill our Dict with all our users in the file
while True:

	read_sockets, _, exception_sockets = select.select(socket_list, [], socket_list)
	for notified_socket in read_sockets: 
		#-----New Client Connection-----#
		if notified_socket == server_socket:
			client_socket, client_address = server_socket.accept()

			user = receivemsg(client_socket)
			cont_header = f"{len('T'):<{HEADER_LENGTH}}".encode('utf-8')
			if user is False:
				continue

			maxine = user['data'].decode("utf-8")
			splitmsg = maxine.split(" ", 1)
			if len(splitmsg) < 2:
				client_socket.send(cont_header + "F".encode('utf-8'))
				continue
			user['data'] = splitmsg[1].encode("utf-8")
			
			#-----Login-----#
			if(splitmsg[0] == "login"):
				if not login(user['data']):
					client_socket.send(cont_header + "F".encode('utf-8'))
					continue
			
			#-----Make a New Account-----#
			elif(splitmsg[0] == "newuser"):
				cont = newuser(user['data'])
				if not (cont == "T"):
					client_socket.send(cont_header + cont.encode('utf-8'))
					continue
			else:#A number of things could be wrong on the client side if this is tripped
				print("Panicpanicpanicpanicpanicpanic")

			
			#-----Store Our New Client Connection-----#
			maxine = user['data'].decode("utf-8")
			splitmsg = maxine.split(" ")
			user['data'] = splitmsg[0].encode("utf-8")
			client_socket.send(cont_header + "T".encode('utf-8'))
			socket_list.append(client_socket)
			clients[client_socket] = user
			print(f"{user['data'].decode('utf-8')} has joined the chat!")
			outputmsg = f"{user['data'].decode('utf-8')} has joined the chat!"
			outputmsg_header = f"{len(outputmsg):<{HEADER_LENGTH}}".encode("utf-8")
			client_socket.send(outputmsg_header + outputmsg.encode('utf-8'))
			# for client_socket in clients:#Notify Everyone!
			# 	try:
			# 		client_socket.send(outputmsg_header + outputmsg.encode('utf-8'))
			# 	except IOError as e:
			# 		continue
			# 	except Exception as e:
			# 		continue

		
		#-----Send New Messages To All Users-----#
		else:
			message = receivemsg(notified_socket)

			#-----A Client Left-----#
			if message is False:
				print(f"{clients[notified_socket]['data'].decode('utf-8')} has left the chat.")
				outputmsg = f"{clients[notified_socket]['data'].decode('utf-8')} has left the chat."
				outputmsg_header = f"{len(outputmsg):<{HEADER_LENGTH}}".encode("utf-8")
				for client_socket in clients:#Notify Everyone
					try:
						client_socket.send(outputmsg_header + outputmsg.encode('utf-8'))
					except IOError as e:
						#if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
							#print('A user force quit', str(e))
						continue
					except Exception as e:
						continue

				socket_list.remove(notified_socket)
				del clients[notified_socket]
				continue

			user = clients[notified_socket]
			#-----Handle Special Cases-----#
			msgtext = message['data'].decode('utf-8')
			specialcase = msgtext.split(" ", 1)
			outputmsg = ""
			#---WHO---#
			if(specialcase[0] == "SERVER_COMMAND_WH0"):
				outputmsg = f"Users in the chat are:"
				for client_socket in clients:
					fulluser = clients[client_socket]
					username = fulluser['data'].decode('utf-8')
					outputmsg = f"{outputmsg} {username}" 
				outputmsg_header = f"{len(outputmsg):<{HEADER_LENGTH}}".encode("utf-8")
				notified_socket.send(outputmsg_header + outputmsg.encode('utf-8'))
			#---SEND ALL---#
			elif(specialcase[0] == "all"):
				message['data'] = specialcase[1]
				print(f"{user['data'].decode('utf-8')} > All: {message['data']}")
				outputmsg = f"{user['data'].decode('utf-8')} > All: {message['data']}"
				outputmsg_header = f"{len(outputmsg):<{HEADER_LENGTH}}".encode("utf-8")
				for client_socket in clients:#Notify Everyone!
					client_socket.send(outputmsg_header + outputmsg.encode('utf-8'))
					# try:
					# 	client_socket.send(outputmsg_header + outputmsg.encode('utf-8'))
					# except IOError as e:
					# 	continue
					# except Exception as e:
					# 	continuesocket.send(outputmsg_header + outputmsg.encode('utf-8'))
			#---SEND TO USER---#
			else:
				contcheck = True
				for client_socket in clients:
					fulluser = clients[client_socket]
					username = fulluser['data'].decode('utf-8')
					if(specialcase[0] == username):
						message['data'] = specialcase[1]
						print(f"{user['data'].decode('utf-8')} > {username}: {message['data']}")
						outputmsg = f"{user['data'].decode('utf-8')} > {username}: {message['data']}"
						outputmsg_header = f"{len(outputmsg):<{HEADER_LENGTH}}".encode("utf-8")
						client_socket.send(outputmsg_header + outputmsg.encode('utf-8'))
						contcheck = False
						continue
			#-----DEFAULT SEND CASE-----#
				if(contcheck):
					print(f"{user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
					outputmsg = f"{user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}"
					outputmsg_header = f"{len(outputmsg):<{HEADER_LENGTH}}".encode("utf-8")
					for client_socket in clients:#Notify Everyone!
						client_socket.send(outputmsg_header + outputmsg.encode('utf-8'))
						# try:
						# 	client_socket.send(outputmsg_header + outputmsg.encode('utf-8'))
						# except IOError as e:
						# 	continue
						# except Exception as e:
						# 	continue
	#-----Delete Users Who Left-----#
	for notified_socket in exception_sockets:
		socket_list.remove(notified_socket)
		del clients[notified_socket]