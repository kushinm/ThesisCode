import argparse
from recordtype import *
from random import *
from math import * 
import sys
import numpy

parser = argparse.ArgumentParser(description='Run iterrated prisoners dilemma model')
parser.add_argument('-n', default=50, help='NumInteraction value')
parser.add_argument('-w', default=0.5, help='Global Group value')
parser.add_argument('-g', default=10, help='Number of groups')
parser.add_argument('-r', default=3, help='Reward Payoff Value')
parser.add_argument('-t', default=5, help='Temptation Payoff Value')
parser.add_argument('-s', default=0, help='Sucker Payoff Value')
parser.add_argument('-p', default=1, help='Punishment payoff value')
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

		pop.append(Agent(lin,0,choice(groups),BaseRate,CoopRates,randTwo(),randTwo(),randTwo(),randTwo(),[random(),random()]))

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
		partnerCoops = (random() <= coopFunc(partner.CoopRates[x]))

		if agentCoops and partnerCoops:
			partner.Fitness += together
			agent.Fitness += together
			if RecipriSelection:
				partner.CoopRates[x] += partner.CoopChange
				agent.CoopRates[partnerInt] += agent.CoopChange
		elif agentCoops and not partnerCoops:
			partner.Fitness += tempt
			agent.Fitness += suckers
			if RecipriSelection:
				partner.CoopRates[x] += partner.CoopChange
				agent.CoopRates[partnerInt] += agent.DefectChange
		elif not agentCoops and partnerCoops:
			partner.Fitness += suckers
			agent.Fitness += tempt
			if RecipriSelection:
				partner.CoopRates[x] += partner.DefectChange
				agent.CoopRates[partnerInt] += agent.CoopChange
		elif not agentCoops and not partnerCoops:
			partner.Fitness += punish
			agent.Fitness += punish
			if RecipriSelection:
				partner.CoopRates[x] += partner.DefectChange
				agent.CoopRates[partnerInt] += agent.DefectChange

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
	newAgent = Agent(agent.Lineage,0,agent.Group,agent.BaseRate,agent.CoopRates,agent.KinChange,agent.CoopChange,agent.DefectChange,agent.GroupChange,[random(),random()])

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

def addDataSTD(pop,gen,world):
	output = "{E},{MF},{MB},{MK},{MC},{MD},{MG},{SF},{SB},{SK},{SC},{SD},{SG}"

	Fitnesses = []
	Bases = []
	Kins = []
	Coops = []
	Defects = []
	Groups = []

	for agent in pop:
		Fitnesses.append(agent.Fitness)
		Bases.append(agent.BaseRate)
		Kins.append(agent.KinChange)
		Coops.append(agent.CoopChange)
		Defects.append(agent.DefectChange)
		Groups.append(agent.GroupChange)

	Fitnesses = numpy.array(Fitnesses)
	Bases = numpy.array(Bases)
	Kins = numpy.array(Kins)
	Coops = numpy.array(Coops)
	Defects = numpy.array(Defects)
	Groups = numpy.array(Groups)

	print output.format( E = gen, MF = numpy.mean(Fitnesses), MB = numpy.mean(Bases), MK = numpy.mean(Kins), MC = numpy.mean(Coops), MD = numpy.mean(Defects), MG = numpy.mean(Groups), 
								  SF = numpy.std(Fitnesses), SB = numpy.std(Bases), SK = numpy.std(Kins), SC = numpy.std(Coops), SD = numpy.std(Defects), SG = numpy.std(Groups))


def runMany(num):
	for w in range(num):
		#print >> sys.stderr, "World:", w
		pop = setup(startPop)
		distArray = makeDistArray(pop)
		for g in range(gens):
			lastSize = len(pop)
			for i in range(numInteractions):
				pop = runInteraction(pop,distArray)
			addData(pop,g,w)
			#addDataSTD(pop,g,w)
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
mutationRate = 0.75					
globalGroup = float(args['w'])		
attemptsToFind = 25				
startPop = 100						
gens = 100							
worlds = 50

numInteractions = int(args['n'])

#IPD Rewards
suckers = int(args['s'])
tempt = int(args['t'])
punish = int(args['p'])
together = int(args['r'])

#print "Generation,Mean_Fitness,Mean_BaseRate,Mean_KinChange,Mean_CoopChange,Mean_DefectChange,Mean_GroupChange,SD_Fitness,SD_BaseRate,SD_KinChange,SD_CoopChange,SD_DefectChange,SD_GroupChange"

print "World,Generation,Fitness,BaseRate,KinChange,CoopChange,DefectChange,GroupChange"

seed(7)
runMany(worlds)





