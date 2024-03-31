import pandas as pd
import json
import dart_Extractor

# 속도 개선을 위해서 temp_report_list와 temp_report_url에 크롤링을 하려는 기업과 주소를 미리 저장한 후 실행하였음.
# 따라서, temp_report_list와 temp_report_url가 없는 경우 주석을 해제하여 사용해야함.

# param : api key text file path
Extractor = dart_Extractor.Dart_Extractor('./dart_api_key.txt') 

companies = []

f = open('./kospi_top_30.txt', 'r', encoding = 'utf-8')
lines = f.readlines()

# KOSPI 상위 30개의 기업을 추출 목록으로 선정
for line in lines :
    companies.append(line.strip())


# 회사 고유코드 얻어오는 method <- report_list.json 파일 없을 때 사용
# report_list = a.getReportCode(companies) # param : 회사 리스트

# with open('./20230101_20240329_report_list.json', 'w', encoding = 'utf-8')  as f : # report list json 파일로 저장
#     json.dump(report_list, f, ensure_ascii=False, indent = '\t')

#이미 report_list.json 파일 있는 경우 사용
with open('./20230101_20240329_report_list.json', 'r', encoding = 'utf-8')  as f :
    report_list = json.load(f)

# 회사 고유코드로 사업보고서 url 가져오는 method <- report_url.json 파일 없을 때 사용
# report_url = a.getReportURL(report_list) # param : report num dict

# with open('./20230101_20240329_report_url.json', 'w', encoding = 'utf-8')  as f : # report url json 파일로 저장
#     json.dump(report_url, f, ensure_ascii=False, indent = '\t')

#이미 report_url.json 파일 있는 경우 사용
with open('./20230101_20240329_report_url.json', 'r', encoding = 'utf-8') as f :
    report_url = json.load(f)

report_data = Extractor.getReportData(report_url)

with open('./20230101_20240329_report_data.json', 'w', encoding = 'utf-8') as f :
    json.dump(report_data, f, ensure_ascii = False, indent = '\t')

# xml to json
# pip install xmltodict

# import xmltodict

# jsonString = json.dumps(xmltodict.parse(xml_text), indent='\t', ensure_ascii=False)

# print("\nJSON output(output.json):")
# print(jsonString)

# with open("xml_to_json.json", 'w', encoding='utf-8') as f:
#     f.write(jsonString)