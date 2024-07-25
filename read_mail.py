from imap_tools import MailBox, AND
import re

# Get date, subject and body len of all emails from INBOX folder
with MailBox('outlook.office365.com').login('peytonktmzu91@outlook.com.vn', 'i^QJYCI^Hq') as mailbox:
    code = None
    for msg in mailbox.fetch():
        print(msg.subject)
        if msg.subject == 'Snapchat Login Verification Code':
            data = msg.html.split('\n')
            code = data[31].strip()
            

    print(code)

