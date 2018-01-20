# Thesis

Code for my Thesis

* In this repository there are 4 different things:
	* Python code models
	* R data analysis code
	* Data from the models
	* Graphs of the data

* Models:
	* All models are meant to be run from the command line and take different command line arguments
	* These allow you to change the number of interactions, the global grouping percentage, the number of groups, and game specific variables
	* IPD-2.py:
		* This models the iterated prisoner’s dilemma
		* The model specific variables are the rewards for playing the IPD
	* Gifting-2.py:
		* This model is a game which allows agents to give their fitness to other agents
		* The model specific variables are the gift amount value, the multiplier (set to 1 in most cases), the starting fitness 
	* Public-2.py:
		* This models a standard public goods game between agents
		* The model specific variables are the maximum donation amount, agent’s starting fitness, the size of the groups made, and the pool multiplier

* R Code:
	* The R code gets the mean and SDs across all the different runs for the same generation
	* This is then used to create line graphs showing the means of the different individual variables with the SDs at each generation
	* Also shows the percent of time cooperation happened over a generation

* Data and Graphs:
	* All data and graphs are in folders that are named corresponding to what is in them
	
