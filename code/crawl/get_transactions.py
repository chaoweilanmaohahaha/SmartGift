import urllib3
import json
import time
# 2253
latest_blocknum = 10128210
want_to_get_num = 957
dir_path = "E:\\EtherscanInfo\\transactions\\"

http = urllib3.PoolManager()

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'}

proxy = urllib3.ProxyManager('http://114.99.54.65:8118', headers={'connection': 'keep-alive'})
i = 0
while i < want_to_get_num:
    print("Processing the block:" + str(latest_blocknum - i))
    try:
        res = proxy.request("GET", "http://api-cn.etherscan.com/api?module=proxy&action=eth_getBlockByNumber&tag="+ str(hex(latest_blocknum - i)) +"&boolean=true&apikey=YourApiKeyToken")
        raw_res = res.data.decode("UTF-8")
        json_res = json.loads(raw_res)
        print(json_res["result"]["transactions"])
        transactions = json_res["result"]["transactions"]
        file = open(dir_path + str(latest_blocknum - i) + ".txt", mode="w+", encoding="UTF-8")
        file.write(json.dumps({"transactions": transactions}))
        file.close()
        i = i + 1
    except Exception as e:
        print("error")
        time.sleep(5)  # whatever the error is, wait 100 sec more or less