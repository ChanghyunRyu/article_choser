import json
from flask import Flask, request, jsonify
import convertor

app = Flask(__name__)


@app.route('/crawl', methods=['POST'])
def crawl_content():
    response = {'success': False}

    paramaters = json.loads(request.get_data(), encoding='utf-8')
    title = paramaters['title']
    site = paramaters['site']
    url = paramaters['url']
    lan = paramaters['lan']
    content = convertor.extract_content(title, url, site, lan)
    if content is not None:
        response['result'] = content
        response['success'] = True
    return jsonify(response)


@app.route('/check')
def get_text():
    return "running server"


if __name__=='__main__':
    app.run(host='0.0.0.0', port='8081')
