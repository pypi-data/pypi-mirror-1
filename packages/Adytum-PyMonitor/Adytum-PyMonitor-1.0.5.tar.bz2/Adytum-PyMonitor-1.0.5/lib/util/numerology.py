ASCII_BASE = 97
BASE_SUBTR = ASCII_BASE - 1
NUMEROL_MODULUS = 9
DEBUG = False

def getLetterNumber(letter):
    return ord(letter.lower()) - BASE_SUBTR

def reduceLetterToNumber(letter):
    mod = getLetterNumber(letter) % NUMEROL_MODULUS
    if not mod:
        mod = NUMEROL_MODULUS
    if DEBUG:
        print "%s = %d" % (letter, mod)
    return mod

def reduceDigits(number):
    number = str(number)
    if len(number) == 1: 
        return number
    else:
        total = sum([ int(x) for x in str(number) ])
        return reduceDigits(total)

def numerolSum(letter_list):
    number_list = [ reduceLetterToNumber(letter) for letter in letter_list ]
    total = sum(number_list)
    return reduceDigits(total)

def makeLetterList(word):
    return [ letter for letter in word ]

def makeWordList(words):
    return [ word for word in words.split(' ') ]

def getNumerologicalValue(words):
    result = ''
    num_list = []
    for word in makeWordList(words):
        letter_list = makeLetterList(word)
        word_sum =  numerolSum(letter_list)
        num_list.append(word_sum)
        if DEBUG:
            print "%s\n%s\n%s\n" % (str(letter_list), str(word_sum), str(num_list))
        result += '%s (%s)\n' % (str(word_sum), word)
    if DEBUG:
        print result
    return int(''.join([str(integer) for integer in num_list]))
