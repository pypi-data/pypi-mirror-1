from random import random
from math import ceil

def decision(choice_count, reverse=False):
    '''
    Simply put, this is a funtion to whether something is decided
    to be True or False, given the number of choices in 'choice_count'.
    '''
    choice = bool(int(ceil(random()*choice_count)) % choice_count)
    if reverse: return not choice
    return choice

class Walk(object):
    '''

    '''
    def __init__(self, start=0, length=100, step=1, mpos=1, mneg=1, mres=1):
        self.setStartElement(start)
        self.setWalkLength(length)
        self.setStepLength(step)
        self.setMultipliers(mpos, mneg, mres)

    def setStartElement(self, element):
        self.start = element

    def setWalkLength(self, length):
        self.length = length

    def setStepLength(self, step):
        self.step = step

    def setPositiveMultiplier(self, pos):
        self.positive_multiplier = pos

    def setNegativeMultiplier(self, neg):
        self.negative_multiplier = neg

    def setResultMultiplier(self, res):
        self.result_multiplier = res

    def setMultipliers(self, pos, neg, res):
        self.setPositiveMultiplier(pos)
        self.setNegativeMultiplier(neg)
        self.setResultMultiplier(res)

    def nextStep(self, last_point, last_choice):
        new_point = last_point
        # let's do a 1 in two chance of choosing the same 'direction'
        # of the walk as last time
        if decision(2):
            new_point += self.step
            return (new_point, last_choice)
	# let's do another 1 in 2 chance, but this time to choose
	# which 'direction' to go in
        choice = decision(2)
        if choice:
            # positive direction
            new_point += self.step * random() * self.positive_multiplier
        else:
            # negative direction
            new_point -= self.step * random() * self.negative_multiplier
        return (new_point, choice)

    def getWalk(self):
        old = self.start
        choice = decision(2)
        for i in range(int(self.start), int(self.length)):
            new, choice = self.nextStep(old, choice)
            old = new
            yield new * self.result_multiplier

    def getWalkAsList(self):
        return list(self.getWalk())
