from fake_useragent import UserAgent
import json
ua = UserAgent()

res = []

# Or get user-agent string from a specific browser
while 1:
    a = ua.getChrome
    # if a['os'] == 'win10' and a['useragent'] not in res:
    # res.append(a['useragent'])
    if 'Windows' in a['useragent']:
        open('user-agents.txt', 'a', encoding='utf-8').write(a['useragent'] + '\n')
        print(a['useragent'])





