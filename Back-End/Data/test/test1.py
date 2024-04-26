# Test1 : Dart 클래스 작동 여부 테스트

import Dart

Dart_class = Dart.Dart()
corp_list = Dart_class.getCorpList()
print("회사 리스트")
print(corp_list[88270])

corp_report_code = Dart_class.getReportCode(corp_list[88270])
print("공시보고서 코드")
print(corp_report_code)

corp_report_url = Dart_class.getReportURL(corp_report_code)
print("공시보고서 링크")
print(corp_report_url)

corp_report_data = Dart_class.getEveryReportData(corp_report_url)
print("사업보고서 크롤링 데이터")
print(corp_report_data)