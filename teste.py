import smtplib
import mariadb
import sys
import mysql.connector
import pymysql.cursors
from email.message import EmailMessage


# Connect to the database
'''connection = pymysql.connect(host='10.0.52.47', user='vogel', password='vogel@123', database='inventario_vogel', cursorclass=pymysql.cursors.DictCursor)
with connection:
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * FROM inventario"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
exit()


# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="vogel",
        password="vogel@123",
        host="10.0.52.47",
        port=3306,
        database="inventario_vogel"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()
cur.execute("SELECT ip FROM inventario")
for ip in cur:
    print(ip)

exit()'''

def set_email(email_subject, email_content):
    try:
        mailserver = smtplib.SMTP('smtp.office365.com',587)
        mailserver.ehlo()
        mailserver.starttls()
        #mailserver.login('anti-ddos@vogeltelecom.com', 'V0g3lt3l3c0m')
        mailserver.login('anti-ddos', 'V0g3lt3l3c0m')
        msg = EmailMessage()
        msg['Subject'] = email_subject
        msg['From'] = 'anti-ddos@vogeltelecom.com'
        msg['To'] = 'tarcisio.oliveira@vogeltelecom.com'
        #msg['Cc'] = 'tarcisio.oliveira@vogeltelecom.com'
        msg.set_content(email_content)
        mailserver.send_message (msg)
        mailserver.quit()
    except smtplib.SMTPException as error:
        #logging.debug('[set_email] Houve uma erro no envio de email. Erro: ' + str(error))
        print('Error: ' + str(error))

set_email('SMTP Server Test', 'SMTP Server Test')


def set_email(email_subject, email_content):
    try:
        mailserver = smtplib.SMTP('smtp.office365.com',587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.login('anti-ddos@vogeltelecom.com', '*********')
        msg = EmailMessage()
        msg['Subject'] = email_subject
        msg['From'] = 'anti-ddos@vogeltelecom.com'
        msg['To'] = 'tarcisio.oliveira@vogeltelecom.com'
        msg.set_content(email_content)
        mailserver.send_message (msg)
        mailserver.quit()
    except smtplib.SMTPException as error:
        print('Error: ' + str(error))

set_email('SMTP Server Test', 'SMTP Server Test')

