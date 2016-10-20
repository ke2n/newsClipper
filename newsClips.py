# -*- coding: utf-8 -*-
import urllib2
from goose import Goose
from goose.text import StopWordsKorean
import newspaper
from bs4 import BeautifulSoup
import urlparse

# 본문 수집 메서드
def getArticles(url):
    resultMap = {
        "goose": getArticlesByGoose,
        "newspaper": getArticlesByNewspaper,
        "beautifulsoup": getArticlesBySoup
    }
    # url의 url형식(파라미터)일경우의 처리 (구글case)
    parsed = urlparse.urlparse(url)
    if url.rfind('url')!=-1: url = urlparse.parse_qs(parsed.query)['url'][0]

    # 각 수집메서드에 대해 iteration함(정상적으로 수집됐다 판단되면 break)
    for key in resultMap:
        returnVal = resultMap.get(key)(url)
        returnVal['source'] = key
        if isWellClipped(returnVal): break

    return returnVal

# 줄수정 관련 메서드
def replaceLine(text):
    if isinstance(text, str):
        return text.replace("\n\n", "\n")
    else:
        return text

# 제대로 수집했는지 체크
def isWellClipped(article, CONDITION=20):
    if article is None or article["text"] is None: return False
    if len(article["text"])>CONDITION: return True
    else: return False

# Goose를 이용하여 본문 수집
def getArticlesByGoose(url):
    g = Goose({'stopwords_class': StopWordsKorean})
    article = g.extract(url=url)

    try:
        image_src = article.top_image.src
    except AttributeError as e:
        image_src = None

    text_val = replaceLine(article.cleaned_text)

    returnVal = {
        "link": url,
        "text": text_val,
        "image": image_src
    }

    return returnVal

# newspaper를 이용하여 본문 수집
def getArticlesByNewspaper(url):
    article = newspaper.Article(url)
    article.download()
    article.parse()
    
    returnVal = {
        "link": url,
        "text": replaceLine(article.text),
        "image": article.top_image
    }
    return returnVal

# soup를 이용하여 본문 수집
def getArticlesBySoup(url):
    try:
        opener = urllib2.build_opener()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:10.0.1) Gecko/20100101 Firefox/10.0.1'}
        opener.addheaders = headers.items()

        res = opener.open(url)
        source = res.read()
    except IOError as e:
        print "IOError : " + url + "\n" + str(e)
        return None
    except TypeError as e:
        print "TypeError : " + url + "\n" + str(e)
        return None

    soup = BeautifulSoup(source)
    selectMap = {
        "join": soup.find(attrs={'class': 'article_body'}),
        "zdnet": soup.find(id='content')
    }

    for key in selectMap:
        div = selectMap.get(key)
        if div: break

    for br in div.find_all("br"):
        br.replace_with("\n")

    returnText = div.text
    returnVal = {
        "link": url,
        "text": replaceLine(returnText),
        "image": None
    }
    return returnVal