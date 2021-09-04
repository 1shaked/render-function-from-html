from bs4 import BeautifulSoup, element
import json

attributes_to_delete :list = ['@class', '@style', '@onclick'] # '@data-player'
REMOVE_ATTRIBUTES: list= ['class','lang','language','onmouseover','onmouseout','script','style','font', 'onclick', 'data-player', 'height', 'width', 'data-bind']
RESERVED_PROPERTIES: dict= { 'iframe': ['width', 'height'] }
CONTENT :str= 'content'
TAG :str= 'tag'
ATTRS :str= 'attrs'
class HtmlConverter: 
    def __init__(self):
        pass
        
    def initWithHtml(self, flash: str):
        self.parseHtmlContent(flash)

    def parseHtmlContent(self, content = None, ads = True):
        soup :BeautifulSoup = BeautifulSoup(content, "html.parser")
        tags_to_delete :list[str] = ['head', 'style','script', 'noscript', 'link'] # here are list of tags you want to delete
        # deleting the tags
        for tag in tags_to_delete:
            els = soup.select(tag)
            for el in els:
                el.extract()
        
        elements_soup: list = soup.find_all(lambda tag: len(tag.attrs) > 0)
        for tag in elements_soup:
            # region a tag
            if tag.name == 'a': # exaple of auto rename tag to components
                if 'https://twitter.com' in tag.attrs['href']:
                    tag.name = 'twitter-component'
            # endregion 
            for tag_to_remove in REMOVE_ATTRIBUTES:
                if tag_to_remove in tag.attrs:
                    if tag.name in RESERVED_PROPERTIES and tag_to_remove in RESERVED_PROPERTIES[tag.name]:
                        continue
                    del tag[tag_to_remove]
            # tag.attrs = [(key,value) for key,value in tag.attrs if key not in REMOVE_ATTRIBUTES]
        self.soup :BeautifulSoup = soup
        if soup.body is not None:
            self.html = soup.body.prettify(formatter='html')
            self.html = self.html.replace('\n', '').replace('<!DOCTYPE html>', '')
        else:
            self.html = str(soup)

    def soupToJson(self):
        res = pushToArray(self.soup, [])
        with open('test.json', 'w') as f: # if you want to save the result in json file
            f.write(json.dumps(res, indent=4, ensure_ascii=False))
        return res[0] # TODO: remove the object at the start so you getting object and not array

    def saveToFile(self):
        with open('test.json', mode='w', encoding='utf8') as f:
            f.write(json.dumps(self.json, indent=4, ensure_ascii=False))


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
                content.append({TAG: 'div', CONTENT: [] })
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
    return content # 

def printTypesRecursive(obj): # getting the object from pushToArray method to see all the types
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



    
    