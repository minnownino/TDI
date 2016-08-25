
import MySQLdb
import csv
import scipy
from scipy.stats import pearsonr
import collections

#This script is used to calculate spot to spot correlation coefficents for all drivers that has somatic mutations

class DEGCorrelation: 

	def __init__(self):
		self.db = MySQLdb.connect("localhost", "fanyu", "hellowork", "TDI")

	def findGeneName(self, geneID):
		cursor = self.db.cursor()
		query = "SELECT gene_name FROM Genes WHERE gene_id= '%s'" %(geneID)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		return results[0][0]

	def findGeneId(self, geneName):
		cursor = self.db.cursor()
		query = "SELECT gene_id FROM Genes WHERE gene_name= '%s'" %(geneName)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		return results[0][0]

	def findPatient(self, patient_id):
		cursor = self.db.cursor()
		query = "SELECT name FROM Patients WHERE patient_id= '%s'" %(patient_id)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		return results[0][0]

	def findSMDriver(self):
		cursor = self.db.cursor()
		#find all TDI records that satisfy the posterior threshold
		query1 = "SELECT T.patient_id, T.SGA_id, T.DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id"
		cursor.execute(query1)
		query1_results = cursor.fetchall()
		cursor.close()

		#organize TDI records to a dictionary, key is (tumorid , SGA_id), value is DEG_id
		tumor_SGA = {}
		for row in query1_results:
			temp_tuple = (row[0], row[1])
			if tumor_SGA.has_key(temp_tuple):
				tumor_SGA[temp_tuple].append(row[2])
			else :
				tumor_SGA[temp_tuple] = []
				tumor_SGA[temp_tuple].append(row[2])

		#filter out SGA which regulate less than 5 degs
		tumor_SGA = dict((k,v) for k, v in tumor_SGA.iteritems() if len(v) >= 5)
		#extract driver from dictionary tumor_SGA
		allDriver = []
		for key in tumor_SGA:
			allDriver.append(key)
		allDriver = list(set(allDriver))

		#init a new dictionary SMdriver, key is SGA_id, value is tumor_id
		SMdriver = {}
		#only keep drivers that have somatic mutations		
		cursor = self.db.cursor()
		for tup in allDriver:
			query2 = "SELECT patient_id, gene_id from Somatic_Mutations WHERE patient_id = '%s' AND gene_id = '%s' and protein_func_impact = 1"%(tup[0], tup[1])
			cursor.execute(query2)
			query2_results = cursor.fetchall()
			if len(query2_results) > 0:
				row = query2_results[0]
				if SMdriver.has_key(row[1]):
					SMdriver[row[1]].append(row[0])
				else:
					SMdriver[row[1]] = []
					SMdriver[row[1]].append(row[0])
		return SMdriver

	#filter out drivers that has been called driver less than a certain number of tumors
	def SMDriverSubset(self, threshold):
		drivers = self.findSMDriver()
		driver_subset = dict((k,v) for k, v in drivers.iteritems() if len(v) >= threshold)
		return driver_subset

	#@Description: given a SGA gene id, find the number of tumors which has somatic mutations on every spots
	#@Details: find all somatic mutation records for given SGA first, then group this result by mutation spots by a dictionary, key is 
	#mutation spots of given SGA, value is a list of tumors. This dictionary is return value of this function. This function will also 
	#output a csv file, which contains 3 columns, SGA name, Mutation spots and Numbers of tumors. Each row in this csv file indicates 
	#how many tumors has mutation on the given spots of given SGA
	#@Parameter: SGA gene id
	#@Return: a dictionary, key is mutation spot, value is a list of tumors
	def mutLocTable(self, SGA):
		cursor = self.db.cursor()
		query = "SELECT patient_id, aa_loc FROM Somatic_Mutations WHERE gene_id = '%s' and protein_func_impact = 1"%(SGA)
		cursor.execute(query)
		query_results = cursor.fetchall()
		cursor.close()
		#{aa_loc : tumor}
		loc_tumor = {}
		for row in query_results:
			if row[1] != "null":
				if loc_tumor.has_key(row[1]):
					loc_tumor[row[1]].append(row[0])
				else:
					loc_tumor[row[1]] = []
					loc_tumor[row[1]].append(row[0])
		table_name = "SpotDriverCount"
		for loc in loc_tumor.keys():
			sga = self.findGeneName(SGA)
			with open("%s_%s.csv"%(table_name, sga), 'wb') as csvfile:
				writer=csv.writer(csvfile, delimiter=',',)
				writer.writerow(["SGA", "loc", "NumberOfTumors"])				
				for loc in loc_tumor.keys():
					writer.writerow([sga, loc, len(loc_tumor[loc])])
		return loc_tumor

	#@Description: given a SGA, return a nested dictionary called loc_deg_ratio, key is mutation spot, value is a dictionary called deg_ratio
	#deg_ratio dictionary, key is deg, ratio is call rate of this deg on this spot
	#@Details: 
	#@Parameter: SGA gene id, loc_tumor_subset, flag
	#loc_tumor_subset is a dictionary, key is mutation spot, value is a list of somatic driven tumors on this spot for given SGA
	#flag is a boolean value. If true, this function will out put a CSV file for given tumor, containning 2 columns, column 1 is deg, column 2 is call
	#rate for this deg. If false, there will be no output csv file 
	#@Return: a loc_deg_ratio dictionary. key is mutation spot, value is a dictionary called deg_ratio
	#deg_ratio dictionary, key is deg, ratio is call rate of this deg on this spot
	def findDEGsAssociatedWithEveryHotspotOfAGivenSGA(self, SGA, loc_tumor_subset, flag):
		cursor = self.db.cursor()
		#{loc : {deg : count}}
		loc_deglist = {}
		for loc in loc_tumor_subset.keys():
			#{deg: count}
			deg_count = {}
			tumors = loc_tumor_subset[loc]
			for tumor in tumors:
				query = "SELECT T.DEG_id FROM TDI_Results AS T, SGAPPNoiseThreshold as S WHERE T.SGA_id = '%s' AND T.patient_id = '%s'\
				AND T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id"%(SGA, tumor)
				cursor.execute(query)
				query_result=cursor.fetchall()
				for row in query_result:
					if deg_count.has_key(row[0]):
						deg_count[row[0]] = deg_count[row[0]] + 1
					else:
						deg_count[row[0]] = 1
			loc_deglist[loc] = {}
			loc_deglist[loc] = deg_count

		loc_deg_ratio ={}
		for loc in loc_deglist.keys():
			deg_ratio = {}
			for deg in loc_deglist[loc].keys():
				deg_name = self.findGeneName(deg)
				numberOfTotalTumors = len(loc_tumor_subset[loc])
				numberOfCalledRumors = loc_deglist[loc][deg]
				ratio = (float)(numberOfCalledRumors)/numberOfTotalTumors
				deg_ratio[deg_name] = ratio
			loc_deg_ratio[loc] = {}
			loc_deg_ratio[loc] = deg_ratio	

		if flag == True:
			for loc in loc_deg_ratio.keys():
				with open("%s_%s.csv"%(SGA, loc), 'wb') as csvfile:
					writer=csv.writer(csvfile, delimiter=',',)
					writer.writerow([loc])
					writer.writerow([len(loc_tumor_subset[loc])])
					writer.writerow(["DEG", "Ratio"])
					for deg in loc_deg_ratio[loc].keys():
						writer.writerow([deg, loc_deg_ratio[loc][deg]])
		return loc_deg_ratio

	#@Description: calculate pearson correlation coefficient for every driver on every pair of mutation spots
	#@Details: first find all drivers that has somatic mutations, then iterate the driver set, for every driver, find its deg and corresponding
	#call rate on all mutation spots for this driver
	#@Parameter: threshold for cutting off drivers that doesn't have numbers of driver calls that equal or larger than this threshold
	#@Return:  output are csv files, each driver has a file with 4 columns, first column is SGA name, second and third column is mutation spots, 
	#fourth column is pearson correation coefficient of these two mutation spots
	def findDEGsAssociatedWithEveryHotspotOfEverySGA(self, threshold):
		#for compare if two lists are identical
		compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
		#find all driver SGA that has somatic mutation
		drivers = self.SMDriverSubset(threshold)
		tablename = "SGAMutationSpotCorelation"		
		#iterate driver set, for every SGA, calculate the pearson correlation coefficent for every pair of mutation spots
		for driver in drivers.keys():
			#find driver name of current driver
			SGA = self.findGeneName(driver)	
			#get the tumor list of current driver
			tumors = drivers[driver]
			#get the loc_tumor dictionary of current driver
			#loc_tumor dictionart, key is mutation spot, value is a list of tumors
			#indicates in these tumors, current SGA has somatic mutation of this spot
			loc_tumor = self.mutLocTable(driver)
			loc_tumor_subset = {}			
			#find somatic mutation driven tumors at different mutation spot	for current driver
			#e.g. filter out drivers tumors that not has a driver call for current driver 	
			for loc in loc_tumor.keys():
				for tumor in loc_tumor[loc]:
					tumor_subset = set(loc_tumor[loc]).intersection(set(tumors))
					if len(tumor_subset) != 0:
						loc_tumor_subset[loc] = loc_tumor[loc]
			#loc_deg_ratio is nested dictionary, key is mutation spot, value is deg_ratio dictionary
			#deg_ratio dictionary, key is deg, ratio is call rate of this deg on this spot
			loc_deg_ratio = self.findDEGsAssociatedWithEveryHotspotOfAGivenSGA(driver, loc_tumor_subset, False)
			loc_list = loc_deg_ratio.keys()
			with open("%s_%s.csv"%(tablename, SGA), 'wb') as csvfile:
				writer=csv.writer(csvfile, delimiter=',',)
				writer.writerow(["SGA", "Loc1", "Loc2", "Correlation"])
				#pair-wise mutation spots
				for i in range(0, len(loc_list)):
					for j in range(i + 1, len(loc_list)):
						loc1 = loc_list[i]
						loc2 = loc_list[j]	
						degList = loc_deg_ratio[loc1].keys()
						length = len(degList)
						loc1_degRatioList = loc_deg_ratio[loc1].values()
						loc2_degRatioList = [0] * length
						for deg in loc_deg_ratio[loc2].keys():
							if deg in degList:
								idx = degList.index(deg)
								loc2_degRatioList[idx] = loc_deg_ratio[loc2][deg]
							else :
								loc1_degRatioList.append(0)
								loc2_degRatioList.append(loc_deg_ratio[loc2][deg])	
						if all(x == loc1_degRatioList[0] for x in loc1_degRatioList) and compare(loc1_degRatioList, loc2_degRatioList): 
							coefficient = 1.0
							writer.writerow([SGA, loc1, loc2, coefficient])					
						else:
							coefficient = pearsonr(loc1_degRatioList, loc2_degRatioList)
							writer.writerow([SGA, loc1, loc2, coefficient[0]])
		print "Done"

def main():
	tdi = DEGCorrelation()
	tdi.findDEGsAssociatedWithEveryHotspotOfEverySGA(30)
if __name__ == "__main__":
    main()






