# 对profile进行编号,

import pickle
import sys

file = open('profileRankWord.pkl','rb') 
profiles = pickle.load(file)
print(len(profiles))
print(type(profiles))
print(profiles[:250])

profiles = profiles[:250]
sum = 0
for item in profiles:
    sum += item[1]//60
print(sum)
sys.exit(0)

profilesDict = {str(index):profiles[index] for index in range(len(profiles))}  # 在这一步做了匿名化处理

with open('profileWordDict.pkl', 'wb') as f:
    pickle.dump(profilesDict, f)
    
    
    