import MySQLdb
import csv
import re

class FindDEGforAllSGA:
	def __init__(self):
		self.db = MySQLdb.connect("localhost", "fanyu", "hellowork", "TDI")

	#@parameter: gene name
	#@return: TDI database gene_id for input gene
	def findGeneId(self, geneName):
		cursor = self.db.cursor()
		query = "SELECT gene_id FROM Genes WHERE gene_name = '%s'" %(geneName)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		return results[0][0]

	#@parameter: TDI database gene_id
	#@return: gene name for in put gene
	def findGeneName(self, geneID):
		cursor = self.db.cursor()
		query = "SELECT gene_name FROM Genes WHERE gene_id= '%s'" %(geneID)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		return results[0][0]

	#@parameter: SGA unit/group name
	#@return: TDI database id for this SGA Unit/Group
	def findSGAUnitGroupId(self, SGA):
		cursor = self.db.cursor()
		query = "SELECT group_id FROM SGA_Unit_Group WHERE name= '%s'" %(SGA)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		return results[0][0]

	#@parameter: SGA unit/group id
	#@return: SGA unit/group name for this SGA Unit/Group
	def findSGAUnitGroupName(self, SGA_id):
		cursor = self.db.cursor()
		query = "SELECT name FROM SGA_Unit_Group WHERE group_id = '%s'" %(SGA_id)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		return results[0][0]

	#@parameter: TDI patient_id
	#@return: TCGA tumor name
	def findPatientName(self, patient_id):
		cursor = self.db.cursor()
		query = "SELECT name FROM Patients WHERE patient_id= '%s'" %(patient_id)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		return results[0][0]

	#@parameter: TCGA tumor name 
	#@return: TDI patient_id
	def findPatientId(self, patient_name):
		cursor = self.db.cursor()
		query = "SELECT patient_id FROM Patients WHERE name= '%s'" %(patient_name)
		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		return results[0][0]

	def findAllGeneDriver(self, driverCallThreshold, callRateThreshold, cutoff):
		#find all TDI records that satisfy the posterior threshold		
		cursor = self.db.cursor()
		query_SGAGene = "SELECT DISTINCT gene_id FROM SGAs WHERE gene_id IS NOT NULL"
		cursor.execute(query_SGAGene)
		query_SGAGene_result = cursor.fetchall()

		SGA_gene = {}
		for row1 in query_SGAGene_result:
			SGA = self.findGeneName(row1[0])
			print SGA
			tumor_deg_gene = {}
			query = "SELECT T.patient_id, T.DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id AND T.SGA_id = '%s'"%(row1[0])
			cursor.execute(query)
			query_result = cursor.fetchall()
			for row2 in query_result:
				if tumor_deg_gene.has_key(row2[0]):
					tumor_deg_gene[row2[0]].append(row2[1])
				else :
					tumor_deg_gene[row2[0]] = []
					tumor_deg_gene[row2[0]].append(row2[1])
			totalTumors = len(tumor_deg_gene.keys())
			if totalTumors != 0: 
				tumor_deg_gene = dict((k,v) for k, v in tumor_deg_gene.iteritems() if len(v) >= 5)
				driverTumors = len(tumor_deg_gene.keys())
				callRate = driverTumors/(float)(totalTumors)
				if (driverTumors < driverCallThreshold or callRate < callRateThreshold):
					continue
				else:
					deg_tumor = {}
					for tumor in tumor_deg_gene.keys():
						degList = tumor_deg_gene[tumor]
						for deg in degList:
							if deg_tumor.has_key(deg):
								deg_tumor[deg].append(tumor)
							else:
								deg_tumor[deg] = []
								deg_tumor[deg].append(tumor)				
					with open("%s.csv"%(SGA), 'wb') as csvfile:
						writer=csv.writer(csvfile, delimiter=',',)
						writer.writerow(["DEG_name", "NumberOfTumorsCalledDriver", "NumberOfTumorsThisDEGCalledTarget", "CallRate"])
						for key in deg_tumor:
							ratio = len(deg_tumor[key])/(float)(driverTumors)
							if ratio >= cutoff:		
								deg = self.findGeneName(key)
								writer.writerow([deg, driverTumors, len(deg_tumor[key]), ratio])
		print "Done"

	def findAllUnitDriver(self, driverCallThreshold, callRateThreshold, cutoff):
		#find all TDI records that satisfy the posterior threshold

		cursor = self.db.cursor()
		query_SGAunit = "SELECT DISTINCT unit_group_id FROM SGAs WHERE unit_group_id IS NOT NULL"
		cursor.execute(query_SGAunit)
		query_SGAunit_result = cursor.fetchall()

		SGA_unit = {}
		for row1 in query_SGAunit_result:
			SGA = self.findSGAUnitGroupName(row1[0])
			print SGA
			tumor_deg_unit = {}
			query = "SELECT T.patient_id, T.DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_unit_group_id = S.group_id AND T.SGA_unit_group_id = '%s'"%(row1[0])
			cursor.execute(query)
			query_result = cursor.fetchall()
			for row2 in query_result:
				if tumor_deg_unit.has_key(row2[0]):
					tumor_deg_unit[row2[0]].append(row2[1])
				else :
					tumor_deg_unit[row2[0]] = []
					tumor_deg_unit[row2[0]].append(row2[1])
			totalTumors = len(tumor_deg_unit.keys())
			if totalTumors != 0: 
				tumor_deg_unit = dict((k,v) for k, v in tumor_deg_unit.iteritems() if len(v) >= 5)
				driverTumors = len(tumor_deg_unit.keys())
				callRate = driverTumors/(float)(totalTumors)
				if (driverTumors < driverCallThreshold or callRate < callRateThreshold):
					continue
				else:
					deg_tumor = {}
					for tumor in tumor_deg_unit.keys():
						degList = tumor_deg_unit[tumor]
						for deg in degList:
							if deg_tumor.has_key(deg):
								deg_tumor[deg].append(tumor)
							else:
								deg_tumor[deg] = []
								deg_tumor[deg].append(tumor)				
					with open("%s.csv"%(SGA), 'wb') as csvfile:
						writer=csv.writer(csvfile, delimiter=',',)
						writer.writerow(["DEG_name", "NumberOfTumorsCalledDriver", "NumberOfTumorsThisDEGCalledTarget", "CallRate"])
						for key in deg_tumor:
							ratio = len(deg_tumor[key])/(float)(driverTumors)
							if ratio >= cutoff:		
								deg = self.findGeneName(key)
								writer.writerow([deg, driverTumors, len(deg_tumor[key]), ratio])
		print "Done"


	def findAllGeneSGA(self, driverCallThreshold, callRateThreshold):
		#find all TDI records that satisfy the posterior threshold		
		cursor = self.db.cursor()
		query_SGAGene = "SELECT DISTINCT gene_id FROM SGAs WHERE gene_id IS NOT NULL"
		cursor.execute(query_SGAGene)
		query_SGAGene_result = cursor.fetchall()

		SGA_gene = {}
		table_name = "AllDriver_DEG_tumor Table"
		with open("%s.csv"%(table_name), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["SGA", "Tumor_Name", "DEG"])
			# for row1 in query_SGAGene_result:
			row1 = []
			row1.append(10264)
			SGA = self.findGeneName(row1[0])
			print SGA
			tumor_deg_gene = {}
			query = "SELECT T.patient_id, T.DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id AND T.SGA_id = '%s'"%(row1[0])
			cursor.execute(query)
			query_result = cursor.fetchall()
			for row2 in query_result:
				if tumor_deg_gene.has_key(row2[0]):
					tumor_deg_gene[row2[0]].append(row2[1])
				else :
					tumor_deg_gene[row2[0]] = []
					tumor_deg_gene[row2[0]].append(row2[1])
			totalTumors = len(tumor_deg_gene.keys())
			print tumor_deg_gene
			if totalTumors != 0: 
				tumor_deg_gene = dict((k,v) for k, v in tumor_deg_gene.iteritems() if len(v) >= 5)
				driverTumors = len(tumor_deg_gene.keys())
				callRate = driverTumors/(float)(totalTumors)
				# if (driverTumors < driverCallThreshold or callRate < callRateThreshold):
				# 	continue
				# else:			
				for tumor in tumor_deg_gene.keys():
					tumor_name = self.findPatientName(tumor)
					for deg in tumor_deg_gene[tumor]:
						DEG_name= self.findGeneName(deg)
						writer.writerow([SGA, tumor_name, DEG_name])
		print "Done"

	def findAllGeneDriverForASingleGene(self, SGA_name, driverCallThreshold, callRateThreshold, cutoff):
		#find all TDI records that satisfy the posterior threshold		
		SGA = self.findGeneId(SGA_name)
		tumor_deg_gene = {}
		cursor = self.db.cursor()
		query = "SELECT T.patient_id, T.DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
			WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id AND T.SGA_id = '%s'"%(SGA)
		cursor.execute(query)
		query_result = cursor.fetchall()
		for row in query_result:
			if tumor_deg_gene.has_key(row[0]):
				tumor_deg_gene[row[0]].append(row[1])
			else :
				tumor_deg_gene[row[0]] = []
				tumor_deg_gene[row[0]].append(row[1])
		totalTumors = len(tumor_deg_gene.keys())
		if totalTumors != 0: 
			tumor_deg_gene = dict((k,v) for k, v in tumor_deg_gene.iteritems() if len(v) >= 5)
			driverTumors = len(tumor_deg_gene.keys())
			callRate = driverTumors/(float)(totalTumors)
			if (driverTumors < driverCallThreshold or callRate < callRateThreshold):
				return
			else:
				deg_tumor = {}
				for tumor in tumor_deg_gene.keys():
					degList = tumor_deg_gene[tumor]
					for deg in degList:
						if deg_tumor.has_key(deg):
							deg_tumor[deg].append(tumor)
						else:
							deg_tumor[deg] = []
							deg_tumor[deg].append(tumor)				
				with open("%s.csv"%(SGA), 'wb') as csvfile:
					writer=csv.writer(csvfile, delimiter=',',)
					writer.writerow(["DEG_name", "NumberOfTumorsCalledDriver", "NumberOfTumorsThisDEGCalledTarget", "CallRate"])
					for key in deg_tumor:
						ratio = len(deg_tumor[key])/(float)(driverTumors)
						if ratio >= cutoff:		
							deg = self.findGeneName(key)
							writer.writerow([deg, driverTumors, len(deg_tumor[key]), ratio])
		print "Done"

def main():
	tdi = FindDEGforAllSGA()
	# tdi.findAllUnitDriver(30, 0.5, 0.2)
	tdi.findAllGeneDriverForASingleGene("PIK3CA", 30,  0.5, 0.2)
	# tdi.findAllGeneSGA(30, 0.5)
if __name__ == "__main__":
    main()

		



