import json
import sys
import re
import datetime
from string import digits
from gensim import corpora, models, similarities
from gensim.models import Doc2Vec
from bert_serving.client import BertClient
from sklearn.metrics.pairwise import cosine_similarity

import nltk
import nltk.tokenize as tk
from nltk.tokenize import word_tokenize


TaggededDocument = models.doc2vec.TaggedDocument

def process_bytes(s):
    s = json.loads(json.dumps(s))
    if type(s) is dict:
        data = s['data']
        hexstr = "0x"
        for idx in range(len(data)):
            ele = "{:02x}".format(data[idx])
            hexstr = hexstr + ele
        return hexstr
    else:
        hexstrings = []
        for item in s:
            hexstrings.append(process_bytes(item))
        return hexstrings

# give a file with the contract abi, extract all the function information
# from the abi file
def read_targets_from_abi(filepath):
    funcs_in_abi = []
    with open(filepath) as fp:
        abi = fp.read()
        abi_json = json.loads(abi)
        for single_func in abi_json:
            if single_func["type"] == "function":
                fun_sig = {"name" : single_func["name"], "inputs" : single_func["inputs"]}
                funcs_in_abi.append(json.dumps(fun_sig))
    return funcs_in_abi

# read the database functions from the json file
def read_funcdef_from_file(filename):
    func_list = []
    input_list = []
    with open(filename) as fp:
        file = fp.read()
        json_file_list = json.loads(file)
        for i in range(len(json_file_list)):
            func_list.append(json_file_list[i]['function'])
            input_list.append(json_file_list[i]['inputs'])

    #res_list = process_functions(func_list)
    return func_list, input_list

# the input is from the contractFuzzer, randomly choosed function definition
def process_input(input):
    input_type_list = []
    test_str = ''
    json_input = json.loads(input)
    test_str += process_name(json_input["name"]) + ' '
    for item in json_input["inputs"]:
        test_str += item["type"] + ' '
        input_type_list.append(item["type"])
    return test_str, input_type_list

# process the function definion to the string format
# the format like: functionName param1 type1 param2 type2 ....
def process_functions(funclist, input_type_list, input_list, k):
    func_def_list = []
    # print(funclist)
    funclist, inputlist ,level= trim_func(funclist, input_type_list, input_list, k)
    for i in range(len(funclist)):
        # cur_func = json.loads(funclist[i])
        func_str = ''
        func_str += process_name(funclist[i]["method"]) + ' '
        for j in range(len(funclist[i]["types"])):
            func_str += funclist[i]["types"][j] + ' '
        func_def_list.append(func_str)
    return func_def_list, funclist, inputlist, level

# choose the functions that exist the type info
def trim_func(func_list, input_type_list, input_list, k):
    print("trim size: " + str(k))
    level = 'first_level'
    first_level = []
    first_level_input = []
    second_level = []
    second_level_input = []
    remove_digits = str.maketrans('', '', digits)

    # process the first level functions
    # every type must exist
    # first level means totally the same, e.g. int256 --> int 256
    for i in range(len(func_list)):
        type_json = func_list[i]["types"]
        have_set = []
        types_are_all_exist = 0
        for input_type in input_type_list:
            # input_type = str(input_type).split('[')[0].translate(remove_digits)
            input_type = str(input_type).split('[')[0]
            for j in range(len(type_json)):
                # func_type = str(type_json[j]).split('[')[0].translate(remove_digits)
                func_type = str(type_json[j]).split('[')[0]
                if func_type == input_type and (j not in have_set):
                    types_are_all_exist += 1
                    have_set.append(j)
                    break
        if types_are_all_exist == len(input_type_list):
            first_level.append(func_list[i])
            first_level_input.append(input_list[i])

    # process the second level functions
    # second level means almost the same
    for i in range(len(func_list)):
        type_json = func_list[i]["types"]
        have_set = []
        types_are_all_exist = 0
        for input_type in input_type_list:
            input_type = str(input_type).split('[')[0]
            if len(re.findall("\d+", str(input_type).split('[')[0])) > 0:
                input_type_num = int(re.findall("\d+", str(input_type).split('[')[0])[0])
            else:
                input_type_num = 256
            for j in range(len(type_json)):
                func_type = str(type_json[j]).split('[')[0]
                if len(re.findall("\d+", str(type_json[j]).split('[')[0])) > 0:
                    func_type_num = int(re.findall("\d+", str(type_json[j]).split('[')[0])[0])
                else:
                    func_type_num = 256
                if func_type == input_type and (j not in have_set) and input_type_num >= func_type_num:
                    types_are_all_exist += 1
                    have_set.append(j)
                    break
                # not very restrict
                elif (("int" in func_type and "int" in input_type) or ("byte" in func_type and "byte" in input_type)) and input_type_num >= func_type_num and (j not in have_set):
                    types_are_all_exist += 1
                    have_set.append(j)
                    break
        if types_are_all_exist == len(input_type_list):
            second_level.append(func_list[i])
            second_level_input.append(input_list[i])

    if len(first_level) < k:
        if len(second_level) < k:
            level = "third_level"
            print("third level")
            return func_list,input_list, level
        else:
            level = "second_level"
            print("second level")
            return second_level,second_level_input, level
    print("first level")
    return first_level,first_level_input,level

# process the function name, such as aaaBaa
def process_name(methodname):
    name_str = ''
    last_name = str(methodname)
    for i in range(len(last_name)):
        if (last_name[i] <= 'z' and last_name[i] >= 'a') or (last_name[i] <= '9' and last_name[i] >= '0'):
            name_str += last_name[i]
        elif last_name[i] <= 'Z' and last_name[i] >= 'A':
            name_str += ' ' + last_name[i].lower()
        elif last_name[i] == '_':
            name_str += ' '
    return name_str

# training the word vector and calculate the similarity
# using TFIDF
# def train_and_get_similarity(list, test):
#     for item in list:
#         print(item)
#     tokenizer = tk.WhitespaceTokenizer()
#     base_items = [[i for i in tokenizer.tokenize(item)] for item in list]
#     dictionary = corpora.Dictionary(base_items)
#     corpus = [dictionary.doc2bow(item) for item in base_items] # 运用词袋去生成语料库
#     tf = models.TfidfModel(corpus)
#     num_features = len(dictionary.token2id.keys())
#     index = similarities.SparseMatrixSimilarity(tf[corpus], num_features = num_features)
#     test_words = [word for word in tokenizer.tokenize(test)]
#     new_vec = dictionary.doc2bow(test_words) # 通过TFIDF模型获取新文本的向量
#     sim = index.get_similarities(tf[new_vec])
#     print(sim)
#     return sim

# using doc2vec
# def train_and_get_similarity(list, test):
#     x_train = []
#     for item in list:
#         print(item)
#     for i in range(len(list)):
#         word_list = list[i].split(' ')
#         document = TaggededDocument(word_list, tags=[i])
#         x_train.append(document)
#     model = Doc2Vec(x_train,min_count=1, window = 3, vector_size = 100, sample=1e-3, negative=5, workers=4)
#     model.train(x_train, total_examples=model.corpus_count, epochs=70)
#     test_text = test.split(' ')
#     inferred_vec = model.infer_vector(doc_words=test_text, alpha=0.025, steps=500)
#     sim = model.docvecs.most_similar([inferred_vec], topn=5)
#     print(sim)
#     for i,sima in sim:
#         print(list[i])
#     return sim

# using bert
# in theory should divide into three level
def train_and_get_similarity(wordlist, test):
    client = BertClient(ip='127.0.0.1')
    test_token = word_tokenize(test)
    sample_token = []
    for item in wordlist:
        sample_token.append(word_tokenize(item))
    sample_vec = client.encode(sample_token, is_tokenized=True)
    test_vec = client.encode([test_token], is_tokenized=True)
    sim = cosine_similarity(sample_vec, test_vec.reshape(1, -1))
    final_sim = []
    for item in sim:
        final_sim.append(item[0])
    return final_sim


# from the calculated similarity to choose the top similar definition
def choose_topk_input(similarity, k):
    print("here top k: " + str(k))
    tmp_similarity = []
    for i in range(len(similarity)):
        tmp_similarity.append((i, similarity[i]))

    choice = sorted(tmp_similarity, key=lambda x:x[1], reverse=True)
    return choice[0:k]

# output to the seed file based on different type
# just like the format as the initial seed file
def output(topk, func_list, input_list, target_input, level):
    target_input_json = json.loads(target_input)
    target_func = target_input_json["name"]
    remove_digits = str.maketrans('', '', digits)
    input_pool = []
    # target_input means the function which we want to get the input
    cnt = 0
    for idx,_ in topk:
        similar_func = func_list[idx]
        similar_inputs = input_list[idx]
        input_pool.append({"similar_func" : similar_func, "inputs": []})
        for item in similar_inputs:
            input_pool[cnt]["inputs"].append(item)
        cnt+=1

    # determine a path to output
    return {"func": target_input_json, "func_inputs": input_pool}



        

def main():
    # if len(sys.argv) <= 3:
    #     print("arguments are not enough")
    #     return
    # this file contains a lot of records: 
    # {"inputs": inputs, "function": {"method": methodName, "types": methodType, "params": paramName}}
    # word_list is full of functions and input_list is full of inputs
    # input_list[i] is the input of the function word_list[i]
    filepath = sys.argv[1] # target abi
    samplepath = sys.argv[2]
    outputpath = sys.argv[3] # output file path
    k = int(sys.argv[4]) #topk
    word_list,input_list = read_funcdef_from_file(samplepath)
    
    
    # target_functions is full of functions in the target abi
    # {"name" : name, "inputs" : [{"name" : inputname, "type" : type}]}
    target_functions = read_targets_from_abi(filepath)

    file_output = []
    starttime = datetime.datetime.now()
    for item in target_functions:
        print(item)
        # test_word is a sentence with functionname, inputname and inputtype
        # funcName type1 inputName1 type2 inputName2 ... 
        # input_type_list is all the types in target_function
        test_word, input_type_list = process_input(item)
        if(len(input_type_list) == 0):
            file_output.append(output([], [], [], item, "no_level")) # if no inputs
            continue
        
        # final_word_list is full of the sentence in the source abi
        # like funcName type1 inputName1 type2 inputName2 ... 
        # final_func_list is full of source functions
        # final_input_list is full of the inputs, which final_func_list[i]'s input is final_input_list[i]
        final_word_list, final_func_list, final_input_list, level = process_functions(word_list, input_type_list, input_list, 5)
        sim_matrix = train_and_get_similarity(final_word_list, test_word)

        # get the most possible function index in the topk_list
        topk_list = choose_topk_input(sim_matrix, k)
        file_output.append(output(topk_list, final_func_list, final_input_list, item, level))

    endtime = datetime.datetime.now()
    print("time cost is:" + str((endtime - starttime).seconds) + " seconds")

    target_abi = filepath.split('/')[-1]
    with open(outputpath + '/' + target_abi +".output.json", "w+") as fp:
        fp.write(json.dumps(file_output))
        fp.close()

if __name__ == '__main__':
    main()
    exit(0)
