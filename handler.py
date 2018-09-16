import json
import boto3
from boto3 import client as boto3_client
from datetime import datetime
import newspaper
from newspaper import news_pool
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('newsTable')
print(table.item_count)
lambda_client = boto3_client("lambda")

def lambdaStarter(event, context):
    msg =  ['https://www.cnn.com/health', 'https://www.cnn.com/us', 'https://www.cnn.com/politics']
    for item in msg:
        invoke_response = lambda_client.invoke(FunctionName='numpy-test-dev-numpy', InvocationType='Event', Payload=json.dumps(item))
        print(invoke_response)

def main(event, context):
    paper = event
    papers = []
    paper_temp = newspaper.build(paper, memoize_articles=True)
    papers.append(('cnn', paper_temp))
    total_added = 0
    items = []
    for paper in papers:
        paper_name = paper[0]
        for article in paper[1].articles:
            article_url = article.url
            article.download()
            article.parse()
            article_text = article.text  
            title = article.title
            if 'opinion' not in article_url and 'video' not in article_url:
                total_added += 1
                dict_val = {"url": article_url, "title": title, "text": article_text, "news_name": paper_name}
                items.append(dict_val)
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(
                Item = {
                'url': item['url'],
                'title': item['title'],
                'text': item['text'],
            })
if __name__ == "__main__":
    main('https://www.cnn.com/health', "")

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration