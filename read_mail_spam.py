import imaplib
import email

# Thông tin đăng nhập
username = 'loganotd846@outlook.com.vn'
password = 'Amorrisxlj308'

# Kết nối với máy chủ IMAP của Hotmail (Outlook)
imap_server = 'imap-mail.outlook.com'
imap_port = 993

# Kết nối tới máy chủ
mailbox = imaplib.IMAP4_SSL(imap_server, imap_port)
mailbox.login(username, password)

# Chọn thư mục Spam (Junk)
mailbox.select('Junk')

# Tìm tất cả email trong thư mục Spam
status, messages = mailbox.search(None, 'ALL')
mail_ids = messages[0].split()

# Duyệt qua tất cả email
for i in mail_ids:
    status, data = mailbox.fetch(i, '(RFC822)')
    for response_part in data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject = email.header.decode_header(msg['Subject'])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()

            print(f"Email Subject: {subject}")
            print(f"From: {msg['From']}")
            print(f"Date: {msg['Date']}")

            # Print the email body
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if "attachment" not in content_disposition:
                        if content_type == "text/plain":
                            print(part.get_payload(decode=True).decode())
            else:
                # If the message isn't multipart, it's a simple email
                print(msg.get_payload(decode=True).decode())

# Đóng kết nối và đăng xuất
mailbox.close()
mailbox.logout()
