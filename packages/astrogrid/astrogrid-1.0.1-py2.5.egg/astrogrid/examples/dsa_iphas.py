#!/usr/bin/python

from astrogrid import config
config._config['plastic']=False

from astrogrid import DSA

iphas = DSA('ivo://uk.ac.cam.ast/IPHAS/catalogue_test/ceaApplication')
adql='<?ag-adql-schema-version v1.0a1?><v1:Select xmlns:v1="http://www.ivoa.net/xml/ADQL/v1.0"><v1:Restrict Top="10000"/><v1:SelectionList><v1:Item xsi:type="v1:allSelectionItemType" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/></v1:SelectionList><v1:From><v1:Table Name="ChipsAll" Alias="a" xsi:type="v1:tableType" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/></v1:From></v1:Select>'

res=[]

for i in range(1):
	res.append(iphas.query(adql, saveAs='#test/dsa-iphas.vot'))
	


