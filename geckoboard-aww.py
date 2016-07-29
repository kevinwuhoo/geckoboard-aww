from flask import Flask, jsonify, g
import requests
import os
import random
import redis


app = Flask(__name__)
IMAGE_SET = 'images'


@app.route('/')
def get_awws():

    db = connect_redis()

    # fetch more on every 10th request or if less than 100 images stored
    if random.random() < 0.1 or db.scard(IMAGE_SET) < 100:
        images = get_subreddit_submissions('aww') + get_subreddit_submissions('animalsbeingderps')
        db.sadd(IMAGE_SET, *images)

    awws = db.srandmember(IMAGE_SET, 10)
    awws = [{"text": "<img src=\"%s\" style=\"width:200px\">" % (url)} for url in awws]

    # if more than 1000 images stored, randomly remove 0-1000 elements
    if db.scard(IMAGE_SET) > 1000:
        remove_randomly = db.srandmember(IMAGE_SET, int(random.random() * 1000))
        db.srem(IMAGE_SET, *remove_randomly)

    return jsonify({"item": awws})


def get_subreddit_submissions(subreddit):
    ua = {'User-Agent': 'Geckoboard awws by /u/episome'}
    page1 = requests.get("http://www.reddit.com/r/{}.json".format(subreddit), headers=ua).json()
    page2 = requests.get("http://www.reddit.com/r/{}.json?after={}".format(subreddit, page1['data']['after']), headers=ua).json()

    return parse_awws(page1) + parse_awws(page2)


def parse_awws(awws):
    valid_awws = []

    for aww in awws['data']['children']:
        if not 'url' in aww['data']:
            return

        if aww['data']['url'].endswith(('png', 'gif', 'jpg', 'jpeg')):
            valid_awws.append(aww['data']['url'])

        if aww['data']['url'].endswith('gifv'):
            valid_awws.append(aww['data']['url'].replace('gifv', 'gif'))

    return valid_awws


def connect_redis():
    if not hasattr(g, 'redis'):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        g.redis = redis.from_url(redis_url)

    return g.redis

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
