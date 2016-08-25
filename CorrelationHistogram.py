import MySQLdb
import csv
import scipy
from scipy.stats import pearsonr
import math

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pylab

def drawHisto(inputFile, SGA):
	data = []
	bincounts = [0] * 100
	with open(inputFile, "r") as file:
		next(file)
		for line in file:
			coef = float(line.strip().split(",")[3])
			data.append(coef)
			idx = int(math.floor((coef + 0.99999999)/0.02))
			bincounts[idx] += 1
	print bincounts
	plt.hist(data, bins = 100, range = ([-1, 1]))
	plt.title("%s_Spot_Coefficient"%(SGA))
	plt.xlabel("Value")
	plt.ylabel("Frequency")
	pylab.savefig("%s_Spot_Coefficient.pdf"%(SGA))

drawHisto("SGAMutationSpotCorelation_PTEN.csv", "PTEN")

					