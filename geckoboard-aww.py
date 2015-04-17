from flask import Flask, jsonify
import requests
import os
import random

app = Flask(__name__)


@app.route('/')
def get_awws():
    ua = {'User-Agent': 'Geckoboard awws by /u/episome'}
    awws_page1 = requests.get("http://www.reddit.com/r/aww.json", headers=ua).json()
    awws_page2 = requests.get("http://www.reddit.com/r/aww.json?after=%s" % (awws_page1['data']['after']), headers=ua).json()

    awws = random.sample(parse_awws(awws_page1) + parse_awws(awws_page2), 10)
    awws = [{"text": "<img src=\"%s\" style=\"width:200px\">" % (url)} for url in awws]
    return jsonify({"item": awws})


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
