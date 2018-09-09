import json
import boto3
import newspaper
from newspaper import news_pool

def main(event, context):
    papers = []
    sources = [('cnn pol', 'https://www.cnn.com/politics')]
    for paper_source in sources:
        paper_temp = newspaper.build(paper_source[1], memoize_articles=False)
        papers.append((paper_source[0], paper_temp))
        print("total size for %s is %d" % (paper_source[0], paper_temp.size()))

    papers_news_pool = [x[1] for x in papers]
    news_pool.set(papers_news_pool, threads_per_source=3)
    news_pool.join()

    print("am i even here?")
    total_added = 0
    for paper in papers:
        paper_name = paper[0]
        print("Going to: " + paper_name)
        print("Total papers to get from this source: %d" % (paper[1].size()))
        for article in paper[1].articles:
            article_url = article.url
            article.download()
            article.parse()
            article_text = article.text
            if 'opinion' not in article_url and 'video' not in article_url:
                total_added += 1
                dict_val = {"url": article_url, "text": article_text, "news_name": paper_name}
                print("Adding this article: %s, total added so far is: %d" % (article.title, total_added))
                s3 = boto3.resource('s3')
                obj = s3.Object('econ-dev-network-articles', 'article' + str(total_added) + '.json')
                obj.put(Body=json.dumps(dict_val))
                print("total added in final is: %d" % (total_added))
if __name__ == "__main__":
    main('','')

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
