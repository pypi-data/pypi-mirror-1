import smtplib
import email.MIMEText

# todo: Rework email dispatching. We just need one good boundary object.

# NB Behaviour defaults to localhost and standard port (25).
# todo: Make SMTP usage configurable.

# Procedural code to send simple emails.
# todo: Convert procedural to object oriented code.
smtp = smtplib.SMTP()
COMMASPACE = ', '

def send(from_address, to_addresses, subject, body):
    emailMessage = email.MIMEText.MIMEText(body)
    emailMessage['Subject'] = subject
    emailMessage['From'] = from_address
    emailMessage['To'] = COMMASPACE.join(to_addresses)
    # todo: Add try/except around this external system call.
    smtp.connect()
    smtp.sendmail(from_address, to_addresses, emailMessage.as_string())
    smtp.close()
