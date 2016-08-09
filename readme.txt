{\rtf1\ansi\ansicpg1252\cocoartf1404\cocoasubrtf470
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
\margl1440\margr1440\vieww12200\viewh10440\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 This class served as a set of common TDI queries.\
\
(Intermediate) Function 1: findGeneId(geneName)\
Description: Given gene name, return TDI database id for this gene\
Input: gene name\
Output: TDI database id\
Example: findGeneId(\'93PIK3CA\'94)\
\
(Intermediate) Function 2: findGeneName(geneID)\
Description: Given TDI database gene_id, return gene name for the gene\
Input: TDI database id\
Output: gene name\
Example: findGeneName(11375)\
\
(Intermediate) Function 3: findSGAUnitGroupId(SGA)\
Description: Given a SGA unit/group name, return TDI database id for this SGA unit/group\
Input: SGA unit/group name\
Output: TDI database id of input SGA\
Example: findSGAUnitGroupId(\'93SGA.unit.10\'94)\
\
(Intermediate) Function 4: findSGAUnitGroupName(SGA_id)\
Description: Given a TDI database SGA unit/group id, return its SGA unit/group name\
Input: TDI database id of a SGA unit/group\
Output: SGA unit/group name\
Example: findSGAUnitGroupName(1)\
\
(Intermediate) Function 5: findPatientName(patient_id) \
Description: Given a TDI database patient id, return is tumor name\
Input: TDI database patient id\
Output: tumor name\
Example: findPatientName(\'93~~~~~~~~\'94)\
\
(Intermediate) Function 6: findPatientId(patient_name)\
Description: Given tumor name, return its TDI database patient_id\
Input: tumor name\
OutPut: TDI database patient_id\
Example: findPatientId(\'93~~~~~~\'94)\
\
Function 7: findDriverInAGivenTumor(tumor_name)\
Description: Given a tumor, find drivers including SGA and SGA unit/group that are drivers in this tumor. Drivers are defined as regulate no less that 5 DEGs with posterior equal or larger than the threshold for a specific SGA gene and SGA unit/group\
Input: tumor name\
Output: a cvs file with two columns, first column is driver name, second column is numbers of DEGs this driver regulated in given tumor\
Example: findDriverInAGivenTumor(\'93~~~~~~~\'94)\
\
Function 8: findDriversForListOfDEGsInAGivenTumor(tumor_name, degList)\
Description: Given a tumor and a list of DEGs, find drivers in this tumor that regulate at least one gene in given DEGs list\
Input: a tumor name, a list of DEGs\
Output: a csv file with two columns, first column is driver name, second column is numbers of DEGs this driver regulated in given tumor also existed in given DEG list\
Example: findDriversForListOfDEGsInAGivenTumor(tumor_name, degList)\
\
(Intermediate) Function 9: findTumorsInWhichAGivenSGAIsDriver(SGA)\
Description: Given a SGA(it could be a gene name or SGA unit/group name), find in which tumors this Given SGA is a driver\
Input: SGA name(gene name or SGA unit group name) \
Output: a dictionary, key is a tumor, value is a list of DEGs in the tumor that are regulated by a given SGA\
Example: findTumorsInWhichAGivenSGAIsDriver(SGA)\
\
(Intermediate) Function 10: findTumorsHasSMForAGivenSGA(SGA)\
Description: Given a SGA gene, find in which tumors it has somatic mutations\
Input: SGA gene name\
Output: a list a tumors in which the given SGA has somatic mutations\
Example: findTumorsHasSMForAGivenSGA(\'93PIK3CA\'94)\
\
(Intermediate) Function 11: findTumorsHasSMForAGivenSGAInGivenHopspot(SGA, hotspot)\
Description: Given a SGA gene, find in which tumors it has somatic mutations at given hotspot\
Input: SGA gene name\
Output: a list a tumors in which the given SGA has somatic mutations at Given hotspot\
Example: findTumorsHasSMForAGivenSGAInGivenHopspot(\'93PIK3CA\'94, 1047)\
\
(Intermediate) Function 12: findTumorsHasSCNAForAGivenSGA(SGA)\
Description: Given a SGA gene, find in which tumors it has copy number alternation\
Input: SGA gene name\
Output: a list a tumors in which the given SGA has copy number alternation at Given hotspot\
Example: findTumorsHasSCNAForAGivenSGA(\'93PIK3CA\'94)\
\
(Intermediate) Function 13: queryPatientsAndDEGsForAGivenSGAandTumorset(SGA, tumors)\
Description: Given a SGA name(it could be a SGA gene name or a SGA unit/group name) and a list of tumors, find DEGs that regulated by this SGA in each tumor\
Input: SGA name, a list of tumors\
Output: a dictionary, key is DEG that regulated by given SGA, value is a list of tumors, it means in these tumors given SGA called key DEG as a target\
\
Function 14: findDEGforAGivenSGA(SGA, cutoff, tumors = None)\
Description: tumors parameter is an optional parameter here. If no tumors parameter, it means given a SGA (a SGA unit/group name or a SGA gene name) and a cutoff value, find the DEGs regulated by the given SGA in all tumors with call rate no less than given cutoff, otherwise it means given a SGA (a SGA unit/group name or a SGA gene name), and a cutoff value, find the DEGs regulated by the given SGA in given tumor sets with call rate no less than given cutoff.\
Input: a SGA unit/group name or a SGA gene name, cutoff value, a list of tumors\
Output: a cvs file with 4 columns, column1 is DEG, column2 is numbers of tumors that called given SGA as a driver, column3 is numbers of tumors the DEG is called target by given SGA, column4 is call rate(value in column2 divided by value is column3)\
\
Function 15: findDEGofSCNAForAGivenSGA(SGA, cutoff)\
Description: given a SGA gene name, find targeted DEG of SCNA regulated by this SGA with call rate no less than given cutoff\
Input: a SGA gene, a cutoff\
Output: a cvs file with 4 columns, column1 is DEG, column2 is numbers of tumors that called given SGA as a driver, column3 is numbers of tumors the DEG is called target by given SGA, column4 is call rate(value in column2 divided by value is column3)\
\
Function 16: findDEGsOfSMForAGivenSGA(SGA, cutoff)\
Description: given a SGA gene name, find targeted DEG of Somatic Mutation regulated by this SGA with call rate no less than given cutoff\
Input: a SGA gene, a cutoff\
Output: a cvs file with 4 columns, column1 is DEG, column2 is numbers of tumors that called given SGA as a driver, column3 is numbers of tumors the DEG is called target by given SGA, column4 is call rate(value in column2 divided by value is column3)\
\
Function 17: findDEGsInHotspotOfAGivenSGA(SGA, hotspot, cutoff)\
Description: Given a SGA gene name, a mutation hotspot, and a cutoff value, find target DEGs regulated by given SGA that has mutation on given hotspot with call rate no less than given cutoff value\
Input: a SGA gene name, a mutation hotspot, a cutoff value\
Output: a cvs file with 4 columns, column1 is DEG, column2 is numbers of tumors that called given SGA as a driver, column3 is numbers of tumors the DEG is called target by given SGA, column4 is call rate(value in column2 divided by value is column3)\
\
Function 18: findDEGsInHotspotOfAGivenSGAForTwoHotspot(SGA, hotspot1, hotspot2, cutoff)\
Description: Given a SGA gene name, two mutation hotspots, and a cutoff value, find target DEGs regulated by given SGA that has mutations on given hotspots with call rate no less than given cutoff value\
Input: a SGA gene name, a mutation hotspot, a cutoff value\
Output: a cvs file with 4 columns, column1 is DEG, column2 is numbers of tumors that called given SGA as a driver, column3 is numbers of tumors the DEG is called target by given SGA, column4 is call rate(value in column2 divided by value is column3)\
\
Function 19: findTumorsInWhichASGAIsADriverOutputBySMAndSCNA(SGA)\
Description: Given a SGA gene name, find tumors called given SGA as a driver\
Input: a SGA gene name\
Output: a csv file with 7 columns, column1 is tumor name. Column2 is alternation type. Column3 is gistic_score if column2 is SCNA, otherwise column 3 is null. Column4 is mutate type if column2 is SM otherwise it is null. Column5 is aa_norm value if column2 is SM otherwise it is null, column 6 is aa_loc value if column2 is SM otherwise it is null, column7 is aa_mut value if if column2 is SM otherwise it is null.\
\
Function 20: findCommonDEGListForTwoSGA(SGA1, SGA2)\
Description: given two SGAs (the SGA could be a SGA gene name or a SGA unit/group name), find the common DEG list for these two SGA\
Input: two SGAs\
Output: a csv file with 1 column of DEG\
\
Function 21: findSGADriverForAGivenDEG(DEG)\
Description: given a pair of DEGs, find SGA drivers regulate given pair of DEGs in a tumor\
Input: two DEG gene name\
Output: a csv file with 1 column of SGA\
\
\
}