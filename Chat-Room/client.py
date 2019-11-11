#----------Christopher Foeller-----Lab 3-----5/1/19----------#
# Description: 	This is a simple chat room using a server and client
#				made using socket. It supports login/logout, making a
#				new account, and sending messages to all users in the
#				chat room. You can also look up all of the commands by
#				typing help and exit the client by typing exit
#
# File: This is the file the the user will run to connect to the chat room

import socket
import select
import errno
import sys
import time

#-------------------------Establish Variables-------------------------#
HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 14745


#------------------------------Functions------------------------------#
#-----Connect to Server-----#
def startup():
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((IP, PORT))
	client_socket.setblocking(False)
	return client_socket

#-----Handle User Input-----#
def runcommands(splitmsg, login, inputmsg):
	#-----EXIT-----#
	if splitmsg[0] == "exit":
		print("Bye!")
		sys.exit()
	#-----HELP-----#
	elif splitmsg[0] == "help":
		print("LIST OF COMMANDS:")
		print("\"login [username] [password]\" - Login to the server")
		print("\"newuser [username] [password]\" - Make an account")
		print("\"send [username] [message goes here]\" - Send a message to a certain user")
		print("\"send all [message goes here]\" - Send a message to all users")
		print("\"send [message goes here]\" - Send a message to all users")
		print("\"logout\" - Logout of the server")
		print("\"exit\" - Close client")

	elif(login):
		#-----SEND-----#
		if splitmsg[0] == "send":
			if len(splitmsg) < 2:
				return login
			message = splitmsg[1].encode("utf-8")
			message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
			client_socket.send(message_header + message)
		#-----WHO-----#
		elif splitmsg[0] == "who":
			message = "SERVER_COMMAND_WH0".encode("utf-8")
			message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
			client_socket.send(message_header + message)
		#-----LOGOUT-----#
		elif splitmsg[0] == "logout":
			print("You have logout.")
			return False
		#-----Inform User about double login attempt-----#
		elif(splitmsg[0] == "login" or splitmsg[0] == "newuser"):
			print("You are already login.")
		#-----Invalid Commannd-----#
		else:
			print("Invalid command. Type \"help\" for list of commands")
	else:
		#-----LOGIN-----#
		if splitmsg[0] == "login":
			if len(splitmsg) < 2:
				print("Try again entering \"login [username] [password]\".")
				return False
			username = inputmsg.encode("utf-8")
			username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
			client_socket.send(username_header + username)
			time.sleep(0.2)
			a_header = client_socket.recv(HEADER_LENGTH)
			a_length = int(a_header.decode("utf-8").strip())
			a = client_socket.recv(a_length).decode("utf-8")
			if(a == "T"):
				print("Login Successful")
				return True
			else:
				print("Username or Password is incorrect")
				return False
		#-----NEWUSER-----#
		elif splitmsg[0] == "newuser":
			if len(splitmsg) < 2:
				print("Try again entering \"newuser [username] [password]\".")
				return False
			username = inputmsg.encode("utf-8")
			username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
			client_socket.send(username_header + username)
			time.sleep(0.2)
			a_header = client_socket.recv(HEADER_LENGTH)
			a_length = int(a_header.decode("utf-8").strip())
			a = client_socket.recv(a_length).decode("utf-8")
			if(a == "T"):
				print("Account Created!")
				return True
			elif(a == "E"):
				print("Username is already taken.")
				return False
			elif(a == "N"):
				print("Sorry, please enter a password between 4 and 8 characters.")
			else:
				print("That didn't work. Please try again")
				return False



		else:
			print("You need to login first. You can do that by typing \"login [username] [password]\".")
			print("To make an account, type \"newuser [username] [password]\"")

	return login


def runchatroom():
	login = False
	keepalive = True
	while keepalive:
		inputmsg = input(">")

		if inputmsg:
			splitmsg = inputmsg.split(" ", 1)
			login = runcommands(splitmsg, login, inputmsg)
			if login == False:
				keepalive = False

		try:
			while True:
				time.sleep(0.1)
				outputmsg_header = client_socket.recv(HEADER_LENGTH)
				if not len(outputmsg_header):
					print("Connection closed by server")
					sys.exit()

				outputmsg_length = int(outputmsg_header.decode("utf-8").strip())
				outputmsg = client_socket.recv(outputmsg_length).decode("utf-8")
				print(outputmsg)

		except IOError as e:
			if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
				print('Error Reading From Server', str(e))
				sys.exit()
			continue

		except Exception as e:
			print('Panicpanicpanicpanicpanicpanic', str(e))
			sys.exit()


while True:
	client_socket = startup()
	runchatroom()
	client_socket.shutdown(socket.SHUT_RDWR)
	client_socket.close()
	input("Type any key to start a new session!")