import collections
import classes

def score(actualMatches, outputMatches):
	correctCount = 0.0
	totalCount = 0.0
	for a, o in zip(actualMatches, outputMatches):
		if a.winner() == o.winner():
			correctCount += 1.0
		totalCount += 1.0
	print str(correctCount) + " correct predictions out of " + str(totalCount) + " total matches."
	accuracy = correctCount/totalCount
	print "Accuracy: " + str(accuracy)
