from flask import Flask, render_template, request,jsonify, redirect, url_for
import numpy as np
import pandas as pd
import nltk
import logging
from nltk.corpus import conll2000
import json

# sentence segmentation, tokenization, POS tagging
def ie_preprocess(document):
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences


def final_nouns(ans1, ans2):
    ans11 = []  # trigrams
    ans21 = []
    j_store = 0
    for i in range(len(ans1)):
        k = 0
        l = 0
        for j in range(len(ans2)):
            if ans2[j][0].lower() in ans1[i][0].lower():
                l = 1
                if ans2[j][1] >= ans1[i][1]:
                    ans21.append(ans2[j])
                    k = k + 1
                else:
                    if k < 1:
                        ans11.append(ans1[i])
            else:
                ans21.append(ans2[j])

        if k == 0 and l == 0:
            ans11.append(ans1[i])

    ans11 = list(set(ans11))
    ans21 = list(set(ans21))
    return ans11, ans21



#collect keywords with counts in news
def keywords_collect(sentence):
    final_keys = []
    occurance = {}
    one_doc_occ = {}

    for index in range(len(sentence)):

        grammar = "NP: {<NN.*><NN.*><NN.*>}"  # trigrams
        trigram = []
        cp = nltk.RegexpParser(grammar)
        for s in sentence[index]:
            result = cp.parse(s)
            for node in result:
                if type(node) != tuple:
                    prat = ''
                    for n in node:
                        prat += n[0]
                        prat += ' '
                    trigram.append(prat[:-1])

        ct_trigram = {x: trigram.count(x) for x in set(trigram)}
        ans1 = list(ct_trigram.items())
        ans1.sort(key=lambda x: -x[1])

        #bigrams extractor
        grammar = "NP: {<NN.*><NN.*>}"  # bigrams
        bigram = []
        cp = nltk.RegexpParser(grammar)
        for k in sentence[index]:
            result = cp.parse(k)
            for node in result:
                if type(node) != tuple:
                    prat = ''
                    for n in node:
                        prat += n[0]
                        prat += ' '
                    prat = prat.lower()
                    bigram.append(prat[:-1])

        ct_trigram = {x: bigram.count(x) for x in set(bigram)}
        ans2 = list(ct_trigram.items())
        ans2.sort(key=lambda x: -x[1])


        #
        ans1, ans2 = final_nouns(ans1, ans2)

        # occurance in multiple docs to cal tfidf

        for i in ans1:
            if i in occurance.keys():
                occurance[i[0]] = occurance[i[0]] + 1
            else:
                occurance[i[0]] = 1
        for j in ans2:
            if j in occurance.keys():
                occurance[j[0]] = occurance[j[0]] + 1
            else:
                occurance[j[0]] = 1

        # append all nouns with more than 1 occurance in final list

        for i in range(len(ans1)):
            if ans1[i][1] > 1:
                final_keys.append(ans1[i])

        for i in range(len(ans2)):
            if ans2[i][1] > 1:
                final_keys.append(ans2[i])

    for i in final_keys:
        one_doc_occ[i[0]] = i[1]

    return one_doc_occ, occurance, final_keys



#compute TF score
def computeTF(one_doc_occ, final_keys):
    tfDict = {}
    bagOfWordsCount = len(final_keys)
    for word, count in one_doc_occ.items():
        tfDict[word] = count / float(bagOfWordsCount)
    return tfDict

#compute IDF score
def computeIDF(occurance, sentence):
    idfDict2 = {}
    import math
    N = len(sentence)
    idfDict = dict.fromkeys(occurance.keys(), 0)
    for word in occurance.keys():
        if occurance[word] > 0:
            idfDict[word] += occurance[word]

    for word, val in idfDict.items():
        idfDict2[word] = math.log(N / float(val))
    return idfDict2


#calculate TFIDF score
def computeTFIDF(tfd, idfd):
    tfidf = {}
    for word, val in tfd.items():
        tfidf[word] = val * idfd[word]
    return tfidf


def remove_extremes(tfidf):
    for key in tfidf.keys():
        if "mr" in key.lower():        #to remove "mr"
            value=0

        wh = ["who","what","where","how","whom","taken","mr","ms","mrs","www"]
        for word in wh:                                         #to remove wh nouns
            if word in key.lower():
                tfidf[key] = 0

        if "’" == key[-1]:                   #to remove appostrophy
            tfidf[key] = 0

        # remove extra characters
        if (ord(key[-1])>65 and ord(key[-1])<90) or (ord(key[-1])>97 and ord(key[-1])<122) :
            pass
        if (ord(key[0])>65 and ord(key[0])<90) or (ord(key[0])>97 and ord(key[0])<122) :
            pass
        else :
            tfidf[key] = 0

    return tfidf

def convert(sequenced) :
    s={"noun_chunks":{"nc":""}}
    lis = []
    l=0
    for key in sequenced.keys():
        if(l==10):
            break
        l = l+1
        lis.append(key)
        s["noun_chunks"]["nc"] = lis
    return json.dumps(s)


#returning result

def requestResults(df) :
    sentence = []
    for i in range(20):
        sentence.append(ie_preprocess(df["data"][i]))

    one_doc_occ, occurance, final_keys = keywords_collect(sentence)

    tfd = computeTF(one_doc_occ, final_keys)
    idfd = computeIDF(occurance, sentence)
    tfidf = computeTFIDF(tfd, idfd)
    tfidf_modified = remove_extremes(tfidf)
    sequenced = dict(sorted(tfidf_modified.items(), key=lambda item: -item[1]))
    output = convert(sequenced)
    return output

