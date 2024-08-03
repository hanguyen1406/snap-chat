from imap_tools import MailBox, AND
import re

# Get date, subject and body len of all emails from INBOX folder
with MailBox('outlook.office365.com').login('juliaveslb95@outlook.com.vn', 'o6ya4QrmHq') as mailbox:
    code = None
    for msg in mailbox.fetch():
        if msg.subject == 'Snapchat Login Verification Code':
            data = msg.html.split('\n')
            code = data[31].strip()
    
    print(code)
    mailbox.logout()
