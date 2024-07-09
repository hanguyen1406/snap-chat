from imap_tools import MailBox, AND
import re

# Get date, subject and body len of all emails from INBOX folder
with MailBox('outlook.office365.com').login('jackiarzo80@outlook.com.vn', 'fsNzfavHHq') as mailbox:
    for msg in mailbox.fetch():
        if msg.subject == 'Snapchat Login Verification Code':
            data = msg.html.split('\n')
            code = data[31].strip()
            print(code)