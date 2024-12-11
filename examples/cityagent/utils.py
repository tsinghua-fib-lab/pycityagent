import argparse
import json
import math
import pickle
import random
# -*- coding: utf-8 -*-
import sys
from datetime import datetime, timedelta
from operator import itemgetter
from random import choice

import numpy as np

def getEventNum():
    '''
    通过真实概率值采样,得到
    '''
    value = [3, 5, 4, 8, 6, 7, 10, 9, 14, 16, 13, 11, 12, 17, 15, 21]
    prob = [0.5162918266593527, 0.1417443773998903, 0.20065825562260012, 0.019199122325836534, 0.06297312122874382, 0.03708173340647285, 0.005156335710367526, 0.00811848601206802, 0.0009873834339001646, 0.0005485463521667581, 0.0012068019747668679, 0.0029621503017004938, 0.0020844761382336806, 0.00032912781130005483, 0.0005485463521667581, 0.00010970927043335162]
    index = list(range(len(value)))
    sample = np.random.choice(index, size=1, p=prob)  # 根据计算出来的概率值进行采样
    return value[sample[0]]

def getTimeDistribution():
    file = open('DataLocal/事件的时间分布/timeDistribution_Event.pkl','rb') 
    timeDistribution_Event = pickle.load(file)
    timeDistribution_Event['banking and financial services'] = timeDistribution_Event['handle the trivialities of life']
    timeDistribution_Event['cultural institutions and events'] = timeDistribution_Event['handle the trivialities of life']
    return timeDistribution_Event

def setIO(modeChoice, keyid):
    if modeChoice == 'labeld':
        file = open('DataLocal/人物profile统计无年龄/标注数据人物profile.pkl','rb') 
        profileDict = pickle.load(file)  # 标注数据是需要id的
        profileIds = list(profileDict.keys())
        profiles = list(profileDict.values())
        personNum = len(profiles)
        genIdList = [keyid]  # 对一类人生成5个模板,将key分配到id上进行加速
        loopStart = 0
        loopEnd = personNum
        return profileIds, profiles, personNum, genIdList, loopStart, loopEnd
    
    elif modeChoice == 'realRatio':
        file = open('DataLocal/人物profile统计无年龄/profileWordDict.pkl','rb') 
        profileDict = pickle.load(file)  # 其中的keys已经做了匿名化
        profileIds = list(profileDict.keys())
        profilesAndNum = list(profileDict.values())
        profiles = [item[0] for item in profilesAndNum]
        personNum = len(profiles)
        genIdList = [0] # list(range(10))  # 现在生成10次
        loopStart = keyid*60  # 将多key放到id上加速,top300其实也是可以的
        loopEnd = keyid*60+60
        return profileIds, profiles, personNum, genIdList, loopStart, loopEnd
    
    else:
        print('error!')
        sys.exit(0)
        
def getBasicData6(personBasicInfo, day, N):
    '''
    0122: 去除了anchor机制,使得生成更加自由
    0124: 加入example强调回家的作用.
    0125: 恢复原始的轮询式提问方式,在global中提问中注意改变全局的提问.
    0128: 加入COT机制,试图增强性能. But I doubt that.
    '''
    # age, education, gender, consumption, occupation = personBasicInfo.split('-')
    # ageDescription = "" if age == '0' else "Age: {}; ".format(age)
    education, gender, consumption, occupation = personBasicInfo.split('-')
    genderDescription = "" if gender == 'uncertain' else "Gender: {}; ".format(gender)
    educationDescription = "" if education == 'uncertain' else "Education: {}; ".format(education)
    consumptionDescription = "" if consumption == 'uncertain' else "Consumption level: {}; ".format(consumption)
    occupationDescription = "" if occupation == 'uncertain' else "Occupation or Job Content: {};".format(occupation)

    personDescription = """You are a person and your basic information is as follows:
{}{}{}{}""".format(genderDescription, educationDescription, consumptionDescription, occupationDescription)

    day = day if day != 'Saturday' and day != 'Sunday' else day + '. It is important to note that people generally do not work on weekends and prefer entertainment, sports and leisure activities. There will also be more freedom in the allocation of time.'
   
    globalInfo = [
        # 首先交待任务,申明轨迹点的一般形式.
        {"role": "system","content":
"""{}

Now I want you to generate your own schedule for today.(today is {}).
The specific requirements of the task are as follows:
1. You need to consider how your character attributes relate to your behavior.
2. I want to limit your total number of events in a day to {}. I hope you can make every decision based on this limit.
3. I want you to answer the reasons for each event.

Note that: 
1. All times are in 24-hour format.
2. The generated schedule must start at 0:00 and end at 24:00. Don't let your schedule spill over into the next day.
3. Must remember that events can only be choosed from [go to work, go home, eat, do shopping, do sports, excursion, leisure or entertainment, go to sleep, medical treatment, handle the trivialities of life, banking and financial services, cultural institutions and events].
4. I'll ask you step by step what to do, and you just have to decide what to do next each time.

Here are some examples for reference. For each example I will give a portrait of the corresponding character and the reasons for each arrangement.

Example 1:
This is the schedule of a day for a coder who works at an Internet company.
[
["go to sleep", "(00:00, 11:11)"], (Reason: Sleep is the first thing every day.)
["go to work", "(12:08, 12:24)"], (Reason: Work for a while after sleep. This person's working hours are relatively free, there is no fixed start and finish time.) 
["eat", "(12:35, 13:01)"], (Reason: It's noon after work. Go get something to eat.)
["go to work", "(13:15, 20:07)"],   (Reason: After lunch, the afternoon and evening are the main working hours. And he works so little in the morning that he need to work more in the afternoon and evening. So this period of work can be very long.)
["go to sleep", "(21:03, 23:59)"]  (Reason: It was already 9pm when he got off work, and it is time to go home and rest.)
]

Example 2:
This is the schedule of a day for a salesperson at a shopping mall.
[
["go to sleep", "(00:00, 08:25)"], (Reason: Of course the first thing of the day is to go to bed.)
["go to work", "(09:01, 19:18)"], (Reason: Generally, the business hours of shopping malls are from 9 am to 7 pm, so she works in the mall during this time and will not go anywhere else.)
["go home", "(20:54, 23:59)"], (Reason: It's almost 9pm after getting off work. Just go home and rest at home.)
]

Example 3:
This is the schedule of a day for a manager who is about to retire.
[
["go to sleep", "(00:00, 06:04)"], (Reason: He is used to getting up early, so he got up around 6 o'clock in the morning.)
["eat", "(08:11, 10:28)"], (Reason: He has the habit of having morning tea after getting up and enjoys the time of slowly enjoying delicious food in the morning.)
["go home", "(12:26, 13:06)"], (Reason: After breakfast outside, take a walk for a while, and then go home at noon.)
["excursion", "(13:34, 13:53)"], (Reason: He stays at home most of the morning, so he decides to go out for a while in the afternoon.)
["go to work", "(14:46, 16:19)"], (Reason: Although life is already relatively leisurely, he still has work to do, so he has to go to the company to work for a while in the afternoon.)
]

Example 4:
This is the schedule of a day for a lawyer who suffers a medical emergency in the morning.
[
["go to sleep", "(00:00, 09:36)"], (Reason: Sleep until 9:30 in the morning. Lawyers' working hours are generally around 10 o'clock.)
["medical treatment", "(11:44, 12:03)"], (Reason: He suddenly felt unwell at noon, so he went to the hospital for treatment.)
["go to work", "(12:27, 14:56)"], (Reason: After seeing the doctor, the doctor said there was nothing serious, so he continued to return to the company to work for a while.)
["go to sleep", "(17:05, 23:59)"], (Reason: Since he was not feeling well, he got off work relatively early and went home to rest at 5 p.m.)
]

Example 5:
This is an architect's schedule on a Sunday.
[
["go to sleep", "(00:00, 06:20)"], (Reason: The first thing is of course to sleep.)
["handle the trivialities of life", "(07:18, 07:32)"], (Reason: After getting up, he first dealt with the trivial matters in life that had not been resolved during the week.)
["leisure or entertainment", "(07:38, 17:27)"], (Reason: Since today was Sunday, he didn't have to work, so he decided to go out and have fun.)
["handle the trivialities of life", "(18:22, 19:11)"], (Reason: After coming back in the evening, he would take care of some chores again.)
 ["go to sleep", "(20:51, 23:59)"] (Reason: Since tomorrow is Monday, go to bed early to better prepare for the new week.)
]

Example 6:
This is the schedule of a day for a customer service specialist.
[
[go to work, (9:21, 16:56)], (Reason: Work dominated the day and was the main event of the day.)
[go home, (20:00, 23:59)], (Reason: After a day's work and some proper relaxation, he finally got home at 8 o 'clock.)
]

Example 7:
This is the schedule of a day for a wedding event planner.
[
[go to work, (11:21, 20:56)], (Reason: As a wedding planner, her main working hours are from noon to evening.)
[go home, (23:10, 23:30)], (Reason: After finishing the evening's work, she went home to rest.)
[handle the trivialities of life, (23:30, 23:59)], (Reason: Before she goes to bed, she takes care of the trivial things in her life.)
]

Example 8:
This is the schedule of a day for a high school teacher in Saturday.
[
[eat, (06:11, 7:28)], (Reason: He has a good habit: have breakfast first after getting up in the morning.)
[handle the trivialities of life, (07:48, 08:32)],  (Reason: After breakfast, he usually goes out to deal with some life matters.)
[go home, (9:00, 11:00)], (Reason: After finishing all the things, go home.)
[medical treatment, (13:44, 17:03)], (Reason: Today is Saturday and he doesn't have to work, so he decides to go to the hospital to check on his body and some recent ailments.)
[go home, (19:00, 23:59)], (Reason: After seeing the doctor in the afternoon, he goes home in the evening.)
]

As shown in the example, a day's planning always starts with "go to sleep" and ends with "go to sleep" or "go home".
""".format(personDescription, day, N)},
    ]
    # print('Basic Data perpare done!')

    return globalInfo



def getDay():
    '''
    随机采样今天是星期几
    '''
    value = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    prob = [0.1428, 0.1428, 0.1428, 0.1428, 0.1428, 0.1428, 0.1432]
    index = list(range(len(value)))
    sample = np.random.choice(index, size=1, p=prob)  # 根据计算出来的概率值进行采样
    return value[sample[0]]


def sampleTime(event):
    '''
    根据事件的类型,在真实数据统计出的分布中进行采样,获取时间
    '''
    # genEs = ["go to work", "go home", "eat", "do shopping", "do sports", "excursion", "leisure or entertainment", "go to sleep", "medical treatment", "handle the trivialities of life", "banking and financial services", "cultural institutions and events"]
    # realEs = ['excursion', 'leisure or entertainment', 'eat', 'go home', 'do sports', 'handle the trivialities of life', 'do shopping', 'go to work', 'medical treatment', 'go to sleep']
    # for item in genEs:
    #     if item not in realEs:
    #         print(item)

    # print(timeDistribution_Event.keys())
    timeDistribution_Event = getTimeDistribution()
    timeDis = timeDistribution_Event[event]
    timeZones = list(timeDis.keys())
    # print(timeZones)
    # sys.exit(0)
    length = len(list(timeDis.keys()))
    weightList = list(timeDis.values())
    indexx = list(range(length))
    sample = np.random.choice(indexx, size=1, p=weightList)  # 根据计算出来的概率值进行采样
    timeZone = timeZones[sample[0]]  # 选好了以半小时为度量的区间
    # print(timeZone)
    minutes = getTimeFromZone(timeZone)
    # print(minutes)
    return minutes


def add_time(start_time, minutes):
    """
    计算结束后的时间，给出起始时间和增量时间（分钟）
    :param start_time: 起始时间，格式为 '%H:%M'
    :param minutes: 增量时间（分钟）
    :return: 结束后的时间，格式为 '%H:%M'；是否跨越了一天的标志
    """
    # 将字符串转换为 datetime 对象，日期部分设为一个固定的日期
    start_datetime = datetime.strptime('2000-01-01 ' + start_time, '%Y-%m-%d %H:%M')

    # 增加指定的分钟数
    end_datetime = start_datetime + timedelta(minutes=minutes)

    # 判断是否跨越了一天
    if end_datetime.day != start_datetime.day:
        cross_day = True
    else:
        cross_day = False

    # 将结果格式化为字符串，只包含时间部分
    end_time = end_datetime.strftime('%H:%M')

    return end_time, cross_day

def getTimeFromZone(timeZone0):
    time0, time1 = timeZone0.split('-')
    time0 = float(time0)/2  # 这里已经化成小时了
    time1 = float(time1)/2
    # print(time0)
    # print(time1)
    
    sampleResult = random.uniform(time0, time1)  # 采样一个具体的时间值出来,单位是小时
    # print(sampleResult)  
    minutes = int(sampleResult*60)
    return minutes

def sampleGapTime():
    '''
    事件之间的间隔时间
    '''
    minutes = getTimeFromZone('0-2')  # 将事件的间隔时间设置为0到1个小时
    return minutes


def choiceHW():
    file = open('DataLocal/家和工作地汇总/hws.pkl','rb') 
    HWs = pickle.load(file)
    (home, work) = choice(HWs)
    return (home, work)
    
def get_poi(sim, id):
    result = sim.map.get_poi(id)
    res = {}
    res['poi_id'] = result['id']
    res['aoi_id'] = result['aoi_id']
    res['name'] = result['name']
    res['x'] = result['position']['x']
    res['y'] = result['position']['y']
    (res['long'],  res['lati']) = sim.map.xy2lnglat(result['position']['x'], result['position']['y'])
    return res


def getDirectEventID(event):
    # 直接从event查询具体的POI, 也不再问具体的类目
    if event in ['have breakfast', 'have lunch', 'have dinner', 'eat']:
        return "10"
    elif event == 'do shopping':
        return "13"
    elif event == 'do sports':
        return "18"
    elif event == 'excursion':  # 这里指短期的旅游景点
        return "22"
    elif event == 'leisure or entertainment':
        return "16"
    elif event == 'medical treatment':
        return "20"
    elif event == 'handle the trivialities of life':
        return "14"
    elif event == 'banking and financial services':
        return "25"
    elif event == 'government and political services':
        return "12"
    elif event == 'cultural institutions and events':
        return "23"
    else:
        print('\nIn function event2cate: The selected choice is not in the range!\n')
        sys.exit(0)
        
def event2poi_gravity_matrix(sim, map, label, nowPlace):
    nowPlace = map.get_poi(nowPlace[1])  # 由poi id查询到poi的全部信息
    labelQueryId = label
    
    # 现在就假设是在10km内进行POI的选择,10km应该已经是正常人进行出行选择的距离上限了,再远就不对劲了。
    pois10k = sim.get_pois_from_matrix(
            center = (nowPlace['position']['x'], nowPlace['position']['y']), 
            prefix= labelQueryId, 
        )
    if len(pois10k) > 10000:
        pois10k = pois10k[:10000]
    
    if pois10k[-1][1] < 5000:
            pois10k = map.query_pois(
            center = (nowPlace['position']['x'], nowPlace['position']['y']), 
            radius = 10000,  # 10km查到5000个POI是一件非常轻松的事情
            category_prefix= labelQueryId, 
            limit = 30000  # 查询10000个POI
        )  # 得到的pois是全部的信息.
    
    N = len(pois10k)
    # 这么一番操作之后的POI数量应该会有很多了, 关于密度如何计算的问题
    # 关于POI的密度的问题，相对于我现在的位置而言，密度有多少。
    pois_Dis = {"1k":[], "2k":[], "3k":[], "4k":[], "5k":[], "6k":[], "7k":[], "8k":[], "9k":[], "10k":[], "more":[]}
    for poi in pois10k:
        iflt10k = True
        for d in range(1,11):
            if (d-1)*1000 <= poi[1] < d*1000:
                pois_Dis["{}k".format(d)].append(poi)
                iflt10k = False
                break
        if iflt10k:
            pois_Dis["more"].append(poi)
    
    res = []
    distanceProb = []
    for poi in pois10k:
        iflt10k = True
        for d in range(1,11):
            if (d-1)*1000 <= poi[1] < d*1000:
                n = len(pois_Dis["{}k".format(d)])
                S = math.pi*((d*1000)**2 - ((d-1)*1000)**2)
                density = n/S
                distance = poi[1]
                distance = distance if distance>1 else 1
                
                # 距离衰减系数,用距离的平方来进行计算,使得远方的地点更加不容易被选择 TODO 这里是平方倒数, 还是一次方倒数
                weight = density / (distance**2)  # 原来是(distance**2),权重貌似是合理的
                
                # 修改:需要对比较近的POI的概率值进行抑制
                # weight = weight * math.exp(-15000/(distance**1.6))  # 抑制近POI值
                
                res.append((poi[0]['name'], poi[0]['id'], weight, distance))
                
                # TODO 这里的一次选择的概率值也修改了,需要进一步check
                distanceProb.append(1/(math.sqrt(distance)))  # 原来是distanceProb.append(1/(math.sqrt(distance)))
                
                iflt10k = False
                break
    
    # 从中抽取50个.
    distanceProb = np.array(distanceProb)
    distanceProb = distanceProb/np.sum(distanceProb)
    distanceProb = list(distanceProb)
    
    options = list(range(len(res)))
    sample = list(np.random.choice(options, size=50, p=distanceProb))  # 根据计算出来的概率值进行采样
    
    get_elements = itemgetter(*sample)
    random_elements = get_elements(res)
    # printSeq(random_elements)
    # sys.exit(0)
    # random_elements = random.sample(res, k=30)
    
    # 接下来需要对权重归一化,成为真正的概率值
    weightSum = sum(item[2] for item in random_elements)
    final = [(item[0], item[1], item[2]/weightSum, item[3]) for item in random_elements]
    # printSeq(final)
    # sys.exit(0)
    return final
        
def event2poi_gravity(map, label, nowPlace):
    # 直接从意图对应到POI，好处是数量多
    # 这里还是考虑了POI类型的.
    
    if nowPlace[1] in map.pois.keys():
        nowPlace = map.get_poi(nowPlace[1])  # 由poi id查询到poi的全部信息
    else:
        nowPlace = map.get_aoi(nowPlace[1])
        nowPlace['position'] = {'x': nowPlace['positions'][0]['x'], 'y': nowPlace['positions'][0]['y']}
    labelQueryId = label
    
    # 现在就假设是在10km内进行POI的选择,10km应该已经是正常人进行出行选择的距离上限了,再远就不对劲了。
    pois10k = map.query_pois(
            center = (nowPlace['position']['x'], nowPlace['position']['y']), 
            radius = 100000,  # 10km查到5000个POI是一件非常轻松的事情
            category_prefix= labelQueryId, 
            limit = 20000  # 查询10000个POI
        )  # 得到的pois是全部的信息.
    
    print(pois10k)
    
    N = len(pois10k)
    # 这么一番操作之后的POI数量应该会有很多了, 关于密度如何计算的问题
    # 关于POI的密度的问题，相对于我现在的位置而言，密度有多少。
    pois_Dis = {"1k":[], "2k":[], "3k":[], "4k":[], "5k":[], "6k":[], "7k":[], "8k":[], "9k":[], "10k":[], "more":[]}
    for poi in pois10k:
        iflt10k = True
        for d in range(1,11):
            if (d-1)*1000 <= poi[1] < d*1000:
                pois_Dis["{}k".format(d)].append(poi)
                iflt10k = False
                break
        if iflt10k:
            pois_Dis["more"].append(poi)
    
    res = []
    distanceProb = []
    for poi in pois10k:
        iflt10k = True
        for d in range(1,11):
            if (d-1)*1000 <= poi[1] < d*1000:
                n = len(pois_Dis["{}k".format(d)])
                S = math.pi*((d*1000)**2 - ((d-1)*1000)**2)
                density = n/S
                distance = poi[1]
                distance = distance if distance>1 else 1
                
                # 距离衰减系数,用距离的平方来进行计算,使得远方的地点更加不容易被选择 TODO 这里是平方倒数, 还是一次方倒数
                weight = density / (distance**2)  # 原来是(distance**2),权重貌似是合理的
                
                # 修改:需要对比较近的POI的概率值进行抑制
                # weight = weight * math.exp(-15000/(distance**1.6))  # 抑制近POI值
                
                res.append((poi[0]['name'], poi[0]['id'], weight, distance))
                
                # TODO 这里的一次选择的概率值也修改了,需要进一步check
                distanceProb.append(1/(math.sqrt(distance)))  # 原来是distanceProb.append(1/(math.sqrt(distance)))
                
                iflt10k = False
                break
    
    # 从中抽取50个.
    distanceProb = np.array(distanceProb)
    distanceProb = distanceProb/np.sum(distanceProb)
    distanceProb = list(distanceProb)
    
    options = list(range(len(res)))
    sample = list(np.random.choice(options, size=50, p=distanceProb))  # 根据计算出来的概率值进行采样
    
    get_elements = itemgetter(*sample)
    random_elements = get_elements(res)
    # printSeq(random_elements)
    # sys.exit(0)
    # random_elements = random.sample(res, k=30)
    
    # 接下来需要对权重归一化,成为真正的概率值
    weightSum = sum(item[2] for item in random_elements)
    final = [(item[0], item[1], item[2]/weightSum, item[3]) for item in random_elements]
    # printSeq(final)
    # sys.exit(0)
    return final



def sampleNoiseTime():
    noise = random.randint(-10, 10)
    return noise