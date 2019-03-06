from fractions import Fraction
import random
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

base_url = 'https://www.allrecipes.com/recipe/'
urls = [
    '-1',
    base_url + '18511',
    base_url + '212721',
    base_url + '91192',
    base_url + '60598',
    base_url + '103895',
    base_url + '240425',
    base_url + '69125'
    ]
# AllRecipes URL to parse
url = None
# The HTML parsed by BeautifulSoup
soup = None

ingredients = {}
cooking_verbs = [
    'bake', 'barbeque', 'baste', 'batter', 'beat', 'blanch', 'blend', 'boil',
    'broil', 'carmelize', 'chop', 'clarify', 'cream', 'cure', 'deglaze',
    'degrease', 'dice', 'dissolve' 'dredge', 'drizzle', 'dust', 'fillet',
    'flake', 'flambe', 'fold', 'fricasse', 'fry', 'garnish', 'glaze', 'grate',
    'grind', 'julienne', 'knead', 'marinate', 'meuniere', 'mince', 'mix',
    'pan-broil', 'pan-fry', 'parboil', 'pare', 'peel', 'pickle', 'pit', 'plump',
    'poach', 'puree', 'reduce', 'refresh', 'roast', 'saute', 'scald', 'scallop',
    'score', 'sear', 'season', 'shred', 'sift', 'simmer', 'skim', 'steam',
    'steep', 'sterilize', 'stew', 'stir', 'toss', 'truss', 'whip', 'preheat'
    ]
to_be_verbs = [
    'be', 'is', 'are', 'was'
    ]
measurements_list = [
    # Unique Collections
    'bunch', 'can', 'clove', 'pinch', 'slice', 'sprig', 'rib',
    # Volumes
    'tsp', 'teaspoon', 'tbsp', 'tblsp', 'tbs', 'tablespoon', 'c', 'cup', 'pt', 'pint', 'qt', 'quart', 'gal', 'gallon',
    'ml', 'mL', 'milliliter', 'millilitre', 'l', 'L', 'liter', 'litre',
    # Weights
    'oz', 'ounce', 'lb', 'pound',
    'mg', 'milligram', 'milligramme', 'g', 'gram', 'gramme', 'kg', 'kilogram', 'kilogramme',
    # Lengths
    'in', 'inch',
    'cm', 'centimeter', 'centimetre'
    ]
tools = [
    'spoon', 'bowl', 'skillet', 'oven', 'knife', 'whisk', 'fork',
    'cutting board', 'can opener', 'strainer', 'sieve', 'blender', 'pan', 'pot',
    'saucepan', 'peeler', 'measuring cup', 'scoop', 'measuring spoon',
    'colander', 'masher', 'salad spinner', 'grater', 'shears', 'rolling pin',
    'juicer', 'garlic press', 'dish', 'plate', 'platter', 'foil', 'stockpot',
    'crockpot', 'spatula', 'tongs', 'ladle', 'trivet', 'lid', 'splatter guard',
    'paper towel', 'thermometer', 'scale', 'parchment paper', 'baking sheet',
    'glass', 'cup', 'tray', 'press', 'microwave', 'stove', 'stovetop', 'kettle',
    'toaster', 'chopper', 'double boiler', 'steamer'
    ]

class Step:
    def __init__(self, text):
        self.text = "You " + text.strip()[0:1].lower() + text.strip()[1:]
        self.__parse__()

    def __parse__(self):
        nlp = spacy.load('en_core_web_sm')
        tokens = nlp(self.text)
        self.ingredients = []
        for i in range(len(tokens)):
            if (not tokens[i].tag_.startswith('NN')) or tokens[i].text in measurements_list:
                continue
            for key in ingredients.keys():
                ingredient = key.lower()
                if tokens[i].text in ingredient:
                    print("Starting with: " + tokens[i].text)
                    potential_ingredient = tokens[i].text
                    j = i - 1
                    while j > 0 and tokens[j].text in ingredient:
                        potential_ingredient = tokens[j].text + " " + potential_ingredient
                        j -= 1
                    self.ingredients.append(potential_ingredient)
        removals = []
        for i in range(len(self.ingredients)):
            for j in range(i+1, len(self.ingredients)):
                if self.ingredients[i] in self.ingredients[j]:
                    removals.append(i)
                elif self.ingredients[j] in self.ingredients[i]:
                    removals.append(j)
        self.ingredients = [self.ingredients[i] for i in range(len(self.ingredients)) if i not in removals]
        for i in range(len(self.ingredients)):
            self.ingredients[i] = find_largest_intersection(self.ingredients[i])
        self.ingredients = [i for i in self.ingredients if i]
        self.verbs = []
        self.tools = []
        for token in tokens:
            # print(token.text + "\t" + token.tag_ + "\t" + token.dep_)
            if token.tag_ in ["VB", "VBP", "VBZ"] and token.text not in to_be_verbs:
                self.verbs.append(token)
            elif token.text in tools:  # token.tag_ in ["NN"] and
                self.tools.append(token.text)

    def get_verbs(self):
        return [v.text for v in self.verbs]

    def get_tools(self):
        return self.tools


def find_largest_intersection(ingredient):
    ingredient_set = set(ingredient.split())
    largest_intersection = 0
    real_ingredient = None
    for key in ingredients:
        each = key.lower()
        real_set = set(each.replace(',', ' ').split())
        intersect = len(ingredient_set.intersection(real_set))
        if intersect > largest_intersection:
            largest_intersection = intersect
            real_ingredient = each
    return real_ingredient


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2 and len(value) > 2]
    if len(lst3) > 0:
        print("Intersection: " + str(lst3))
    return lst3


def get_recipe(in_url):
    global url
    global soup
    if in_url == '-1':
        url = base_url + str(random.randint(60_000, 250_000))
        print(url)
    else:
        url = in_url
    page = urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')


def get_ingredients():
    checklist_items = soup.find_all(class_='checkList__line')[0:-3]
    nlp = spacy.load('en_core_web_sm')
    global ingredients
    for item in checklist_items:
        text = item.text.strip()
        tokens = nlp(text)
        descriptor = []
        preparation = []
        name = []
        sum = 0
        product = 1
        posn = 0
        cutoff = len(tokens)
        for i in range(len(tokens)):
            # Removing such as
            if i + 1 < len(tokens):
                if tokens[i].text == '(' and tokens[i+1].text == 'such':
                    cutoff = i
                    break
            # Quantities
            if tokens[i].tag_ in ['CD', 'LS'] and tokens[i + 1].text != '(':
                try:
                    sum += float(Fraction(tokens[i].text))
                    posn = i
                except Exception as e:
                    descriptor.append(i)
            elif tokens[i].tag_ in ['CD', 'LS'] and tokens[i + 1].text == '(':
                try:
                    product = float(Fraction(tokens[i].text))
                    posn = i
                except Exception as e:
                    descriptor.append(i)
            # Descriptors
            elif tokens[i].tag_.startswith('JJ') and tokens[i].dep_ not in ['nsubj', 'dobj', 'pobj']:
                descriptor.append(i)
            # Prep steps
            elif tokens[i].tag_ in ['VBN', 'RB']:
                preparation.append(i)
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
        name = ''
        desc = ''
        prep = ''
        for i in range(posn + (2 if unit else 1), cutoff):
            if i in descriptor:
                desc += tokens[i].text + ' '
            elif i in preparation:
                prep += tokens[i].text + ' '
            elif tokens[i].text not in ['or', 'and', ',']:
                name += tokens[i].text + ' '
        name = name.strip()
        desc = desc.strip()
        prep = prep.strip()
        ingredients[text] = (product if product > 0 else None, unit, desc, prep, name)


def is_unit(text):
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


def get_primary_method(steps):
    max = 0
    max_step = 0
    for step in steps:
        num = 0
        tokens = step.text.split()
        if 'minutes' in tokens:
            num = tokens[tokens.index('minutes')-1]
            if num > max:
                max = num
                max_step = step
        if 'hour' in tokens:
            num = 60
            if num > max:
                max = num
                max_step = step
        if 'hours' in tokens:
            num = tokens[tokens.index('hours')-1]
            if num > max:
                max = num
                max_step = step


if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_recipe(sys.argv[1])
    else:
        get_recipe(urls[-2])
    get_ingredients()
    for external_rep, internal_rep in ingredients.items():
        print(external_rep)
        line = ""
        for i in internal_rep:
            line += ((str(i).strip() + " | ") if i else "_ | ")
        print(">> " + line + "\n")
    steps = get_instructions()
    get_primary_method(steps)
    for x in range(len(steps)):
        print("Step " + str(x + 1) + ": " + str(steps[x].text[4:5].upper()) + str(steps[x].text[5:]))
        print(steps[x].get_verbs())
        print(steps[x].get_tools())
        print(steps[x].ingredients)
        print("")
