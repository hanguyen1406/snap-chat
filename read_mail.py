from imap_tools import MailBox, AND
import re

# Get date, subject and body len of all emails from INBOX folder
with MailBox('outlook.office365.com').login('stephanidreessens@hotmail.com', 'D53FbFDFv9Oh') as mailbox:
    codes = []
    for msg in mailbox.fetch():
        # print(msg.subject)
        if msg.subject.find("là mã TikTok của bạn") != -1:
            code = msg.subject.split(' ')[0]
            # print(code)
            codes.append(code)

    print(codes[-1])