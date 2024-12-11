'''
主要就是从全部信息中把人物的profile信息拿出来
'''

import numpy as np
import sys
import pickle

persionInfo = {}
with open("../../Datasets/Tencent/merge_user_multiday_trace_all_10w_seq_user_id_sorted", 
          "r", 
          encoding='utf-8') as f:
    while True:
        data = f.readline()
        if not data:
            break
        index, track, Info = data.split()
        persionInfo[index] = Info

# 需要将profile数据存下来
with open('profiles.pkl', 'wb') as f:
    pickle.dump(persionInfo, f)


