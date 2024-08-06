import poplib, email
from email.header import decode_header
class HotMail:
    def __init__(self, email_address, password):
        self.email = email_address
        self.password = password
        
        self.server = "outlook.office365.com"
        self.port = 995
        if "gmail.com" in self.email:
            self.server = "pop.gmail.com"
        self.mail = poplib.POP3_SSL(self.server, self.port)
        self.mail.user(self.email)
        self.mail.pass_(self.password)         

    def load_pop3(self):
        email_count, total_size = self.mail.stat()
        code = None
        email_ids = range(max(1, email_count - 4), email_count + 1)
        for email_id in email_ids:
            raw_email = b"\n".join(self.mail.retr(email_id)[1])
            msg = email.message_from_bytes(raw_email)
            subject, encoding = decode_header(msg["subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()
            if subject == "Snapchat Login Verification Code":
                # print("Subject:", subject)
                code = body.split('\n')[31].strip()
        return code    

    def load(self):
        return self.load_pop3()
        

if __name__ == "__main__":
    import os

    mails = open("./data/50out.txt", "r").readlines()

    for mail in mails:
        print(mail)
        try:
            un = mail.split("|")[0]
            pw = mail.split("|")[1]
            # os.system("cls")
            email_address = un.strip()
            password = pw.strip()
            email_viewer = HotMail(email_address, password)
            code = email_viewer.load()
            print(code)
        except Exception as e:
            print("Sai mật khẩu hoặc bị lock")
            pass


