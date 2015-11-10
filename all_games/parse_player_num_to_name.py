# Jade Huang
# jayebird@stanford.edu

# glob for *-nodes
# get team name from nodes
# store player name -> player number
# if see same team name, add new players if any

import glob
import re
from collections import defaultdict

node_files = glob.glob("*-nodes")
prefix = "all_players/player_name_to_num-"
teams = defaultdict(list)
print node_files

for node_file in node_files:
	m = re.match("^.*-(.*)-nodes$", node_file)
	if m:
		team =  m.group(1)
		team_file = open(node_file, "r")
		for line in team_file:
			num, name = line.rstrip().split("\t")
			if (name, num) not in teams[team]:
				teams[team].append((name, num))
				print "num, name = %s, %s" % (name, num)

for team in teams:
	team_outfile = open(prefix+team, "w+")
	for player in teams[team]:
		name, num = player
		team_outfile.write("%s,%s\n" % (name, num))
		# player_file = open(prefix+team)
