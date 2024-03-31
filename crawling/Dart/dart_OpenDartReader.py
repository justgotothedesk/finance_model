import OpenDartReader
import pandas as pd
import json

# Dart API KEY 입력
API_KEY = 'YOUR API KEY'
dart = OpenDartReader(API_KEY)

with open('./ODR_type.json', 'r', encoding = 'utf-8') as f:
    item = json.load(f)
    report_list = item["사업보고서 형식"]
    event_list = item["주요사항보고서 형식"]
    reg_list = item["증권신고서 형식"]

# 회사명으로 상장이후 모든 공시 목록 가져오기
public_list = dart.list('삼성전자')
# dart.list('005930') <- 종목코드로도 접근 가능

# 공시정보 - 기업 개황
corp = dart.company('005930')
xml_text = dart.document('20240327001155')

# 사업보고서 추출
n = 1
for r in report_list :
    if n % 6 == 0 : print()
    print(r, end = "   ")
    n += 1

Report = dart.report('005930', '배당', 2022)

# 상장기업 재무정보
finance = dart.finstate('삼성전자', 2022)

# 재무제표 XBRL 원본 파일 저장 (삼성전자 2022 사업보고서)
# dart.finstate_xml('20230307000542', save_as='삼성전자_2022_사업보고서_XBRL.zip')

# 지분공시
# 대량보유 상황보고
share = dart.major_shareholders('005930')

# 임원ㆍ주요주주 소유보고
major_share = dart.major_shareholders('005930')

# 주요사항보고서
# dart.event(corp, event, start = None, end = None)
n = 0
for event in event_list :
    if n % 6 == 0 : print()
    print(event, end = "   ")
    n += 1

Event = dart.event('052220', "자기주식처분", start = '1970-01-01', end = '2023-01-01')

# 증권신고서
reg = dart.regstate('사조대림', '합병')

# 삼성전자 2021년 사업보고서
rcp_no = '20220308000798'
samsung_report = dart.sub_docs(rcp_no)