import MySQLdb
import csv
import re
import numpy
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

	def createTumorDEGMatrix(self):
		#find all TDI records that satisfy the posterior threshold		
		cursor = self.db.cursor()
		query_tumors = "SELECT DISTINCT patient_id FROM TDI_Results WHERE exp_id = 1"
		cursor.execute(query_tumors)
		tumors = cursor.fetchall()

		query_DEGs = "SELECT DISTINCT DEG_id FROM TDI_Results WHERE exp_id = 1"
		cursor.execute(query_DEGs)
		DEGs = cursor.fetchall()

		tumors_name = []
		for tumor in tumors:
			tumors_name.append(self.findPatientName(tumor[0]))
		print len(tumors_name)

		DEGs_name = []
		DEGs_name.append("")
		for DEG in DEGs:
			DEGs_name.append(self.findGeneName(DEG[0]))
		print len(DEGs_name)

		
		matrix = [[None for x in range(len(DEGs))] for y in range(len(tumors))]

		for i in range(0, len(tumors)):
			tumor = tumors[i][0]
			print tumor
			for j in range(0, len(DEGs)):
				DEG = DEGs[j][0]
				# print DEG
				query_gene = "SELECT SGA_id FROM TDI_Results WHERE exp_id = 1 AND patient_id = '%s' AND DEG_id = '%s'"%(tumor, DEG)
				cursor.execute(query_gene)
				SGA_gene = cursor.fetchall()
				# print SGA_gene
				query_unit = "SELECT SGA_unit_group_id FROM TDI_Results WHERE exp_id = 1 AND patient_id = '%s' AND DEG_id = '%s'"%(tumor, DEG)
				cursor.execute(query_unit)
				SGA_unit = cursor.fetchall()
				# print SGA_unit
				if (len(SGA_gene) == 0 and len(SGA_unit) == 0):
					matrix[i][j] = None
				elif (SGA_gene[0][0] is not None):
					SGA_name = self.findGeneName(SGA_gene[0][0])
					# print SGA_name
					matrix[i][j] = SGA_name
				elif (SGA_unit[0][0] is not None):
					SGA_name = self.findSGAUnitGroupName(SGA_unit[0][0])
					# print SGA_name
					matrix[i][j] = SGA_name
				else:
					print "Error"			
		table_name = "TumorDEGmatrix"
		with open("%s.csv"%(table_name), 'wb') as file:
			for DEG in DEGs_name:
				file.write(DEG + ',')
			file.write('\n')
			for i in range(0, len(tumors_name)):
				file.write(tumors_name[i] + ',')
				for SGA in matrix[i]:
					if (SGA != None):
						file.write(SGA + ',')
					else:
						file.write("null"+ ',')
				file.write('\n')
		print "Done"

def main():
	tdi = FindDEGforAllSGA()
	tdi.createTumorDEGMatrix()
if __name__ == "__main__":
    main()
