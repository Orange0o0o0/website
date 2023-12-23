import torch.cuda
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import jieba.analyse
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import win32com.client
import json
import pythoncom
import os
import tempfile


def read_doc(file):
    pythoncom.CoInitialize()
    word = win32com.client.Dispatch("Word.Application")
    # 创建一个临时文件
    temp = tempfile.NamedTemporaryFile(delete=False)
    # 将上传的文件保存到临时文件中
    for chunk in file.chunks():
        temp.write(chunk)
    temp.close()
    # 使用临时文件的路径打开文件
    doc = word.Documents.Open(temp.name)
    text = doc.Range().Text
    doc.Close(False)
    word.Quit(False)
    # 删除临时文件
    os.unlink(temp.name)
    return text



from docx import Document

def read_docx(file):
    doc = Document(file)
    return " ".join([paragraph.text for paragraph in doc.paragraphs])

from PyPDF2 import PdfReader

def read_pdf(file):
    reader = PdfReader(file)
    return " ".join([page.extract_text() for page in reader.pages])

# 设置停用词库
jieba.analyse.set_stop_words('static/stop_words.txt')

def extract_topic(text):
    # 创建一个文本解析器
    parser = PlaintextParser.from_string(text, Tokenizer("chinese"))
    # 创建一个摘要生成器
    summarizer = LsaSummarizer()
    # 生成摘要
    summary = summarizer(parser.document, 1)
    # 如果摘要为空，返回一个空字符串
    if not summary:
        return ""
    # 否则，返回摘要的第一句
    return str(summary[0])

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def summarize_text(text):
    # 加载预训练的T5模型和对应的分词器
    tokenizer = AutoTokenizer.from_pretrained("t5-base")
    model = AutoModelForSeq2SeqLM.from_pretrained("t5-base")

    # 使用分词器处理输入文本
    inputs = tokenizer(text, truncation=True, max_length=512, return_tensors="pt")

    # 使用模型进行预测
    summary_ids = model.generate(inputs["input_ids"])

    # 解码生成的摘要
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)

    return summary



@csrf_exempt
def extract_keywords(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        file = request.FILES.get('file')
        if file:
            if file.name.endswith('.doc'):
                text = read_doc(file)
            elif file.name.endswith('.docx'):
                text = read_docx(file)
            elif file.name.endswith('.pdf'):
                text = read_pdf(file)
            else:
                try:
                    text = file.read().decode('utf-8')
                except Exception:
                    text = ""  # 或者你可以设置一个其他的默认值
        keywords_with_weights = jieba.analyse.extract_tags(text, topK=10, withWeight=True)
        keywords, keyword_weights = zip(*keywords_with_weights)
        topic = extract_topic(text)
        summary = summarize_text(text)
        return render(request, 'display.html',
                      {'keywords': keywords, 'topic': topic, 'keyword_weights': json.dumps(keyword_weights),
                       'chart_keywords': json.dumps(keywords), 'summary': summary})
    else:
        return HttpResponse('请通过POST方法提交文本或文件')


