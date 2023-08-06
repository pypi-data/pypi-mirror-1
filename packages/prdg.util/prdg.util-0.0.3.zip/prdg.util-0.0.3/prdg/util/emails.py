import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from StringIO import StringIO

# Code from here: http://snippets.dzone.com/posts/show/757
# By: manatlan - http://manatlan.online.fr/
def send_email(subject, message, smtp_server, to_addr, from_addr, files=()):
    """
    Advanced function to send an email to multiple emails, with attachments
    
    Params:
    
    - subject: Message subject
    - message: Message to send
    - smtp_server: Smtp server to user
    - to_addr: str or tuple/list with the emails to send the email
    - from_addr: who is sending the email
    - files: Files to send attached in the email (Note that this is not 
    required)
    
    Example:
    
    files = ['arq1.txt', 'arq2.txt']
    message = 'The requested files'
    to = ['email@email.com', 'ola@email.com']
    
    send_email('Files', message, 'localhost', to, 'email@email.com', files)
    """
    msg = MIMEMultipart()
    msg['From'] = from_addr
    
    if isinstance(to_addr, str):
        msg['To'] = to_addr
    else:
        msg['To'] = COMMASPACE.join(to_addr)
        
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
            % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(smtp_server)
    smtp.sendmail(from_addr, to_addr, msg.as_string())
    smtp.close()

class EmailIO(StringIO):
    """
    A file-like used to send emails. Just write to it and call close() to send 
    its contents.
    
    The email parameters can be defined on the constructor or modifying the
    corresponding instance attributes, before close() is called.
    """
    
    def __init__(self, subject=None, smtp_server=None, to_addr=None, 
        from_addr=None):
        """
        Constructor.
        
        Arguments:
        subject, smtp_server, to_addr, from_addr -- Email configurations.
        """
        StringIO.__init__(self)
        
        self.subject = subject 
        self.smtp_server = smtp_server
        self.to_addr = to_addr
        self.from_addr = from_addr
    
    def close(self):
        """
        Override: StringIO
        
        Close the file and send the email with the contents.
        """
        message = self.getvalue()
        
        send_email(
            subject=self.subject, 
            message=message, 
            smtp_server=self.smtp_server, 
            to_addr=self.to_addr, 
            from_addr=self.from_addr
        )