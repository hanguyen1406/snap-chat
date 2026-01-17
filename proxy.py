import requests

proxy_server = "sa-pr.lunaproxy.net:20000"

proxies = {"http": f"http://{proxy_server}"}
response = requests.get("http://myip.lunaproxy.io", proxies=proxies)
print(response.text)