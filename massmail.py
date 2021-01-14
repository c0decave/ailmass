#!/usr/bin/env python
# basic script by samlopezf
# tuned and combat ready by dash 
# in the year of the covid outbreak, december
#

import sys
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from IPython import embed
__tool_name__ = 'massmails.py'
__tool_version__ = '0.3'
__tool_author__ = 'dash'
__tool_fork__ = 'https://github.com/samlopezf/Python-Email/'
__tool_desc__ = 'simple tool to test mail servers for robustnes, it will send one email per account to the target email address'


def parseVariable(var):
	if var.find(':')>0:
		out = var.split(':')
		return out[0],out[1]
	
	else:
		print('Sorry, unexpected variable.')
		return False, False

def buildEmail(emailSender, emailTarget, emailSubject, emailBody, emailAttachment):
	msg = MIMEMultipart()
	msg['From'] = emailSender
	msg['To'] = emailTarget
	msg['Subject'] = emailSubject

	body = emailBody
	msg.attach(MIMEText(body,'plain'))


	# is there an attachment specified
	if emailAttachment:
		filename=emailAttachment
		attachment  =open(filename,'rb')

		part = MIMEBase('application','octet-stream')
		part.set_payload((attachment).read())
		encoders.encode_base64(part)
		part.add_header('Content-Disposition',"attachment; filename= "+filename)

		msg.attach(part)

	text = msg.as_string()
	return text

def openFile(filename):
	fr = open(filename,'rb')
	buf = fr.readlines()
	return buf

def run(args):
#    parser.add_argument("-T","--target-list",action="store",required=False,help='list of emails to send to',dest='targetList')
#    parser.add_argument("-E","--sender-list",action="store",required=False,help='sender email list, FORMAT:<email>:<password><CR><LF>',dest='senderList')

	emailSender = args.senderMail
	emailTarget = args.targetMail

	emailTargetList = args.targetList
	emailSenderList = args.senderList

	emailSubject = args.subject
	emailBody = args.body
	emailAttachment = args.attachment

	mtaAddr = args.mtaAddr

	# lets build up vars for mta
	emailMta, emailMtaPort = parseVariable(mtaAddr)
	print('{0}:{1}'.format(emailMta, emailMtaPort))

	if emailSenderList:
		senders = openFile(emailSenderList)
		for emailSender in senders:
			emailSender = emailSender.decode()
			emailSender = emailSender.rstrip('\r')
			emailSender = emailSender.rstrip('\n')
			#print(emailSender)
			emailSender, emailPassword = parseVariable(emailSender)
			print('{0}/{1}'.format(emailSender, emailPassword))

			# build up the mail 
			text = buildEmail(emailSender, emailTarget, emailSubject, emailBody, emailAttachment)
			print(text)

			# lets send the mail 
			server = smtplib.SMTP(emailMta,emailMtaPort)
			server.starttls()
			#embed()
			server.login(emailSender,emailPassword)


			server.sendmail(emailSender,emailTarget,text)
			server.quit()

	else:
		print('Single Mail Test')
		emailSender, emailPassword = parseVariable(emailSender)
		print('{0}/{1}'.format(emailSender, emailPassword))
		text = buildEmail(emailSender, emailTarget, emailSubject, emailBody, emailAttachment)

		server = smtplib.SMTP(emailMta,emailMtaPort)
		server.starttls()
		server.login(emailSender,emailPassword)


		server.sendmail(emailSender,emailTarget,text)
		server.quit()
	
	print('The end my friend')

def main():

    parser_desc = '{0} {1} by {2}'.format(__tool_name__, __tool_version__,__tool_author__)
    prog_desc = __tool_desc__
    parser = argparse.ArgumentParser(prog = prog_desc, description=parser_desc)
#    parser.add_argument("-z","--socket-timeout",action="store",required=False,type=int,help='time to wait for socket (default:5)',dest='sockTimeout',default=5)
    parser.add_argument("-t","--target-email",action="store",required=False,help='single e-mail address the mails to sent to',dest='targetMail')
    parser.add_argument("-T","--target-list",action="store",required=False,help='list of emails to send to',dest='targetList')
    parser.add_argument("-e","--sender-email",action="store",required=False,help='single sender e-mail addr, FORMAT:<email>:<password>',dest='senderMail')
    parser.add_argument("-E","--sender-list",action="store",required=False,help='sender email list, FORMAT:<email>:<password><CR><LF>',dest='senderList')
    parser.add_argument("-s","--email-subject",action="store",required=False,help='the subject',dest='subject',default='Important Notice about your paypal account')
    parser.add_argument("-b","--email-body",action="store",required=False,help='the body, e.g. \'hi there, this is a massive test. please ignore.\'',dest='body',default='Sorry, you have been hacked.')
    parser.add_argument("-a","--email-attachment",action="store",required=False,help='the attachment',dest='attachment',default=None)
    parser.add_argument("-M","--mta",action="store",required=False,help='the mta, FORMAT:<smtp>:<port>, e.g. smtp.provider.com:25',dest='mtaAddr',default='smtp.gmail.com:25')
	
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
        main()

