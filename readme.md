##TDI_queries
This class served as a set of common TDI queries.

1. [findGeneId(geneName)](#func1)
* [findGeneName(geneID)](#func2)
* [findSGAUnitGroupId(SGA)](#func3)
* [findSGAUnitGroupName(SGA_id)](#func4)
* [findPatientName(patient_id)](#func5)
* [findPatientId(patient_name)](#func6)
* [findDriverInAGivenTumor(tumor_name)](#func7)
* [findDriversForListOfDEGsInAGivenTumor(tumor_name, degList)](#func8)
* [findTumorsInWhichAGivenSGAIsDriver(SGA)](#func9)
* [findTumorsHasSMForAGivenSGA(SGA)](#func10)
* [findTumorsHasSMForAGivenSGAInGivenhotspot(SGA, hotspot)](#func11)
* [findTumorsHasSCNAForAGivenSGA(SGA)](#func12)
* [queryPatientsAndDEGsForAGivenSGAandTumorset(SGA, tumors)](#func13)
* [findDEGforAGivenSGA(SGA, cutoff, tumors = None)](#func14)
* [findDEGofSCNAForAGivenSGA(SGA, cutoff)](#func15)
* [findDEGsOfSMForAGivenSGA(SGA, cutoff)](#func16)
* [findDEGsInHotspotOfAGivenSGA(SGA, hotspot, cutoff)
](#func17)
* [findDEGsInHotspotOfAGivenSGAForTwoHotspot(SGA, hotspot1, hotspot2, cutoff)](#func18)
* [findTumorsInWhichASGAIsADriverOutputBySMAndSCNA(SGA)](#func19)
* [findCommonDEGListForTwoSGA(SGA1, SGA2)](#func20)
* [findSGARegulateAPairOfDEGs(DEG1, DEG2)](#func21)
* [findTumorsCalledAGivenSGADriver(SGA)](#func22)
* [findAllSGACallRate()](#func23)

### <a name="func1"></a> Function 1 (*Intermediate*): findGeneId(geneName)

**Description**

Given gene name, return TDI database id for this gene

**Args** 

&nbsp;&nbsp;&nbsp;&nbsp;Param1: (str)gene name

**Returns** 

&nbsp;&nbsp;&nbsp;&nbsp;(int) gene id

**Example** 

```python
findGeneId(“PIK3CA”)
```

### <a name="func2"></a> Function 2 (*Intermediate*): findGeneName(geneID)
**Description** 

Given TDI database gene_id, return gene name for the gene

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (int) gene id

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp;(str) gene name

**Example**

```python
findGeneName(11375)
```

### <a name="func3"></a>  Function 3 (*Intermediate*): findSGAUnitGroupId(SGA)
**Description** 

Given a SGA unit/group name, return TDI database id for this SGA unit/group

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA unit/group name

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; (int) unit/group id of input SGA

**Example** 

```python 
findSGAUnitGroupId(“SGA.unit.10”)
```


###<a name="func4"></a>  Function 4 (*Intermediate*): findSGAUnitGroupName(SGA_id)
**Description** 

Given a TDI database SGA unit/group id, return its SGA unit/group name

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (int) SGA unit/group id

**Returns**
&nbsp;&nbsp;&nbsp;&nbsp; (str) SGA unit/group name

**Example**

```python
findSGAUnitGroupName(1)
```

###<a name="func5"></a>  Function 5 (*Intermediate*): findPatientName(patient_id) 
**Description** 

Given a TDI database patient id, return is tumor name

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (int) patient id

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; (str) tumor name

**Example**

```python
findSGAPatientName(1)
```

###<a name="func6"></a>  Function 6 (*Intermediate*): findPatientId(patient_name)
**Description** 

Given tumor name, return its TDI database patient_id

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) tumor name

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; (int) patient id

**Example**

```python
findSGAPatientId("TCGA-02-0003")
```

### <a name="func7"></a> Function 7: findDriverInAGivenTumor(tumor_name)
**Description** 

Given a tumor, find drivers including SGA and SGA unit/group that are drivers in this tumor. Drivers are defined as regulate 
no less that 5 DEGs** with **posterior equal or larger than the threshold** for a specific SGA gene and SGA unit/group

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) tumor name

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; (int) patient id

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; csv file

| driver name        | num of DEGs this driver regulated in the given tumor           |
| ------------- |:-------------:|


### <a name="func8"></a> Function 8: findDriversForListOfDEGsInAGivenTumor(tumor_name, degList)
**Description** 

Given a tumor and a list of DEGs, find drivers in this tumor that regulate at least one gene in given DEGs list

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) tumor name

&nbsp;&nbsp;&nbsp;&nbsp; Param2: (list) list of DEGs

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; csv file

| driver name        | num of DEGs this driver regulated in the given tumor also existed in given DEG list        |
| ------------- |:-------------:|

**Example** 

```python
findDriversForListOfDEGsInAGivenTumor(tumor_name, degList)
```

### <a name="func9"></a>  Function 9 (*Intermediate*): findTumorsInWhichAGivenSGAIsDriver(SGA)
**Description**  

Given a SGA(it could be a gene name or SGA unit/group name), find in which tumors this Given SGA is a driver

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: SGA name(gene name or SGA unit group name)

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; dictionary &lt; tumor, list of DEGs in the tumor that are regulated by a given SGA &gt;

**Example** 

```python
findTumorsInWhichAGivenSGAIsDriver(SGA)
```

### <a name="func10"></a> Function 10 (*Intermediate*): findTumorsHasSMForAGivenSGA(SGA)
**Description**  

Given a SGA gene, find in which tumors it has somatic mutations

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA gene name

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; (list) tumors in which the given SGA has somatic mutations

**Example** 

```python
findTumorsHasSMForAGivenSGA(“PIK3CA”)
```
### <a name="func11"></a> Function 11 (*Intermediate*): findTumorsHasSMForAGivenSGAInGivenhotspot(SGA, hotspot)
**Description**  

Given a SGA gene, find in which tumors it has somatic mutations at given hotspot

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA gene name

&nbsp;&nbsp;&nbsp;&nbsp; Param2: (int) hotspot (aa_loc)

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; (list) tumors in which the given SGA has somatic mutations at given hotspot

**Example** 

```python
findTumorsHasSMForAGivenSGAInGivenhotspot(“PIK3CA”, 1047)
```

### <a name="func12"></a> Function 12 (*Intermediate*): findTumorsHasSCNAForAGivenSGA(SGA)
**Description**  

Given a SGA gene, find in which tumors it has copy number alternation

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA gene name

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; (list) tumors in which the given SGA has copy 

**Example** 

```python
findTumorsHasSCNAForAGivenSGA(“PIK3CA”)
```

### <a name="func13"></a> Function 13 (*Intermediate*): queryPatientsAndDEGsForAGivenSGAandTumorset(SGA, tumors)
**Description**  

Given a SGA name(it could be a SGA gene name or a SGA unit/group name) and a list of tumors, find DEGs that regulated by this SGA in each tumor


**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA gene name

&nbsp;&nbsp;&nbsp;&nbsp; Param2: (list) tumor names

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; dictionary &lt; DEG that is regulated by given SGA, list of tumors in which given SGA is driver of the key DEG &gt;

**Example** 

```python
queryPatientsAndDEGsForAGivenSGAandTumorset(SGA, tumors)
```


### <a name="func14"></a> Function 14: findDEGforAGivenSGA(SGA, cutoff, tumors = None)
**Description**  

tumors parameter is an optional parameter here. If no tumors parameter, it means given a SGA (a SGA unit/group name or a SGA gene name) and a cutoff value, find the DEGs regulated by the given SGA in all tumors with call rate no less than given cutoff, otherwise it means given a SGA (a SGA unit/group name or a SGA gene name), and a cutoff value, find the DEGs regulated by the given SGA in given tumor sets with call rate no less than given cutoff.

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA unit/group name or a SGA gene name

&nbsp;&nbsp;&nbsp;&nbsp; Param2: (int)cutoff value

&nbsp;&nbsp;&nbsp;&nbsp; Param3: (list) tumors

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; Output: cvs file 

| DEG       | num of tumors taht called given SGA as a driver |num of tumors the DEG is called target by given SGA|call rate (col2/col3) |
| ------------- |:-------------:|----------:|--------:|

**Example** 

```python
findDEGforAGivenSGA(SGA, cutoff, tumors = None)
```


### <a name="func15"></a> Function 15: findDEGofSCNAForAGivenSGA(SGA, cutoff)
**Description**  

given a SGA gene name, find targeted DEG of SCNA regulated by this SGA with call rate no less than given cutoff

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA name

&nbsp;&nbsp;&nbsp;&nbsp; Param2: (int) cutoff

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; Output: cvs file 

| DEG       | num of tumors taht called given SGA as a driver |num of tumors the DEG is called target by given SGA|call rate (col2/col3) |
| ------------- |:-------------:|----------:|--------:|


### <a name="func16"></a> Function 16: findDEGsOfSMForAGivenSGA(SGA, cutoff)
**Description**  

given a SGA gene name, find targeted DEG of Somatic Mutation regulated by this SGA with call rate no less than given cutoff

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA name

&nbsp;&nbsp;&nbsp;&nbsp; Param2: (int) cutoff

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; Output: cvs file 

| DEG       | num of tumors taht called given SGA as a driver |num of tumors the DEG is called target by given SGA|call rate (col2/col3) |
| ------------- |:-------------:|----------:|--------:|

### <a name="func17"></a> Function 17: findDEGsInHotspotOfAGivenSGA(SGA, hotspot, cutoff)
**Description**  

Given a SGA gene name, a mutation hotspot, and a cutoff value, find target DEGs regulated by given SGA that has mutation on given hotspot with call rate no less than given cutoff value

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA gene name

&nbsp;&nbsp;&nbsp;&nbsp; Param2: (int) mutation hotspot

&nbsp;&nbsp;&nbsp;&nbsp; Param3: (int) cutoff value

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; Output: cvs file 

| DEG       | num of tumors taht called given SGA as a driver |num of tumors the DEG is called target by given SGA|call rate (col2/col3) |
| ------------- |:-------------:|----------:|--------:|


### <a name="func18"></a> Function 18: findDEGsInHotspotOfAGivenSGAForTwoHotspot(SGA, hotspot1, hotspot2, cutoff)
**Description**  

Given a SGA gene name, two mutation hotspots, and a cutoff value, find target DEGs regulated by given SGA that has mutations on given hotspots with call rate no less than given cutoff value

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA gene name

&nbsp;&nbsp;&nbsp;&nbsp; Param2: (int) mutation hotspot1

&nbsp;&nbsp;&nbsp;&nbsp; Param3: (int) mutation hotspot2

&nbsp;&nbsp;&nbsp;&nbsp; Param4: (int) cutoff value

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; Output: cvs file 

| DEG       | num of tumors taht called given SGA as a driver |num of tumors the DEG is called target by given SGA|call rate (col2/col3) |
| ------------- |:-------------:|----------:|--------:|

### <a name="func19"></a> Function 19: findTumorsInWhichASGAIsADriverOutputBySMAndSCNA(SGA)
**Description**  

Given a SGA gene name, find tumors called given SGA as a driver


**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA gene name

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; Output: csv file 

|tumor name|alternation type |SCNA|SM | aa_norm| aa_loc| aa_mut|
| ------------- |:-------------:|----------:|--------:|--------:|--------:|--------:|


### <a name="func20"></a> Function 20: findCommonDEGListForTwoSGA(SGA1, SGA2)
**Description**  

given two SGAs (the SGA could be a SGA gene name or a SGA unit/group name), find the common DEG list for these two SGA

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA gene name1

&nbsp;&nbsp;&nbsp;&nbsp; Param2: (str) SGA gene name2

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; Output: csv file

|DEG|
| ------------- |

### <a name="func21"></a> Function 21: findSGARegulateAPairOfDEGs(DEG1, DEG2)
**Description**  

given a pair of DEGs, find SGA drivers regulate given pair of DEGs in a tumor

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) DEG gene name1

&nbsp;&nbsp;&nbsp;&nbsp; Param2: (str) DEG gene name2

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; Output: csv file

|SGA|
| ------------- |

### <a name="func22"></a> Function 22: findTumorsCalledAGivenSGADriver(SGA)
**Description**  

given a SGA unit or a SGA gene, find regualted deg list in driven tumors group by tumor type

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA gene name

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; Output: csv file

|cancer type|total number of tumors have SGA events for a given SGA |num of tumors call a given SGA driver|call rate| 
| ------------- |:-------------:|----------:|--------:|--------:|


### <a name="func23"></a> Function 23: findAllSGACallRate()
**Description**  

count number of SGA events and number of driver calls and calculate driver call rate for each SGA

**Args**

&nbsp;&nbsp;&nbsp;&nbsp; Param1: (str) SGA gene/unit name

**Returns**

&nbsp;&nbsp;&nbsp;&nbsp; Output: csv file

|SGA|total number of tumors have SGA events for a given SGA |num of tumors call a given SGA driver|call rate| 
| ------------- |:-------------:|----------:|--------:|--------:|



