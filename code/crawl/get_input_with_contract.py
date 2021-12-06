import os
import json
import urllib3
import time

http = urllib3.PoolManager()
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'
}
proxy = urllib3.ProxyManager('http://61.135.155.82:443', headers={'connection': 'keep-alive'})

file_path = "/home/chaoweilanmao/Desktop/EtherscanInfo/transactions/"
output_path = "/home/chaoweilanmao/Desktop/EtherscanInfo/trcode_with_input/"
file_list = os.listdir(file_path)

k = 0
while k < 1:
    print("processing the block: " + str(file_list[k]))
    file = open(file_path + file_list[k], mode='r+', encoding='UTF-8')
    res = file.read()
    transaction_list = json.loads(res)['transactions']
    i = 0
    while i < len(transaction_list):
        # print(transaction_list[i])
        contract_address = transaction_list[i]['to']
        if contract_address is None:
            i = i + 1
            continue
        input = transaction_list[i]['input']
        print(input)
        if input == "0x":
            i = i + 1
            continue
        print("process the contract" + str(i) + ":" + str(contract_address))
        try:
            response1 = http.request("GET", "http://api-cn.etherscan.com/api?module=proxy&action=eth_getCode&"
                                           "address=" + contract_address, headers = headers, timeout=10.0)
            # print(response1)
            time.sleep(5)
            response2 = http.request("GET", "http://api-cn.etherscan.com/api?module=contract&action=getabi&"
                                            "address=" + contract_address, headers = headers, timeout=10.0)
            # print(response2)
            time.sleep(1)
            raw_string1 = response1.data.decode('UTF-8')
            print(raw_string1)
            raw_string2 = response2.data.decode('UTF-8')
            print(raw_string2)
            json_string1 = json.loads(raw_string1)
            json_string2 = json.loads(raw_string2)
            byte_code = json_string1["result"]
            if byte_code is None:
                continue
            abi = json_string2["result"]
            if abi is None:
                continue
            file = open(output_path + str(i) + "-" + file_list[k].split('.')[0] + "-" + contract_address + '.txt', mode='w+', encoding="UTF-8")
            file.write(json.dumps({"byteCode":byte_code, "abi":abi, "input":input}))
            file.close()
            time.sleep(5)
            i = i + 1

        except Exception as e:
            print(e)
            print("error")
            time.sleep(10)
    k = k + 1