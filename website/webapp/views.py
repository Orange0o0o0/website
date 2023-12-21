from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import jieba.analyse
from collections import Counter
from gensim import corpora, models

# 设置停用词库
jieba.analyse.set_stop_words('static/stop_words.txt')

def extract_topic(text):
    # 从文件中读取停用词
    with open('static/stop_words.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().splitlines()
    # 分词并去除停用词
    words = [word for word in jieba.cut(text) if word not in stop_words]
    # 创建语料库
    dictionary = corpora.Dictionary([words])
    corpus = [dictionary.doc2bow(words)]
    # 创建LDA模型
    lda = models.LdaModel(corpus, id2word=dictionary, num_topics=1)
    # 提取主题
    topics = lda.print_topics(num_words=5)
    return topics[0][1]


@csrf_exempt
def extract_keywords(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        file = request.FILES.get('file')
        if file:
            text = file.read().decode('utf-8')
        keywords = jieba.analyse.extract_tags(text, topK=10)
        topic = extract_topic(text)
        return HttpResponse('关键字：' + ', '.join(keywords) + '<br>' + '主题：' + topic)
    else:
        return HttpResponse('请通过POST方法提交文本或文件')