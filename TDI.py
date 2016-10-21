import MySQLdb
import csv
import re

class TDIqueries:
        #Database connection requires : host, username, password, databse name
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
	#@return: gene name for input gene
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
	def findSGAGeneDriverInAGivenTumor(self, patient):
		cursor = self.db.cursor()
		patient_id = self.findPatientId(patient)
		query = "SELECT SGA_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
			WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id AND T.patient_id = '%s'"%(patient_id)
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
		return sga_deg

	def findSGAUnitDriverInAGivenTumor(self, patient):
		cursor = self.db.cursor()
		patient_id = self.findPatientId(patient)
		query = "SELECT T.gt_unit_group_id, T.DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
			WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.gt_unit_group_id = S.group_id AND T.patient_id = '%s'"%(patient_id)
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
		return sga_deg
	
	def findDriverInAGivenTumor(self, patient):
		gene_driver = findSGAGeneDriverInAGivenTumor(patient)
		unit_driver = findSGAUnitDriverInAGivenTumor(patient)		
		with open("%s.csv"%(patient), 'wb') as csvfile:
			writer = csv.writer(csvfile, delimiter=',',)
			writer.writerow(["Driver_Name", "Number of DEGs"])
			for key in gene_driver.keys():				
				sga = self.findGeneName(key)
				writer.writerow([sga, len(gene_driver[key])])
			for key in unit_driver.keys():
				sga = self.findSGAUnitGroupName(key)
				writer.writerow([sga, len(unit_driver[key])])
		
	#@Parameter: patientname, DEG list 
	#@Return: SGA driver in this tumor, which at least regulate one gene in given target gene list
	#@return: how many degs per SGA covers in given deg list
	def findDriversForListOfDEGsInAGivenTumor(self, patient, degList):
		gene_driver = findSGAGeneDriverInAGivenTumor(patient)
		unit_driver = findSGAUnitDriverInAGivenTumor(patient)

		degSet = set()
		for deg in degList:
			degSet.add(self.findGeneId(deg))

		gene_result = {}
		for key in gene_driver.keys():
			targetDEGs = set(gene_driver[key])
			targets = targetDEGs.intersection(degSet)
			if (len(targets) != 0):
				gene_result[key] = []
				gene_result[key] = targets

		unit_result = {}
		for key in unit_driver.keys():
			targetDEGs = set(unit_driver[key])
			targets = targetDEGs.intersection(degSet)
			if (len(targets) != 0):
				unit_result[key] = []
				unit_result[key] = targets

		with open("%s.csv"%(patient), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["Drive_name", "Number of DEGs"])
			for key in gene_result.keys():
				sga = self.findGeneName(key)
				writer.writerow([sga, len(gene_result[sga])])
			for key in unit_result.keys():
				sga = self.findSGAUnitGroupName(key)
				writer.writerow([sga, len(unit_result[sga])])

	#@Parameter: SGA name (a gene or a SGA unit/group)
	#@Return: List of patient (TDI) id in which input SGA is called a driver
	def findTumorsInWhichAGivenSGAIsDriver(self, SGA):
		cursor = self.db.cursor()
		if re.search("^SGAgroup.", SGA) or re.search("^SGA.unit.", SGA):
			sga_id = self.findSGAUnitGroupId(SGA)
			query = "SELECT patient_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.gt_unit_group_id = S.group_id AND T.gt_unit_group_id = '%s'\
				AND S.name = '%s'"%(sga_id, SGA)
			cursor.execute(query)
		else: 
			sga_id = self.findGeneId(SGA)
			query = "SELECT patient_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id AND T.SGA_id = '%s' AND S.name = '%s'"%(sga_id, SGA)
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
		return tumors

	#@Parameter : SGA name, tumor set
	#@Return : DEGs that called by given SGA in given tumors, organized in a {deg : {tumor list}} dict
	def queryPatientsAndDEGsForAGivenSGAandTumorset(self, SGA, tumors):
		deg_tumor ={}
		cursor = self.db.cursor()
		if re.search("^SGAgroup.", SGA) or re.search("^SGA.unit.", SGA):
			sga_id = self.findSGAUnitGroupId(SGA)
			for tumor in tumors:
				query = "SELECT DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
					WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.gt_unit_group_id = S.group_id AND T.gt_unit_group_id = '%s'\
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
					WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id AND T.SGA_id = '%s'\
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

	#@Parameter: SGA, cutoff
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
	
	#@Parameter: SGA gene name, cutoff 
	#@Return: a csv file contains 4 columns, column1 is DEG name, column2 is numbers of tumors that called given SGA as a driver, 
	#column3 is numbers of tumors the DEG is called target by given SGA
	#column4 is call rate(value in second column divided by value is third column)
	#1. find tumors called SGA as a driver
	#2. choose tumors have SCNA
	#3. find target degs in tumors set
	def findDEGofSCNAForAGivenSGA(self, SGA, cutoff):	
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
		deg_tumor = self.queryPatientsAndDEGsForAGivenSGAandTumorset(SGA, tumors)

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

	#@Parameter: SGA gene name, a cutoff
	#@Return: a csv file contains 4 columns, column1 is DEG name, column2 is numbers of tumors that called given SGA as a driver, 
	#column3 is numbers of tumors the DEG is called target by given SGA
	#column4 is call rate(value in second column divided by value is third column)
	#1. find tumors called SGA as a driver
	#2. choose tumors have somatic mutations
	#3. find target degs in tumors set
	def findDEGsOfSMForAGivenSGA(self, SGA, cutoff):	
		tumor_deg = self.findTumorsInWhichAGivenSGAIsDriver(SGA)
		#total tumors
		patients = tumor_deg.keys()

		SMtumor = self.findTumorsHasSMForAGivenSGA(SGA)
		#tumor subset
		tumors = set(patients).intersection(set(SMtumor))
		tumorsLen = len(tumors)
		#key : DEG_id
		#value : tumorid
		deg_tumor = self.queryPatientsAndDEGsForAGivenSGAandTumorset(SGA, tumors)

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

	#@Parameter: SGA gene name, mutation hotspot, a cutoff 
	#@Return: a csv file contains 4 columns, column1 is DEG name, column2 is numbers of tumors that called given SGA as a driver, 
	#column3 is numbers of tumors the DEG is called target by given SGA
	#column4 is call rate(value in second column divided by value is third column)
	#1. find tumors called SGA as a driver
	#2. choose tumors have somatic mutations
	#3. find target degs in tumors set
	def findDEGsInHotspotOfAGivenSGA(self, SGA, hotspot, cutoff):	
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
	#@Return: a csv file contains 4 columns, column1 is DEG name, column2 is numbers of tumors that called given SGA as a driver, 
	#column3 is numbers of tumors the DEG is called target by given SGA
	#column4 is call rate(value in second column divided by value is third column)
	#1. find tumors called SGA as a driver
	#2. choose tumors have somatic mutations
	#3. find target degs in tumors set
	def findDEGsInHotspotOfAGivenSGAForTwoHotspot(self, SGA, hotspot1, hotspot2, cutoff):	
		tumor_deg = self.findTumorsInWhichAGivenSGAIsDriver(SGA)
		#total tumors
		patients = tumor_deg.keys()

		SMtumor1 = self.findTumorsHasSMForAGivenSGAInGivenHopspot(SGA, hotspot1)
		SMtumor2 = self.findTumorsHasSMForAGivenSGAInGivenHopspot(SGA, hotspot2)
		#tumor subset
		tumors1 = set(patients).intersection(set(SMtumor1))
		tumors2 = set(patients).intersection(set(SMtumor2))
		tumors = tumors1.union(tumors2)
		tumorsLen = len(tumors)
		#key : DEG_id
		#value : tumorid
		deg_tumor = self.queryPatientsAndDEGsForAGivenSGAandTumorset(SGA, tumors)

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
			writer.writerow(["Tumor_name", "Alternation_Type", "SCNA", "SM", "AA_norm", "AA_loc", "AA_mut"])
			tumor_name = findPatientName(row[0])
			for row in SGA_Result:
				writer.writerow([tumor_name, "Somatic Mutation", "null", row[1], row[2], row[3], row[4]])
			for row in SCNA_Result:
				writer.writerow([tumor_name, "SCNA", row[1], "null", "null", "null", "null"])

	#@Parameter: two SGA
	#@Return: a csv file contains 1 column, indicates the common DEG list for these two SGA
	def findCommonDEGListForTwoSGA(self, SGA1, SGA2):
		deg_tumor1 = self.findDEGforAGivenSGA(SGA1)
		deg_tumor2 = self.findDEGforAGivenSGA(SGA2)
		deg1 = deg_tumor1.keys()
		deg2 = deg_tumor2.keys()
		res = deg1.intersection(deg2)
		with open('%s_%s.csv'%(SGAid1, SGAid2), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["DEG_name"])
			for deg in res:
				writer.writerow([deg])

	#@Parameter: two DEG 
	#@Return: a csv file contains 1 column, indicates a SGA driver regulate given pair of DEGs in a tumor
	def findSGARegulateAPairOfDEGs(self, DEG1, DEG2):
		deg_id1 = self.findGeneId(DEG1)
		deg_id2 = self.findGeneId(DEG2)

		cursor = self.db.cursor()
		query_allPatients = "SELECT DISTINCT patient_id FROM Patients"
		cursor.execute(query_allPatients)
		allPatients = cursor.fetchall()
		drivers = []
		for row in allPatients:
			patient = row[0]
			query = "SELECT SGA_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
			WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id AND T.patient_id = '%s'"%(patient)
			cursor.execute(query)
			query_result = cursor.fetchall()
			temp = {}
			for row in query_result:
				if temp.has_key(row[0]):
					temp[row[0]].append(row[1])
				else:
					temp[row[0]] = []
					temp[row[0]].append(row[1])
			#filter out SGA which regulate less than 5 degs
			temp = dict((k,v) for k, v in temp.iteritems() if len(v) >= 5)
			for key in temp.keys():
				if deg_id1 in temp[key] and deg_id2 in temp[key]:
					drivers.append(key)

		with open('%s_%s.csv'%(DEGid1, DEGid2), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["SGA_name"])
			for SGA in drivers:
				writer.writerow([SGA])

	#@Description: given a SGA unit or a SGA gene, find regualted deg list in driven tumors group by tumor type
	#@Parameter: SGA, it can be a SGA unit or a SGA gene
	#@Return: a csv file containning 4 columns. Column1 is cancer type. Column2 is number of tumors which means total numbers of tumors 
	#has SGA events for given SGA. column3 is number of tumors call driver, which means the number of tumors that called given SGA as a driver
	#Column4 is is call rate, it comes from the value in column2 divided by column3
	def findTumorsCalledAGivenSGADriver(self, SGA):
		cursor = self.db.cursor()
		tumor_deg = {}
		if re.search("^SGAgroup.", SGA) or re.search("^SGA.unit.", SGA):
			sga_id = self.findSGAUnitGroupId(SGA)
			query = "SELECT patient_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.gt_unit_group_id = S.group_id AND T.SGA_id = '%s'"%(sga_id)
			cursor.execute(query)
			query_result = cursor.fetchall()
			for row in query_result:
				if tumor_deg.has_key(row[0]):
					tumor_deg[row[0]].append(row[1])
				else :
					tumor_deg[row[0]] = []
					tumor_deg[row[0]].append(row[1])
		else: 
			sga_id = self.findGeneId(SGA)
			query = "SELECT patient_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id AND T.SGA_id = '%s'"%(sga_id)
			cursor.execute(query)
			query_result = cursor.fetchall()
			for row in query_result:
				if tumor_deg.has_key(row[0]):
					tumor_deg[row[0]].append(row[1])
				else :
					tumor_deg[row[0]] = []
					tumor_deg[row[0]].append(row[1])
		cursor.close()

		{cancerType : [{tumor : deg}]}
		cancerType_tumor_deg = {}
		for key in tumor_deg.keys():
			cancer = self.findCancerType(key)
			if cancerType_tumor_deg.has_key(cancer):
				cancerType_tumor_deg[cancer].append(tuple(key, tumor_deg[key]))
			else :
				cancerType_tumor_deg[cancer] = []
				cancerType_tumor_deg[cancer].append(tuple(key, tumor_deg[key]))

		with open("%s_cancer_type_dist.csv"%(SGA), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["Cancer_type", "Number of Tumors", "Number of tumors call driver", "ratio"])
			for cancer in cancerType_tumor_deg.keys():
				totalTumors = len(cancerType_tumor_deg[cancer])
				driverTumors = 0
				for i in range(0, len(cancerType_tumor_deg[cancer])):
					if len(cancerType_tumor_deg[cancer][i]) >= 5:
						driverTumors = driverTumors + 1
				writer.writerow([cancer, totalTumors, driverTumors, driverTumors/totalTumors])
		print "Done"

	#@Description: count number of SGA events and number of driver calls and calculate driver call rate for each SGA
	#@Parameter: SGA, it can be a SGA unit or a SGA gene
	#@Return: a csv file containning 4 columns. Column1 is SGA. Column2 is number of tumors which means total numbers of tumors 
	#has SGA events for given SGA. column3 is number of tumors call driver, which means the number of tumors that called given SGA as a driver
	#Column4 is is call rate, it comes from the value in column2 divided by column3
	def findAllSGACallRate(self):
		cursor = self.db.cursor()
		query_SGAgene = "SELECT DISTINCT gene_id FROM SGAs WHERE gene_id IS NOT NULL"
		cursor.execute(query_SGAgene)
		query_SGAgene_result = cursor.fetchall()

		query_SGAunit = "SELECT DISTINCT unit_group_id FROM SGAs WHERE unit_group_id IS NOT NULL"
		cursor.execute(query_SGAunit)
		query_SGAunit_result = cursor.fetchall()

		SGA_totalTumor_driverTumor_gene = {}
		for row in query_SGAgene_result:
			tumor_deg_gene = {}
			query = "SELECT T.patient_id, T.DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_id AND T.SGA_id = '%s'"%(row[0])
			cursor.execute(query)
			query_result = cursor.fetchall()
			for row in query_result:
				if tumor_deg_gene.has_key(row[0]):
					tumor_deg_gene[row[0]].append(row[1])
				else :
					tumor_deg_gene[row[0]] = []
					tumor_deg_gene[row[0]].append(row[1])
			totalTumors = len(tumor_deg_gene.keys())
			driverTumors = 0
			for key in tumor_deg_gene.keys():
				if len(tumor_deg_gene[key]) >= 5:
					driverTumors = driverTumors + 1
			SGA_totalTumor_driverTumor_gene[row[0]] = tuple(totalTumors, driverTumors)

		SGA_totalTumor_driverTumor_unit = {}
		for row in query_SGAunit_result:
			tumor_dege_unit = {}
			query = "SELECT T.patient_id, T.DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S\
				WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.gt_unit_group_id = S.group_id AND T.SGA_id = '%s'"%(row[0])
			cursor.execute(query)
			query_result = cursor.fetchall()
			for row in query_result:
				if tumor_dege_unit.has_key(row[0]):
					tumor_dege_unit[row[0]].append(row[1])
				else :
					tumor_dege_unit[row[0]] = []
					tumor_dege_unit[row[0]].append(row[1])
			totalTumors = len(tumor_dege_unit.keys())
			driverTumors = 0
			for key in tumor_dege_unit.keys():
				if len(tumor_dege_unit[key]) >= 5:
					driverTumors = driverTumors + 1
			SGA_totalTumor_driverTumor_unit[row[0]] = tuple(totalTumors, driverTumors)

		cursor.close()
		tablename = "AllSGACallRateTable"
		with open("%s.csv"%(tablename), 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["SGA", "Number of Tumors", "Number of tumors call driver", "ratio"])
			for key in SGA_totalTumor_driverTumor_gene.keys():
				SGA_geneName = self.findGeneName(key)
				totalTumors = SGA_totalTumor_driverTumor_gene[key][0]
				driverTumors = SGA_totalTumor_driverTumor_gene[key][1]
				writer.writerow([SGA_geneName, totalTumors, driverTumors, driverTumors/totalTumors])
			for key in SGA_totalTumor_driverTumor_unit.keys():
				SGA_unitName = self.findSGAUnitGroupName(key)
				totalTumors = SGA_totalTumor_driverTumor_unit[key][0]
				driverTumors = SGA_totalTumor_driverTumor_unit[key][1]
				writer.writerow([SGA_unitName, totalTumors, driverTumors, driverTumors/totalTumors])

		print "Done"































