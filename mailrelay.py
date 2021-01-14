#!/usr/bin/env python3
# quick and dirty test script for smtp relay
# 250 2.0.0 0BHI16hQ021841-0BHI16hR021841 Message accepted for delivery
# fortinet session 
#
# Done
# ---- 
# add cc, bcc and lists
# add colors
# add list of receivers
# 
# Todo
# ----
# add response check
# add custom attachment

import os
import sys
import time
import base64
import socket
import random
import argparse

__tool_name__ = 'mailrelay.py'
__tool_version__ = '0.3.1'
__tool_author__ = 'dash'
__tool_desc__ = 'not so quick but dirty\'n\'dirty tool for smtp relay checks, nothing fancy here.'

globTimeout=0

#https://stackoverflow.com/questions/2330245/python-change-text-color-in-shell
def liteUp(string, status, bold):
    attr = []
    if status == 'green':
        attr.append('32')
    elif status == 'red':
        attr.append('31')
    elif status == 'orange':
        attr.append('33')
    elif status == 'purple':
        attr.append('35')
    elif status == 'cyan':
        attr.append('36')
    elif status == 'yellow':
        attr.append('93')
    elif status == 'lightblue':
        attr.append('94')
    elif status == 'pink':
        attr.append('95')
    else:
        # red
        attr.append('90')
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

def buildSocket(host,port):
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	try:
		sock.connect((host,int(port)))

	except socket.gaierror as e:
		errMsg = '{0}:{1}: {2}'.format(host,port,e)
		print(liteUp(errMsg, 'red', 0))
		sys.exit()

	return sock
	
def parseVariable(var):
	if var.find(':')>0:
		out = var.split(':')
		return out[0],out[1]
	else:
		print('Sorry, unexpected variable.')
		return False, False

def parseResponse(respData):
	# response types
	# 250 OK
	# 550 Error
	# 503 Need RCPT (recipient) 
	if respData[:3]==(b'250'):
		#print('yay')
		return True
	else:
		return False

def recvSmtpData(sock):
	# basic recv function should do the trick for now
	try:
		data = sock.recv(1024)
	except socket.timeout as e:
		errMsg = e
		print(liteUp(errMsg, 'red', 0))
		sys.exit()
	except BrokenPipeError as e:
		errMsg = e
		print(liteUp(errMsg, 'red', 0))
		sys.exit()

	return data
	
def sendSmtpData(sock, data):

	# lets send the data over the wire
	try:
		sock.send(data)
	except socket.timeout as e:
#		errMsg = '{0}:{1}: {2}'.format(host,port,e)
		errMsg = e
		print(liteUp(errMsg, 'red', 0))
		sys.exit()
	except BrokenPipeError as e:
#		errMsg = '{0}:{1}: {2}'.format(host,port,e)
		errMsg = e
		print(liteUp(errMsg, 'red', 0))
		sys.exit()

	# add artifical timeout here 
	time.sleep(globTimeout)


	return True, data

def sendEhlo(sock):
	hihello = ['localhost','127.0.0.2','10.10.10.45']
	ehloMe = random.choice(hihello)
	ehloNow = ('ehlo {0}\r\n'.format(ehloMe)).encode()
	sendSmtpData(sock, ehloNow)
	print(liteUp(ehloNow.decode().rstrip('\n'), 'pink', 0))
	recvData = recvSmtpData(sock)
	print(liteUp(recvData.decode().rstrip('\n'), 'orange', 0))
	result = parseResponse(recvData)
	return result

def sendMailFrom(sock, senderMail):
	# prepare smtp mail from
	mf = 'MAIL FROM: <{0}>\r\n'.format(senderMail)
	mf = mf.encode()
	sendSmtpData(sock, mf)
	print(liteUp(mf.decode().rstrip('\n'), 'pink', 0))
	recvData = recvSmtpData(sock)
	print(liteUp(recvData.decode().rstrip('\n'), 'orange', 0))
	result = parseResponse(recvData)

def sendMailTo(sock, targetMail):
	# prepare smtp rcpt to
	rt = 'RCPT TO: <{0}>\r\n'.format(targetMail)
#	rt = 'RCPT TO: <{0}>,<{0}>\r\n'.format(targetMail)
	rt = rt.encode()
	sendSmtpData(sock, rt)
	print(liteUp(rt.decode().rstrip('\n'), 'pink', 0))
	recvData = recvSmtpData(sock)
	print(liteUp(recvData.decode().rstrip('\n'), 'orange', 0))
	result = parseResponse(recvData)

def sendCustom(sock, cmd, recvOn):
	
	# prepare smtp rcpt to
	cmd = cmd.encode()
	sendSmtpData(sock, cmd)
	print(liteUp(cmd.decode().rstrip('\n'), 'pink', 0))

	if recvOn:
		recvData = recvSmtpData(sock)
		print(liteUp(recvData.decode().rstrip('\n'), 'orange', 0))
		result = parseResponse(recvData)
	
	return True

def openFile(targetList):
	fr = open(targetList, 'r')
	buf = fr.readlines()
	return buf

def openFileRead(filename):
	fr = open(filename, 'rb')
	buf = fr.read()
	return buf

def run(args):

	targetMail = args.targetMail
	targetCcMail = args.targetCcMail
	targetBccMail = args.targetBccMail

	targetList = args.targetList
	targetCcList = args.targetCcList
	targetBccList = args.targetBccList

	senderMail = args.senderMail
	subject = args.subject
	body = args.body

	attachment = args.attachment
	attachmentName = args.attachmentName

	mailHost = args.mtaAddr
	mailHost, mailHostPort = parseVariable(mailHost)
	conn = '[+] Connected: {0}:{1}'.format(mailHost, mailHostPort)

	sock = buildSocket(mailHost,mailHostPort)
	print(liteUp(conn, 'ppppink', 0))

	# ehlo at system
	sendEhlo(sock)

	# send mail from 
	sendMailFrom(sock, senderMail)

	if targetList:
		mails = openFile(targetList)
		for targetMail in mails:
			targetMail = targetMail.rstrip('\r')
			targetMail = targetMail.rstrip('\n')
			# send Mail To
			sendMailTo(sock, targetMail)
			

	else:
		# send Mail To
		sendMailTo(sock, targetMail)



	# initiate DATA block for mailcontent
	sendCustom(sock,'DATA\r\n',True)

	# send subject 
	sub = 'SUBJECT: {0}\r\n'.format(subject)
	sendCustom(sock,sub,False)

	# cc list or not
	if targetCcList:
		mails = openFile(targetCcList)
		for targetCcMail in mails:
			targetCcMail = targetCcMail.rstrip('\r')
			targetCcMail = targetCcMail.rstrip('\n')
			# send CC Mail
			custData = 'CC: <{0}>\r\n'.format(targetCcMail)
			sendCustom(sock,custData,False)
	else:
		# initiate DATA block for mailcontent
		custData = 'CC: <{0}>\r\n'.format(targetCcMail)
		sendCustom(sock,custData,False)

	# bcc list or not
	if targetBccList:
		mails = openFile(targetBccList)
		for targetBccMail in mails:
			targetBccMail = targetBccMail.rstrip('\r')
			targetBccMail = targetBccMail.rstrip('\n')
			# send CC Mail
			custData = 'CC: <{0}>\r\n'.format(targetBccMail)
			sendCustom(sock,custData,False)

	else:
		# initiate DATA block for mailcontent
		custData = 'BCC: <{0}>\r\n'.format(targetBccMail)
		sendCustom(sock,custData,False)

	# so you want to send an attachment??
	if not attachmentName:
		attachmentName = attachment

	if attachment:
		buf=openFileRead(attachment)
		attachmentB64 = base64.b64encode(buf)
		# i should patent that crap
		rndBoundary = int((str(random.random()+1)).replace('.',''))
		bndry = '==============={0}=='.format(rndBoundary)
		ct = 'Content-Type: multipart/mixed; boundary="{0}"'.format(bndry)
		ct2 = 'MIME-Version: 1.0'
		sendCustom(sock,ct,False)
		sendCustom(sock,ct2,False)

		ctbody = '--{0}\r\nContent-Type: text/plain; charset="us-ascii"\r\nMIME-Version: 1.0\r\nContent-Transfer-Encoding: 7bit\r\n\r\n{1}\r\n'.format(bndry,body)
		sendCustom(sock,ctbody,False)

		ctattach = '--{0}\r\nContent-Type: application/octet-stream\r\nMIME-Version: 1.0\r\nContent-Transfer-Encoding: base64\r\nContent-Disposition: attachment; filename={1}\r\n\r\n{2}\r\n\r\n--{0}\r\n'.format(bndry,attachmentName, attachmentB64)
		sendCustom(sock,ctattach,False)
	else:
		body = '{0}\r\n'.format(body)
		sendCustom(sock,body,False)

	done = '.\r\n'
	sendCustom(sock,done,True)

	quit = 'quit\r\n'
	sendCustom(sock,quit,True)

	conn = '[+] Finished'
	print(liteUp(conn, 'ppppink', 0))



def main():

    parser_desc = '{0} {1} by {2}'.format(__tool_name__, __tool_version__,__tool_author__)
    prog_desc = __tool_desc__
    parser = argparse.ArgumentParser(prog = prog_desc, description=parser_desc)
    parser.add_argument("-z","--socket-timeout",action="store",required=False,type=int,help='time to wait for socket (defaut:5)',dest='sockTimeout',default=5)
    parser.add_argument("-Z","--manual-timeout",action="store",required=False,type=int,help='time to wait for socket (defat:5)',dest='sockTimeout',default=5)
    parser.add_argument("-t","--target-email",action="store",required=False,help='single e-mail address the mails to sent to',dest='targetMail')
    parser.add_argument("-cc","--target-cc-email",action="store",required=False,help='single CC e-mail address the mails to sent to',dest='targetCcMail', default=False)
    parser.add_argument("-bcc","--target-bcc-email",action="store",required=False,help='single BCC e-mail address the mails to sent to',dest='targetBccMail', default=False)
    parser.add_argument("-CC","--target-cc-list",action="store",required=False,help='single CC e-mail address the mails to sent to',dest='targetCcList', default=False)
    parser.add_argument("-BCC","--target-bcc-list",action="store",required=False,help='single BCC e-mail address the mails to sent to',dest='targetBccList', default=False)
    parser.add_argument("-T","--target-list",action="store",required=False,help='list with email addresses mail sent to',dest='targetList',default= False)
    parser.add_argument("-e","--sender-email",action="store",required=False,help='single sender e-mail addr, FORMAT:<email>password>',dest='senderMail')
    parser.add_argument("-s","--email-subject",action="store",required=False,help='the subject',dest='subject',default='Imptant Notice about your paypal account')
    parser.add_argument("-b","--email-body",action="store",required=False,help='the body, e.g. \'hi there, this is a massivtest. please ignore.\'',dest='body',default='Sorry, you have been hacked.')
    parser.add_argument("-a","--attachment",action="store",required=False,help='send attachment',dest='attachment',default=False)
    parser.add_argument("-A","--attachment-name",action="store",required=False,help='send attachment',dest='attachmentName',default="ls.file")
    parser.add_argument("-m","--mta",action="store",required=False,help='the mta, FORMAT:<smtp>:<port>, e.g. smtp.provider.m:25',dest='mtaAddr',default='smtp.gmail.com:25')

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
        main()


