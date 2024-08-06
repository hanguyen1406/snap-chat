from imap_tools import MailBox, AND
import re, time

mails = open("./data/100out.txt", "r").readlines()

# for mail in mails:
#     un = mail.split("|")[0]
#     pw = mail.split("|")[1]
#     print(un, pw)
try:
    # Get date, subject and body len of all emails from INBOX folder
    with MailBox('outlook.office365.com').login('haylatoinhikhb15a@outlook.com.vn','nhidung01@') as mailbox:
        code = None
        for msg in mailbox.fetch():
            print(msg.subject)
            if msg.subject == 'Snapchat Login Verification Code':
                data = msg.html.split('\n')
                code = data[31].strip()
        
        print(code)
        mailbox.logout()
except Exception as e:
    print(e)
# time.sleep(5)