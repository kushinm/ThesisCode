import sys
import string
import argparse

from recordtype import *
from random import *
from math import * 

seed(7)
print "World,Generation,Fitness,BaseRate,KinChange,CoopChange,DefectChange,GroupChange,CoopPercent,DefectPercent"

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#-----------------------------------PARSER-------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Runs either an IPD, Gift Giving, or Public Goods game model')
parser.add_argument('-n', default=50, help='NumInteraction value')
parser.add_argument('-w', default=0.5, help='Global Group value')
parser.add_argument('-g', default=10, help='Number of groups')

parser.add_argument('-r', default=3, help='Reward Payoff Value (IPD Only)')
parser.add_argument('-t', default=5, help='Temptation Payoff Value (IPD Only)')
parser.add_argument('-s', default=0, help='Sucker Payoff Value (IPD Only)')
parser.add_argument('-p', default=1, help='Punishment payoff value (IPD Only)')

parser.add_argument('-a', default=10, help='Max Contribution Amount (Gifting and Public Goods)')
parser.add_argument('-f', default=50, help='Starting Fitness (Gifting and Public Goods)')

parser.add_argument('-o', default=10, help='Pool Group Size (Public Goods Only)')
parser.add_argument('-m', default=1.75, help='Pool Multiplier Value (Public Goods Only)')

parser.add_argument('-kin', default=True, help='Allows Kin Selection')
parser.add_argument('-recip', default=True, help='Allows Reciprocal Selection')
parser.add_argument('-group', default=True, help='Allows Group Selection')
parser.add_argument('-game', default="None", help='Selects game (type "IPD","GIFT", or "PG")')

args = vars(parser.parse_args())

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#---------------------------GLOBAL VARIABLES-----------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

Agent = recordtype("Agent","Lineage Fitness Group BaseRate CoopRates KinChange CoopChange DefectChange GroupChange Pos CoopTimes DefectTimes")

letters = list(string.ascii_uppercase)
charIDs = []

for L in letters:
	for l in letters:
		charIDs.append(L+l)

#Constants
mutationRate = 0.9
attemptsToFind = 25				
startPop = 10						
gens = 50							
worlds = 50	
mutateSD = 0.05

#Based on Args

#All Games
numInteractions = int(args['n'])
globalGroup = float(args['w'])	
numGroups = int(args['g'])						

#IPD Rewards
together = int(args['r'])
tempt = int(args['t'])			
suckers = int(args['s'])
punish = int(args['p'])

#PG and Gifting Varibles
maxContributeAmount = int(args['a'])
fitStart = int(args['f'])

#Public Goods Varibles
poolSize = int(args['o'])
poolMultiplier = float(args['m'])

#Selection Types
KinSelection = bool(args['kin'])
RecipriSelection = bool(args['recip'])
GroupSelection = bool(args['group'])

#Game Type
gameName = args['game']

#Making Groups
groups = []					
for x in range(0,numGroups):
	groups.append(str(x))


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#---------------------------HELPER FUNCTIONS-----------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


def randTwo():
	#Gets random float between -1 and 1
	#Random() doesn't go negative
	val = randint(-100,100)
	val = val/100.0
	return val

def runInteraction(a,b):
	pass

def guassMutate(val):
	#gets a new value with the mean val and sd of sd
	# caps at 1 and -1
	top = 1
	bottom = -1

	newVal = max(min(gauss(val,mutateSD),top),bottom)

	return newVal


def coopFunc(val):
	#This is a bit of a cheat here as if val < -140 the exponent 
	# is to large and this crashes. But at -140 they are still never going
	# to cooperate, so this should be fine?
	if val < -140:
		val = -140

	#This function determines the probability from 0 to 1
	# of cooperation occuring. Check desmos graphs for
	# better reasons or pictures
	newVal = 1/(1+e**((-5*val)+2.5))
	return newVal

def compKin(mainLin,compLin):
	#This compares the lianges of individuals to see when they last
	# had a common ancestor. I do the split(".") so as to get an array 
	# and to make it easier to read later.
	mainLin = mainLin.split(".")
	compLin = compLin.split(".")
	if mainLin[0] != compLin[0]:
		return 100

	same = 0

	length = len(mainLin)

	for x in range(length):
		if mainLin[x] == compLin[x]:
			same += 1
		else:
			break
	
	return length-same

def dist(pos1,pos2):
	#Calcualtes distance between 2 points

	X1 = pos1[0]
	X2 = pos2[0]
	Y1 = pos1[1]
	Y2 = pos2[1]

	return sqrt((X1 - X2)**2 + (Y1 - Y2)**2)

def makeDistArray(pop):
	popSize = len(pop)

	#Makes 2D array that is popSize by popSize
	distArray = [[0 for x in range(popSize)] for y in range(popSize)]

	#Fills array in with distance between the two agents
	for x in range(popSize):
		for y in range(popSize):
			distArray[x][y] = dist(pop[x].Pos,pop[y].Pos)

	#Changes the distances to 1/distance
	#This makes smaller distance take up more of the 
	# later distArray
	for x in range(popSize):
		for y in range(popSize):
			if distArray[x][y] == 0:
				pass
			else:
				distArray[x][y] = 1/distArray[x][y]

	#Sums all the distances and then divides each point by that
	# so that all the distances added together equals 1.
	#So then it is like a roulette wheel where smaller distances take
	# up more space
	for x in range(popSize):
		sumDist = sum(distArray[x])
		for y in range(popSize):
			distArray[x][y] = distArray[x][y]/sumDist

	return(distArray)	

def progress(world):
	#This prints a progress bar and doesn't print to the output 
	# file by using stderr instead of stdout
	world = world+1
	bar_len = 60
	filled_len = int(round(bar_len * world / float(worlds)))

	percents = round(100.0 * world / float(worlds), 1)
	bar = '=' * filled_len + '-' * (bar_len - filled_len)

	sys.stderr.write('[%s] %s%s\r' % (bar, percents, '%'))
	sys.stderr.flush()

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#----------------------------ALL MODEL FUNCTIONS-------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


def setup(numStart):
	#Makes a whole new beginnign population
	pop = []

	#Makes all the agents with base rates and coopRates based on that
	# then fills out whole random agent
	for x in range(0,numStart):
		BaseRate = randTwo()
		CoopRates = []
		lin = charIDs[x]
		for x in range(0,numStart):
			CoopRates.append(BaseRate)

		pop.append(Agent(lin,fitStart,choice(groups),BaseRate,CoopRates,randTwo(),randTwo(),randTwo(),randTwo(),[random(),random()],0,0))

	#Changes CoopRates based on whether the other
	# agents are in the same group and Lineage
	for x in range(0,numStart):
		agent = pop[x]
		for y in range(0,numStart):
			partner = pop[y]
			coopChance = agent.CoopRates[y]
			if KinSelection and x != y:
				coopChance += agent.KinChange/compKin(agent.Lineage,partner.Lineage)
			if GroupSelection and partner.Group == agent.Group:
				coopChance += agent.GroupChange

			agent.CoopRates[y] = coopChance

	return pop

def processPop(pop):
	fitnesses = []
	newPop = []

	#Adds the fitness of each agent to the list
	for agent in pop:
		fitnesses.append(agent.Fitness)

	#The total sum of all fitnesses is found
	# the tiny amount is added so that when it is divided by
	# if it is 0 then it doesn't give an error
	#Though that would mean no one in the population
	# had any fitness which would be bad.
	sumFit = (sum(fitnesses)*1.0)+0.0000000001

	#Makes all the fitnesses sum to 1
	for x in range(len(fitnesses)):
		fitnesses[x] = fitnesses[x]/sumFit

	#Generates a random number to pick an agent from the
	# "roulette wheel" to reporduce
	# New agent is made with the one selected as a template
	for s in range(startPop):
		desire = random()
		for x in range(len(fitnesses)):
			if desire > 0:
				desire -= fitnesses[x]
				if desire <= 0:
					newPop.append(makeNewAgent(pop[x],charIDs[s]))

	#This sets the CoopRates for each agent in the new popualtion based on 
	# the other agents in the popualtion
	#And based on which other selections are active.
	for x in range(0,startPop):
		agent = newPop[x]
		for y in range(0,startPop):
			partner = newPop[y]
			coopChance = agent.CoopRates[y]
			if KinSelection and x != y:
				coopChance += agent.KinChange/compKin(agent.Lineage,partner.Lineage)
			if GroupSelection and partner.Group == agent.Group:
				coopChance += agent.GroupChange

			agent.CoopRates[y] = coopChance

	return newPop

def makeNewAgent(agent,newID):
	#Makes a new agent from the old agent. Resets CoopTimes and DefectTimes, as well as fitness
	newAgent = Agent(agent.Lineage+"."+newID,fitStart,agent.Group,agent.BaseRate,agent.CoopRates,agent.KinChange,agent.CoopChange,agent.DefectChange,agent.GroupChange,[random(),random()],0,0)

	#Picks one mutation type if one occurs
	# Mutates it using a Guassian curve
	if random() <= mutationRate:
		muteType = randint(0,6)
		if muteType == 0:
			newAgent.Group = choice(groups)
		elif muteType == 1:
			newAgent.BaseRate = guassMutate(agent.BaseRate)
		elif muteType == 2:
			newAgent.KinChange = guassMutate(agent.KinChange)
		elif muteType == 3:
			newAgent.CoopChange = guassMutate(agent.CoopChange)
		elif muteType == 4:
			newAgent.DefectChange = guassMutate(agent.DefectChange)
		elif muteType == 5:
			newAgent.GroupChange = guassMutate(agent.GroupChange)

	newCoop = []

	#Resets the cooperation rates for each agent in reation to each other one
	for x in range(0,startPop):
		newCoop.append(newAgent.BaseRate)

	newAgent.CoopRates = newCoop

	return newAgent

def addData(pop,gen,world):
	#Makes an output format 
	output = "{W},{E},{F},{B},{K},{C},{G},{D},{CT},{DT}"

	#Sets varibles to record data in
	popSize = len(pop)*1.0
	Fitness = 0
	Base = 0
	Kin = 0
	Coop = 0
	Defect = 0
	Group = 0
	CoopPercent = 0
	DefectPercent = 0

	if gameName == "IPD":
		popMod = 2.0
	else:
		popMod = 1.0

	#Gets the information for each agent and divides it by the popSize 
	# in order to get an average for the population
	for agent in pop:
		Fitness += agent.Fitness/popSize
		Base += agent.BaseRate/popSize
		Kin += agent.KinChange/popSize
		Coop += agent.CoopChange/popSize
		Defect += agent.DefectChange/popSize
		Group += agent.GroupChange/popSize
		CoopPercent += agent.CoopTimes/(numInteractions*popMod*popSize)
		DefectPercent += agent.DefectTimes/(numInteractions*popMod*popSize)

	print output.format(F = Fitness, B = Base, K = Kin, C = Coop, D = Defect, G = Group, E = gen, W = world, CT = CoopPercent, DT = DefectPercent)

def runMany(num):
	#For each world....
	for w in range(num):
		#create a pop
		pop = setup(startPop)
		#find the distances 
		distArray = makeDistArray(pop)
		#for each generation...
		for g in range(gens):
			shuffle(charIDs)
			#run the right number of interactions for each agent
			for i in range(numInteractions):
				#Change the popualtion based on the results of the interactions
				pop = runInteraction(pop,distArray)
			#Add the data to the output
			addData(pop,g,w)
			#process popualtion to make next gen
			pop = processPop(pop)
			#make a new dist array
			distArray = makeDistArray(pop)
		#When you finish a world increment the progress bar
		progress(w)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------SPECIFIC GAME FUNCTIONS-------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def runGift(pop,distArray):
	popSize = len(pop)

	inGroup = False

	#Does an interaction for each agent in the generation
	for x in range(popSize):
		agent = pop[x]

		#Determines if getting partner from same group or different group
		if random() <= globalGroup:
			inGroup = True
		
		#Gets the desired distance
		desire = random()

		#Randomly selects an agent based on the distArray roulette wheel
		# see makeDistArray for details
		for y in range(0,popSize):
			if desire > 0:
				desire -= distArray[x][y]
				if desire <= 0:
					partnerInt = y
					partner = pop[partnerInt]
		
		count = 0
		#Tried to find a partner using the roulette method that is correctly
		# in the group when they should be or out of the group when that shoudl be the case
		while (count < attemptsToFind) and ((inGroup and partner.Group != agent.Group) or (not inGroup and partner.Group == agent.Group)):
			desire = random()
			for y in range(0,popSize):
				if desire > 0:
					desire -= distArray[x][y]
					if desire <= 0:
						partnerInt = y
						partner = pop[partnerInt]
			count += 1

		#Determines if the agent cooperates or not
		agentCoops = (random() <= coopFunc(agent.CoopRates[partnerInt]))

		giftAmount = agent.CoopRates[partnerInt] * maxContributeAmount

		if giftAmount > 0:
			#increases the number of tiems cooperated
			agent.CoopTimes += 1

			#Gives the gift amount. If the agent doesn't have
			# enough it gives what it has
			if agent.Fitness < giftAmount:
				agent.Fitness -= agent.Fitness
				partner.Fitness += agent.Fitness
			else:
				agent.Fitness -= giftAmount
				partner.Fitness += giftAmount

			#If reciprocal selection is on then add coop change to partner
			if RecipriSelection:
				partner.CoopRates[x] += partner.CoopChange
			#print "{} gave to {}!".format(x,partnerInt)
		else:
			#increases the number of tiems defected
			agent.DefectTimes += 1
			#If reciprocal selection is on then add Defect Change to partner
			if RecipriSelection:
				partner.CoopRates[x] += partner.DefectChange
			#print "{} didn't gave to {}.".format(x,partnerInt)

	return pop

def runIPD(pop,distArray):
	popSize = len(pop)

	inGroup = False

	#Does an interaction for each agent in the generation
	for x in range(popSize):
		agent = pop[x]

		#Determines if getting partner from same group or different group
		if random() <= globalGroup:
			inGroup = True
		
		#Gets the desired distance
		desire = random()

		#Randomly selects an agent based on the distArray roulette wheel
		# see makeDistArray for details
		for y in range(0,popSize):
			if desire > 0:
				desire -= distArray[x][y]
				if desire <= 0:
					partnerInt = y
					partner = pop[partnerInt]
		
		count = 0
		#Tried to find a partner using the roulette method that is correctly
		# in the group when they should be or out of the group when that shoudl be the case
		while (count < attemptsToFind) and ((inGroup and partner.Group != agent.Group) or (not inGroup and partner.Group == agent.Group)):
			desire = random()
			for y in range(0,popSize):
				if desire > 0:
					desire -= distArray[x][y]
					if desire <= 0:
						partnerInt = y
						partner = pop[partnerInt]
			count += 1

		#Randomly determines if agent shoudl cooperate or not based on their
		# CoopRate for their partner
		agentCoops = (random() <= coopFunc(agent.CoopRates[partnerInt]))
		partnerCoops = (random() <= coopFunc(partner.CoopRates[x]))

		#So based on who cooperates agents get rewarded
		#If both cooperate they get the "together" reward (R)
		#If one defects and the otehr cooperates and the other defects
		# the defecting one gets the "tempt" reward (T) and the other gets
		# the "sucker" reward (S)
		#If they both defect then they both get the "punish" reward (P)
		#
		#If Reciprocal Selection is active then their CoopRates are changed
		#Also now the number of times they cooperated and defected are increased
		if agentCoops and partnerCoops:
			partner.Fitness += together
			agent.Fitness += together
			partner.CoopTimes += 1
			agent.CoopTimes += 1
			if RecipriSelection:
				partner.CoopRates[x] += partner.CoopChange
				agent.CoopRates[partnerInt] += agent.CoopChange
		elif agentCoops and not partnerCoops:
			partner.Fitness += tempt
			agent.Fitness += suckers
			partner.DefectTimes += 1
			agent.CoopTimes += 1
			if RecipriSelection:
				partner.CoopRates[x] += partner.CoopChange
				agent.CoopRates[partnerInt] += agent.DefectChange
		elif not agentCoops and partnerCoops:
			partner.Fitness += suckers
			agent.Fitness += tempt
			partner.CoopTimes += 1
			agent.DefectTimes += 1
			if RecipriSelection:
				partner.CoopRates[x] += partner.DefectChange
				agent.CoopRates[partnerInt] += agent.CoopChange
		elif not agentCoops and not partnerCoops:
			partner.Fitness += punish
			agent.Fitness += punish
			partner.DefectTimes += 1
			agent.DefectTimes += 1
			if RecipriSelection:
				partner.CoopRates[x] += partner.DefectChange
				agent.CoopRates[partnerInt] += agent.DefectChange

	return pop


def runPG(pop,distArray):
	popSize = len(pop)

	#Each interaction selects a group of individuals to share a pool
	# Selects a group of agents equal to poolSizr
	select = sample(range(0,popSize),poolSize)
	donationChances = []
	didDonate = []

	pool = 0

	#For each agent in the selection figure out the average cooperation 
	# feeling for the population. That is added to donation chances
	# after running through the CoopFunc
	for x in range(0,poolSize):
		coopAll = 0
		agent = pop[select[x]]
		for y in range(0,poolSize):
			if x != y:
				coopAll += agent.CoopRates[select[y]]/(poolSize*1.0)
		donationChances.append(coopFunc(coopAll))

	#The donation chance allows the agent to donate a fraction of the 
	# max donation amount to the pool. If they donate 5 or over they
	# are considered to have cooperated.
	for x in range(0,poolSize):
		agent = pop[select[x]]
		donateAmount = donationChances[x] * maxContributeAmount

		if agent.Fitness >= donateAmount:
			pool += donateAmount
			agent.Fitness -= donateAmount
		else:
			pool += agent.Fitness
			agent.Fitness = 0

		if donateAmount >= 5:
			didDonate.append(True)
			agent.CoopTimes += 1
		else:
			didDonate.append(False)
			agent.DefectTimes += 1

	#Payout is the calcualted
	payout = (pool*poolMultiplier)/(poolSize*1.0)

	#Then each agent is paid out from the pool 
	# Then the agent's cooperation is adjusted dependant 
	# on whether other donated. So this isn't secret.
	for x in range(0,poolSize):
		coopAll = 0
		agent = pop[select[x]]
		agent.Fitness += payout
		for y in range(0,poolSize):
			if x != y:
				if didDonate[y]:
					agent.CoopRates[select[y]] += agent.CoopChange
				elif not didDonate[y]:
					agent.CoopRates[select[y]] += agent.DefectChange

	return pop

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#-------------------------LAST SETUP AND RUNNING-------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

#Selects Game:
if gameName == "None":
	print "Please Pick A Game"
	sys.exit()
elif gameName.upper() == "GIFT":
	runInteraction = runGift
elif gameName.upper() == "IPD":
	runInteraction = runIPD
	fitStart = 0
elif gameName.upper() == "PG":
	runInteraction = runPG
else:
	print "Please select IPD,PG,or GIFT"

runMany(worlds)