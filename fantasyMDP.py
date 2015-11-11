import collections, util, math, random
import classes, scoring
import copy
import os
import glob
import re
from collections import defaultdict
import unicodedata

# to compute 15-man roster from available players
class ComputeRosterMDP(util.MDP):

	def __init__(self, players, budget, allTeams, allPlayers):
		self.allPlayers = allPlayers
		self.allTeams=allTeams
		self.players=players
		self.budget=budget
		self.maxPositions={'GK': 2, 'DEF': 5, 'MID': 5, 'STR': 3}

	# a state = (roster, budget, positions, teams)
	# roster -- a list of class Player that represents the players we have 
	#			chosen for our roster thus far
	# budget -- (int) how much money we have left to spend
	# positions -- a dict {"GK":num1; "DEF":num2; "MID":num3; "STR":num4}, where 
	#				num1 = number of goalkeepers on roster
	#				num2 = number of defenders on roster
	#				num3 = number of midfielders on roster
	#				num4 = number of forwardss on roster
	# teams -- dict: {classes.Team: int(number of players from that team on our roster)}
	#			(we can only choose up to 3 players from each Premier league
	#			team to put on our roster)
	def startState(self):
		teams = {t:0 for t in self.allTeams}
		positions = {pos:0 for pos in self.maxPositions}
		return ([], self.budget, positions ,teams)

	#------------League Constraints on Roster--------------#
	# 1) 2 goalkeepers
	# 2) 5 defenders
	# 3) 5 midfielders
	# 4) 3 forwards
	# 5) budget = 100million
	# 6) Can select up to 3 players from a single Premier League team
	def actions(self,state):
		# actions = []		
		# stateRoster, stateBudget, statePositions, stateTeams = state
		# for playerName in self.allPlayers:
		# 	p = self.allPlayers[playerName]
		# 	if p not in state[0]: #if not in roster yet
		# 		positionConstraint = (statePositions[p.position] < self.maxPositions[p.position])
		# 		budgetConstraint = (p.price < stateBudget)
		# 		teamConstraint = (stateTeams[p.team] < 3)
		# 		if positionConstraint and budgetConstraint and teamConstraint:
		# 			actions.append(p)

		# TO DO: experiment. Just always return all possible players
		#        satisfy constraints in succAndProbReward
		#        just like we did in blackjack
		actions = [self.allPlayers[playerName] for playerName in self.allPlayers]
		return actions

	def succAndProbReward(self, state, action):
		# if roster is full
		if len(state[0]) == 15:
			return []

		validPlayer = False
		stateRoster, stateBudget, statePositions, stateTeams = state
		if action not in state[0]: # if not in roster yet
			positionConstraint = (statePositions[p.position] < self.maxPositions[p.position])
			budgetConstraint = (p.price < stateBudget)
			teamConstraint = (stateTeams[p.team] < 3)
			if positionConstraint and budgetConstraint and teamConstraint:
				validPlayer = True
		
		if not validPlayer:
			return []

		# compute new state
		newRoster = state[0]
		newRoster.append(action)
		newBudget = state[1]-action.price
		newPositions = state[2]
		newPositions[action.position] += 1
		newTeams = state[3]
		newTeams[action.team] += 1
		newState = (newRoster, newBudget, newPositions, newTeams)

		# TO DO: Finish reward function
		# reward = 0 
		# goalsScoredWeight = 0
		# if action.position == "GK" or action.position == "DEF":
		# 	goalsScoredWeight = 6
		# elif action.position == "MID":
		# 	goalsScoredWeight = 5
		# else:
		# 	goalsScoredWeight = 4

		# weights={'playedInGame': 1, 'played60Min': 2, 'goalsScored': goalsScoredWeight, \
		# 	'penaltiesReceived' : 1, 'penaltiesConceded': -1, \
		# 	'goalsConceded' : -1, 'yellowCard' : -1, 'redCard':-3, \
		# 	'savesByGK': 1}

		# # commented out features that we may not have stats for
		# # TO DO: some of these are in team stats. Should we use that?

		# playedInGame = False 	# 1pt, M > 0
		# played60Min = False		# 2pt, M >= 60
		# goalsScored = 0			# 6pt if GK or DEF, 5pt if MID, 4 if STR, G & position
		# # assists = 0				# 3pt
		# # noScoreOnGK = False		# 4pt if played 60min
		# # noScoreOnDEF = False	# 4pt if played 60min
		# # noScoreOnMID = False	# 1pt if played 60min
		# penaltiesReceived = 0	# 1pt, FS?
		# penaltiesConceded = 0	# -1pt, FC?
		# # penaltyMisses = 0		# -2pt
		# # penaltySaves = 0		# 5pt
		# # goalsConceded = 0		# -1pt/2goals for GK or MID
		# yellowCard = False		# -1pt, Y
		# redCard = False			# -3pt, R
		# savesByGK = 0			# 1pt/3saves, AB & position is GK
		# # recoveredBalls = 0		# 1pt/5balls

		# # get corresponding feature vector from all_player_features
		# # get feature num to acronym
		# player_ft_values = all_player_features[action.name + "-" + action.team]
		# ft_vector = {}
		# for ft in player_ft:
		# 	ft_acro = feature_num_to_acro[ft]
		# 	if ft_acro == 'M':
		# 		if player_ft[ft] > 0:
		# 			ft_vector['playedInGame'] = 1
		# 		if player_ft[ft] >= 60:
		# 			ft_vector['played60Min'] = 1
		# 	elif ft_acro == 'G':
		# 		ft_vector['goalsScored'] = player_ft[ft]
		# 	elif ft_acro == 'FS':
		# 		ft_vector['penaltiesReceived'] = player_ft[ft]
		# 	elif ft_acro == 'FC':
		# 		ft_vector['penaltiesConceded'] = player_ft[ft]
		# 	elif ft_acro == 'Y':
		# 		ft_vector['yellowCard'] = player_ft[ft]
		# 	elif ft_acro == 'R':
		# 		ft_vector['redCard'] = player_ft[ft]
		# 	elif ft_acro == 'AB':
		# 		if action.position == "GK":
		# 			ft_vector['penaltiesReceived'] = player_ft[ft] / 3.0

		# # dot vector feature and weights
		# for ft in ft_vector:
		# 	reward += weights[ft] * ft_vector[ft]

		# TO DO: confused. This basically looks like the featureExtractor
		# for now, let's say reward is -price
		reward = -1 * action.price

		return [(newState, 1, reward)]

	def discount(self):
		return 1

class ComputeMatchLineupMDP(util.MDP):
	def __init__(self, roster, budget):
		self.roster=roster
		self.budget=budget

	def startState(self):
		return ([],self.budget)

	def actions(self,state):
		return None

	def succAndProbReward(self, state, action):
		return None

#store all player data
players = {}

# list of all players as Players
allPlayers = {}

# for positions, only last names are included along with price, team, and position
lines = [line.rstrip('\n') for line in open('fantasy_player_data/positions/defenders')]
lines = lines + [line.rstrip('\n') for line in open('fantasy_player_data/positions/forwards')]
lines = lines + [line.rstrip('\n') for line in open('fantasy_player_data/positions/goalkeepers')]
lines = lines + [line.rstrip('\n') for line in open('fantasy_player_data/positions/midfielders')]

# compare ignoring accented characters
def check_for_accented_key(k, d):
	for key in d:
		u1 = unicodedata.normalize('NFC', k.decode('utf-8'))
		u2 = unicodedata.normalize('NFC', key.decode('utf-8'))
		if u1 == u2:
			return d[key]
	raise "Couldn't find team name"

# team_to_player_num[team][player_last_name] = player_num
team_to_player_num = defaultdict(lambda: defaultdict(str))

# team_to_player_name[team][player_num] = player_name
team_to_player_name = defaultdict(lambda: defaultdict(str))
# all_player_list includes first and last names for players, player numbers, and teams
all_player_lines = [line.rstrip() for line in open("fantasy_player_data/all_players/all_player_list", 'r')]

for line in all_player_lines[1:]:
	num, name, team = line.rstrip().split(",")

	# get rid of trailing whitespace
	name = re.sub("\s*$", "", name)
	if " " in name:
		last_name = (re.match(".* (.*)$", name)).group(1)
	else: last_name = name

	team_to_player_num[team][last_name] = num
	team_to_player_name[team][num] = name

# team name as String -> Team object
allTeams = {}

# store basic player data
# add players to their corresponding Teams
for line in lines:
	last_name, team, position, price = line.rstrip().split(", ")
	price = float(price)
	team_dict = check_for_accented_key(team, team_to_player_num);

	num = team_dict[last_name]
	p = classes.Player(last_name, num, team, position, price)

	# store player_name-player_num-player_team = Player object
	key = last_name + "-" + num + "-" + team
	allPlayers[key] = p

	if team not in allTeams:
		allTeams[team] = classes.Team(team, [])

	allTeams[team].addPlayer(p)

# all_player_features[player_num + "-" + team] = {ft_num:ft:value}
all_player_features = defaultdict(lambda: defaultdict(float))

# stores feature number -> feature acronym
feature_num_to_acro = {}
team_to_num_games = defaultdict(float)
for matchday in os.listdir("player_statistics/2015-16/"):
	if matchday.endswith(".py")==False and matchday.endswith("Store")==False:

		folder = "player_statistics/2015-16/" + matchday + "/csv/"
		for tf in os.listdir(folder):
			if tf.endswith("features"):
				if not feature_num_to_acro.keys(): # do this once
					ls = [line.rstrip('\n') for line in open(folder+tf)]
					# store feature number -> feature acronym
					for ft in ls:
						ft_num, ft_acronym = ft.split("\t")
						feature_num_to_acro[ft_num] = ft_acronym
			elif tf.endswith("csv")==False and tf.endswith(".py")==False and tf.endswith(".swp")==False:
				# how to aggregate player stats over multiple matches
				#      - add up stats and then normalize at the end

				# store player features for each Player object as a dict

				# each line is a player
				# for each player in a team, aggregate stats
				# use key: player_num-team
				# for each team, keep a sum of how many games played

				# get team name
				m = re.match("^.*-(.*)$", tf)
				if m:
					team = m.group(1)
					team = re.sub("_", " ", team)
					
					with open((folder+tf), 'r') as team_ft_file:
						for player_line in team_ft_file:
							player_ft = defaultdict(float)
							features = player_line.rstrip().split(",")
							player_num = features[0]
							features = features[1:] # slice off player_num
							if len(features) > 1:
								for ft in features:
									ft_num, ft_val = ft.split(":")
									ft_acro = feature_num_to_acro[ft_num]
									ft_val = float(ft_val)
									player_ft[ft_acro] = ft_val
								def aggregate_player_features(key, team, ft_dict):
									for ft in ft_dict:
										all_player_features[key][ft] += ft_dict[ft]
								key = player_num + "-" + team
								aggregate_player_features(key, team, player_ft)
				team_to_num_games[team] += 1

# normalize player features over num games played
for key in all_player_features:
	team = re.sub(".*-", "", key)
	for ft in all_player_features[key]:
		all_player_features[key][ft] /= team_to_num_games[team]

# attach these stats to Player objects in allPlayers
for player in allPlayers:
	last_name, num, team = player.split("-", 2)
	allPlayers[player].stats = all_player_features[num + "-" + team]

'''			
for p in allPlayers.keys():
	print "------------"
	print allPlayers[p].name
	print allPlayers[p].team
	print allPlayers[p].position
	print allPlayers[p].price
	print allPlayers[p].stats
	print "------------"
'''


budget = 100.0
mdp = ComputeRosterMDP(players, budget, allTeams, allPlayers)
rl = util.QLearningAlgorithm(mdp.actions, mdp.discount(), util.fantasyFeatureExtractor)
print "Finished in %s iterations" % rl.numIters
qRewards = util.simulate(mdp, rl, 100, verbose=True)



