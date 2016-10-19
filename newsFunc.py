from goose import Goose
from goose.text import StopWordsKorean
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

    returnVal = {
        "link": url,
        "text": article.cleaned_text.replace("\n\n", "\n"),
        "image": image_src
    }
    return returnVal