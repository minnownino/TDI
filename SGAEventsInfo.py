import MySQLdb
import csv

class SGAEventsInfo: 

	def __init__(self):
		self.db = MySQLdb.connect("localhost", "fanyu", "hellowork", "TDI")
		self.cursor = self.db.cursor()

	def findGeneName(self, geneID):
		query = "SELECT gene_name FROM Genes WHERE gene_id= '%s'" %(geneID)
		self.cursor.execute(query)
		results = self.cursor.fetchall()
		return results[0][0]

	def findGeneId(self, geneName):
		query = "SELECT gene_id FROM Genes WHERE gene_name= '%s'" %(geneName)
		self.cursor.execute(query)
		results = self.cursor.fetchall()
		return results[0][0]

	def findPatient(self, patient_id):
		query = "SELECT name FROM Patients WHERE patient_id= '%s'" %(patient_id)
		self.cursor.execute(query)
		results = self.cursor.fetchall()
		return results[0][0]

	def findDriverTumor(self, geneId):
		query = "SELECT T.patient_id, T.DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = '%s' AND T.SGA_id = S.gene_id" %(geneId)
		self.cursor.execute(query)
		query_results = self.cursor.fetchall()

		#key : (tumorid)
		#value : DEG_id
		tumor_DEG = {}
		for row in query_results:
			if tumor_DEG.has_key(row[0]):
				tumor_DEG[row[0]].append(row[1])
			else :
				tumor_DEG[row[0]] = []
				tumor_DEG[row[0]].append(row[1])

		#filter out SGA which regulate less than 5 degs
		tumor_DEG = dict((k,v) for k, v in tumor_DEG.iteritems() if len(v) >= 5)
		return tumor_DEG	

	def countSGAEvents(self, geneId):
		query = "SELECT COUNT(DISTINCT patient_id) FROM SGAs WHERE gene_id = '%s'" %(geneId)
		self.cursor.execute(query)
		query_results = self.cursor.fetchall()
		return query_results[0][0]

	#filter out drivers that has been called driver less than a certain number of tumors
	def findSMEvents(self, geneId, tumor_DEG):
		query = "SELECT DISTINCT patient_id FROM Somatic_Mutations WHERE gene_id = '%s' AND protein_func_impact = 1" %(geneId)
		self.cursor.execute(query)
		query_results = self.cursor.fetchall()
		numberOfSMEvents = len(query_results)

		if (numberOfSMEvents != 0):
			numberOfSMDriverCall = 0
			for row in query_results:
				if tumor_DEG.has_key(row[0]):
					numberOfSMDriverCall += 1
			return (numberOfSMEvents, numberOfSMDriverCall, float(numberOfSMDriverCall)/numberOfSMEvents)
		else:
			return (0, 0, "NaN")

	def findSCNAmpvents(self, geneId, tumor_DEG):
		query = "SELECT DISTINCT patient_id FROM SCNAs WHERE gene_id = '%s' AND gistic_score = 2" %(geneId)
		self.cursor.execute(query)
		query_results = self.cursor.fetchall()
		numberOfSCNAmpEvents = len(query_results)

		if (numberOfSCNAmpEvents != 0): 
			numberOfSCNAmpDriverCall = 0
			for row in query_results:
				if tumor_DEG.has_key(row[0]):
					numberOfSCNAmpDriverCall += 1
			return (numberOfSCNAmpEvents, numberOfSCNAmpDriverCall, float(numberOfSCNAmpDriverCall)/numberOfSCNAmpEvents)
		else:
			return (0, 0, "NaN")

	def findSCNDelEvents(self, geneId, tumor_DEG):
		query = "SELECT DISTINCT patient_id FROM SCNAs WHERE gene_id = '%s' AND gistic_score = -2" %(geneId)
		self.cursor.execute(query)
		query_results = self.cursor.fetchall()
		numberOfSCNDelEvents = len(query_results)

		if (numberOfSCNDelEvents != 0):
			numberOfSCNDelDriverCall = 0
			for row in query_results:
				if tumor_DEG.has_key(row[0]):
					numberOfSCNDelDriverCall += 1
			return (numberOfSCNDelEvents, numberOfSCNDelDriverCall, float(numberOfSCNDelDriverCall)/numberOfSCNDelEvents)
		else:
			return (0, 0, "NaN")

	def findSGAEventsInforForAllSGA(self):
		# cursor = self.db.cursor()
		# query = "SELECT DISTINCT gene_id FROM SGAs WHERE gene_id IS NOT NULL"
		# cursor.execute(query)
		# query_results = cursor.fetchall()
		tableName = "SGAEvents"
		drivers = self.findDriver(30)
		print len(drivers)
		with open("%s.csv"%(tableName), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["SGA", "#SGAEvents", "#SGA-FI Call", "CallRate", "#SMEvents", "#SM-FI Call", "SMCallRate", "#SCNAmpEvents", "#SCNAmp-FI call", "SCNAmp-FICallRate", "#SCNDelEvents", "#SCNDel-FI call", "SCNDel-FICallRate"])
			# for row in query_results:
			# 	driver = row[0]
			for driver in drivers:
				numberOfSGAEvents = self.countSGAEvents(driver)
				if (numberOfSGAEvents >= 30):
				 	tumor_DEG = self.findDriverTumor(driver)
				 	numberOfSGADriverCall = len(tumor_DEG.keys())
				 	SGAEventsInfo = (numberOfSGAEvents, numberOfSGADriverCall, float(numberOfSGADriverCall)/numberOfSGAEvents)	
					SMEventsInfo = self.findSMEvents(driver, tumor_DEG)
					SCNAmpEventsInfo = self.findSCNAmpvents(driver, tumor_DEG)
					SCNDelEventsInfo = self.findSCNDelEvents(driver, tumor_DEG)
					SGA = self.findGeneName(driver)		
					print SGA
					# print SGAEventsInfo
					# print SMEventsInfo
					# print SCNAmpEventsInfo
					# print SCNDelEventsInfo
					writer.writerow([SGA, SGAEventsInfo[0], SGAEventsInfo[1], SGAEventsInfo[2],  SMEventsInfo[0], SMEventsInfo[1], SMEventsInfo[2], SCNAmpEventsInfo[0], SCNAmpEventsInfo[1], SCNAmpEventsInfo[2], SCNDelEventsInfo[0], SCNDelEventsInfo[1], SCNDelEventsInfo[2]])
		print "done"

	def findDriver(self, threshold):
		#find all TDI records that satisfy the posterior threshold
		query = "SELECT T.patient_id, T.SGA_id, T.DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id"
		self.cursor.execute(query)
		query_results = self.cursor.fetchall()

		#organize TDI records to a dictionary, key is (tumorid , SGA_id), value is DEG_id
		tumor_SGA = {}
		for row in query_results:
			temp_tuple = (row[0], row[1])
			if tumor_SGA.has_key(temp_tuple):
				tumor_SGA[temp_tuple].append(row[2])
			else :
				tumor_SGA[temp_tuple] = []
				tumor_SGA[temp_tuple].append(row[2])

		#filter out SGA which regulate less than 5 degs
		tumor_SGA = dict((k,v) for k, v in tumor_SGA.iteritems() if len(v) >= 5)
		#extract driver from dictionary tumor_SGA
		SGA_tumor = {}
		for key in tumor_SGA:
			if SGA_tumor.has_key(key[1]):
				SGA_tumor[key[1]].append(key[0])
			else:
				SGA_tumor[key[1]] = []
				SGA_tumor[key[1]].append(key[0])

		SGA_tumor_subset = dict((k,v) for k, v in SGA_tumor.iteritems() if len(v) >= threshold)
		return SGA_tumor_subset.keys()

def main():
	tdi = SGAEventsInfo()
	tdi.findSGAEventsInforForAllSGA()

if __name__ == "__main__":
    main()
