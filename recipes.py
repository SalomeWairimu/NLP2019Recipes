from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys
import ssl 

ssl._create_default_https_context = ssl._create_unverified_context
url = 'https://www.allrecipes.com/recipe/212721/indian-chicken-curry-murgh-kari/?internalSource=hub%20recipe&referringContentType=Search' #will be given this
page = urlopen(url)
soup = BeautifulSoup(page, 'html.parser')
checklist_items = soup.find_all(class_= 'checkList__line')
checklist_items = checklist_items[0:-3] #gets rid of last 3 elems we dont need 
ingredients= []
for item in checklist_items:
    text = item.text.strip()
    ingredients.append(text)

print(ingredients)

#print(checklist_items)