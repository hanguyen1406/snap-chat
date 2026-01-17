import imaplib, re, os, sys, poplib, email
from os import system
from email.header import decode_header
from getpass import getpass
class HotMail:
    def __init__(self, email_address, password, protocol="imap"):
        self.email = email_address
        self.password = password
        self.protocol = protocol.lower()
        
        if self.protocol == "imap":
            self.server = "outlook.office365.com"
            self.port = 993
            if "gmail.com" in self.email:
                self.server = "imap.gmail.com"
            self.mail = imaplib.IMAP4_SSL(self.server, self.port)
            self.mail.login(self.email, self.password)
        elif self.protocol == "pop3":
            self.server = "outlook.office365.com"
            self.port = 995
            if "gmail.com" in self.email:
                self.server = "pop.gmail.com"
            self.mail = poplib.POP3_SSL(self.server, self.port)
            self.mail.user(self.email)
            self.mail.pass_(self.password)
        else:
            raise ValueError("Protocol must be either 'imap' or 'pop3'")

    def load_imap(self):
        self.mail.select("inbox")
        result, data = self.mail.search(None, "ALL")
        # print(data)   
        email_ids = data[0].split()[-6:][::-1]  # Get the last 5 emails
        for email_id in email_ids:
            result, msg_data = self.mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    # print("="*50)
            print("Subject:", subject)
            print("From:", msg.get("From"))
            if "Snapchat Login Verification" in subject:
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                else:
                   body = msg.get_payload(decode=True).decode()
                code = body.split('\n')[36].strip()
                print("Code:", code)
                return code
        return None        

    def load_pop3(self):
        email_count, total_size = self.mail.stat()
        print(f"Number of emails: {email_count}")
        print(f"Total size: {total_size} bytes")

        email_ids = range(max(1, email_count - 4), email_count + 1)
        for email_id in email_ids:
            raw_email = b"\n".join(self.mail.retr(email_id)[1])
            msg = email.message_from_bytes(raw_email)
            subject, encoding = decode_header(msg["subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            from_ = msg.get("from")
            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()
            print("Subject:", subject)
            print("From:", from_)
            print("=" * 50)

    def load(self):
        if self.protocol == "imap":
            self.load_imap()
        elif self.protocol == "pop3":
            self.load_pop3()
        else:
            raise ValueError("Protocol must be either 'imap' or 'pop3'")
        

if __name__ == "__main__":
    import os

   
    try:
        un = "nguyenbahiep707@gmail.com"
        pw = "nexm sbef syaq ahhn"
        # os.system("cls")
        email_address = un.strip()
        password = pw.strip()
        email_viewer = HotMail(email_address, password)
        code = email_viewer.load()
        print(code)
    except Exception as e:
        print('sai mật khẩu:', e)
        pass


