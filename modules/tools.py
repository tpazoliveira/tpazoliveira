import sys
import logging
import os
import csv
from datetime import datetime
import re
from netaddr import IPNetwork, IPAddress
import pandas as pd
import smtplib
from email.message import EmailMessage


path_file_name = os.path.join("../internal_protect", 'internal_protect.log')
logging.basicConfig(level=logging.DEBUG, filename=path_file_name, format=' %(asctime)s - %(message)s')

def delete_file(filename):
    try:
        path_file_name = os.path.join("../internal_protect/utils", filename)
        if os.path.exists(path_file_name):
            os.remove(path_file_name)
            logging.debug('[delete_file] Arquivo ' + str(filename) + ' excluído com sucesso.' )
    except Exception as error:
        logging.debug('[delete_file] Não foi possível apagar o arquivo '+ str(filename)+ '.' )

def set_email(email_subject, email_content):
    try:
        mailserver = smtplib.SMTP('smtp.office365.com',587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.login('cgr.automacao@vogeltelecom.com', 'Aut@1025')
        msg = EmailMessage()
        msg['Subject'] = email_subject
        msg['From'] = 'cgr.automacao@vogeltelecom.com'
        msg['To'] = 'nocvogel@vogeltelecom.com'
        msg['Cc'] = 'tarcisio.oliveira@vogeltelecom.com'
        msg.set_content(email_content)
        mailserver.send_message (msg)
        mailserver.quit()
    except smtplib.SMTPException as error:
    #except Exception as error:
        logging.debug('[set_email] Houve uma erro no envio de email. Erro: ' + str(error))