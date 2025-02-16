import json
import asyncio
import aiohttp
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector
import time
import requests


#########################################################################################
#  В блоке "if update:" вручную задан каждый сервис тк они хранят данные в разном формате
#  и нужен индивидуальный подход)
# 
#  Все пркоси хранятся в формате '{proxy_protocol} {proxy_ip_and_port}' построчно
#
#  Флаг update: Нужно ли опять запрашивать данные с сайтов
#  Флаг need_check: Нужно ли перепроверять полученные списки прокси
#  Параметр timeout: максимальное время ожидание ответа сервера при использовании прокси
#  Параметр times_to_try: количество попыток получение ответа 
#
#  Файл raw_proxy: Хранит только что полученный список прокси с сайтов
#  Файл checked_proxy: Хранит проверенный список прокси с сайтов


update = True
need_check = True

#url = 'http://httpbin.org/ip'
url = 'https://www.google.ru/'
timeout = 7
times_to_try = 3

    
if update:
    proxies_list_first = requests.get('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.json').json()
    proxies_list_first = [i for i in proxies_list_first]


    proxies_list_second = requests.get('https://proxyfreeonly.com/api/free-proxy-list?limit=500&page=1&sortBy=lastChecked&sortType=desc').json()
    proxies_list_second = [i for i in proxies_list_second]


    with open('./raw_proxy', mode='w') as out:
        for i in (proxies_list_first):
            out.write(f'{i['protocol'].lower()} {i['ip']}:{i['port']}' + '\n')


        for proxy in (proxies_list_second):
            if len(proxy['protocols']) > 1:
                for proto in proxy['protocols']:
                    out.write(f'{proto} {proxy['ip']}:{proxy['port']}' + '\n')

            else:
                out.write(f'{proxy['protocols'][0]} {proxy['ip']}:{proxy['port']}' + '\n')



async def check_proxy(ip, protocol, verbose=True, timeout=timeout, url=url, times_to_try=times_to_try):
    connector = ProxyConnector.from_url(f"{protocol}://{ip}")
    error = None
    async with aiohttp.ClientSession(connector=connector) as session:
        for _ in range(times_to_try):
            start = time.time()
            try:
                async with session.get(url, timeout=timeout) as response:
                    end = time.time()
                    print(f"{ip} {protocol} ok, time: {end - start}ms")
                    print("----------------------------------------------------------")
                    return {'ip': ip, 'protocol': protocol}

            except Exception as e:
                error = e
                pass

    if verbose:
        print(f"{ip} {protocol} error {error}")
        print("----------------------------------------------------------")
    return


async def check_manager(url):
    proxies_list = []

    with open('./raw_proxy', mode='r') as inpt:
        for i in inpt.readlines():
            tmp = i.strip().split()
            proxies_list.append({'ip': tmp[1], 'protocol': tmp[0]})

    print('Start magic')
    print("----------------------------------------------------------")

    return await asyncio.gather(*[asyncio.ensure_future(check_proxy(proxy['ip'], proxy['protocol'])) for proxy in proxies_list])


if need_check:
    loop = asyncio.new_event_loop()
    checked = [proxy for proxy in loop.run_until_complete(check_manager(url)) if proxy]
    with open('./checked_proxy', mode='w') as out:
        for proxy in checked:
            out.write(f'{proxy['protocol']} {proxy['ip']} ' + '\n')


#Examples for aiohttp_socks
#connector = ProxyConnector.from_url('socks5://user:password@127.0.0.1:1080')
### or use ProxyConnector constructor
# connector = ProxyConnector(
#     proxy_type=ProxyType.SOCKS5,
#     host='127.0.0.1',
#     port=1080,
#     username='user',
#     password='password',
#     rdns=True # default is True for socks5
# )

### proxy chaining (since ver 0.3.3)
# connector = ChainProxyConnector.from_urls([
#     'socks5://user:password@127.0.0.1:1080',
#     'socks4://127.0.0.1:1081',
#     'http://user:password@127.0.0.1:3128',
# ])

