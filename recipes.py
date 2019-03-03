from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys
import ssl
from measurement.measures import Volume
import nltk
from nltk import word_tokenize
from fractions import Fraction


ssl._create_default_https_context = ssl._create_unverified_context
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
url = 'https://www.allrecipes.com/recipe/18511/hash-brown-casserole-ii/?internalSource=hub%20recipe&referringContentType=Search' #will be given this
page = urlopen(url)
soup = BeautifulSoup(page, 'html.parser')
ingredients = []


class Step:
    def __init__(self, text):
        self.text = 'You ' + text

    def __parse__(self):
        global ingredients
        tokenized = word_tokenize(self.text)
        self.verbs = []
        tags = nltk.pos_tag(tokenized)
        #print(tags)
        self.step_ingreds = []
        for i in range(len(tokenized)):
            if tags[i][1].startswith('VB'):
                self.verbs.append(tags[i][0])
        for ing in ingredients:
            if ing[2] in self.text:
                self.step_ingreds.append(ing[2])


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def get_ingredients():
    checklist_items = soup.find_all(class_= 'checkList__line')[0:-3]
    global ingredients
    for item in checklist_items:
        text = item.text.strip()
        tokenized = word_tokenize(text)
        descriptor = []
        prep = []
        name = []
        sum = 0
        product = 1
        tags = nltk.pos_tag(tokenized)
        posn = 0
        for i in range(len(tags)):
            if tags[i][1] == 'CD' and tags[i + 1][1] != '(':
                sum += float(Fraction(tags[i][0]))
                posn = i
            elif tags[i][1] == 'CD' and tags[i + 1][1] == '(':
                product = float(Fraction(tags[i][0]))
                posn = i
            # elif tags[i][1].startswith('JJ'): #descriptor words
            #     descriptor.append(tags[i][0])
            # elif tags[i][1].startswith('VB'): #prep verbs
            #     prep.append(tags[i][0])
            # elif tags[i][1].startswith('NN'): #its a name
            #     name.append(tags[i][0])
        product = sum * product
        unit = tags[posn + 1][0]
        if tags[posn + 2][0] == ')':
            posn += 2
        # name = ' '.join([x for x in name if x != unit])
        name = ' '.join(tokenized[posn + 2:])
        ingredients.append((product, unit, name)) #descriptor, prep))


def get_instructions():
    instructions = soup.find_all(class_='recipe-directions__list--item')[0:-1]
    steps = []
    for instruct in instructions:
        text = instruct.text.strip().split('.')
        steps += [Step(t) for t in text]
    return steps


if __name__ == "__main__":
    get_ingredients()
    steps = get_instructions()
    print(steps[0].__parse__())

#print(ingredients)
#print(checklist_items)

#text = word_tokenize(ingredients[12])
#print(nltk.pos_tag(text))

