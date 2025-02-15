import requests
from fake_useragent import UserAgent
import json

#########################################################################################
#  В блоке "if update:" вручную задан каждый сервис тк они хранят данные в разном формате
#  и нужен индивидуальный подход)
# 
#  Все пркоси хранятся в формате '{proxy_protocol} {proxy_ip_and_port}' построчно
#
#  Флаг update: Нужно ли опять запрашивать данные с сайтов
#  Флаг need_check: Нужно ли перепроверять полученные списки прокси
#  Параметр timeout: максимальное время ожидание ответа сервера при использовании прокси
#
#  Файл raw_proxy: Хранит только что полученный список прокси с сайтов
#  Файл checked_proxy: Хранит проверенный список прокси с сайтов



timeout = 1.9
update = True
need_check = True
url = 'http://httpbin.org/ip'

def check_proxy(ip, protocol, verbose=True, timeout=timeout, url=url):
    user_agent = UserAgent().random
    headers = {'User-Agent': user_agent}
    proxy_dict = {"http": f"{protocol}://{ip}"}

    try:
        response = requests.get(url, proxies=proxy_dict, headers=headers, timeout=timeout)

        if response.status_code == 200:
            time = int(response.elapsed.total_seconds() * 1000)

            if verbose:
                print(f"{ip} {protocol} ok, time: {time}ms")
                print("----------------------------------------------------------")

            return {'ip': ip, 'protocol': protocol}
    
    except Exception as e:
        if verbose:
            print(f"{ip} {protocol} error {e}")
            print("----------------------------------------------------------")
        return

    
if update:
    proxies_list_first = requests.get('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.json').json()
    proxies_list_first = [i for i in proxies_list_first]


    proxies_list_second = requests.get('https://proxyfreeonly.com/api/free-proxy-list?limit=500&page=1&sortBy=lastChecked&sortType=desc').json()
    proxies_list_second = [i for i in proxies_list_second]



    with open('raw_proxy', mode='w') as out:
        for i in (proxies_list_first):
            out.write(f'{i['protocol']} {i['ip']}:{i['port']}' + '\n')


        for proxy in (proxies_list_second):
            if len(proxy['protocols']) > 1:
                for proto in proxy['protocols']:
                    out.write(f'{proto} {proxy['ip']}:{proxy['port']}' + '\n')

            else:
                out.write(f'{proxy['protocols'][0]} {proxy['ip']}:{proxy['port']}' + '\n')



if need_check:
    proxies_list = []

    with open('raw_proxy', mode='r') as inpt:
        for i in inpt.readlines():
            tmp = i.strip().split()
            proxies_list.append({'ip': tmp[1], 'protocol': tmp[0]})

    with open('checked_proxy', mode='w') as out:
        for proxy in proxies_list:
            res = check_proxy(proxy['ip'], proxy['protocol'])
            if res:
                out.write(f'{res['protocol']} {res['ip']} ' + '\n')

            
            