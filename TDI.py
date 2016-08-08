import MySQLdb
import csv
import re

class TDIqueries:
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
		query = "SELECT name FROM SGA_Unit_Group WHERE group_id = '%s'" %(SGA)
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

	#@Parameter: a tumor name (TCGA patient_id)
	#@return:  driver SGA in this tumor
	#to do : number of degs, rank from largest to smallest
	def findDriverInAGivenTumor(self, patient):
		cursor = self.db.cursor()
		patient_id = self.findPatientId(patient)
		query = "SELECT patient_id, SGA_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
			WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_unit_id AND T.patient_id = '%s'"%(patient_id)

		query = "SELECT patient_id, SGA_unit_group, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
			WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_unit_id AND T.patient_id = '%s'"%(patient_id)

		cursor.execute(query)
		results = cursor.fetchall()
		cursor.close()
		#{sga_id : deg_id}
		sga_deg = {}		
		for row in results:
			if sga_deg.has_key(row[0]):
				sga_deg[row[0]].append(row[1])
			else:
				sga_deg[row[0]] = []
				sga_deg[row[0]].append(row[1])
		#filter out SGA which regulate less than 5 degs
		sga_deg = dict((k,v) for k, v in sga_deg.iteritems() if len(v) >= 5)
			
		with open("%s.csv"%(patient), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["Driver_Name", "Number of DEGs"])
			for key in sga_deg.keys():
				if re.search("^SGAgroup.", SGA) or re.search("^SGA.unit.", SGA):
					sga = self.findGeneName(key)
					writer.writerow([sga, len(sga_deg[key])])

		print "finish"
		return sga_deg
		
	#@Parameter: patientname, DEG list 
	#@Return: SGA driver in this tumor, which at least regulate one gene in given target gene list
	#@return: how many degs per SGA covers in given deg list
	def findDriversForListOfDEGsInAGivenTumor(self, patient, degList):
		cursor = self.db.cursor()
		sga_deg = self.findDriverInGivenTumor(patient)
		degSet = set()
		for deg in degList:
			degSet.add(self.findGeneId(deg))

		result = {}
		for key in sga_deg.keys():
			targetDEGs = set(sga_degs[key])
			targets = targetDEGs.intersection(degSet)
			if (len(targets) != 0):
				result[key] = []
				result[key] = targets

		with open("%s.csv"%(patient), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["Drive_name", "Number of DEGs"])
			for key in result.keys():
				sga = self.findGeneName(key)
				writer.writerow([sga, len(result[sga])])
		print "finish"

	#@Parameter: SGA name (a gene or a SGA unit/group)
	#@Return: List of patient (TDI) id in which input SGA is called a driver
	def findTumorsInWhichAGivenSGAIsDriver(self, SGA):
		cursor = self.db.cursor()
		if re.search("^SGAgroup.", SGA) or re.search("^SGA.unit.", SGA):
			sga_id = self.findSGAUnitGroupId(SGA)
			query = "SELECT patient_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_unit_group_id = S.gene_unit_id AND T.SGA_unit_group_id = '%s'\
				AND S.name = '%s'"%(sga_id, SGA)
			cursor.execute(query)
		else: 
			sga_id = self.findGeneId(SGA)
			query = "SELECT patient_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_unit_id AND T.SGA_id = '%s' AND S.name = '%s'"%(sga_id, SGA)
			cursor.execute(query)
		
		results = cursor.fetchall()
		cursor.close()

		#key : tumorid
		#value : DEG_id
		tumor_deg = {}
		for row in results:
			if tumor_deg.has_key(row[0]):
				tumor_deg[row[0]].append(row[1])
			else :
				tumor_deg[row[0]] = []
				tumor_deg[row[0]].append(row[1])

		#filter out SGA which regulate less than 5 degs
		tumor_deg = dict((k,v) for k, v in tumor_deg.iteritems() if len(v) >= 5)

		#flatten dict {(tumorid, SGA_id) : DEG_id} to list [tumor_id, SGA_id, DEG_id]
		print len(tumor_deg.keys())
		return tumor_deg

	#@Parameter : SGA name
	#@Return : tumors that has mutation of given SGA
	def findTumorsHasSMForAGivenSGA(self, SGA):
		cursor = self.db.cursor()
		SGA_id = self.findGeneId(SGA)
		query = "SELECT patient_id FROM Somatic_Mutations WHERE gene_id = '%s'" %(SGA_id)
		cursor.execute(query)
		tumors =cursor.fetchall()
		tumors = sum(tumors, ())
		print "finish"
		return tumors

	#@Parameter : SGA name, mutation hotspot
	#@Return : tumors that has mutation of given SGA in given hotspot
	def findTumorsHasSMForAGivenSGAInGivenHopspot(self, SGA, hotspot):
		cursor = self.db.cursor()
		SGA_id = self.findGeneId(SGA)
		query = "SELECT patient_id FROM Somatic_Mutations WHERE aa_loc = '%s' AND gene_id = '%s'" %(hotspot, SGA_id)
		cursor.execute(query)
		tumors =cursor.fetchall()
		tumors = sum(tumors, ())
		print "finish"
		return tumors

	#@Parameter : SGA name
	#@Return : tumors that has copy number alternation of given SGA
	def findTumorsHasSCNAForAGivenSGA(self, SGA):
		cursor = self.db.cursor()
		SGA_id = self.findGeneId(SGA)
		query = "SELECT patient_id FROM SCNAs WHERE gene_id = '%s' AND gistic_score IN (-2, 2)"%(SGA_id)
		cursor.execute(query)
		tumors =cursor.fetchall()
		tumors = sum(tumors, ())
		print "finish"
		return tumors

	#@Parameter : SGA name, tumor set
	#@Return : DEGs that called by given SGA in given tumors, organized in a {deg : {tumor list}} dict
	def queryPatientsAndDEGsForAGivenSGAandTumorset(self, SGA, tumors):
		deg_tumor ={}
		cursor = self.db.cursor()
		print "start query deg"
		if re.search("^SGAgroup.", SGA) or re.search("^SGA.unit.", SGA):
			sga_id = self.findSGAUnitGroupId(SGA)
			for tumor in tumors:
				query = "SELECT DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
					WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_unit_group_id = S.gene_unit_id AND T.SGA_unit_group_id = '%s'\
					AND S.name = '%s' AND T.patient_id = '%s'"%(sga_id, SGA, tumor)
				cursor.execute(query)
				query_result=cursor.fetchall()
				for row in query_result:
					if deg_tumor.has_key(row[0]):
						deg_tumor[row[0]].append(tumor)
					else :
						deg_tumor[row[0]] = []
						deg_tumor[row[0]].append(tumor)
		else: 
			sga_id = self.findGeneId(SGA)
			for tumor in tumors:
				query = "SELECT DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
					WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_unit_id AND T.SGA_id = '%s'\
					AND S.name = '%s' AND T.patient_id = '%s'"%(sga_id, SGA, tumor)
				cursor.execute(query)
				query_result=cursor.fetchall()
				for row in query_result:
					if deg_tumor.has_key(row[0]):
						deg_tumor[row[0]].append(tumor)
					else :
						deg_tumor[row[0]] = []
						deg_tumor[row[0]].append(tumor)
		cursor.close()
		return deg_tumor

	#@Parameter: SGA gene name, cutoff
	#@Return: a csv file contains 4 column, column1 is deg, column2 is tumor name
	#colum3 is total number of tumors the sga is called a driver, column 4 is number of tumors the deg is called target
	#1. find tumors called SGA as a driver
	#2. find target degs
	def findDEGforAGivenSGA(self, SGA, cutoff, tumors = None):
		tumor_deg = self.findTumorsInWhichAGivenSGAIsDriver(SGA)
		#total tumors		
		if tumors is not None:
			keys_to_remove = []
			for tumor in tumors:
				if not tumor_deg.has_key(tumor):
					keys_to_remove.add(tumor)
			map(tumor_deg.pop, keys_to_remove)

		patients = tumor_deg.keys()
		tumorsLen = len(patients)
		deg_tumor = self.queryPatientsAndDEGsForAGivenSGAandTumorset(SGA, patients)

		with open("%s.csv"%(SGA), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["DEG_name", "NumberOfTumorsCalledDriver", "NumberOfTumorsThisDEGCalledTarget", "CallRate"])
			for key in deg_tumor:
				ratio = len(deg_tumor[key])/(float)(tumorsLen)
				if ratio >= cutoff:		
					deg = self.findGeneName(key)
					writer.writerow([deg, tumorsLen, len(deg_tumor[key]), ratio])
		print "finish"
		return deg_tumor
	
	#@Parameter: SGA gene name, mutation hotspot
	#@Return: a csv file contains 4 column, column1 is deg, column2 is tumor name
	#colum3 is total number of tumors the sga is called a driver, column 4 is number of tumors the deg is called target
	#1. find tumors called SGA as a driver
	#2. choose tumors have somatic mutations
	#3. find target degs in tumors set
	def findDEGofSCNAForAGivenSGA(self, SGA, cutoff):	
		SGA_id = self.findGeneId(SGA)
		tumor_deg = self.findTumorsInWhichAGivenSGAIsDriver(SGA)
		#total tumors
		patients = tumor_deg.keys()
		#tumor of SCNA
		SCNAtumor = self.findTumorsHasSCNAForAGivenSGA(SGA)
		#tumor subset
		tumors = set(patients).intersection(set(SCNAtumor))
		tumorsLen = len(tumors)
		print tumorsLen
		#key : DEG_id
		#value : tumorid
		deg_tumor = self.queryPatientsAndDEGsForAGivenSGAandTumorset(SGA_id, tumors)

		# print deg_tumor
		with open("%s_SCNA.csv"%(SGA), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["DEG_name", "NumberOfTumorsCalledDriver", "NumberOfTumorsThisDEGCalledTarget", "CallRate"])
			for key in deg_tumor:
				ratio = len(deg_tumor[key])/(float)(tumorsLen)
				if ratio >= cutoff:		
					deg = self.findGeneName(key)
					writer.writerow([deg, tumorsLen, len(deg_tumor[key]), ratio])
		print "finish"
		return deg_tumor

	#@Parameter: TCGA SGA gene name
	#@Return: a csv file contains 4 column, column1 is deg, column2 is tumor name
	#colum3 is total number of tumors the sga is called a driver, column 4 is number of tumors the deg is called target
	#1. find tumors called SGA as a driver
	#2. choose tumors have somatic mutations
	#3. find target degs in tumors set
	def findDEGsOfSMForAGivenSGA(self, SGA, cutoff):	
		SGA_id = self.findGeneId(SGA)
		tumor_deg = self.findTumorsInWhichAGivenSGAIsDriver(SGA)
		#total tumors
		patients = tumor_deg.keys()

		SMtumor = self.findTumorsHasSMForAGivenSGA(SGA)
		#tumor subset
		tumors = set(patients).intersection(set(SMtumor))
		tumorsLen = len(tumors)
		#key : DEG_id
		#value : tumorid
		deg_tumor = self.queryPatientsAndDEGsForAGivenSGAandTumorset(SGA_id, tumors)

		# print deg_tumor
		with open("%s_SM.csv"%(SGA), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["DEG_name", "NumberOfTumorsCalledDriver", "NumberOfTumorsThisDEGCalledTarget", "CallRate"])
			for key in deg_tumor:
				ratio = len(deg_tumor[key])/(float)(tumorsLen)
				if ratio >= cutoff:		
					deg = self.findGeneName(key)
					writer.writerow([deg, tumorsLen, len(deg_tumor[key]), ratio])
		print "finish"
		return deg_tumor

	#@Parameter: TCGA SGA gene name, mutation hotspot
	#@Return: a csv file contains 4 column, column1 is deg, column2 is tumor name
	#colum3 is total number of tumors the sga is called a driver, column 4 is number of tumors the deg is called target
	#1. find tumors called SGA as a driver
	#2. choose tumors have somatic mutations
	#3. find target degs in tumors set
	def findDEGsInHotspotOfAGivenSGA(self, SGA, hotspot, cutoff):	
		SGA_id = self.findGeneId(SGA)
		tumor_deg = self.findTumorsInWhichAGivenSGAIsDriver(SGA)
		#total tumors
		patients = tumor_deg.keys()

		SMtumor = self.findTumorsHasSMForAGivenSGAInGivenHopspot(SGA, hotspot)
		#tumor subset
		tumors = set(patients).intersection(set(SMtumor))
		tumorsLen = len(tumors)
		#key : DEG_id
		#value : tumorid
		deg_tumor = self.queryPatientsAndDEGsForAGivenSGAandTumorset(SGA, tumors)
		with open("%s_%s.csv"%(SGA, hotspot), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["DEG_name", "NumberOfTumorsCalledDriver", "NumberOfTumorsThisDEGCalledTarget", "CallRate"])
			for key in deg_tumor:
				ratio = len(deg_tumor[key])/(float)(tumorsLen)
				if ratio >= cutoff:		
					deg = self.findGeneName(key)
					writer.writerow([deg, tumorsLen, len(deg_tumor[key]), ratio])
		print "finish"
		return deg_tumor

	#@Parameter: TCGA SGA gene name, mutation hotspot
	#@Return: a csv file contains 4 column, column1 is deg, column2 is tumor name
	#colum3 is total number of tumors the sga is called a driver, column 4 is number of tumors the deg is called target
	#1. find tumors called SGA as a driver
	#2. choose tumors have somatic mutations
	#3. find target degs in tumors set
	def findDEGsInHotspotOfAGivenSGAForTwoHotspot(self, SGA, hotspot1, hotspot2, cutoff):	
		SGA_id = self.findGeneId(SGA)
		tumor_deg = self.findTumorsInWhichAGivenSGAIsDriver(SGA)
		#total tumors
		patients = tumor_deg.keys()

		SMtumor1 = self.findTumorsHasSMForAGivenSGAInGivenHopspot(SGA, hotspot1)
		SMtumor2 = self.findTumorsHasSMForAGivenSGAInGivenHopspot(SGA, hotspot2)
		#tumor subset
		tumors1 = set(patients).intersection(set(	))
		tumors2 = set(patients).intersection(set(SMtumor2))
		tumors = tumors1.union(tumors2)
		tumorsLen = len(tumors)
		#key : DEG_id
		#value : tumorid
		deg_tumor = self.queryPatientsAndDEGsForAGivenSGAandTumorset(SGA_id, tumors)

		with open("%s_%s_%s.csv"%(SGA, hotspot1, hotspot2), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["DEG_name", "NumberOfTumorsCalledDriver", "NumberOfTumorsThisDEGCalledTarget", "CallRate"])
			for key in deg_tumor:
				ratio = len(deg_tumor[key])/(float)(tumorsLen)
				if ratio >= cutoff:		
					deg = self.findGeneName(key)
					writer.writerow([deg, tumorsLen, len(deg_tumor[key]), ratio])
		print "finish"
		return deg_tumor

	#@Parameter: SGA
	#@Return: tumor_id, alternation_type, SCNA type is alternation type is SCNA, SM mutate type, norm type, mutate location is alternation type is SM
	def findTumorsInWhichASGAIsADriverOutputBySMAndSCNA(self, SGA):
		cursor = self.db.cursor()
		SGA_id = self.findGeneId(SGA)
		patients = (self.findTumorsInWhichAGivenSGAIsDriver(SGA)).keys()
		SGA_query = "SELECT DISTINCT patient_id, Mut_type, aa_norm, aa_loc, aa_mut FROM Somatic_Mutations WHERE patient_id in (%s) AND gene_id = '%s')"%(patients, SGA_id)	
		cursor.execute(SGA_query)
		SGA_result=cursor.fetchall()
	
		SCNA_query = "SELECT Distinct patient_id, gistic_score FROM SCNAs WHERE gistic_score IN (-2, 2) AND patient_id in (%s) AND gene_id = '%s'" %(patients, SGA_id)
		cursor.execute(SCNA_query)
		SCNA_result=cursor.fetchall()
		cursor.close()

		with open('%s.csv'%(SGA), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["Tumor_id", "Alternation_Type", "SCNA", "SM", "AA_norm", "AA_loc", "AA_mut"])
			for row in SGA_Result:
				writer.writerow([row[0], "Somatic Mutation", "null", row[1], row[2], row[3], row[4]])
			for row in SCNA_Result:
				writer.writerow([row[0], "SCNA", row[1], "null", "null", "null", "null"])
		print "finish"

	
		


	def findCommonDEGListForTwoSGA(self, SGA1, SGA2):
		deg_tumor1 = self.findTargetDEGforAGivenSGA(self.findGeneId(SGA1))
		deg_tumor2 = self.findTargetDEGforAGivenSGA(self.findGeneId(SGA2))
		
		with open('%s_%s.csv'%(SGAid1, SGAid2), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["DEG_name"])
			for row in query_result:
				writer.writerow([row[0]])

		print "finish"
	
	def findSGADriverForAGivenDEG(self, DEG):
		deg_id = self.findGeneId(DEG)
		
		cursor = self.db.cursor()
		query = "SELECT gene_name FROM\
		(SELECT DISTINCT(SGA_id)FROM TDI_Results WHERE DEG_id = '%s' UNION\
			SELECT DISTINCT(SGA_id) FROM TDI_Results WHERE DEG_id = '%s') as Temp, Genes as G\
		WHERE G.gene_id = Temp.SGA_id"
		
		cursor.execute(query)
		query_result=cursor.fetchall()
		cursor.close()
		with open('%s_%s.csv'%(DEGid1, DEGid2), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["SGA_name"])
			for row in query_result:
				writer.writerow([row[0]])

		print "finish"


	#must be driver
	def findSGARegulateAPairOfDEGs(self, DEG1, DEG2):
		deg_id1 = self.findGeneId(DEG1)
		deg_id2 = self.findGeneId(DEG2)

		cursor = self.db.cursor()
		query = "SELECT gene_name FROM\
		(SELECT DISTINCT(SGA_id)FROM TDI_Results WHERE DEG_id = '%s' UNION\
			SELECT DISTINCT(SGA_id) FROM TDI_Results WHERE DEG_id = '%s') as Temp, Genes as G\
		WHERE G.gene_id = Temp.SGA_id"
		
		cursor.execute(query)
		query_result=cursor.fetchall()
		cursor.close()
		with open('%s_%s.csv'%(DEGid1, DEGid2), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["SGA_name"])
			for row in query_result:
				writer.writerow([row[0]])

		print "finish"
