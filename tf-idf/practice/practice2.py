from sklearn.feature_extraction.text import CountVectorizer
import time
from konlpy.tag import Okt
import scipy as sp


def dist_raw(v1, v2):
    delta = v1 - v2   # 벡터 사이의 거리를 구하기 위해 빼줌
    return sp.linalg.norm(delta.toarray())


start = time.time()
vectorizer = CountVectorizer(min_df=1)
t = Okt()
contents = ['이준석 징계 논의 與 윤리위, 오는 22일 개최',
            '[속보] 이준석 징계 논의 국민의힘 윤리위, 모레 저녁 7시 개최',
            '국민의힘, 성상납 의혹 이준석 징계 논의한다',
            '국민의힘 윤리위, 오는 22일 이준석 대표 징계 심의',
            '이준석 "윤리위 참석 의사 밝혀…별다른 걱정은 안 해"(종합)']
contents_tokens = [t.morphs(row) for row in contents]

contents_for_vectorize = []

for content in contents_tokens:
    sentence = ''  # 만들 문장 초기화
    for word in content:  # 단어 하나하나 뽑아서 공백과 합쳐주기
        sentence = sentence + ' ' + word
    contents_for_vectorize.append(sentence)

X = vectorizer.fit_transform(contents_for_vectorize)

new_post = ['이준석 징계 논의 어쩌다 시작되었나']
new_post_tokens = [t.morphs(row) for row in new_post]
new_post_vec = vectorizer.transform(new_post)
new_post_vec.toarray()

new_post_for_vectorize = []

for content in new_post_tokens:
    sentence = ''
    for word in content:
        sentence = sentence + ' ' + word

    new_post_for_vectorize.append(sentence)

best_doc = None
best_dist = 65535
best_i = None

num_samples, num_features = X.shape

for i in range(0, num_samples):
    post_vec = X.getrow(i)

    # 함수 호출
    d = dist_raw(post_vec, new_post_vec)

    print('== Post %i with dist=%.2f : %s' % (i, d, contents[i]))

    if d < best_dist:
        best_dist = d
        best_i = i

end = time.time()
print(end-start)
