############################################################
import utilSearch
from collections import defaultdict
import re
import unicodedata
import classes
import os

class RosterProblem(utilSearch.SearchProblem):

    def __init__(self, players, budget, allTeams, allPlayers):
        self.allPlayers = allPlayers
        self.allTeams=allTeams
        self.players=players
        self.budget=budget
        self.maxPositions={'GK': 2, 'DEF': 5, 'MID': 5, 'STR': 3}

    def startState(self):
        teams = tuple([(t,0) for t in self.allTeams])
        positions = tuple([(pos,0) for pos in self.maxPositions])
        return ((), self.budget, positions, teams)

    def isGoal(self, state):
        # TO DO: eventually, should be 15
        return len(state[0]) == 5

    def succAndCost(self, state):
        results = []
        validPlayer = False
        stateRoster, stateBudget, statePositions, stateTeams = state

        statePositions = dict(statePositions)
        stateTeams = dict(stateTeams)
        for action in self.allPlayers:
            player = self.allPlayers[action]
            # return (action, newState, cost)
            # which is (player, newState, cost)
            if player not in state[0]: # if not in roster yet
                positionConstraint = (statePositions[p.position] < self.maxPositions[p.position])
                budgetConstraint = (p.price < stateBudget)
                teamConstraint = (stateTeams[p.team] < 3)
                if positionConstraint and budgetConstraint and teamConstraint:
                    validPlayer = True
            
            if not validPlayer:
                continue # skip over this player

            # compute new state
            newRoster = list(stateRoster)
            newRoster.append(player)
            newBudget = stateBudget-player.price
            newPositions = statePositions
            newPositions[player.position] += 1
            newTeams = stateTeams
            newTeams[player.team] += 1

            # convert back into tuple
            newPositions = tuple(newPositions.items())
            newTeams = tuple(newTeams.items())

            newState = (tuple(newRoster), newBudget, newPositions, newTeams)
            cost = -1 * player.price
            results.append((player, newState, player.price))

        return results

def findBestRoster(players, budget, allTeams, allPlayers):
    print "Finding best roster"
    # ucs = util.UniformCostSearch(verbose=2)
    ucs = utilSearch.UniformCostSearch(verbose=2)
    ucs.solve(RosterProblem(players, budget, allTeams, allPlayers))

    history = " ".join(ucs.actions)
    return history

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

# print allPlayers

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
                #if not feature_num_to_acro.keys(): # do this once
                ls = [line.rstrip('\n') for line in open(folder+tf)]
                # store feature number -> feature acronym
                for ft in ls:
                    ft_num, ft_acronym = ft.split("\t")
                    feature_num_to_acro[ft_num] = ft_acronym
                break
        for tf in os.listdir(folder):
            if tf.endswith("features")==False and tf.endswith("csv")==False and tf.endswith(".py")==False and tf.endswith(".swp")==False:
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

budget = 100.0
# call roster RosterProblem
bestRoster =  findBestRoster(players, budget, allTeams, allPlayers)
print bestRoster
