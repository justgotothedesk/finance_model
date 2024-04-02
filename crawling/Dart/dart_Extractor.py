import OpenDartReader
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

class Dart_Extractor:
    # 크롬 드라이버와 크롬 버전 충돌 발생 시, 동일 버전의 크롬 드라이버 경로 입력
    # CHROME_DRIVER_PATH = 'YOUR_PATH'

    def __init__(self, file: str):
        with open('./dart_api_key.txt', 'r') as f :
            API_KEY = f.readline()
        self.dart = OpenDartReader(API_KEY)

    # 공시보고서 코드를 회사마다 dictionary에 담아서 return
    def getReportCode(self, comps: list): 
        report_codes = {}

        for comp in comps:
            # dart.list 함수 호출했을 때, data 없는 경우에도 exception raise하지 않고 {"status":"013","message":"조회된 데이타가 없습니다."} 출력하는 오류 있습니다.
            try: 
                report_list = self.dart.list(comp, start = '2023-01-01', end = '2024-03-28', kind = 'A')
                corp_code = report_list['corp_code'][0]
                report_codes[corp_code] = []

                for report_code in report_list['rcept_no'] :
                    report_codes[corp_code].append(report_code)
            
            except:
                continue
        
        return report_codes
    
    # report_list 받아서 공시보고서 url 생성
    def getReportURL(self, report_list: dict):
        report_url = {}

        for corp_code in report_list.keys():
            report_url[corp_code] = {}

            for report_num in report_list[corp_code] :
                report_url[corp_code][report_num] = {}

                for idx, row in self.dart.sub_docs(report_num).iterrows():
                    report_url[corp_code][report_num][row['title']] = row['url']
            
        return report_url
    
    # report_url_list 받아서 url에서 text 가져옴
    def getReportData(self, report_url: dict): 
        
        report_data = {}

        # 크롬 드라이버와 크롬 버전이 충돌하여, 직접 크롬 드라이버의 주소를 기입할 경우에 아래의 코드 사용
        # driver = webdriver.Chrome(Service(executable_path=CHROME_DRIVER_PATH))

        driver = webdriver.Chrome()

        # 사업보고서 결과물 읽기
        fp = open('./crawling_result.txt', 'a', encoding = 'utf-8')

        for corp_code in report_url.keys():
            report_data[corp_code] = {}

            for report_num in report_url[corp_code]:
                report_data[corp_code][report_num] = {}

                for title in report_url[corp_code][report_num]:
                    url = report_url[corp_code][report_num][title]
                    report_data[corp_code][report_num][title] = []
                    fp.write(title + "\n")

                    driver.get(url)
                    time.sleep(2)

                    report_string = driver.find_element(By.TAG_NAME, 'body').text
                    lines = report_string.splitlines()

                    for line in lines:
                        # 빈 줄 삭제
                        if len(line) < 1:
                            continue
                        report_data[corp_code][report_num][title].append(line + "\n")
                        fp.write(line + "\n")

                    fp.write("\n")

        driver.quit()

        return report_data
    
    # 보고서 내의 원하는 목차만을 추출
    def getReportData2(self, report_url: dict):
        # 보고서에서 뽑아올 목차 담는 list
        indices = []

        f = open('./index.txt', 'r', encoding = 'utf-8')
        lines = f.readlines()
        for line in lines :
            indices.append(line.strip())
        f.close()

        f = open('./corp_name_code_mapping.txt', 'r', encoding='utf-8')
        mapping = dict()

        for line in f.readlines():
            a = line.strip().split()
            mapping[a[0]] = a[1]
        f.close()

        # 크롬 드라이버와 크롬 버전이 충돌하여, 직접 크롬 드라이버의 주소를 기입할 경우에 아래의 코드 사용
        # driver = webdriver.Chrome(Service(executable_path=CHROME_DRIVER_PATH))

        driver = webdriver.Chrome()

        report_data = {}

        for corp_code in report_url.keys():
            corp_name = mapping[corp_code]
            report_data[corp_name] = {}

            for report_num in report_url[corp_code]:
                report_data[corp_name][report_num] = {}

                for title in report_url[corp_code][report_num]:
                    # 뽑아야 할 목차인지 확인
                    extract = False
                    
                    for index in indices:
                        if index in title:
                            extract = True

                    if extract:
                        report_data[corp_name][report_num][title] = []
                        url = report_url[corp_code][report_num][title]

                        driver.get(url)
                        time.sleep(2)

                        report_string = driver.find_element(By.TAG_NAME, 'body').text

                        lines = report_string.splitlines()

                        for line in lines:
                            if len(line) < 1:
                                continue

                            report_data[corp_name][report_num][title].append(line + '\n')

        driver.quit()

        return report_data