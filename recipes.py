from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys
import ssl
import nltk
from nltk import word_tokenize
from fractions import Fraction


ssl._create_default_https_context = ssl._create_unverified_context
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# url = 'https://www.allrecipes.com/recipe/18511/hash-brown-casserole-ii/'
url = 'https://www.allrecipes.com/recipe/212721/indian-chicken-curry-murgh-kari/'
page = urlopen(url)
soup = BeautifulSoup(page, 'html.parser')
ingredients = []
cooking_verbs = ['bake', 'barbeque', 'baste', 'batter', 'beat', 'blanch', 'blend', 'boil', 'broil', 'carmelize', 'chop', 'clarify', 'cream', 'cure', 'deglaze', 'degrease', 'dice', 'dissolve' 'dredge', 'drizzle', 'dust', 'fillet', 'flake', 'flambe', 'fold', 'fricasse', 'fry', 'garnish', 'glaze', 'grate', 'grind', 'julienne', 'knead', 'marinate', 'meuniere', 'mince', 'mix', 'pan-broil', 'pan-fry', 'parboil', 'pare', 'peel', 'pickle', 'pit', 'plump', 'poach', 'puree', 'reduce', 'refresh', 'roast', 'saute', 'scald', 'scallop', 'score', 'sear', 'shred', 'sift', 'simmer', 'skim', 'steam', 'steep', 'sterilize', 'stew', 'stir', 'toss', 'truss', 'whip', 'preheat']


class Step:
    def __init__(self, text):
        self.text = 'You ' + text

    def __parse__(self):
        global ingredients
        tokenized = word_tokenize(self.text)
        self.verbs = []
        tags = nltk.pos_tag(tokenized)
        self.step_ingreds = []  # ingredients which pertain to the current STEP (sentence)
        for i in range(len(tokenized)):
            if tags[i][1].startswith('VB'):
                self.verbs.append(tags[i][0])
        for ing in ingredients:
            if ing[2] in self.step_ingreds:
                ind = tokenized.index(intersection(ing[2].split(), tokenized)[0])
                while ind > 0:
                    if tags[ind][1] == 'CD':
                        self.step_ingreds.append(tags[ind][0] + ' ' + ing[1] + ' ' + ing[2])
                        break
                    ind -= 1
            elif intersection(ing[2].split(), tokenized):  # if the ingredient is in our step, add to list of pertaining ingredients
                self.step_ingreds.append(ing[2])
        self.step_ingreds = set(self.step_ingreds)
        print("Ingrediaents: " + str(self.step_ingreds))
        print("Verbs: " + str(self.verbs))


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2 and len(value) > 2]
    if len(lst3) > 0:
        print("Intersection: " + str(lst3))
    return lst3


def get_ingredients():
    checklist_items = soup.find_all(class_='checkList__line')[0:-3]
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
        ingredients.append((product, unit, name))  # descriptor, prep))


def get_instructions():
    instructions = soup.find_all(class_='recipe-directions__list--item')[0:-1]
    steps = []
    for instruct in instructions:
        text = instruct.text.strip().split('.')
        steps += [Step(t) for t in text if len(t) > 0]
    return steps


if __name__ == "__main__":
    get_ingredients()
    steps = get_instructions()
    for x in range(len(steps)):
        print("Step " + str(x) + ": " + str(steps[x].text[3:]))
        steps[x].__parse__()
        print("")
