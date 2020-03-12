#!/usr/bin/env python
# coding: utf-8

# In[22]:

import sys
from pyspark.sql import SparkSession
import json
from itertools import *
from pyspark.sql import *
from collections import Counter
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import lit, col
from pyspark.sql.types import *


sc = SparkContext.getOrCreate()
spark = SparkSession(sc)
class jumble:
    def __init__(self,file):
        super().__init__()
        self.f=file
        self.dictionary = self.create_sorted_dict()
        self.answer=self.solve_jumble()
    
#Sorts the letters in a word
    def get_sorted(self,key):
        word_list = list(key)
        word_list.sort()
        word = "".join(word_list)
        return word

#Sorts the values ([word, score] pairings) of a key (sorted word) so that the first value
# in the list is the most frequently used word
    def sort_values(self,curr:list,new):
        if curr is None:
            curr.append(new)
        else:
            if new[1]==0:
                curr.append(new)
            else:
                i=0
                while (curr[i][1]!=0) and(i<(len(curr)-1)):
                    if new[1]<curr[i][1]:
                        break
                    i+=1
                curr.insert(i,new)
        return curr

#turns the freq_dict into a dictionary with (sorted_word: list([word, score])) pairs
    def create_sorted_dict(self):
        with open('/Users/christinacampbell/Downloads/jumble/freq_dict.json') as f:
                freq_dict = json.load(f)
        keys = list(freq_dict.keys())
        values = list(freq_dict.values())
        dictionary = spark.createDataFrame(zip(keys, values), schema=['keys', 'values'])

        dict_sorted={}
        for row in dictionary.rdd.collect():
            word = self.get_sorted(row.keys)
            if word not in dict_sorted.keys():
                dict_sorted[word]=[[row.keys,row.values]]
            else:
                curr= dict_sorted[word]
                dict_sorted[word]= self.sort_values(curr,[row.keys,row.values])
        sorted_keys = list(dict_sorted.keys())
        sorted_values = list(dict_sorted.values())
        sorted_dict =spark.createDataFrame(zip(sorted_keys, sorted_values), schema=['sorted_keys', 'sorted_values']).toPandas().set_index('sorted_keys')
        return sorted_dict
# given a word, sort the word and look it up in the sorted_dict
    def find_anogram(self,input):
        sorted = self.get_sorted(input)
        answers=self.dictionary.loc[sorted][0][0]
        return answers

# removes letters from the list of letters from the answers that make up the final phrase anogram
    def remove_letters(self,word1,lst_letters):
        for i in word1:
            if i in lst_letters:
                lst_letters.remove(i)
        return lst_letters
# returns the score of a phrase. This is how I determined what is the most likely answer to 
#the anogogram phrases. I made 0=10000, because I wanted it to be considered the worst score.
# The lowest score represents the best choice, because it is made of the most frequently used 
#words.
    def get_score(self,words):
        score = 0
        for w in words:
            s = int(self.dictionary.loc[w][0][0][1])
            if s==0:
                score= score + 10000
            else: score= score + s
        return score
# takes in a list of the circled letters from the anagram words that will make up the anagram
# phrase, and an array with the lengths of the words in the phrase.
    def solution(self,answers_list, word_sizes):
    # if the phrase is one word, call find_anagram and return
        if len(word_sizes)==1:
            return self.find_anogram(answers_list)
        # if not, we need to check all of the different combinations of the letters from answers
        #list of the desired lengths.
        solution_options = []
        combos=[]
        for i in word_sizes:
            combo=combinations(answers_list,i)
            combo_list= []
            #sort the word and check if it is in the dictionary (AKA is it a word?)
            for i in combo:
                word=list(i)
                word.sort()
                word_str = "".join(word)
                if word_str not in combo_list and word_str in self.dictionary.index.values:
                    combo_list.append(word_str)
            combos.append(combo_list)
        # make a set of the different combinations of the possible words in the phrase
        combos_check = set(product(*combos))
        # check to see which combinations of words uses all of the letters in answer_list
        for words in combos_check:
            letters = answers_list[:]
            score = self.get_score(words)
            for w in words:
                letters= self.remove_letters(w,letters)
            if len(letters)==0:
                solution_options.append([words,score])
        # sort the list of possible solutions so we can return the answer with the lowest 
        #score
        solution_options.sort(key = lambda x: x[1])
        return solution_options[0]
    def solve_jumble(self):
    # load in the jumble data
        with open(self.f) as f:
            jumble = json.load(f)
        answer = []
        # solve each anagram in the jumble data, and add the circled letters to the
        # answer list
        for word in jumble:
            if word=='ans': break
            ano= self.find_anogram(word)[0]
            for i in jumble[word]:
                answer.append(ano[i])
        # call solution on the list of letters with the array of lengths of the words
        sol_jumbled = self.solution(answer,jumble['ans'])
        phrase = ""
        # combine the words returned from solution to return the answer phrase
        for w in sol_jumbled[0]:
            phrase+= self.dictionary.loc[w].sorted_values[0][0] + " "
        return( phrase)
#To call in terminal, use the below code
# jumble(sys.argv[1])
#To call in an IDE, use the below code
f = open('answers.txt','w+')
j=jumble("/Users/christinacampbell/Downloads/jumble/puzzle1.json")
f.writelines(j.answer)
j=jumble("/Users/christinacampbell/Downloads/jumble/puzzle2.json")
f.writelines(j.answer)
j=jumble("/Users/christinacampbell/Downloads/jumble/puzzle3.json")
f.writelines(j.answer)
j=jumble("/Users/christinacampbell/Downloads/jumble/puzzle4.json")
f.writelines(j.answer)
j=jumble("/Users/christinacampbell/Downloads/jumble/puzzle5.json")
f.writelines(j.answer)
f.close()



# In[ ]:




