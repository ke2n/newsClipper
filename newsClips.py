# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from pymongo import MongoClient
import newsFunc
import urlparse
import feedparser
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

if len(sys.argv) != 2:
    print "argument error"
    sys.exit()

S_TYPE = sys.argv[1]

if S_TYPE.upper()=="GOOGLE":
    RSS_URL = 'https://news.google.co.kr/news?cf=all&hl=ko&pz=1&ned=kr&output=rss'
    RSS_SOURCE = S_TYPE.upper()
    RSS_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'
elif S_TYPE.upper()=="DAUM":
    RSS_URL = 'http://media.daum.net/rss/today/primary/all/rss2.xml'
    RSS_SOURCE = S_TYPE.upper()
    RSS_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'
else:
    print "type error"
    sys.exit()

SYS_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

#pymongo init
client = MongoClient('ds061076.mlab.com', 61076)
db = client["kein-db"]
db.authenticate('db_user', '1', source='kein-db')

#rss init
parsed_rss = feedparser.parse(RSS_URL)
rss_reg_date = datetime.strptime(parsed_rss.feed.published, RSS_DATE_FORMAT)
rss_reg_date = (rss_reg_date + timedelta(hours=9)).strftime(SYS_DATE_FORMAT)
current_date = datetime.now()

print current_date.strftime(SYS_DATE_FORMAT)

for post in parsed_rss.entries:
    str_to_date = datetime.strptime(str(post.published), RSS_DATE_FORMAT)
    formatted_date = (str_to_date + timedelta(hours=9)).strftime(SYS_DATE_FORMAT)

    find_rows = db.newsCollection.find({
        "rss_date": {"$gte": (current_date + timedelta(hours=-1)).strftime(SYS_DATE_FORMAT)},
        "source": RSS_SOURCE,
        "title": post.title
    })

    if find_rows.count()==0:
        post_article = newsFunc.getArticles(post.link)
        print RSS_SOURCE + " insert : " + post.title + " : " + formatted_date + " : " + post_article["source"] + "(" + str(len(post_article["text"])) + ")"

        db.newsCollection.insert_one({
            'url': post_article["link"],
            'title': post.title,
            'contents': post_article["text"],
            'image': post_article["image"],
            'date': formatted_date,
            'rss_date': rss_reg_date,
            'source': RSS_SOURCE
        })
    else:
        for row in find_rows:
            print RSS_SOURCE + " duplicate : " + post.title + " : " + str(row["_id"])
            # count duplicate news
            db.newsDuplCollection.update({"_id": row["_id"]}, {"$inc": {"count": 1}}, True)

print "\n"