from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import jieba.analyse
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# 设置停用词库
jieba.analyse.set_stop_words('static/stop_words.txt')

def extract_topic(text):
    # 创建一个文本解析器
    parser = PlaintextParser.from_string(text, Tokenizer("chinese"))
    # 创建一个摘要生成器
    summarizer = LsaSummarizer()
    # 生成摘要
    summary = summarizer(parser.document, 1)
    # 返回摘要的第一句
    return str(summary[0])

@csrf_exempt
def extract_keywords(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        file = request.FILES.get('file')
        if file:
            text = file.read().decode('utf-8')
        keywords = jieba.analyse.extract_tags(text, topK=10)
        topic = extract_topic(text)
        return render(request, 'display.html', {'keywords': keywords, 'topic': topic})
    else:
        return HttpResponse('请通过POST方法提交文本或文件')
