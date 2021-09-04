
import requests
from bs4 import BeautifulSoup, element
import json
from copy import deepcopy

className :str= '@class'
video :str = 'video'
div :str= 'div'
img :str= 'img'
video_class :str = 'a7video IVideo'
youtube :str= 'youtube-component'
style :str = '@style'
invisible_el :str= "display: none"
attributes_to_delete :list = [className, style, '@onclick', '@data-player']
REMOVE_ATTRIBUTES = ['class','lang','language','onmouseover','onmouseout','script','style','font', 'onclick', 'data-player']

class HtmlConverter: 
    def __init__(self, articleId :int):
        
        self.articleId = articleId
        self.html :str= ''
        self.json :dict = {}
        

        html_string :str= self.getHtmlContent()
        self.parseHtmlContent(html_string)
        # self.removeUnusedParams()
        self.saveToFile()

    def getHtmlContent(self):
        url :str= f'https://www.inn.co.il/Generic/NewApi/Item?Type=0&item={self.articleId}'
        respond :dict= requests.get(url).json()
        return respond['content']
        

    def parseHtmlContent(self, html_string :str):
        soup :BeautifulSoup =BeautifulSoup(html_string, "html.parser")
        tags_to_delete :list[str] = ['head', 'style','script']
        # deleting the tags
        for tag in tags_to_delete:
            els = soup.select(tag)
            for el in els:
                el.extract()

        for viedos in soup.find_all("div", class_="a7video IVideo"): # [0].contents
            for img in viedos:
                if type(img) == element.Tag:
                    if 'video' in img.attrs['class']:
                        viedos['poster'] = img.attrs['src']

                img.extract()
        
        
        for img in soup.select('img'):
            if ('style' in img.attrs):
                if 'display: none' in img.attrs['style']:
                    img.extract()
                    continue
            if 'class' in img.attrs:
                if ('video' in img.attrs['class']) or ('play' in img.attrs['class']):
                    img.extract()


        for v in soup.find_all("div", class_="a7video IVideo"): 
            v.name = 'youtube-component'

        
        
        for tag in soup.find_all(lambda tag: len(tag.attrs) > 0):
            for tag_to_remove in REMOVE_ATTRIBUTES:
                if tag_to_remove in tag.attrs:
                    del tag[tag_to_remove]
            # tag.attrs = [(key,value) for key,value in tag.attrs if key not in REMOVE_ATTRIBUTES]

        self.soup :BeautifulSoup = soup
        self.html = soup.body.prettify(formatter='html')
        self.html = self.html.replace('\n', '').replace('<!DOCTYPE html>', '')


    def removeUnusedParams(self):
        body = self.json['html']['body']
        
        print('removing unused params....')


    def saveToFile(self):
        with open('test.json', mode='w', encoding='utf8') as f:
            f.write(json.dumps(self.json, indent=4, ensure_ascii=False))


