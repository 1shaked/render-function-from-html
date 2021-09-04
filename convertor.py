import requests
from bs4 import BeautifulSoup, element
import json
from json import loads
className :str= '@class'
video :str = 'video'
div :str= 'div'
img :str= 'img'
video_class :str = 'a7video IVideo'
youtube :str= 'youtube-component'
style :str = '@style'
invisible_el :str= "display: none"
IFRAME: str= 'iframe'
attributes_to_delete :list = [className, style, '@onclick'] # '@data-player'
REMOVE_ATTRIBUTES: list= ['class','lang','language','onmouseover','onmouseout','script','style','font', 'onclick', 'data-player', 'height', 'width', 'data-bind']
RESERVED_PROPERTIES: dict= { IFRAME: ['width', 'height'] }
SRC: str = 'src'
DATA_SRC = 'data-src'
CONTENT :str= 'content'
TAG :str= 'tag'
ATTRS :str= 'attrs'
BASE_URL: str = 'https://www.inn.co.il/Generic/NewApi/Item?Type=0&item='
DATA_PLAYER: str = 'data-player'
youtube_component = 'youtube-component'
class HtmlConverter: 
    def __init__(self):
        pass
        
    def initWithFlash(self, flash: str):
        self.parseHtmlContent(flash)
        
    def initWithArticle(self, articleId: int):
        self.articleId = articleId
        self.html :str= ''
        self.json :dict = {}
        self.respond: dict= {}

        self.getHtmlContent()
        self.parseHtmlContent()
    
    def getHtmlContent(self):
        url :str= f'{BASE_URL}{self.articleId}'
        self.respond :dict= requests.get(url).json()

    def parseHtmlContent(self, content = None, ads = True):
        if content:
            soup :BeautifulSoup = BeautifulSoup(content, "html.parser")
        else:
            soup :BeautifulSoup = BeautifulSoup(self.respond[CONTENT], "html.parser")
        tags_to_delete :list[str] = ['head', 'style','script', 'noscript', 'link']
        # deleting the tags
        for tag in tags_to_delete:
            els = soup.select(tag)
            for el in els:
                el.extract()
        
        elements_soup: list = soup.find_all(lambda tag: len(tag.attrs) > 0)
        for tag in elements_soup:
            # region a tag
            if tag.name == 'a':
                if 'https://twitter.com' in tag.attrs['href']:
                    tag.name = 'twitter-component'
            # endregion 
            # region audio tag
            elif tag.name == 'audio':
                print(tag.attrs[DATA_PLAYER]) # {"type":3,"id":2088396,"title":"סנונית ראשונה? עו\\"ד פאלק","url":"a7radio/misc/audio/21/jan/falk27-1.mp3","image":0,"author":"","date":"2021-01-27T15:00:48","credit":"צילום: ערוץ 7"} 
                data_player = loads(tag.attrs[DATA_PLAYER])
                tag.name = 'audio-component'
                required_attrs = ['id', 'title', 'credit']
                for attrs in required_attrs:
                    if attrs in data_player:
                        tag.attrs[attrs] = data_player[attrs]
            # endregion
            # region ifrem
            elif tag.name == IFRAME:
                if 'youtube' in tag.attrs[SRC]:
                    id_youtube = tag.attrs[SRC].split('/')[-1]
                    tag.name = youtube_component
                    tag.attrs['vid'] = id_youtube
                    del tag.attrs['src']
                    print(tag.attrs, tag.attrs.keys())
                    
                elif "googletagmanager" in tag.attrs[SRC]:
                    tag.extract()
            # endregion
            # region videos tag
            elif tag.name == 'div' and 'class' in tag.attrs and 'a7video' in tag.attrs['class'] and 'IVideo' in tag.attrs['class']:
                data_player = tag.attrs[DATA_PLAYER]
                print(data_player)
                for img in tag:
                    if type(img) == element.Tag:
                        if 'video' in img.attrs['class']:
                            tag['poster'] = img.attrs['src']

                    img.extract()
                if 'mp4' in tag.attrs['data-src']:
                    tag.name = 'video-component'
                    data_player = loads(tag.attrs[DATA_PLAYER])
                    # fields: list = ['credit', 'date', 'title', 'author']
                    tag.attrs['credit'] = data_player['credit']
                    tag.attrs['alt'] = data_player['title']
                else:
                    tag.name = youtube_component
                    if tag.attrs['data-src']:
                        id_youtube = tag.attrs['data-src'].split('/')[-1]
                        tag.attrs["vid"] = id_youtube
                        del tag.attrs['src']
                try:
                    tag.parent.next_sibling.next_sibling.extract()
                except Exception as e:
                    print(e)
            # endregion
            # region img tag
            elif tag.name == 'img':
                if ('style' in tag.attrs):
                    if 'display: none' in tag.attrs['style']:
                        tag.extract()
                        continue
                if 'class' in tag.attrs:
                    if ('video' in tag.attrs['class']) or ('play' in tag.attrs['class']):
                        tag.extract()
                        continue
                
                img_details = tag.next_sibling
                tag.name = 'img-component'
                if img_details != None:
                    credit_div = img_details.find("div", {"class": "ImageCredit"})
                    tag.attrs[SRC] = tag.attrs[SRC].split('/')[-1].split('.')[0] # get the id from 'path/to/id.png' => 'id.png' => id call flow
                    if 'class' in img_details.attrs and 'ImageDesc' in img_details.attrs['class']:
                        tag.attrs["alt"] = self.getImggeAlt(img_details) # str(img_details.contents[0]) or str(img_details.text) # credit
                        tag.attrs["credit"] = credit_div.text.replace('\n', '') or img_details.text # credit
                        img_details.extract()
            # endregion
            for tag_to_remove in REMOVE_ATTRIBUTES:
                if tag_to_remove in tag.attrs:
                    if tag.name in RESERVED_PROPERTIES and tag_to_remove in RESERVED_PROPERTIES[tag.name]:
                        continue
                    del tag[tag_to_remove]
            # tag.attrs = [(key,value) for key,value in tag.attrs if key not in REMOVE_ATTRIBUTES]
        self.soup :BeautifulSoup = soup
        if ads:
            self.addAds()
        if soup.body is not None:
            self.html = soup.body.prettify(formatter='html')
            self.html = self.html.replace('\n', '').replace('<!DOCTYPE html>', '')
        else:
            self.html = str(soup)

    def soupToJson(self):
        self.respond['Content2'] = pushToArray(self.soup, [])[0][CONTENT][0][CONTENT][0][CONTENT] # TODO: remove nesting so many objects (there is the default XXX and body and then main div)

    def saveToFile(self):
        with open('test.json', mode='w', encoding='utf8') as f:
            f.write(json.dumps(self.json, indent=4, ensure_ascii=False))

    def addAds(self):
        temp_soup: BeautifulSoup = BeautifulSoup()
        amount_of_paragraphs = len(self.soup.body.contents)
        counter = 1
        for ads_number in range(1, amount_of_paragraphs , 4 ):
            t_name = 'ad-component'
            attrs  = { 'uid': counter }
            if counter % 2 == 0:
                t_name = 'taboola-component'
                attrs = {'category': "article", 'mode': "rbox-only-video", 'placement': "rbox-only-video", 'uid': counter}
            new_tag = temp_soup.new_tag(name=t_name, attrs=attrs)
            insert_position = ads_number + counter
            self.soup.body.contents.insert(insert_position, new_tag)
            counter += 1

    def getImggeAlt(self, tag):
        if (tag.contents[0]) == element.NavigableString:
            return str(tag.contents[0].string)
        return str(tag.text)
        



def pushToArray(elements, content :list= []):
    if type(elements) == element.NavigableString:
        if elements.string != '\n' and bool(elements.string.strip()):
            if type(content) == list: 
                content[0][CONTENT].append(str(elements.string))
            elif type(content) == dict:
                content[CONTENT].append(str(elements.string))
    for el in elements.contents:
        if type(el) == element.NavigableString:
            if el.string != '\n' and bool(el.string.strip()):
                if type(content) == list:
                    content[0][CONTENT].append(str(el.string))
                elif type(content) == dict:
                    content[CONTENT].append(str(el.string))
        elif type(el) == element.Tag:
            if (len(content) == 0):
                content.append({TAG: 'XXX', CONTENT: [] })
            if len(el.contents) == 1 and type(el.contents[0]) == element.NavigableString:
                if type(content) == dict:
                    content[CONTENT].append({TAG: el.name,ATTRS: el.attrs, CONTENT: str(el.contents[0].string)})
                elif type(content) == list:
                    content[0][CONTENT].append({TAG: el.name,ATTRS: el.attrs, CONTENT: str(el.contents[0].string)})
                else:
                    print(type(el))
            else:
                if type(content) == list:
                    content[0][CONTENT].append(pushToArray(el, {TAG: el.name,ATTRS: el.attrs, CONTENT: []})) 
                elif type(content) == dict:
                    content[CONTENT].append(pushToArray(el, {TAG: el.name,ATTRS: el.attrs ,CONTENT: []}))
                else:
                    print(type(el))
            # content.append()
    return content # 

def printTypesRecursive(obj):
    if type(obj) == list:
        for el in obj:
            printTypesRecursive(el)
    elif type(obj) == dict:
        for key in obj:
            printTypesRecursive(obj[key])
    elif type(obj) == str:
        return
    else:
        print(obj)
        print(type(obj))
        return type(obj)

def handleFlashes(flashes):
    for index, flash in enumerate(flashes['Items']):
        html = HtmlConverter()
        if flash['content']:
            html.parseHtmlContent(flash['content'], ads=False)
            res = pushToArray(html.soup, [{TAG: 'XXX', CONTENT: [] }])[0][CONTENT]
            flashes['Items'][index][CONTENT] = res
    return flashes


if __name__ == "__main__":
    html = HtmlConverter() #int(497178) 495011 494979 471064 496027 465835 495190 466498 468418 497178 471884
    html.initWithArticle(503161)
    html.soupToJson()
    import json
    printTypesRecursive(html.respond['Content2'])
    with open('test.json', mode='w') as f:
        f.write(json.dumps(
            {
                'html': html.html,
                'json': html.respond['Content2']
            }
            , indent=4, ensure_ascii=False))

    
    