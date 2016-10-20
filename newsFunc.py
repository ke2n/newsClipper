from goose import Goose
from goose.text import StopWordsKorean
import newspaper
import urlparse


def getArticles(url):
    parsed = urlparse.urlparse(url)

    if url.rfind('url')!=-1:
        url = urlparse.parse_qs(parsed.query)['url'][0]
    else:
        url=url

    g = Goose({'stopwords_class': StopWordsKorean})
    article = g.extract(url=url)

    try:
        image_src = article.top_image.src
        
    except AttributeError as e:
        image_src = None

    text_val = article.cleaned_text.replace("\n\n", "\n")

    if len(text_val) > 10:
        returnVal = {
            "link": url,
            "text": text_val,
            "image": image_src
        }
    else:
        returnVal = getArticles_new(url)

    return returnVal

def getArticles_new(url):
    article = newspaper.Article(url)
    article.download()
    article.parse()
    
    returnVal = {
        "link": url,
        "text": article.text.replace("\n\n", "\n"),
        "image": article.top_image
    }
    return returnVal
