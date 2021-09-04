from flask import Flask, request
from convertor import HtmlConverter, handleFlashes
from flask_cors import CORS, cross_origin
# import os
import requests as r
app = Flask(__name__)
cors = CORS(app)

@app.route('/<int:post_id>')
@cross_origin()
def index(post_id):
    print(post_id)
    try:
        html = HtmlConverter()
        html.initWithArticle(int(post_id))
        html.soupToJson()
        return {"success": "Successfully got article.", "data": html.respond }
    except Exception as e:
        print(e)
        return {"error": "no article in this id" }

import json
@app.route('/api/')
@cross_origin()
def api_get():
    path_args = request.args.get('path')
    try:
        BASE_URL: str= 'https://www.inn.co.il/'
        res = r.get(BASE_URL + path_args)
        is_flash = 'Generic/NewApi/Cat?type=10'.lower() in path_args.lower()
        if is_flash:
            respond = handleFlashes(res.json())
            return respond
        return res.json()
    except Exception as e:
        print(e)
        return {"error": "no article in this id" }




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80 )