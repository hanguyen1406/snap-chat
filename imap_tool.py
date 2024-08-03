import imaplib
import email
from email.header import decode_header
import socks
import ssl


# Proxy information (replace with your actual proxy details)
proxy_host = "101.255.209.118"
proxy_port = 8089
proxy_username = "  "
proxy_password = ""  

# Hotmail account information
username = "jackiarzo80@outlook.com.vn"
password = "fsNzfavHHq"
imap_server = "imap-mail.outlook.com"
port = 993

# Create a proxy socket
proxy_sock = socks.socksocket()
proxy_sock.set_proxy(socks.HTTP, proxy_host, proxy_port)

# Connect to the proxy
proxy_sock.connect((imap_server, port))

# Wrap the proxy socket with SSL
ssl_sock = ssl.create_default_context().wrap_socket(proxy_sock, server_hostname=imap_server)

# Create an IMAP4_SSL object using the wrapped socket
mail = imaplib.IMAP4_SSL(imap_server, port)
mail.sock = ssl_sock

# Log in to your account
mail.login(username, password)

# Select the mailbox you want to read from
mail.select("inbox")

# Search for all emails in the mailbox
status, messages = mail.search(None, "ALL")

# Convert messages to a list of email IDs
email_ids = messages[0].split()

# Fetch the most recent email
latest_email_id = email_ids[-1]

# Fetch the email by ID
status, msg_data = mail.fetch(latest_email_id, "(RFC822)")

# Parse the email
for response_part in msg_data:
    if isinstance(response_part, tuple):
        msg = email.message_from_bytes(response_part[1])

        # Decode the email subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            # If it's a bytes, decode to str
            subject = subject.decode(encoding if encoding else "utf-8")

        # Decode email sender
        from_ = msg.get("From")

        print("Subject:", subject)


# Close the connection and logout
mail.close()
mail.logout()
