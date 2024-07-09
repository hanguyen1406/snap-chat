import requests

def get_proxys(n, url):
	atr = url.split('&')
	atr[1] = 'num=' + str(n)
	link = '&'.join(atr)
	# print(link)
	response = requests.get(url)
	if response.status_code == 200:
		prxs = response.text.split('\n')
		return prxs
	else:
		print(f"Request failed with status code: {response.status_code}")
		return []
	


url = "https://tq.lunaproxy.com/getflowip?neek=1329474&num=2&type=1&sep=1&regions=sa&ip_si=2&level=1&sb="
get_proxys(10, url)


