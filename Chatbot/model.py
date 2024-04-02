from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
from llama_index.llms.openai import OpenAI
import chromadb
import os
import json

# chromadb collection 저장경로
DB_SAVE_PATH = 'CHROMADB_STORE_PATH'

# collection 이름
COLLECTION_NAME = 'whole_240331_0901_json'

# embedding model
EMBEDDING_MODLE = 'sentence-transformers/all-mpnet-base-v2'

# 추출된 파일 저장 경로(미리 데이터를 추출한 경우에만 사용
# DATA_PATH = 'DATA_PATH'

# 추출할 item들의 항목(default는 모두 선택)
EXTRACTED_ITEMS = [ "1", "1A", "1B", "2", "3", "4", "5", "6", "7", "7A",
                 	"8", "9", "9A", "9B", "10", "11", "12", "13", "14", "15"]

# GPT API KEY
try:
    with open('Chatbot/GPT_API_KEY.txt', 'r') as f:
        API_KEY = f.readline()
except FileNotFoundError:
    # 파일이 없을 경우 직접 입력
    API_KEY = input("GPT API KEY를 입력하세요: ")

# API_KEY = ''

# json에 해당 키 값 존재 유무
def is_json_key_present(json, key):
    try:
        buf = json[key]
    except KeyError:
        return False

    return True

# Edgar 데이터 문서화
def edgar(path: str, option: int):
    if os.path.exists(path):
        file_list = os.listdir(path)

    else :
        print(f'There is no \"{path}\" folder')
        exit()

    documents = []

    for file_name in file_list:
        file_path = os.path.join(path, file_name)

        with open(file_path, 'r', encoding = 'utf-8') as f:
            file = json.load(f)

        # field 값 설정 후 document화 하기
        file_name = file['company']+file['period_of_report']

        # title별로 문서화
        if option == 1:
            for items in EXTRACTED_ITEMS:
                if is_json_key_present(file,f'item_{items}') == False:
                    continue

                text = file[f'item_{items}']
                included_items = f'item_{items}'
                doc_id = 'EDGAR_'+file['filing_type']+'_'+file['cik']+'_'+file['period_of_report']+':'+included_items

                doc = Document(text = text,doc_id = doc_id, metadata = {'filename' : file_name, 'items' : included_items, 
                                                    'filing_type' : file['filing_type'], 'htm_filing_link' : file['htm_filing_link'], 'report_date' : file['period_of_report']  })
                documents.append(doc)

        # 사업보고서별로 문서화(전체 내용 반환)
        elif option == 2:
            text = ''
            included_items =''
            for items in EXTRACTED_ITEMS:
                if is_json_key_present(file,f'item_{items}') == False:
                    continue
                text += file[f'item_{items}']
                included_items += f'item_{items}, '

            included_items = included_items[0:-2]
            doc_id = 'EDGAR_'+file['filing_type']+'_'+file['cik']+'_'+file['period_of_report']+':'+included_items

            doc = Document(text = text,doc_id = doc_id, metadata = {'filename' : file_name, 'items' : included_items, 
                                                'filing_type' : file['filing_type'], 'htm_filing_link' : file['htm_filing_link'], 'report_date' : file['period_of_report']  })
            documents.append(doc)

    return documents

# Dart 데이터 문서화
def dart(path: str, option: int):
    if os.path.exists(path):
        file = os.listdir(path)[0]
    else:
        print(f'There is no \"{path}\" folder')
        exit()

    file_path = os.path.join(path, file)
    documents = []

    with open(file_path, 'r', encoding = 'utf-8') as f:
        data = json.load(f)

    # title별로 문서화
    if option == 1:
        # 회사명
        for corp_name in data.keys():
            # 보고서 번호
            for report_number in data[corp_name].keys():
                print(f"회사명 : {corp_name}, 보고서 번호 : {report_number}")
                # 보고서 하위 목차
                for title in data[corp_name][report_number].keys(): 
                    text = ""
                    file_name = corp_name + "_" + report_number + "_" + title
                    for element in data[corp_name][report_number][title] :
                        text += element

                    doc_id = "DART_" + corp_name + "_" + report_number + "_" + title
                    doc = Document(text = text, doc_id = doc_id, metadata = {'filename' : file_name, "corp_name" : corp_name,
                                                                                "report_number" : report_number, 'title' : title})
                    documents.append(doc)

    # 사업보고서별로 문서화(전체 내용 반환)
    elif option == 2:
        # 회사명
        for corp_name in data.keys():
            # 보고서 번호
            for report_number in data[corp_name].keys():
                print(f"회사명 : {corp_name}, 보고서 번호 : {report_number}")
                text = ""
                file_name = corp_name + '_' + report_number
                doc_id = "DART_" + corp_name + '_' + report_number
                # 보고서 하위 목차
                for title in data[corp_name][report_number].keys(): 
                    for element in data[corp_name][report_number][title] :
                        text += element

                doc = Document(text = text, doc_id = doc_id, metadata = {'filename' : file_name, "corp_name" : corp_name,
                                                                        "report_number" : report_number})
                documents.append(doc)

    return documents

def main():
    # API_KEY 와 LLM 세팅. 터미널에서도 수정 가능
    os.environ['OPENAI_API_KEY'] = API_KEY
    Settings.llm = OpenAI(model = 'gpt-4', temperature = 0)

    # vector embedding 저장 위치
    chroma_client = chromadb.PersistentClient(path = DB_SAVE_PATH)

    # vector embedding 담겨있는 collection 데이터 초기화 여부
    print(chroma_client.list_collections())
    i = input('Wanna clean collection ( database )? (y/n) : ')

    if i == 'y' or i == 'Y' or i == '1' or i == 'ㅛ':
        collection = chroma_client.get_collection(name = COLLECTION_NAME) # name 변수 할당 가능

        y = input('Are you sure? (y/n) : ')
        if y == 'y' or y == 'Y' or y == '1' or y == 'ㅛ':
            chroma_client.delete_collection(name = COLLECTION_NAME)
            print('Collection has been deleted.')

    # cosine 유사도 기반으로 데이터 저장(현재 사용 중인 모델인 HuggingFaceEmbeddings는 논문에서 존재하길래 사용한 임시 모델)
    collection = chroma_client.get_or_create_collection(name = COLLECTION_NAME,metadata={'hnsw:space' : 'cosine'})
    embed_model = LangchainEmbedding(
        HuggingFaceEmbeddings(model_name = EMBEDDING_MODLE)
    )

    # llamaindex에서 chromadb 다루기
    vector_store = ChromaVectorStore(chroma_collection = collection)
    storage_context = StorageContext.from_defaults(vector_store = vector_store)

    while True:
        print('Choose one')
        i = int(input('(1) Store from document data and get answer, (2) Get answer from existing vector : '))
        
        # 새로운 데이터를 문서화해서 저장 후 질문
        if i == 1:
            print('(1) selected')
            
            v = int(input('(1) Store separate by each items, (2) Store whole report : '))

            if v == 1:
                print('Separate by each items - selected')
            elif v == 2:
                print('Whole report - selected')
            else:
                print('Please choose \'1\' or \'2\'')
                continue

            documents = []

            while True:
                print('Which data do you want?')
                n = int(input("(1) Edgar, (2) Dart : "))
                if n == 1:
                    documents = edgar("data-edgar", v)
                    break
                elif n == 2:
                    documents = dart("data-dart", v)
                    break
                else:
                    print('Please choose \'1\' or \'2\'')
                    continue

            index = VectorStoreIndex.from_documents(
                documents, storage_context = storage_context, embed_model = embed_model
            )
            break

        # 이미 존재하는 데이터를 불러와서 질문
        if i == 2 :
            print('(2) selected')
            index = VectorStoreIndex.from_vector_store(
                vector_store,
                embed_model = embed_model,
            )
            break
        else:
            print('Please choose \'1\' or \'2\'')
            continue
    
    while True:
        option = int(input("(1) EDGAR mode, (2) DART mode : "))
        if option == 1:
            print("-------EDGAR mode-------")
            context = (
                'You are an assistant tasked with analyzing EDGAR SEC filings. It is important to provide clients with specific information, including precise examples and the current situation, to help them make informed investment decisions.',
                'You must respond in Korean, and if you cannot find an exact English equivalent, you may provide both the Korean and English terms.',
                'and provide as much information as you can.'
            )
            break
        elif option == 2:
            print("-------DART mode-------")
            context = (
                '너는 DART의 사업보고서를 분석해주는 조력자야. 너는 고객들에게 정확한 예시, 투자를 위한 정보를 가지고 싶어하는 고객을 위한 현상황 등의 자세한 정보를 제공해야해.',
                '답변은 한국어로 하고, 너가 아는대로 최대한 많은 정보를 자세하게 제공해줘'
            )
            break
        else:
            print('Please choose \'1\' or \'2\'')
            continue

    # LLM 모델에 프롬프트 전달
    chat_engine = index.as_chat_engine(
        chat_mode='context',
        system_prompt = context
    )

    while True:
        question = input("Message to Mo (Please enter \'q\' to quit) ~ ")
        if question == 'q' or question == 'Q' or question == 'ㅂ':
            break

        response = chat_engine.chat(question)

        # 답변 출력
        print(response)

if __name__ == '__main__':
    main()