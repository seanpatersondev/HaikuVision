#Haiku Vision
#Created by Sean Paterson (sgp23)
import io, os, pyphen, nltk, collections, re
from random import *
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
from nltk.corpus import stopwords

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

# Instantiates a client
client = vision.ImageAnnotatorClient()
dic = pyphen.Pyphen(lang='en')

image = input("Enter the file path of your image: ")

# The name of the image file to annotate
file_name = os.path.join(
    os.path.dirname(__file__),
    image)

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = types.Image(content=content)

# Performs label detection on the image file
response = client.label_detection(image=image)
labels = response.label_annotations
tags = []
for label in labels:
    tags.append(label.description.split(' ', 1)[0].lower())

# Get another word from the dictList data structure using @param word as the key. The word must conform to the syllable requirements
def getword(word, syll, maxSyll):
   # Get the 25 words probability pairs that most commonly appear after the given word
   poss = dictList[word][:25]
   words = []
   prob = []
   selection = []
   # For each word if it is invalid then do not add it to the set of valid words
   for pair in range(len(poss)):
      likelihood = poss[pair][1]
      curWord = poss[pair][0]
      search = re.search("[\:\.‘',—\d\(\,\?\\-\)`]", curWord)
      tempSyll = getsyll(curWord)
      if not(search or curWord == word or (syll + tempSyll) > maxSyll):
         words.append(curWord.lower())
         prob.append(likelihood)
   # If valid word set empty then return random valid word
   if len(words) == 0:
         return randomWord(maxSyll-syll)
   # Else probabablistically choose a word from the set
   return words[wordProb(prob)]

# Select a random key from dictList, search its bigram list to find a valid word
def randomWord(remainingSyll):
   keys = list(dictList.keys())
   for i in range(100):
      word = choice(keys)
      search = re.search("[\:\.‘',—\d\(\,\?\\-\)`]", curWord)
      if getsyll(word) <= remainingSyll and not(search):
         return word.lower()
   # In the case nothing is found return "the" to maintain some semblance of cohesion
   return "the"

# Take a list of probabilities, normalize the probablities 0-1, find the index that a random number lies between, return that index
def wordProb(prob):
   sumProb = sum(prob)
   for num in range(len(prob)):
      if num > 0:
         prob[num] = (prob[num]/sumProb) + prob[num-1]
      else:
         prob[num] = prob[num]/sumProb
   selection = random()
   for num in range(len(prob)):
      if selection < prob[num]:
         return num

# Count the syllables in a given word, if error return 1
def getsyll(word):
   try:
      num = len(dic.positions(word)) + 1
   except:
      return 1
   return num
   
# Instantiate dictionary used to count syllables
dic = pyphen.Pyphen(lang='en')

# Instantiate corpus reader for word selection
ignoredWords = set(stopwords.words("english"))
filterStops = lambda w: len(w) < 3 or w in ignoredWords

# Load the brown corpus, get the collocations for each word and scores based on the likelihood of occurrence
bigramMeasures = BigramAssocMeasures()
finder = BigramCollocationFinder.from_words(nltk.corpus.brown.words())
scored = finder.score_ngrams(bigramMeasures.likelihood_ratio)

# Create dictionary of lists to associate keys with all their bigram pairs (word, likelihood ratio)
dictList = collections.defaultdict(list)
for key, score in scored:
   dictList[key[0]].append((key[1], score))

# Get words from picture and assess for suitability
first = choice(tags)
tags.remove(first)
second = choice(tags)
tags.remove(second)
third = choice(tags)

# Create lists to hold words, syllables and max syllables for each line
lines = [[first], [second], [third]]
linesSyll = [getsyll(lines[0][0]), getsyll(lines[1][0]), getsyll(lines[2][0])]
linesSyllMax = [5, 7, 5]

# For each line, fill the line with words until the max syllable count is reached
for x in range(3):
   curWord = lines[x][0]
   while linesSyll[x] < linesSyllMax[x]:
      nextWord = getword(curWord, linesSyll[x], linesSyllMax[x])
      lines[x].append(nextWord)
      linesSyll[x] += getsyll(nextWord)
      curWord = nextWord

# Output the haiku
for x in range(3):
   for y in lines[x]:
      print(y, end=' ')
   print()
