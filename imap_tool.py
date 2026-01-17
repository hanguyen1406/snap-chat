import requests
import urllib.parse


def readImapWithProxy(email, password):
    en = urllib.parse.quote(email)
    pw = urllib.parse.quote(password)
    url = f'http://127.0.0.1:3000/imap?un={en}&pw={pw}'
    res = requests.get(url)
    print(res.text)
    res = res.json()
    if res['status'] == 'success':
        return res['code']
    else:
        return None


code = readImapWithProxy('haylatoinhikhb15a@outlook.com.vn', 'nhidung01@')

print(code)
