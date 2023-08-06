#!/bin/env python
# encoding: utf-8

# Name Generator written by Pointon: 
# http://www.uselesspython.com/showcontent.php?author=27

# Adapted by Arne Babenhauserheide 2007

## I got sick of the absence of plain weird and quirky name generators out there. This comes up with unpronounceable results about 1/5th of the time.
## The namegen function has three parameters: lower_limit and upper_limit govern the length. ratio governs the vowels:consonants ratio. The lower the ratio, the less vowels per consonant.


import random

result = ""
fricatives = ["j", "ch", "h", "s", "sh", "th", "f", "v", "z"]
vowels = ["a", "e", "i", "o", "u", "y", "ya", "ye", "yi", "yo", "yu", "wa", "we", "wi", "wo", "wu", "ae", "au", "ei", "ie", "io", "iu", "ou", "uo", "oi", "oe", "ea"]
consonantsNormal = ["c", "g", "t", "d", "p", "b", "x", "k", "ck", "ch"]
consonantsNasal = ["n", "m", "ng", "nc"]
randomLength = 0
vowelSyllables = 0
vowelRatio = 0

def namegen(ratio=5, lower_limit=3, upper_limit=11):
    ratio = ratio + 3
    if ratio < 4:
        ratio = 4
    elif ratio > 14:
        ratio = 14
    global result, vowelSyllables, randomLength, vowelRatio
    vowelRatio = ratio
    result = ""
    vowelSyllables = 0
    randomLength = random.randrange(lower_limit, upper_limit)
    sylgen()
    return result.capitalize()

def sylgen():
    global result, vowelSyllables, randomLength, syllableOnlyVowels, vowelRatio
    syllableOnlyVowels = 1
    maincongen()
    if vowelSyllables < (vowelRatio/4):
        vowgen()
    maincongen()
    if syllableOnlyVowels == 1:
        vowelSyllables = vowelSyllables + 1
    if len(result) < randomLength:
        sylgen()

def fricgen():
    global result, vowelSyllables, syllableOnlyVowels, fricatives
    result = result + fricatives[random.randrange(0, len(fricatives))]
    syllableOnlyVowels = 0
    vowelSyllables = 0

def vowgen():
    global result, vowels
    result = result + vowels[random.randrange(0, len(vowels))]

def congen():
    global result, vowelSyllables, randomLength, syllableOnlyVowels, consonantsNormal
    result = result + consonantsNormal[random.randrange(0, len(consonantsNormal), 1)]
    syllableOnlyVowels = 0
    vowelSyllables = 0

def con2gen():
    global result, vowelSyllables, syllableOnlyVowels
    if random.randrange(0, 2) == 0:
        result = result + "r"
    else:
        result = result + "l"
    syllableOnlyVowels = 0
    vowelSyllables = 0

def con3gen():
    global result, vowelSyllables, syllableOnlyVowels, consonantsNasal
    result = result + consonantsNasal[random.randrange(0, len(consonantsNasal))]
    syllableOnlyVowels = 0
    vowelSyllables = 0

def maincongen():
    global result, randomLength, vowelRatio
    if len(result) < randomLength:
        randomNumber = random.randrange(0, vowelRatio)
        if randomNumber == 0:
            fricgen()
            if len(result) < randomLength:
                randomNumber = random.randrange(0, vowelRatio/4 * 3)
                if randomNumber == 0:
                    congen()
                    if len(result) < randomLength:
                        randomNumber = random.randrange(0, vowelRatio/2)
                        if randomNumber == 0:
                            con2gen()
                elif randomNumber == 1:
                    con2gen()
                elif randomNumber == 2:
                    con3gen()
        elif randomNumber == 1:
            congen()
            if len(result) < randomLength:
                randomNumber = random.randrange(0, vowelRatio/2)
                if randomNumber == 0:
                    con2gen()
        elif randomNumber == 2:
            con2gen()
        elif randomNumber == 3:
            con3gen()
