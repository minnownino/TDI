import MySQLdb

def populateNoiseThresholdTable(inputFile, delimiter):
	mydb = MySQLdb.connect("localhost", "fanyu", "hellowork", "TDI")
	cursor = mydb.cursor()
	geneTableInput = open(inputFile, "r")
	for line in geneTableInput:
		dataFields = line.strip().split(delimiter)
		#form the sql query by parsing a line from the input file
		sql = "INSERT IGNORE INTO SGAPPNoiseThreshold(name, threshold) VALUES('%s', %s)" %(dataFields[0], dataFields[1])
		try:
			cursor.execute(sql)
			mydb.commit()
		except:
			print "Error trying to input gene into table."
			print sql
			mydb.rollback()
	print "finish"

def populateSGATable(inputFile, delimiter):
	mydb = MySQLdb.connect("localhost", "fanyu", "hellowork", "TDI")
	cursor = mydb.cursor()
	geneTableInput = open(inputFile, "r")
	for line in geneTableInput:
		dataFields = line.strip().split(delimiter)
		#print len(dataFields)
		#if len(dataFields) > 0 :
		#form the sql query by parsing a line from the input file
		sql = "INSERT IGNORE INTO SGAs(patient_name, SGA_name) VALUES('%s', '%s')" %(dataFields[0], dataFields[1])
		try:
			cursor.execute(sql)
			mydb.commit()
		except:
			print "Error trying to input gene into table."
			print sql
			mydb.rollback()
	print "finish"

def populateSMTable(inputFile, delimiter):
	mydb = MySQLdb.connect("localhost", "fanyu", "hellowork", "TDI")
	cursor = mydb.cursor()
	geneTableInput = open(inputFile, "r")
	for line in geneTableInput:
		dataFields = line.strip().split(delimiter)
		#print len(dataFields)
		#if len(dataFields) > 0 :
		#form the sql query by parsing a line from the input file
		str1 = dataFields[7].replace("'", "''")
		str2 = dataFields[8].replace("'", "''")
		sql = "INSERT IGNORE INTO Somatic_Mutations(patient_name, gene_name, tissue, chrome, start_pos, end_pos, strand,variant_class, consequence, ref_allele, tumor_allele1, tumor_allele2, seq_source, aa_norm, aa_loc, aa_mut, protein_func_impact) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %(dataFields[0], dataFields[1], dataFields[2], dataFields[3], dataFields[4], dataFields[5], dataFields[6], str1, str2, dataFields[9], dataFields[10], dataFields[11], dataFields[12], dataFields[13], dataFields[14], dataFields[15], dataFields[16])
		try:
			cursor.execute(sql)
			mydb.commit()
		except:
			print "Error trying to input gene into table."
			print sql
			mydb.rollback()
	print "finish"

populateNoiseThresholdTable("PANCAN.PostProbcutoff.perGT.p=0.001..v9.4Drlu.csv", ",")

# CREATE TABLE SGAPPNoiseThreshold (
# 	id int(11) NOT NULL AUTO_INCREMENT,  
# 	gene_id int(11) DEFAULT NULL,
# 	group_id int(11) DEFAULT NULL,  
# 	name varchar(50) DEFAULT NULL,  
# 	threshold float DEFAULT NULL,  
# 	exp_id int(11) DEFAULT '1',  
# 	PRIMARY KEY (id), 
# 	CONSTRAINT Noises_ibfk_1 FOREIGN KEY (exp_id) REFERENCES Experiments (exp_id) ON DELETE CASCADE, 
# 	CONSTRAINT Noises_ibfk_2 FOREIGN KEY (gene_id) REFERENCES Genes (gene_id) ON DELETE CASCADE, 
# 	CONSTRAINT Noises_ibfk_3 FOREIGN KEY (group_id) REFERENCES SGA_Unit_Group (group_id) ON DELETE CASCADE);
#update SGAPPNoiseThreshold as SP set gene_unit_id =(Select SU.group_id from SGA_Unit_Group as SU where SP.name = SU.name);
#update SGAPPNoiseThreshold as SP set gene_unit_id =(Select G.gene_id from Genes as G where SP.name = G.gene_name) where SP.gene_unit_id = 0;
#CREATE TABLE SGAs (SGA_id int(11) NOT NULL AUTO_INCREMENT, patient_id int(50), gene_id int(11), unit_group_id int(11), patient_name varchar(50), SGA_name varchar(50), PRIMARY KEY(SGA_id), CONSTRAINT SGAs_ibfk_1 FOREIGN KEY (patient_id) REFERENCES Patients (Patient_id) ON DELETE CASCADE, CONSTRAINT SGAs_ibfk_2 FOREIGN KEY (gene_id) REFERENCES Genes (gene_id) ON DELETE CASCADE, CONSTRAINT SGAs_ibfk_3 FOREIGN KEY (unit_group_id) REFERENCES SGA_Unit_Group (group_id) ON DELETE CASCADE);

# CREATE TABLE Somatic_Mutations (
# 	sm_id int(11) NOT NULL AUTO_INCREMENT, 
# 	patient_id int(50) DEFAULT NULL, 
# 	patient_name varchar(50) DEFAULT NULL,
# 	gene_id int(11) DEFAULT NULL,
# 	gene_name varchar(50) DEFAULT NULL,
# 	tissue enum('T','N') DEFAULT NULL,
# 	chrome varchar(10) DEFAULT NULL,
# 	start_pos int(11) DEFAULT NULL,
# 	end_pos int(11) DEFAULT NULL,
# 	strand varchar(5) DEFAULT NULL,
# 	variant_class varchar(50) DEFAULT NULL,
# 	consequence varchar(50) DEFAULT NULL,
# 	ref_allele varchar(20) DEFAULT NULL,
# 	tumor_allele1 varchar(20) DEFAULT NULL,
# 	tumor_allele2 varchar(20) DEFAULT NULL,
# 	seq_source varchar(20) DEFAULT NULL,
# 	aa_norm varchar(20) DEFAULT NULL,
# 	aa_loc varchar(20) DEFAULT NULL,
# 	aa_mut varchar(20) DEFAULT NULL,
# 	protein_func_impact varchar(20) DEFAULT NULL,
# 	PRIMARY KEY(sm_id), CONSTRAINT Somatic_Mutations_ibfk_1 FOREIGN KEY (patient_id) REFERENCES Patients (Patient_id) ON DELETE CASCADE, CONSTRAINT Somatic_Mutations_ibfk_1 FOREIGN KEY (gene_id) REFERENCES Genes (gene_id) ON DELETE CASCADE);