import pickle
import sys


def turnInfoStr(profileStr):
    age, education, gender, consumption, _, occupation,_ = profileStr.split(',')
    _, age = age.split(":")
    _, education = education.split(":")
    _, gender = gender.split(":")
    _, consumption = consumption.split(":")
    # _, occupation = occupation.split(":")
    # _, occupation, _ = occupation[1:-1].split(',')
    
    return education+'-'+gender+'-'+consumption+'-'+ occupation # 注意，里面现在是没有年龄的信息的


def printSeq(someSeq):
    for item in someSeq:
        print(item)

def transfer(str):
    education, gender, consumption, occupation = sen.split('-')

    educationDict = {"1":"Doctoral degree", "2":"Master's degree", "3":"Bachelor's degree", "4":"High school diploma", "5":"Junior high school diploma", "6":"Elementary school diploma", "7":"associate degree", 'n':'uncertain'}
    genderDict = {'1':'man', '2':'woman', 'n':'uncertain'}
    consumptionDict = {'1':'low', '2':'slightly low', '3':'medium' ,'4':'slightly high' ,'5':'high','n':'uncertain'}
    occupationDict = {
        '1000':'IT Engineer/Designer/Product Manager', 
        '48':'Online Sales/Operations/Service',
        '182':'Training Instructor',
        '159':'Technical Worker/Technician',
        '2':'Investment/Financial Advisor',
        '66':'Copywriting/Event Planning',
        '45':'Front Desk Reception/Telephone Operator',
        '217':'Biomedical Engineering/Pharmaceutical/Medical and Health',
        '554':'Finance/Accounting/Audit/Tax/Accountant',
        '47':'Sales Manager',
        '130':'Teacher',
        '808':'Public Relations/Media',
        '3':'Administrative Officer/Assistant',
        '384':'Construction Engineering/Civil Engineering/Interior Design/Building Materials',
        '629':'Warehousing/Logistics/Supply Chain/Transportation',
        '50':'Customer Service Representative/Assistant',
        '733':'Lawyer/Legal Affairs/Political and Legal Affairs/Judge',
        '178':'Store Manager/Manager',
        '208':'Quality Inspector/Tester',
        '330':'Apparel/Textile/Leather',
        '793':'Housekeeping/Home Services',
        '18':'Software Engineer',
        '41':'Pre-sales/Post-sales Technical Support Engineer',
        '131':'Hardware Engineer',
        '191':'Web Design/Production/Graphics/Art',
        '199':'Product Manager'
        }

    occu = occupationDict[occupation]
    if '/' in occu:
        occuList = occu.split('/')
        occu = occuList[0]
    res = educationDict[education]+ '-' + genderDict[gender]+ '-' +consumptionDict[consumption]+ '-' +occu
    return res
       

if __name__ == '__main__':
    
    # file = open('profiles.pkl','rb') 
    # profiles = pickle.load(file)

    # print(len(profiles))  # 现在是整整10W人
    # profileStrs = {}
    # ids = list(profiles.keys())
    # for id in ids:
    #     profileStrs[id] = turnInfoStr(profiles[id])
    
    # allv = list(profileStrs.values())
    # profileSet = set(allv)
    # print(len(profileSet))  # 一共有23456种不同的profile
    
    # a = {}
    # for i in profileSet:
    #     a[i] = allv.count(i)
    # a = sorted(a.items(), key=lambda item:item[1], reverse=True)
    
    # with open('profileRank.pkl', 'wb') as f:
    #     pickle.dump(a, f)
    
    
    file = open('profileRank.pkl','rb') 
    sortProfiles = pickle.load(file)
    sortProfilesUsingWord = []
    for item in sortProfiles:
        sen, num = item
        profile = transfer(sen)
        sortProfilesUsingWord.append((profile, num))
        
        
    printSeq(sortProfilesUsingWord[:200])  # 看看前一百种的profile的信息.
    
    # with open('profileRankWord.pkl', 'wb') as f:
    #     pickle.dump(sortProfilesUsingWord, f)

    # {"age":0,"education":n,"gender":n,"consumption":n,"occupation":"110067,66,0.000"}