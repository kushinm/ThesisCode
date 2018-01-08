import argparse
from recordtype import *
from random import *
from math import * 
import sys

parser = argparse.ArgumentParser(description='Run iterrated prisoners dilemma model')
parser.add_argument('-n', default=50, help='NumInteraction value')
parser.add_argument('-w', default=0.75, help='Global Group value')
parser.add_argument('-g', default=20, help='Number of groups')
parser.add_argument('-a', default=3, help='Gift Amount Value')
parser.add_argument('-m', default=3, help='Gift Multiplier Value')
parser.add_argument('-f', default=50, help='Starting Fitness')

args = vars(parser.parse_args())

Agent = recordtype("Agent","Lineage Fitness Group BaseRate CoopRates KinChange CoopChange DefectChange GroupChange Pos")

def randTwo():
	val = randint(-100,100)
	val = val/100.0
	return val

def coopFunc(val):
	newVal = 1/(1+e**((-5*val)+2.5))
	return newVal

def setup(numStart):
	pop = []

	for x in range(0,numStart):
		BaseRate = randTwo()
		CoopRates = []
		lin = x
		for x in range(0,numStart):
			CoopRates.append(BaseRate)

		pop.append(Agent(lin,fitStart,choice(groups),BaseRate,CoopRates,randTwo(),randTwo(),randTwo(),randTwo(),[random(),random()]))

	for x in range(0,numStart):
		agent = pop[x]
		for y in range(0,numStart):
			partner = pop[y]
			coopChance = agent.CoopRates[y]
			if KinSelection and partner.Lineage == agent.Lineage:
				coopChance += agent.KinChange
			if GroupSelection and partner.Group == agent.Group:
				coopChance += agent.GroupChange

			agent.CoopRates[y] = coopChance

	return pop

def makeDistArray(pop):
	popSize = len(pop)

	distArray = [[0 for x in range(popSize)] for y in range(popSize)]

	for x in range(popSize):
		for y in range(popSize):
			distArray[x][y] = dist(pop[x].Pos,pop[y].Pos)

	for x in range(popSize):
		for y in range(popSize):
			if distArray[x][y] == 0:
				pass
			else:
				distArray[x][y] = 1/distArray[x][y]

	for x in range(popSize):
		sumDist = sum(distArray[x])
		for y in range(popSize):
			distArray[x][y] = distArray[x][y]/sumDist

	return(distArray)


def dist(pos1,pos2):
	X1 = pos1[0]
	X2 = pos2[0]
	Y1 = pos1[1]
	Y2 = pos2[1]

	return sqrt((X1 - X2)**2 + (Y1 - Y2)**2)	

def runInteraction(pop,distArray):
	popSize = len(pop)

	inGroup = False

	for x in range(popSize):
		agent = pop[x]

		if random() <= globalGroup:
			inGroup = True
		
		desire = random()
		for y in range(0,popSize):
			if desire > 0:
				desire -= distArray[x][y]
				if desire <= 0:
					partnerInt = y
					partner = pop[partnerInt]
		
		count = 0
		while (count < attemptsToFind) and ((inGroup and partner.Group != agent.Group) or (not inGroup and partner.Group == agent.Group)):
			desire = random()
			for y in range(0,popSize):
				if desire > 0:
					desire -= distArray[x][y]
					if desire <= 0:
						partnerInt = y
						partner = pop[partnerInt]
			count += 1

		agentCoops = (random() <= coopFunc(agent.CoopRates[partnerInt]))

		if random() <= agent.CoopRates[partnerInt]:
			if agent.Fitness < giftAmount:
				agent.Fitness -= agent.Fitness
				partner.Fitness += agent.Fitness * giftMultiplier
			else:
				agent.Fitness -= giftAmount
				partner.Fitness += giftAmount * giftMultiplier
			if RecipriSelection:
				partner.CoopRates[x] += partner.CoopChange
				if partner.CoopRates[x] > 1:
					partner.CoopRates[x] = 1
				elif partner.CoopRates[x] < 0:
					partner.CoopRates[x] = 0
			#print "{} gave to {}!".format(x,partnerInt)
		else:
			if RecipriSelection:
				partner.CoopRates[x] += partner.DefectChange
				if partner.CoopRates[x] > 1:
					partner.CoopRates[x] = 1
				elif partner.CoopRates[x] < 0:
					partner.CoopRates[x] = 0
			#print "{} didn't gave to {}.".format(x,partnerInt)

	return pop

def processPop(pop):
	fitnesses = []
	
	newPop = []

	for agent in pop:
		fitnesses.append(agent.Fitness)

	sumFit = (sum(fitnesses)*1.0)+0.0000000001

	for x in range(len(fitnesses)):
		fitnesses[x] = fitnesses[x]/sumFit

	for s in range(startPop):
		desire = random()
		for x in range(len(fitnesses)):
			if desire > 0:
				desire -= fitnesses[x]
				if desire <= 0:
					newPop.append(makeNewAgent(pop[x]))


	for x in range(0,startPop):
		agent = newPop[x]
		for y in range(0,startPop):
			partner = newPop[y]
			coopChance = agent.CoopRates[y]
			if KinSelection and partner.Lineage == agent.Lineage:
				coopChance += agent.KinChange
			if GroupSelection and partner.Group == agent.Group:
				coopChance += agent.GroupChange

			agent.CoopRates[y] = coopChance

	return newPop

def makeNewAgent(agent):
	newAgent = Agent(agent.Lineage,fitStart,agent.Group,agent.BaseRate,agent.CoopRates,agent.KinChange,agent.CoopChange,agent.DefectChange,agent.GroupChange,[random(),random()])

	if random() <= mutationRate:
		muteType = randint(0,6)
		if muteType == 0:
			newAgent.Group = choice(groups)
		elif muteType == 1:
			newAgent.BaseRate = randTwo()
		elif muteType == 2:
			newAgent.KinChange = randTwo()
		elif muteType == 3:
			newAgent.CoopChange = randTwo()
		elif muteType == 4:
			newAgent.DefectChange = randTwo()
		elif muteType == 5:
			newAgent.GroupChange = randTwo()

	newCoop = []

	for x in range(0,startPop):
		newCoop.append(newAgent.BaseRate)

	newAgent.CoopRates = newCoop

	return newAgent

def addData(pop,gen,world):
	output = "{W},{E},{F},{B},{K},{C},{G},{D}"
	popSize = len(pop)*1.0
	Fitness = 0
	Base = 0
	Kin = 0
	Coop = 0
	Defect = 0
	Group = 0

	for agent in pop:
		Fitness += agent.Fitness/popSize
		Base += agent.BaseRate/popSize
		Kin += agent.KinChange/popSize
		Coop += agent.CoopChange/popSize
		Defect += agent.DefectChange/popSize
		Group += agent.GroupChange/popSize

	print output.format(F = Fitness, B = Base, K = Kin, C = Coop, D = Defect, G = Group, E = gen, W = world)

def runMany(num):
	for w in range(num):
		pop = setup(startPop)
		distArray = makeDistArray(pop)
		for g in range(gens):
			lastSize = len(pop)
			for i in range(numInteractions):
				pop = runInteraction(pop,distArray)
			addData(pop,g,w)
			pop = processPop(pop)
			distArray = makeDistArray(pop)
		progress(w)
			
def progress(world):
    bar_len = 60
    filled_len = int(round(bar_len * world / float(worlds-1)))

    percents = round(100.0 * world / float(worlds-1), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stderr.write('[%s] %s%s\r' % (bar, percents, '%'))
    sys.stderr.flush()


KinSelection = True
RecipriSelection = True
GroupSelection = True
									
numGroups = int(args['g'])						
groups = []					
for x in range(0,numGroups):
	groups.append(str(x))
mutationRate = 1					
globalGroup = int(args['w'])		
attemptsToFind = 25				
startPop = 100						
gens = 100							
worlds = 50

numInteractions = int(args['n'])

#Gift Rewards
giftAmount = int(args['a'])
giftMultiplier = int(args['m'])
fitStart = int(args['f'])


print "World,Generation,Fitness,BaseRate,KinChange,CoopChange,DefectChange,GroupChange"

seed(77)
runMany(worlds)





