import sys
counter = 1
team1 = {}
team2 = {}
team3 = {}
teamList = [team1, team2, team3]

for line in sys.stdin:
	# sys.stderr.write("line: " + line)
	value1, value2, value3 = line.rstrip().split()
	team1[counter] = value1
	team2[counter] = value2
	team3[counter] = value3
	counter += 1

for i in xrange(len(teamList)):
	line = "%s, " % (i+1)
	for key in teamList[i]:
		if teamList[i][key] != "0":
			line += str(key) + ":" + str(teamList[i][key]) + ", "
	line = line[:-2]
	print line




