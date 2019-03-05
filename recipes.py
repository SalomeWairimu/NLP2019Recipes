from fractions import Fraction
import ssl
import sys
from urllib.request import urlopen

from bs4 import BeautifulSoup
from measurement.measures import Volume
import nltk
from nltk import word_tokenize
import spacy

ssl._create_default_https_context = ssl._create_unverified_context
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
urls = ['https://www.allrecipes.com/recipe/18511/hash-brown-casserole-ii/',
        'https://www.allrecipes.com/recipe/212721/indian-chicken-curry-murgh-kari/',
        'https://www.allrecipes.com/recipe/91192/french-onion-soup-gratinee/',
        'https://www.allrecipes.com/recipe/60598/vegetarian-korma/'
        ]
url = urls[3]
page = urlopen(url)
soup = BeautifulSoup(page, 'html.parser')
ingredients = []
cooking_verbs = ['bake', 'barbeque', 'baste', 'batter', 'beat', 'blanch', 'blend', 'boil', 'broil', 'carmelize', 'chop', 'clarify', 'cream', 'cure', 'deglaze', 'degrease', 'dice', 'dissolve' 'dredge', 'drizzle', 'dust', 'fillet', 'flake', 'flambe', 'fold', 'fricasse', 'fry', 'garnish', 'glaze', 'grate', 'grind', 'julienne', 'knead', 'marinate', 'meuniere', 'mince', 'mix', 'pan-broil', 'pan-fry', 'parboil', 'pare', 'peel', 'pickle', 'pit', 'plump', 'poach', 'puree', 'reduce', 'refresh', 'roast', 'saute', 'scald', 'scallop', 'score', 'sear', 'season', 'shred', 'sift', 'simmer', 'skim', 'steam', 'steep', 'sterilize', 'stew', 'stir', 'toss', 'truss', 'whip', 'preheat']
to_be_verbs = ['be', 'is', 'are', 'was']
measurements_list = ['bunch', 'clove', 'pinch', 'slice', 'sprig', 'cup', 'tablespoon', 'teaspoon', 'ounce', 'can', 'pint', 'quart', 'gallon', 'tsp', 'tbsp', 'tblsp', 'tbs', 'lb', 'pound', 'oz', 'c', 'pt', 'qt', 'gal']


class Step:
    def __init__(self, text):
        self.text = "You " + text.strip()[0:1].lower() + text.strip()[1:]
        self.__parse__()

    def __parse__(self):
        nlp = spacy.load('en_core_web_sm')
        tokens = nlp(self.text)
        self.verbs = []
        for token in tokens:
            print(token.text + "\t" + token.tag_ + "\t" + token.dep_)
            if token.tag_ in ["VB", "VBP", "VBZ"] and token.text not in to_be_verbs:
                self.verbs.append(token)

    def get_verbs(self):
        return [v.text for v in self.verbs]


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2 and len(value) > 2]
    if len(lst3) > 0:
        print("Intersection: " + str(lst3))
    return lst3


def get_ingredients():
    checklist_items = soup.find_all(class_='checkList__line')[0:-3]
    nlp = spacy.load('en_core_web_sm')
    global ingredients
    for item in checklist_items:
        text = item.text.strip()
        # tokenized = word_tokenize(text)
        tokens = nlp(text)
        # descriptor = []
        # prep = []
        name = []
        sum = 0
        product = 1
        # tags = nltk.pos_tag(tokenized)
        posn = 0
        for i in range(len(tokens)):
            print(tokens[i].text + "\t" + tokens[i].tag_ + "\t" + tokens[i].dep_)
            if tokens[i].tag_ in ['CD', 'LS'] and tokens[i + 1].tag_ != '(':
                sum += float(Fraction(tokens[i].text))
                posn = i
            elif tokens[i].tag_ in ['CD', 'LS'] and tokens[i + 1].tag_ == '(':
                product = float(Fraction(tokens[i].text))
                posn = i
        # for i in range(len(tags)):
        #     if tags[i][1] == 'CD' and tags[i + 1][1] != '(':
        #         sum += float(Fraction(tags[i][0]))
        #         posn = i
        #     elif tags[i][1] == 'CD' and tags[i + 1][1] == '(':
        #         product = float(Fraction(tags[i][0]))
        #         posn = i
        #     elif tags[i][1].startswith('JJ'): #descriptor words
        #         descriptor.append(tags[i][0])
        #     elif tags[i][1].startswith('VB'): #prep verbs
        #         prep.append(tags[i][0])
        #     elif tags[i][1].startswith('NN'): #its a name
        #         name.append(tags[i][0])
        product = sum * product
        potential_unit = tokens[posn + 1]
        if not potential_unit.tag_.startswith('JJ'):
            unit = potential_unit.text if is_unit(potential_unit.text) else None
        else:
            second_unit = potential_unit.head.text
            unit = (potential_unit.text + " " + second_unit) if is_unit(second_unit) else None
            posn += 1 if unit else 0
        if tokens[posn + 2].text == ')':
            posn += 2
        # name = ' '.join([x for x in name if x != unit])
        name = ''.join(tokens[posn + (2 if unit else 1):].text)
        ingredients.append((product if product > 0 else None, unit, name))  # descriptor, prep))


def is_unit(text):
    # for unit in measurements_list:
    #     if text in unit or text[0:-1] in unit or (len(text) > 2 and text[0:-2] in unit):
    if text in measurements_list or text[0:-1] in measurements_list or (len(text) > 2 and text[0:-2] in measurements_list):
        return True
    return False


def get_instructions():
    instructions = soup.find_all(class_='recipe-directions__list--item')[0:-1]
    steps = []
    for instruct in instructions:
        text = instruct.text.strip().split('.')
        steps += [Step(t) for t in text if len(t) > 0]
    return steps


if __name__ == "__main__":
    get_ingredients()
    for ingredient in ingredients:
        print(ingredient)
    steps = get_instructions()
    for x in range(len(steps)):
        print("Step " + str(x + 1) + ": " + str(steps[x].text))
        print(steps[x].get_verbs())
        print("")
