# Jade Huang
# jayebird@stanford.edu

# glob for *-nodes
# get team name from nodes

import glob
import re
from collections import defaultdict

node_files = glob.glob("*-nodes")
teams = set()

for node_file in node_files:
	m = re.match("^.*-(.*)-nodes$", node_file)
	if m:
		team =  m.group(1)
		team = re.sub("_", " ", team)
		teams.add(team)

all_teams_outfile = open("all-teams", "w+")
for team in teams:
	all_teams_outfile.write(team + "\n")
