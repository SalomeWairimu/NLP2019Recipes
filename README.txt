# Recipe Project 2019

A Python script for parsing and transforming recipes from the AllRecipes website.
The source code for this project is located at [GitHub](https://github.com/ulyanakurylo/NLP2019Recipes)

## Required dependencies

Python version 3.7.0 or greater

BeautifulSoup:
`python3 -m pip install beautifulsoup4`

spaCy:
`python3 -m pip install -U spacy
python3 -m spacy download en_core_web_sm`

measurement:
`python3 -m pip install measurement`

## Using the API

To begin running the program, navigate to the folder containing `recipes.py`, run `python3 recipes.py`.
Providing an optional parameter (`python3 recipes.py https://www.allrecipes.com/recipe/xxxx`) will cause the program to scrape from that particular recipe. Otherwise, it will default to a random recipe.

Once the program is running, type a number corresponding to the transformation option you want to see.

To see our internal representations, you can enter `~` at the prompt to enable debug printing.

## Extras

We implemented extra styles and transformations (which can be seen at the prompt).

Enabling debug printing will break our ingredients down into the following:
 - Quantity
 - Unit
 - Descriptors
 - Preparatory descriptors
 - Ingredient name

It will also show additional information (if it exists) about each step, including:
 - Actions taken
 - Tools
 - Ingredients used
 - Primary cooking method in that particular step

## Authors

* **Michael Huyler** - *2020*  - [GitHub](https://github.com/KobraKid)
* **Robert Smart** - *2019*  - [GitHub](https://github.com/rbrtsmart)
* **Salome Wairimu** - *2020*  - [GitHub](https://github.com/SalomeWairimu)
* **Ulyana Kurylo** - *2020*  - [GitHub](https://github.com/ulyanakurylo)
