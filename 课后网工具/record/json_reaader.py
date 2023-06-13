import json
try:
    with open('record.json','r') as f:
        a = json.load(f)
    for one in a:
        print(one)
except:
    print('No record!(can not find "record.json")')
input()
