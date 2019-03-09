from fractions import Fraction
import os
import platform
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
debug = False

base_url = 'https://www.allrecipes.com/recipe/'
urls = [
    # Random URl
    # If random recipe DNE or has been deleted, AllRecipes will default to:
    # Johnsonville® Three Cheese Italian Style Chicken Sausage Skillet Pizza
    '-1',  # 0. Random
    # Test URLs
    base_url + '18511',  # 1. Hash Brown Casserole II
    base_url + '212721',  # 2. Indian Chicken Curry (Murgh Kari)
    base_url + '91192',  # 3. French Onion Soup Gratinee
    base_url + '60598',  # 4. Vegetarian Korma
    base_url + '240425',  # 5. Dutch Oven Vegetable Beef Soup
    ]
# AllRecipes URL to parse
url = None
# The HTML parsed by BeautifulSoup
soup = None
recipe_name = ''

# If a verb is in this list, we consider it a cooking action
cooking_verbs = [
    'bake', 'barbeque', 'baste', 'batter', 'beat', 'blanch', 'blend', 'boil',
    'broil', 'caramelize', 'carmelize', 'chop', 'cook', 'clarify', 'cream',
    'cure', 'deglaze', 'degrease', 'dice', 'dissolve' 'dredge', 'drizzle',
    'dust', 'fillet', 'flake', 'flambe', 'fold', 'fricasse', 'fry', 'garnish',
    'glaze', 'grate', 'grind', 'julienne', 'knead', 'marinate', 'melt',
    'meuniere', 'mince', 'mix', 'pan-broil', 'pan-fry', 'parboil', 'pare',
    'peel', 'pickle', 'pit', 'plump', 'poach', 'preheat', 'puree', 'refresh',
    'roast', 'saute', 'scald', 'scallop', 'score', 'sear', 'season', 'serve',
    'shred', 'sift', 'simmer', 'skim', 'spread', 'sprinkle', 'steam', 'steep',
    'sterilize', 'stew', 'stir', 'toss', 'truss', 'whip'
    ]
# Used to resolve ties
primary_verbs = ['bake', 'boil', 'fry', 'simmer', 'saute', 'roast', 'steam', 'stew']
# Exclude conjugations of "to be" no matter what
to_be_verbs = [
    'be', 'is', 'are', 'was'
    ]
# Used to help conversion between vegetarian and non-vegetarian
meat_products = [
    'beef', 'chicken', 'pork', 'bacon', 'sausage', 'ham', 'lamb', 'meat', 'venison', 'veal', 'steak', 'ribs', 'filet mignon', 'shrimp',
    'snail', 'oyster', 'fish', 'tilapia', 'tuna', 'salmon', 'walleye', 'mussels', 'pepperoni', 'salami', 'patty', 'turkey']
# Maps meat products to suitable vegetarian replacements
veggie_replacements = {
    # 'tofu': ['beef', 'chicken', 'pork', 'shrimp', 'snail', 'oyster', 'mussels'],
    'seitan': ['beef', 'chicken', 'pork', 'filet mignon', 'steak', 'venison', 'lamb', 'meat', 'ribs', 'turkey'],
    'tempeh': ['fish', 'tilapia', 'tuna', 'salmon', 'walleye']}
# If a word is in this list, we consider it a measurement unit.
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
# If a word is in this list, we consider it a cooking tool/implement.
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
        nlp = spacy.load('en_core_web_sm')
        self.tokens = nlp(self.text)
        self.__parse__()
        self.__get_time()

    def __parse__(self):
        self.ingredients = []
        for i in range(len(self.tokens)):
            if (not self.tokens[i].tag_.startswith('NN')) or self.tokens[i].text in measurements_list:
                continue
            for key in ingredients.keys():
                ingredient = key.lower()
                if self.tokens[i].text in ingredient:
                    # print("Starting with: " + self.tokens[i].text)
                    potential_ingredient = self.tokens[i].text
                    j = i - 1
                    while j > 0 and self.tokens[j].text in ingredient:
                        potential_ingredient = self.tokens[j].text + " " + potential_ingredient
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
        for token in self.tokens:
            # print(token.text + "\t" + token.tag_ + "\t" + token.dep_)
            if token.tag_ in ["VB", "VBP", "VBZ"] and token.text not in to_be_verbs and token.text in cooking_verbs:
                self.verbs.append(token)
            elif token.text in tools:  # token.tag_ in ["NN"] and
                self.tools.append(token.text)

    def __get_time(self):
        self.time = 0
        self.primary_method = ''
        last_verb = ''
        for i in range(len(self.tokens)):
            if self.tokens[i].text in cooking_verbs:
                last_verb = self.tokens[i].text
            if self.tokens[i].tag_ in ['CD', 'LS'] or self.tokens[i].text == 'an':
                unit = self.tokens[i + 1].text
                if unit == 'hours':
                    try:
                        t = int(Fraction(self.tokens[i].text)) * 60
                        if t > self.time:
                            self.time = t
                            self.primary_method = last_verb
                    except Exception as e:
                        print(self.tokens[i].text)
                if unit == 'hour':
                    t = 60
                    if t > self.time:
                        self.time = t
                        self.primary_method = last_verb
                if unit == 'minutes':
                    try:
                        t = int(Fraction(self.tokens[i].text))
                        if t > self.time:
                            self.time = t
                            self.primary_method = last_verb
                    except Exception as e:
                        print(self.tokens[i].text)

    def get_tools(self):
        return self.tools

    def get_verbs(self):
        return [v.text for v in self.verbs]


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
        print("intersection: " + str(lst3))
    return lst3


def get_recipe(in_url):
    """Given a url for an AllRecipes page,
    open the page and prepare for parsing.
    """
    global url
    global soup
    global recipe_name
    if in_url == '-1':
        url = base_url + str(random.randint(60_000, 250_000))
        print(url)
    else:
        url = in_url
    try:
        page = urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        recipe_name = soup.find('h1', {'id': 'recipe-main-content'}).text
    except Exception as e:
        print('Failed to open recipe: ' + url)
        print(e)
        sys.exit(1)


def get_ingredients():
    """Iterates through each item in the ingredients section of the recipe
    page, extracting useful information including quantity and units, as well
    as descriptions of ingredients which may modify the ingredient, and
    preparation actions which need to be done before starting the recipe.
    """
    checklist_items = soup.find_all(class_='checkList__line')[0:-3]
    nlp = spacy.load('en_core_web_sm')
    ingredients = {}
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
        potential_unit = tokens[posn + 1] if posn + 1 < len(tokens) else tokens[posn]
        if not potential_unit.tag_.startswith('JJ'):
            unit = potential_unit.text if is_unit(potential_unit.text) else None
        else:
            second_unit = potential_unit.head.text
            unit = (potential_unit.text + ' ' + second_unit) if is_unit(second_unit) else None
            posn += 1 if unit else 0
        if posn + 2 < len(tokens) and tokens[posn + 2].text == ')':
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
        # 0: quantity 1: unit 2: description 3: prep step 4: name
        ingredients[text] = (product if product > 0 else None, unit, desc, prep, name)
    return ingredients


def is_unit(text):
    """Given a string, determines if the string represents
    a unit of measurement in the context of cooking.
    """
    if text in measurements_list or text[0:-1] in measurements_list or (len(text) > 2 and text[0:-2] in measurements_list):
        return True
    return False


def get_instructions():
    """Splits a recipe on each sentence, so that we can regard
    each individual sentence as a separate step in our recipe.
    """
    instructions = soup.find_all(class_='recipe-directions__list--item')[0:-1]
    steps = []
    for instruct in instructions:
        text = instruct.text.strip().split('.')
        steps += [Step(t) for t in text if len(t) > 0]
    return steps


def get_primary_method(steps):
    """Check each step in our recipe, and try to find a cooking
    action that is paired with the longest span of time in our recipe.
    """
    max = 0
    max_step = "0"
    for step in steps:
        if step.time > max:
            max = step.time
            max_step = step.primary_method
        elif step.time == max:
            if max_step in primary_verbs:
                continue
            max_step = step.primary_method
    return "Primary cooking method is " + max_step + " for %d minutes." % max


def convert_vegetarian(steps):
    """Converts a recipe to vegetarian.
    """
    veg_ingredients = {}
    for ingredient in ingredients:
        veg_ingredients[ingredient] = ingredients[ingredient]
        for meat in meat_products:
            if meat in ingredients[ingredient][4]:
                replacement = "tofu"
                for veggie in veggie_replacements:
                    if meat in veggie_replacements[veggie]:
                        replacement = veggie
                veg_ingredients[ingredient] = (
                    ingredients[ingredient][0],
                    ingredients[ingredient][1],
                    ingredients[ingredient][2],
                    ingredients[ingredient][3],
                    replacement
                )
    display_recipe(veg_ingredients, steps, 'Vegetarian ')


def display_recipe(ingredients, steps, style):
    """Given a set of ingredients and steps,
    display them in a nice way to the user.
    """
    print(style + recipe_name + "\n")
    for external_rep, internal_rep in ingredients.items():
        print(external_rep)
        if not debug:
            continue
        line = ''
        for i in internal_rep:
            line += ((str(i).strip() + ' | ') if i else '_ | ')
        print('>> ' + line)
    print()
    for x in range(len(steps)):
        print('Step ' + str(x + 1) + ': ' + str(steps[x].text[4:5].upper()) + str(steps[x].text[5:]))
        print('\tActions: ' + ', '.join(steps[x].get_verbs())) if steps[x].get_verbs() else 0
        print('\tTools: ' + ', '.join(steps[x].get_tools())) if steps[x].get_tools() else 0
        print('\tIngredients: ' + ', '.join(steps[x].ingredients)) if steps[x].ingredients else 0
        print('\tPrimary Method: ' + steps[x].primary_method + ' %d minutes' % steps[x].time) if steps[x].primary_method else 0
        print()
    print(get_primary_method(steps))


if __name__ == "__main__":
    get_recipe(sys.argv[1] if (len(sys.argv) > 1) else urls[-1])
    ingredients = get_ingredients()
    steps = get_instructions()
    val = '0'
    while val != 'q':
        # Used to change debug flag
        if val == '~':
            debug = not debug
            val = '0'
        # Difficulty level 1
        if val == 'D1':
            val = '0'
        # Difficulty level 2
        elif val == 'D2':
            val = '0'
        # Difficulty level 3
        elif val == 'D3':
            val = '0'
        # Show original Recipe
        elif val == '0':
            display_recipe(ingredients, steps, '')
        # Make a non-vegetarian recipe vegetarian
        elif val == '1':
            convert_vegetarian(steps)
        # Make a vegetarian recipe non-vegetarian
        elif val == '2':
            pass
        # Make a recipe healthy
        elif val == '3':
            pass
        # Make a recipe unhealth
        elif val == '4':
            pass
        # Unused
        elif val == '5':
            pass
        # Unused
        elif val == '6':
            pass
        # Invalid option
        else:
            print("Invalid option: " + val)
            display_recipe(ingredients, steps, '')
        val = input("""
0: Show Original Recipe
1: Convert to Vegetarian
2: Convert From Vegetarian
3: Convert to Healthy Style
4: Convert from Healthy Style
5: Convert to ____ Style
6: Convert to ____ Style
D1: Difficulty level 1 (Easy)
D2: Difficulty level 2 (Medium)
D3: Difficult level 3 (Hard)
Q: Quit\n>>""").strip().lower()
        os.system('cls') if platform.platform().lower().startswith('windows') else os.system('clear')
    print("Goodbye!")
