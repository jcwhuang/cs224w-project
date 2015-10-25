import sys
counter = 1
team1 = {}
team2 = {}
for line in sys.stdin:
	value1, value2 = line.rstrip().split()
	team1[counter] = value1
	team2[counter] = value2
	counter += 1

line =  "1, "
for key in team1:
	if team1[key] != "0":
		line += str(key) + ":" + str(team1[key]) + ", "
line = line[:-2]
sys.stdout.write(line + "\n")

line =  "2, "
for key in team2:
	 if team2[key] != "0":
		line += str(key) + ":" + str(team2[key]) + ", "
line = line[:-2]
sys.stdout.write(line + "\n")




