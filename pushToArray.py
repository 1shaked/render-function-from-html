

from bs4 import BeautifulSoup, element
# from lxml.html import parse
import json
import HtmlConvertar as h

h.HtmlConverter(492085)
'''
<p>this is p with <a>a tag</a></p>
<p>this is p with <a>a tag inside more <p>p tag</p></a></p>
'''
html_c = '''
<body>    
    <div>text and <p> here is p </p> with more</div>
</body>
'''
# html_c = '<body><div>text and <p> here is p </p> with more</div></body>'


html_s = BeautifulSoup(html_c)
elsements_list :list = []
CONTENT :str= 'content'
TAG :str= 'tag'
ATTRS :str= 'attrs'

def pushToArray(elemnts, content :list= []):
    if type(elemnts) == element.NavigableString:
        if elemnts.string != '\n':
            if type(content) == list: 
                content[0][CONTENT].append(elemnts.string)
            elif type(content) == dict:
                content[CONTENT].append(elemnts.string)
    for el in elemnts.contents:
        if type(el) == element.NavigableString:
            if el.string != '\n':
                if type(content) == list:
                    content[0][CONTENT].append(el.string)
                elif type(content) == dict:
                    content[CONTENT].append(el.string)
        elif type(el) == element.Tag:
            elsements_list.append(el.name)
            if (len(content) == 0):
                content.append({TAG: 'XXX', CONTENT: [] })
            if len(el.contents) == 1 and type(el.contents[0]) == element.NavigableString:
                if type(content) == dict:
                    content[CONTENT].append({TAG: el.name,ATTRS: el.attrs, CONTENT: el.contents[0].string})
                elif type(content) == list:
                    content[0][CONTENT].append({TAG: el.name,ATTRS: el.attrs, CONTENT: el.contents[0].string})
            else:
                if type(content) == list:
                    content[0][CONTENT].append(pushToArray(el, {TAG: el.name,ATTRS: el.attrs, CONTENT: []})) 
                elif type(content) == dict:
                    content[CONTENT].append(pushToArray(el, {TAG: el.name,ATTRS: el.attrs ,CONTENT: []}))
            # content.append()
    return content


html = h.HtmlConverter(492085)

contnet = pushToArray(html.soup, [])
contnet = contnet[0][CONTENT][0][CONTENT][0][CONTENT]
print(contnet)
contnet
with open('contentXX.json', mode='w', encoding='utf-8') as f:
    string :str= json.dumps(contnet, indent=4, ensure_ascii=False)
    f.write(string) 