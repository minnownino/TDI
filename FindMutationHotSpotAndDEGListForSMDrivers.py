import TDI
import MySQLdb
import csv
import re
import DEGCorrelationAmongSGAMutationSpots

class FindMutationHotSpotAndDEGListForSMDrivers:
	def __init__(self):
		self.db = MySQLdb.connect("localhost", "fanyu", "hellowork", "TDI")

	#@parameter: TDI database gene_id
	#@return: gene name for in put gene
	def findGeneName(self, geneID):
		cursor = self.db.cursor()
		query = "SELECT gene_name FROM Genes WHERE gene_id= '%s'" %(geneID)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		return results[0][0]

	#@return: a dictionary contains all driver that has somatic mutation events
	#key is SGA, value is a list of tumors
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
					SMdriver[row[1]].add(row[0])
				else:
					SMdriver[row[1]] = set()
					SMdriver[row[1]].add(row[0])
		return SMdriver

	#Description: filter out drivers that has been called driver less than a certain number of tumors
	#@Parameter: threshold
	#@return: return a {SGA : tumors} dictionary
	def SMDriverSubset(self, threshold):
		drivers = self.findSMDriver()
		driver_subset = dict((k,v) for k, v in drivers.iteritems() if len(v) >= threshold)
		return driver_subset

	#@Parameter: a gene SGA, a list of tumors, 
	def countNumberOfDrivenTumorsForEachMutationSpots(self, SGA, tumors):
		cursor = self.db.cursor()
		query= "SELECT DISTINCT patient_id, aa_loc FROM Somatic_Mutations WHERE gene_id = '%s' AND aa_loc != 'null' and aa_mut in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')"%(SGA)
		
		cursor.execute(query)
		query_result = cursor.fetchall()
		loc_tumor = {}
		for row in query_result:
			if loc_tumor.has_key(row[1]):
				loc_tumor[row[1]].add(row[0])
			else:
				loc_tumor[row[1]] = set()
				loc_tumor[row[1]].add(row[0])
		for loc in loc_tumor.keys():
			loc_tumor[loc] = loc_tumor[loc].intersection(tumors)
		# print loc_tumor
		return loc_tumor

	def countMutationFreqForEachMutationSpots(self, SGA):
		mutation_type = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 
				'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
		cursor = self.db.cursor()
		query_tumors = "SELECT DISTINCT patient_id FROM SGAs WHERE gene_id = '%s'"%(SGA)
		cursor.execute(query_tumors)
		query_tumors_result = cursor.fetchall()
		tumors = set()
		for row in query_tumors_result:
			tumors.add(row[0])
		query = "SELECT DISTINCT patient_id, aa_loc FROM Somatic_Mutations WHERE gene_id = '%s' AND aa_loc != 'null' and aa_mut in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')"%(SGA)
		
		cursor.execute(query)
		query_result = cursor.fetchall()
		loc_tumor = {}
		for row in query_result:
			if loc_tumor.has_key(row[1]):
				loc_tumor[row[1]].add(row[0])
			else:
				loc_tumor[row[1]] = set()
				loc_tumor[row[1]].add(row[0])
		for loc in loc_tumor.keys():
			loc_tumor[loc] = loc_tumor[loc].intersection(tumors)
		# print loc_tumor
		return loc_tumor

	def findMutationHotSpotAssociatedDEGListForAllDriver(self, drivenTumor_threshold, hotSpotProportion_Threshold, mutationSpotCallRate_Threshold):
		cursor = self.db.cursor()
		drivers = self.SMDriverSubset(drivenTumor_threshold)

		table_name = "MutationHotSpotAndDEGList"
		allSGAMutationHpCallrate = []
		for driver in drivers.keys():
			SGA = self.findGeneName(driver)
			print SGA
			driverCallTumors = drivers[driver]
			loc_tumor_MutationFreq = self.countMutationFreqForEachMutationSpots(driver)
			loc_tumor_numberOfDriverTumor = self.countNumberOfDrivenTumorsForEachMutationSpots(driver, driverCallTumors)
			
			#filter out mutation spot that not satisfy mutationSpotCallRate_Threshold
			#{mutationspot : mutationFrequency, numberOfDrivenTumors, mutationSpotCallRate, drivenTumorList}
			loc_dict = {}
			sumDrivenTumors = 0
			tumor_set = set()
			for loc in loc_tumor_MutationFreq:
				if len(loc_tumor_MutationFreq[loc]) != 0:
					mutationSpotCallRate = (float)(len(loc_tumor_numberOfDriverTumor[loc]))/len(loc_tumor_MutationFreq[loc]) 
					if mutationSpotCallRate < mutationSpotCallRate_Threshold or len(loc_tumor_numberOfDriverTumor[loc]) < 3:
						continue
					else :
						loc_dict[loc] = tuple([len(loc_tumor_MutationFreq[loc]), len(loc_tumor_numberOfDriverTumor[loc]), mutationSpotCallRate, loc_tumor_numberOfDriverTumor[loc]])
						for tumor in loc_tumor_numberOfDriverTumor[loc]:
							tumor_set.add(tumor)
			sumDrivenTumors = len(tumor_set)

			#filter out mutation spot that not satisfy hotSpotProportion_Threshold
			loc_dict_subset = {}
			for loc in loc_dict.keys():
				if ((float)(loc_dict[loc][1])/sumDrivenTumors) >= hotSpotProportion_Threshold or loc_dict[loc][1] >= 20:
					loc_dict_subset[loc] = loc_dict[loc]

			loc_dict_DEG = {}
			#a nested dictionary: {mutationspot : {DEG : tumor}}
			for loc in loc_dict_subset.keys():
				DEGs = set()
				DEG_tumor = {}
				#mutation spot tumor list
				for tumor in loc_dict_subset[loc][3]:
					query = "SELECT DISTINCT T.DEG_id FROM TDI_Results AS T, SGAPPNoiseThreshold as S WHERE T.SGA_id = '%s' AND T.patient_id = '%s'\
							AND T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id"%(driver, tumor)
					cursor.execute(query)
					query_result = cursor.fetchall()					
					for row in query_result:
						if DEG_tumor.has_key(row[0]):
							DEG_tumor[row[0]].add(tumor)
						else:
							DEG_tumor[row[0]] = set()
							DEG_tumor[row[0]].add(tumor)
				#mutationFrequency, numberOfDrivenTumors, mutationSpotCallRate, deg_tumor dictionary
				loc_dict_DEG[loc] = tuple([loc_dict_subset[loc][0], loc_dict_subset[loc][1], loc_dict_subset[loc][2], DEG_tumor])

			if len(loc_dict_DEG) > 0:
				with open("%s_%s.csv"%(SGA, table_name), 'wb') as csvfile:
					writer=csv.writer(csvfile, delimiter=',',)
					writer.writerow(["MutationSpot", "NumberOfTumorsCalledDriver", "DEG", "NumberOfTumorsCalledTargetDEG", "MutationSpotDEGAssociationRate"])
					for loc in loc_dict_DEG.keys():
						allSGAMutationHpCallrate.append(tuple([SGA, loc, loc_dict_subset[loc][0], loc_dict_subset[loc][1], loc_dict_subset[loc][2]]))
						for DEG_id in loc_dict_DEG[loc][3]:
							DEG = self.findGeneName(DEG_id)
							ratio = (float)(len(loc_dict_DEG[loc][3][DEG_id]))/loc_dict_DEG[loc][1]
							if ratio >= 0.2:
								writer.writerow([loc, loc_dict_DEG[loc][1], DEG, len(loc_dict_DEG[loc][3][DEG_id]), ratio])

			table_name2 = "AllSGAMutationHotspotCallRate"
			with open("%s.csv"%(table_name2), 'wb') as csvfile:
				writer=csv.writer(csvfile, delimiter=',',)
				writer.writerow(["SGA", "Hotspot", "MutationFrequency", "NumbersOfTumorsCallDriver", "CallRate"])
				for row in allSGAMutationHpCallrate:
					writer.writerow([row[0], row[1], row[2], row[3], row[4]])
		print "Done"


	def findMutationHotSpotForEachSGATest(self, drivenTumor_threshold, mutationSpotCallRate_Threshold):
		cursor = self.db.cursor()
		drivers = self.SMDriverSubset(drivenTumor_threshold)

		table_name = "MutationHotSpotAndDEGList"
		# for driver in drivers.keys():
		driver = 9443
		SGA = self.findGeneName(driver)
		print SGA
		driverCallTumors = drivers[driver]
		loc_tumor_MutationFreq = self.countMutationFreqForEachMutationSpots(driver)
		loc_tumor_numberOfDriverTumor = self.countNumberOfDrivenTumorsForEachMutationSpots(driver, driverCallTumors)
		loc_dict = {}
		sumDrivenTumors = 0
		for loc in loc_tumor_MutationFreq:
			if len(loc_tumor_MutationFreq[loc]) != 0:
				mutationSpotCallRate = (float)(len(loc_tumor_numberOfDriverTumor[loc]))/len(loc_tumor_MutationFreq[loc]) 
				if mutationSpotCallRate < mutationSpotCallRate_Threshold:
					continue
				else :
					loc_dict[loc] = tuple([len(loc_tumor_MutationFreq[loc]), len(loc_tumor_numberOfDriverTumor[loc]), mutationSpotCallRate, loc_tumor_numberOfDriverTumor[loc]])
					sumDrivenTumors += len(loc_tumor_numberOfDriverTumor[loc])
		print len(loc_dict)
		print sumDrivenTumors
		with open("%s.csv"%(SGA), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)	
			writer.writerow(["MutationSpot", "Mutation Frequency", "Number of driven tumors", "ratio"])
			for loc in loc_dict.keys():
				ratio = (float)(loc_dict[loc][1])/sumDrivenTumors	
				writer.writerow([loc, loc_dict[loc][0], loc_dict[loc][1], ratio])
def main():
	tdi = FindMutationHotSpotAndDEGListForSMDrivers()
	tdi.findMutationHotSpotAssociatedDEGListForAllDriver(30, 0.1, 0.5)
	# tdi.countMutationFreqForEachMutationSpots(4110)
	# tdi.countMutationFreqForEachMutationSpots(4110)
	# tdi.SMDriverSubset(30)

if __name__ == "__main__":
    main()





























