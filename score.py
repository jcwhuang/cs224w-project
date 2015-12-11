# Score using fantasy football rules

import os
import re
from collections import defaultdict
import unicodedata
import classes
import sys
import glob

#store all player data
players = {}

# list of all players as Players
allPlayers = {}
defenders = []
goalkeepers = []
midfielders = []
forwards = []

# for positions, only last names are included along with price, team, and position
lines = [line.rstrip('\n') for line in open('fantasy_player_data/positions/defenders')]
lines += [line.rstrip('\n') for line in open('fantasy_player_data/positions/forwards')]
lines += [line.rstrip('\n') for line in open('fantasy_player_data/positions/goalkeepers')]
lines += [line.rstrip('\n') for line in open('fantasy_player_data/positions/midfielders')]

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

# team name as String -> Team object
allTeams = {}

# all_player_features[player_num + "-" + team] = {ft_num:ft:value}
all_player_features = defaultdict(lambda: defaultdict(float))

# stores feature number -> feature acronym
feature_num_to_acro = {}
team_to_num_games = defaultdict(float)

def store_data():

	for line in all_player_lines[1:]:
		num, name, team = line.rstrip().split(",")

		# get rid of trailing whitespace
		name = re.sub("\s*$", "", name)
		if " " in name:
			last_name = (re.match(".* (.*)$", name)).group(1)
		else: last_name = name

		team_to_player_num[team][last_name] = num
		team_to_player_name[team][num] = name


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
		if position == "GK":
			goalkeepers.append(key)
		elif position == "DEF":
			defenders.append(key)
		elif position == "MID":
			midfielders.append(key)
		elif position == "STR":
			forwards.append(key)

		if team not in allTeams:
			allTeams[team] = classes.Team(team, [])

		allTeams[team].addPlayer(p)

	matchdays = os.listdir("player_statistics/2015-16/")

	for matchday in matchdays:
		if not matchday.endswith(".py") and not matchday.endswith("Store"):

			folder = "player_statistics/2015-16/" + matchday + "/csv/"

			ls = [line.rstrip('\n') for line in open(folder+"features")]
			# store feature number -> feature acronym
			for ft in ls:
				ft_num, ft_acronym = ft.split("\t")
				feature_num_to_acro[ft_num] = ft_acronym

			for tf in os.listdir(folder):
				if not tf.endswith("features") and not tf.endswith("csv") and not tf.endswith(".py") and not tf.endswith(".swp"):
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
	# for key in all_player_features:
	# 	team = re.sub(".*-", "", key)
	# 	for ft in all_player_features[key]:
	# 		all_player_features[key][ft] /= team_to_num_games[team]

	# attach these stats to Player objects in allPlayers
	for player in allPlayers:
		last_name, num, team = player.split("-", 2)
		allPlayers[player].stats = all_player_features[num + "-" + team]

	# for player in allPlayers:
	# 	print player, allPlayers[player]

# score based on fantasy football rules
# playing in game: 1  = M > 0 ? 1 : 0
# playing at least 60 min: 2 = M >= 60 ? 2 : 0
# goals scored by goalkeeper/defender: 6 = if GK/DEF ? 6 * G : 0
# goals scored by midfielders: 5 if MID ? 5 * G : 0
# goals scored by forward: 4 if STR ? 4 * G : 0
# yellow card: -1 = Y * -1
# red card: -3 = R * -3
# downweight goalies by -1 per article
def score(outfilename, position):
	
	outfile = open(outfilename, "w+")

	for p in position:
		stats = allPlayers[p].stats
		pos = allPlayers[p].position

		score = 0
		if len(stats) > 0:
			score += 1 if stats["M"] > 0 else 0
			score += 2 if stats["M"] >= 60 else 0
			score += stats["G"] * 6 if pos == "GK" or pos == "DEF" else 0
			score += stats["G"] * 5 if pos == "MID" else 0
			score += stats["G"] * 4 if pos == "STR" else 0
			score += -1 * stats["Y"]
			score += -3 * stats["R"]
			score += -1 if pos == "GK" else 0
		outfile.write("%s, %d\n" % (p, score))

store_data()
direct = "fantasy_player_data/scores/"
sys.stderr.write("Scoring DEF")
score(direct + "score-defenders.csv", defenders)

sys.stderr.write("Scoring GK")
score(direct + "score-goalkeepers.csv", goalkeepers)

sys.stderr.write("Scoring MID")
score(direct + "score-midfielders.csv", midfielders)

sys.stderr.write("Scoring STR")
score(direct + "score-forwards.csv", forwards)

