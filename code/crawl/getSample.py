import json

fd = open('./samples/all_funcs_need.json')
content = fd.read()
json_content = json.loads(content)
fd.close()
sample_content = json_content[0:]
# print(len(sample_content))
sample_dic = {}

for i in range(len(sample_content)):
	cur_func = sample_content[i]
	func_name = cur_func['function']['name']
	signature = func_name
	for item in cur_func['function']['inputs']:
		signature += ' ' + item['type']
	
	if signature in sample_dic.keys():
		sample_dic[signature].append(cur_func)
	else:
		sample_dic[signature] = [cur_func]

res = []


for item in sample_dic.keys():
	isFirst = True
	l = sample_dic[item]
	one_func = {'inputs': [], 'function': {'types': []}}
	for funcs in l:
		
		# one_func = json.loads(json.dumps(one_func))
		if isFirst:
			one_func['function']['method'] = funcs['function']['name']
			print(funcs['function']['name'])
			for t in funcs['function']['inputs']:
				one_func['function']['types'].append(t['type'])
				# one_func['function']['params'].append(t['name'])
			one_func['inputs'].append(funcs['input'])
		else:
			one_func['inputs'].append(funcs['input'])
		isFirst = False

	res.append(one_func)

print(len(res))
fd = open('./samples/sample.json', 'w+')
fd.write(json.dumps(res))

