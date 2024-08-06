import requests

def TmProxy(api_key: str):
	json_site = {"api_key": api_key,"sign": "string","id_location": 0}
	while True:
		requests_proxy1 = requests.post('https://tmproxy.com/api/proxy/get-new-proxy', json=json_site).json()
		if requests_proxy1['code'] == 0:
			return {'status': "success", 'http': requests_proxy1['data']['https']}
		elif requests_proxy1['code'] == 5:
			requests_proxy2 = requests.post('https://tmproxy.com/api/proxy/get-current-proxy', json={"api_key": api_key}).json()
			if requests_proxy2['data']['timeout'] >= 300:
				return {'status': "success", 'http': requests_proxy2['data']['https']}
			else:
				giay=str(requests_proxy2['message']).split('after ')[1].split(' sec')[0]
				return {'status': "wait", 'time': giay}
		else:
			return {'status': "error", 'mess': requests_proxy2['message']}

prx = TmProxy('2de068c5aa064df4cd3867721a4772ad')

print(prx)
