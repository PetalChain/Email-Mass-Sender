from shutil import copyfile
import smtplib
import ssl
import mimetypes

from time import sleep
from email.message import EmailMessage


def parse_receiver_addresses(file):
    """
    This function reads all email addresses from file into a list. Then it stores only the first num_of_addresses email addresses
    into a new list (gmail 100 emails/day limit) and returns it for use. It then deletes the n email addresses just
    used and overwrites the original file removing the emails just used leaving only unused email addresses.
    Also duplicates the original address file into a `.bak` file before modifying the original file.

    :param file: file name (string)
    :param num_of_addresses: number of email addresses you want to send to (int)
    :return: returns only the first num_of_addresses from original email address file
    """

    with open(file, 'r') as f:
        all_addresses = f.read().splitlines()       # read all email addresses into all address list

    return all_addresses

def parse_sender_addresses(file):
    with open(file, 'r') as f:
        all_addresses = f.read().splitlines()       # read all email addresses into all address list

    return all_addresses

def create_message(subject, sender, receiver, body, attachments=None):
    """
    Creates and email message with a subject, sender, receiver, and the body text.
    :param subject: a string for the email subject
    :param sender: a string for the email address sending the email
    :param receiver: a string for the email address receiving the email
    :param body: a string for the body text of the email
    :param attachments (default: None): a string or a list of strings with the filenames of the attachments
    :return: returns a built email message from the paramaters received
    """
    message = EmailMessage()

    message['Subject'] = subject
    message['From'] = sender
    message['To'] = receiver
    message.set_content(body)

    ## Add attachments (if any)
    if attachments:

        if isinstance(attachments, str):
            attachments = [attachments]
        
        for attachment in attachments:

            file_type, file_encoding = mimetypes.guess_type(attachment)
            if file_type is None or file_encoding is not None:
                file_type = 'application/octet-stream'
            
            file_maintype, file_subtype = file_type.split('/',1)
            with open(attachment, 'rb') as att:
                data = att.read()
                message.add_attachment(data, 
                    maintype=file_maintype,
                    subtype=file_subtype, 
                    filename=att.name)

    return message


def send_email(username, password, message):
    """
    Creates an smtp server, logs into your email provider, and sends email.
    :param username: a string of your email username
    :param password: a string of your email password
    :param message: a built email message created by the create_message function
    :return: sends an email
    """

    email_server = 	'smtp.gmail.com'
    port = 587

    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(email_server, port)

        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(username, password)

        server.send_message(message)

    except smtplib.SMTPException as exc:

        print('FROM:'+username+"("+password+"):Error sending email.")
        print(exc)

    finally:
        server.quit()

