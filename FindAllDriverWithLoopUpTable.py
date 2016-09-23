import MySQLdb
import csv

class FindDriverSGA:
	def __init__(self):
		self.db = MySQLdb.connect("localhost", "fanyu", "hellowork", "TDI")

	def findGeneName(self, geneID):
		cursor = self.db.cursor()
		query = "SELECT gene_name FROM Genes WHERE gene_id= '%s'" %(geneID)
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

	def findAllSGA(self):
		cursor = self.db.cursor()
		query = "SELECT patient_id as tumor_id, SGA_id, DEG_id FROM TDI_Results as T, SGAPPNoiseThreshold as S WHERE T.exp_id = 1 AND T.posterior >= S.threshold AND T.SGA_id = S.gene_unit_id"
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

		print len(tumor_SGA)
		#filter out SGA which regulate less than 5 degs
		tumor_SGA = dict((k,v) for k, v in tumor_SGA.iteritems() if len(v) >= 5)
		print len(tumor_SGA)
		
		#flatten dict {(tumorid, SGA_id) : DEG_id} to list [tumor_id, SGA_id, DEG_id]
		records = []
		for key in tumor_SGA.keys():
			for deg in tumor_SGA[key]:
				records.append([key[0], key[1], deg])
		print len(records)

		#key : SGA_id
		#value : (tumor_id, DEG_id)
		tumor_SGA2 = {}
		for row in records:
			temp_tuple = (row[0], row[2])
			if tumor_SGA2.has_key(row[1]):
				tumor_SGA2[row[1]].append(temp_tuple)
			else :
				tumor_SGA2[row[1]] = []
				tumor_SGA2[row[1]].append(temp_tuple)


		##flatten dict {SGA_id : (tumorid, DEG_id)} to list [tumor_id, SGA_id, DEG_id] 
		records2 = []
		for key in tumor_SGA2.keys():
			for tup in tumor_SGA2[key]:
				records2.append([tup[0], key, tup[1]])
		print len(records2)

		with open("AllDriver_WithLookUpTable2.csv", 'wb') as csvfile:
			writer=csv.writer(csvfile, delimiter=',',)
			writer.writerow(["Tumor_id", "SGA", "DEG"])
			for row in records2:
				tumor_id = ""
				if (row[0] is not None):
					tumor_id = self.findPatient(row[0])
				else :
					tumor_id = "Null"
				sga = ""
				if (row[1] is not None):
					sga = self.findGeneName(int(row[1]))
				else :
					sga = "Null"

				deg = ""
				if  (row[2] is not None):
					deg = self.findGeneName(int(row[2]))
				else:
					deg = "Null"
					
				if (sga is not "A0"):
					writer.writerow([tumor_id, sga, deg])
		print "finish"


