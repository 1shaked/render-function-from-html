from flask import Flask
from convertor import HtmlConverter
from flask_cors import CORS, cross_origin
from flask import request
# import os
app = Flask(__name__)
cors = CORS(app)

@app.route('/', methods=['POST'])
@cross_origin()
def index(): # html_content is a string 
    html_content = request.form.get('html')
    try:
        html = HtmlConverter()
        html.initWithHtml(html_content)
        
        return {"success": "Successfully got render func.", "data": html.soupToJson() }
    except Exception as e:
        print(e)
        return {"error": "no article in this id" }


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80 )