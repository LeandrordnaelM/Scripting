#! /usr/bin/python3


SMTPserver = '...'
sender =     '...'
destination = ['...']

USERNAME = "..."
PASSWORD = "..."

# typical values for text_subtype are plain, html, xml
text_subtype = 'plain'

import sys
import os
import re
import socket
import time
from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
import platform
# old version
# from email.MIMEText import MIMEText
from email.mime.text import MIMEText
hostname=socket.gethostname()

subject="Sent from " + hostname
date= time.strftime("%H:%M:%S")
sistema=os.getlogin()

content=  sistema +" "+  date


try:
    msg = MIMEText(content, text_subtype)
    msg['Subject']=       subject
    msg['From']   = sender # some SMTP servers will do this automatically, not all

    conn = SMTP(SMTPserver)
    conn.set_debuglevel(False)
    conn.login(USERNAME, PASSWORD)
    try:
        conn.sendmail(sender, destination, msg.as_string())
    finally:
        conn.quit()

except:
    sys.exit( "mail failed; %s" % "CUSTOM_ERROR" ) # give an error message

