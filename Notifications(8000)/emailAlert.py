import smtplib
from email.message import EmailMessage
import pywhatkit as kit
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
subject = "iCMS Alert"

def email_alert(subject, body , to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "saseetharanvishnuka25@gmail.com"
    msg['from']= user
    password = "dbieqijfedrzerhx"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)

    server.quit()
    print("Eamilsend to:", to)

# phone_number = "+94762279871"
# body = "iCSMS alert"
# def whatsapp_alert(body):
#     kit.sendwhatmsg_instantly(phone_number, body)
#     time.sleep(10)

#     driver.quit()

# firefox_options = Options()
# firefox_options.headless = True

# # Initialize the Firefox web driver
# driver = webdriver.Firefox(options=firefox_options)
# whatsapp_alert(body)