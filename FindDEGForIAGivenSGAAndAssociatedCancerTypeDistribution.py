import MySQLdb
import csv
from collections import OrderedDict
class FindDEGForIAGivenSGAAndAssociatedCancerTypeDistribution:
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

	def findCancerType(self, patient_id):
		cursor = self.db.cursor()
		query = "SELECT C.cancer_name FROM Patients as P, Cancer_Types as C WHERE P.cancer_type_id = C.cancer_type_id and P.patient_id= '%s'" %(patient_id)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		return results[0][0]


	#@Description: for a given SGA, find all tumor, SGA, DEG events record first, then filter out no-driver calls
	#return a tumor_SGA dictionary, key is tumor, value is list of deg 
	#@Parameter: a SGA gene id
	#@Return: output is a csv files with 3 columns, first column is SGA name, second is tumor, third is deg.
	def findDEGCalledByAGivenSGADriver(self, SGA):
		cursor = self.db.cursor()
		sga_id = self.findGeneId(SGA)
		query = "SELECT patient_id, SGA_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
		WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_unit_id AND T.SGA_id = '%s'"%(sga_id)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()

		#key : (tumorid , SGA_id)
		#value : DEG_id
		tumor_SGA = {}
		for row in results:
			temp_tuple = (row[0], row[1])
			if tumor_SGA.has_key(temp_tuple):
				tumor_SGA[temp_tuple].append(row[2])
			else :
				tumor_SGA[temp_tuple] = []
				tumor_SGA[temp_tuple].append(row[2])

		#filter out SGA which regulate less than 5 degs
		tumor_SGA = dict((k,v) for k, v in tumor_SGA.iteritems() if len(v) >= 5)

		#flatten dict {(tumorid, SGA_id) : DEG_id} to list [tumor_id, SGA_id, DEG_id]
		records = []
		for key in tumor_SGA.keys():
			for deg in tumor_SGA[key]:
				records.append([key[0], key[1], deg])
		print len(records)	

		sga = self.findGeneName(SGA)
		#output each tumor id 
		with open("%s_allDegs.csv"%(SGA), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)			
			writer.writerow(["SGA", "Tumor_id", "DEG"])
			for row in records:
				patient_name = self.findPatient(row[0])			
				deg = self.findGeneName(int(row[2]))
				writer.writerow([sga, patient_name, deg])
		print "Done"
		return tumor_SGA

	#@Description: for a given SGA, find all tumor, SGA, DEG events record, return a tumor_SGA dictionary, key is tumor, value is list of deg 
	#@Parameter: a SGA gene id
	#@Return: output is a csv files with 3 columns, first column is SGA name, second is tumor, third is deg.
	def findDEGCalledByAGivenSGA(self, SGA):
		cursor = self.db.cursor()
		sga_id =  self.findGeneId(SGA)
		query = "SELECT patient_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
		WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_unit_id AND T.SGA_id = '%s'"%(sga_id)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()

		#key : tumorid
		#value : DEG_id
		tumor_DEG = {}
		for row in results:
			if tumor_DEG.has_key(row[0]):
				tumor_DEG[row[0]].append(row[2])
			else :
				tumor_DEG[row[0]] = []
				tumor_DEG[row[0]].append(row[2])

		sga = self.findGeneName(SGA)
		#output each tumor id 
		with open("%s_allDegs_NoneDriver.csv"%(SGA), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["SGA", "Tumor_id", "DEG"])			
			for row in results:
				patient_name = self.findPatient(row[0])
				deg = self.findGeneName(int(row[1]))
				writer.writerow([sga, patient_name, deg])
		return tumor_DEG

	#@Description: calculate pearson correlation coefficient for every driver on every pair of mutation spots
	#@Details: first find all drivers that has somatic mutations, then iterate the driver set, for every driver, find its deg and corresponding
	#call rate on all mutation spots for this driver
	#@Parameter: threshold for cutting off drivers that doesn't have numbers of driver calls that equal or larger than this threshold
	#@Return:  output are csv files, each driver has a file with 4 columns, first column is SGA name, second and third column is mutation spots, 
	#fourth column is pearson correation coefficient of these two mutation spots
	def findCancerTypeDistributionForAGivenSGA(self, SGA, isDriver):
		tumor_sga ={}
		if isDriver is True:
			tumor_sga = self.findDEGCalledByAGivenSGADriver(SGA)
		else:
			tumor_sga = self.findDEGCalledByAGivenSGA(SGA)
			
		cancer_count = {}
		for key in tumor_sga.keys():
			cancer = self.findCancerType(key[0])
			if cancer in cancer_count.keys():
				cancer_count[cancer] = cancer_count[cancer] + 1
			else :
				cancer_count[cancer] = 1
		d_sorted_by_value = OrderedDict(sorted(cancer_count.items(), key=lambda x: x[1] , reverse=True))

		isDriverName = ""
		if isDriver is not True:
			isDriverName = "NoneDriver"
		else:
			isDriverName = "Driver"

		with open("%s_cancer_type_dist_%s.csv"%(SGA,isDriverName), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["Cancer_type", "Count"])
			for cancer in d_sorted_by_value.keys():
				writer.writerow([cancer, cancer_count[cancer]])
		print "Done"

def main():
	tdi = FindDEGForIAGivenSGAAndAssociatedCancerTypeDistribution()
	tdi.findDEGCalledByAGivenSGADriver("IDH1")
	tdi.findDEGCalledByAGivenSGADriver("IDH2")
	tdi.findDEGCalledByAGivenSGA("IDH1")
	tdi.findDEGCalledByAGivenSGA("IDH2")
	tdi.findCancerTypeDistributionForAGivenSGA("IDH1", True)
	tdi.findCancerTypeDistributionForAGivenSGA("IDH2", True)
	tdi.findCancerTypeDistributionForAGivenSGA("IDH1", False)
	tdi.findCancerTypeDistributionForAGivenSGA("IDH2", False)

if __name__ == "__main__":
    main()


	