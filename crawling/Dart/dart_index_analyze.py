import OpenDartReader
import pandas as pd
import json

with open('./dart_api_key.txt', 'r') as f :
    API_KEY = f.readline()
dart = OpenDartReader(API_KEY)

companies = []

# 코스피 시총 상위 30개 회사
f = open('./kospi_top_30.txt', 'r', encoding = 'utf-8')
lines = f.readlines()

for line in lines :
    companies.append(line.strip())

# 회사명, 보고서 번호를 담는 딕셔너리
# company_info[회사 코드][보고서 번호] 형태의 2차원으로 저장
company_info = {}
corp_code_mapping = {}

for comp in companies:    
    try:
        report_list = dart.list(comp, start = '2023-01-01', end = '2024-03-28', kind = 'A')
        corp_code = report_list['corp_code'][0]
        corp_code_mapping[corp_code] = comp
        company_info[corp_code] = []

        for report_code in report_list['rcept_no']:
            company_info[corp_code].append(report_code)

    except:
        continue

dictionary = dict()
n = 0

# company_info의 딕셔너리를 바탕으로 해당 보고서 목차의 url을 담는 딕셔너리
# company_info_url[회사 코드][보고서 번호][보고서 목차 제목] 형태의 3차원으로 저장
company_info_url = {}

for corp_code in company_info.keys():
    company_info_url[corp_code] = {}
    for report_num in company_info[corp_code] :
        company_info_url[corp_code][report_num] = {}
        for idx, row in dart.sub_docs(report_num).iterrows():
            company_info_url[corp_code][report_num][row['title']] = row['url']
            

for corp_code in company_info_url.keys():
    for report_number in company_info_url[corp_code].keys():
        n += 1
        for title in company_info_url[corp_code][report_number].keys():
            if title not in dictionary.keys():
                dictionary[title] = [1, []]
                dictionary[title][1].append(corp_code_mapping[corp_code])
            else :
                dictionary[title][0] += 1
                dictionary[title][1].append(corp_code_mapping[corp_code])

print(f"total # of report : {n}")
for key in dictionary.keys() :
    print(f"제목 : {key}, 목차 포함 수 : {dictionary[key][0]}")
    print(set(dictionary[key][1]))
    print()

data = {}
data["제목"] = []

for corp_name in corp_code_mapping.values():
    data[corp_name] = ['-' for _ in range(len(dictionary.keys()))]

# 회사 별, 사업 보고서의 형태가 다르기 때문에 목차 역시 다름
# 각 목차가 존재하면 *****로 저장, 그렇지 않으면 공백으로 저장
row = 0
for key in dictionary.keys():
    data["제목"].append(key)
    for corp in set(dictionary[key][1]):
        data[corp][row] = '★' * 5

    row += 1

df = pd.DataFrame(data)
df.set_index("제목", inplace = True)
df.head()

df.to_csv('./목차분석.csv')