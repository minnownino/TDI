import MySQLdb
import csv
from scipy.stats import hypergeom
class GlobalDriverDEGAssociation:
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

	def hypergeom(self, white_balls_drawn,population, white_balls_in_population, total_balls_drawn):
		"""
		hypergeometric function for probability value 
    	@param white_balls_drawn -- associated gene in input genesubset
    	@param population -- population (here use the offical home sapiens genes in NCBI)
    	@param white_balls_in_population -- assoicated genes in population
   		@param total_balls_drawn -- input genelist size
		"""
		prob = 1-hypergeom.cdf(white_balls_drawn - 1, population, white_balls_in_population, total_balls_drawn)
		return prob

	def calcChiTestForGlobalDriverAndDEGPair(self, SGA, DEG):
		cursor = self.db.cursor()
		query_SGAEvents = "SELECT DISTINCT patient_id FROM SGAs WHERE gene_id = '%s'"%(SGA)
		cursor.execute(query_SGAEvents)
		query_SGAEvents_results = cursor.fetchall()
		SGA_tumors = set()
		for row in query_SGAEvents_results:
			SGA_tumors.add(row[0])
		query_DEGEvents = "SELECT DISTINCT patient_id FROM DEGs WHERE gene_id = '%s' AND exp_id = 1"%(DEG)
		cursor.execute(query_DEGEvents)
		query_DEGEvents_results = cursor.fetchall()
		DEG_tumors = set()
		for row in query_DEGEvents_results:
			DEG_tumors.add(row[0])
		overlapTumors = SGA_tumors.intersection(DEG_tumors)

		query_totalTumors = "SELECT COUNT(DISTINCT patient_id) FROM Patients"
		cursor.execute(query_totalTumors)
		query_totalTumors_results = cursor.fetchall()
		numberOfTotalTumors = query_totalTumors_results[0][0]
		p_value = self.hypergeom(len(overlapTumors), numberOfTotalTumors, len(SGA_tumors), len(DEG_tumors))
		return p_value

	def countDEGEventsTumorsAndTDICallEvents(self, SGA, DEG):
		cursor = self.db.cursor()
		query_DEGEvents = "SELECT DISTINCT patient_id FROM DEGs WHERE gene_id = '%s' AND exp_id = 1"%(DEG)
		cursor.execute(query_DEGEvents)
		query_DEGEvents_results = cursor.fetchall()
		DEGEventsTumors = set()
		for row in query_DEGEvents_results:
			DEGEventsTumors.add(row[0])
		numberOfDEGEvents = len(DEGEventsTumors)

		query_TDICall = "SELECT DISTINCT patient_id FROM TDI_Results WHERE SGA_id = '%s' AND DEG_id = '%s' AND exp_id = 1"%(SGA, DEG)
		cursor.execute(query_TDICall)
		query_TDICall_results = cursor.fetchall()
		numberOfTDIEvents = 0
		for row in query_TDICall_results:
			if row[0] in DEGEventsTumors:
				numberOfTDIEvents += 1
		ratio = 0.0
		if numberOfDEGEvents != 0:
			ratio = (float)(numberOfTDIEvents)/numberOfDEGEvents
		return (numberOfDEGEvents, numberOfTDIEvents, ratio)

	def globalDriverDEGAssociation(self):
		cursor = self.db.cursor()
		#find all TDI records that satisfy the posterior threshold
		query = "SELECT DISTINCT SGA_id, DEG_id FROM Global_Driver WHERE SGA_id IS NOT NULL"
		cursor.execute(query)
		query_results = cursor.fetchall()
		cursor.close()
		tableName = "GlobalDriver_DEG_Association"
		with open("%s.csv"%(tableName), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["Global_Driver", "DEG", "chi_test", "#DEGEventTumors", "#TDIcallTumors", "ratio"])
			for row in query_results:
				SGA = self.findGeneName(row[0])
				DEG = self.findGeneName(row[1])
				chi_test = self.calcChiTestForGlobalDriverAndDEGPair(row[0], row[1])					
				DEGeventsInfo = self.countDEGEventsTumorsAndTDICallEvents(row[0], row[1])
				writer.writerow([SGA, DEG, chi_test, DEGeventsInfo[0], DEGeventsInfo[1], DEGeventsInfo[2]])
		print "Done"

	def sgaDEGExplainationForAPairOfSGADEG(self, SGA, DEG):
		cursor = self.db.cursor()
		query_DEGEvents = "SELECT DISTINCT patient_id FROM DEGs WHERE gene_id = '%s' AND exp_id = 1"%(DEG)
		cursor.execute(query_DEGEvents)
		query_DEGEvents_results = cursor.fetchall()
		DEGEventsTumors = set()
		for row in query_DEGEvents_results:
			DEGEventsTumors.add(row[0])
		numberOfDEGEvents = len(DEGEventsTumors)

		query_SGAEvents = "SELECT DISTINCT patient_id FROM SGAs WHERE gene_id = '%s'"%(SGA)
		cursor.execute(query_SGAEvents)
		query_SGAEvents_results = cursor.fetchall()
		SGAEventsTumors = set()
		for row in query_SGAEvents_results:
			SGAEventsTumors.add(row[0])

		tumorIntersection = SGAEventsTumors.intersection(DEGEventsTumors)
		if (len(tumorIntersection) == 0):
			print DEG
			return None
		else:
			numberOfGD_DEG_TDIcall = 0
			numberOfNonGD_DEG_TDIcall = 0
			for tumor in tumorIntersection:
				query_SGA_DEG = "SELECT COUNT(*) FROM TDI_Results WHERE SGA_id = '%s' AND DEG_id = '%s' AND patient_id = '%s' AND exp_id = 1"%(SGA,DEG, tumor)
				cursor.execute(query_SGA_DEG)
				query_SGA_DEG_results = cursor.fetchall()
				if query_SGA_DEG_results[0][0] > 1:
					print "Error, duplicate records found in TDI_Results table"
				elif query_SGA_DEG_results[0][0] == 1:
					numberOfGD_DEG_TDIcall += 1
			numberOfNonGD_DEG_TDIcall = len(tumorIntersection) - numberOfGD_DEG_TDIcall
			ratioOfTDICall = (float)(numberOfGD_DEG_TDIcall)/len(tumorIntersection)
			ratioOfNonTDICall = (float)(numberOfNonGD_DEG_TDIcall)/len(tumorIntersection)
			return (len(tumorIntersection), numberOfGD_DEG_TDIcall, ratioOfTDICall, numberOfNonGD_DEG_TDIcall, ratioOfNonTDICall)

	def sgaDEGExplaination(self):
		cursor = self.db.cursor()
		#find all TDI records that satisfy the posterior threshold
		query = "SELECT DISTINCT SGA_id, DEG_id FROM Global_Driver WHERE SGA_id IS NOT NULL"
		cursor.execute(query)
		query_results = cursor.fetchall()
		cursor.close()
		tableName = "SGA_DEG_Explaination"
		with open("%s.csv"%(tableName), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["Global_Driver", "DEG", "#NumberOfTumorIntersection", "#GD_DEG_TDIcall","TDICallRatio", "#NonGD_DEG_TDIcall", "NonTDICallRatio"])
			for row in query_results:
				SGA = self.findGeneName(row[0])
				DEG = self.findGeneName(row[1])
				records = self.sgaDEGExplainationForAPairOfSGADEG(row[0], row[1])
				if records is not None:
					writer.writerow([SGA, DEG, records[0], records[1], records[2], records[3]])
		print "Done"
		
def main():
	tdi = GlobalDriverDEGAssociation()
	# tdi.globalDriverDEGAssociation()
	tdi.sgaDEGExplaination()

if __name__ == "__main__":
    main()





























