from sklearn.feature_extraction.text import TfidfVectorizer
from konlpy.tag import Okt
import time

okt = Okt()

start = time.time()
doc_list = ['이준석 징계 논의 왜 시작되었나',
            '이준석 징계 논의 與 윤리위, 오는 22일 개최',
            '[속보] 이준석 징계 논의 국민의힘 윤리위, 모레 저녁 7시 개최',
            '국민의힘, 성상납 의혹 이준석 징계 논의한다',
            '국민의힘 윤리위, 오는 22일 이준석 대표 징계 심의',
            '이준석 "윤리위 참석 의사 밝혀…별다른 걱정은 안 해"(종합)']
# okt 실행 시 시간 소모가 가장 많음, 분산화 진행 필요
tfidf_vectorizer = TfidfVectorizer(min_df=1)
tfidf_matrix = tfidf_vectorizer.fit_transform(doc_list)
doc_similarities = (tfidf_matrix * tfidf_matrix.T)

print(doc_similarities.toarray()[0])

end = time.time()
print(end-start)
