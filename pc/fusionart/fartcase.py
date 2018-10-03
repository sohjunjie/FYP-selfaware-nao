from fusionART import *

#initialize the fusionART object
fa = FusionART(numspace=3,lengths=[4,4,2],beta=[1.0,1.0,1.0],alpha=[0.1,0.1,0.1],gamma=[1.0,1.0,1.0],rho=[0.2,0.2,0.5])

#setting up the F1 field definition using schema in JSON
fa.F1FieldsSetup([{'name':'state','compl':True,'attrib':['s1','s2']},{'name':'action','attrib':['a1','a2','a3','a4']},{'name':'Q','compl':True,'attrib':['q']}])

#display the current network's weights and activation 
fa.displayNetwork()


fa.setActivityF1([[1,0,0,1],[0,0,0,1],[0.6,0.4]]) #set the input vectors activations of F1 fields
J = fa.resSearch() #search for a resonant code J
print 'selected ', J
if fa.uncommitted(J):		#check if the code selected is committed or uncommitted
	print 'uncommitted selected'
fa.autoLearn(J,printoutGenCode=True) #automatically expand the F2 codes if j is uncommitted and learn it based on input
fa.doReadoutF1(J)	#readout the selected code J to F1 field

#display the current network's weights and activation
fa.displayNetwork()

fa.setActivityF1([[0,1,1,0],[1,0,0,0],[0.3,0.7]]) #set the input with another different pattern
J = fa.resSearch()
print ''
print 'selected ', J
if fa.uncommitted(J):
	print 'uncommitted selected'
fa.autoLearn(J,printoutGenCode=True)
fa.doReadoutF1(J)

fa.displayNetwork()

#set the input in F1 based on F1 schema which includes complemented code (for 'state' and 'Q')
fa.updateF1bySchema([{'name':'state','val':[1,0]},{'name':'action','val':[0,0,0,1]},{'name':'Q','val':[0.2]}],refresh=True)
J = fa.resSearch()
print ''
print 'selected ', J
if fa.uncommitted(J):
	print 'uncommitted selected'
fa.autoLearn(J,printoutGenCode=True)
fa.doReadoutF1(J)

fa.displayNetwork()

#set the input in F1 based on particular attributes in the schema field (with complement coded) 
fa.updateF1byAttVal({'s1':0.0,'s2':1.0},name='state')
fa.updateF1byAttVal({'a1':1,'a2':0, 'a3':0, 'a4':0},name='action')
fa.updateF1byAttVal({'q':0.3},name='Q')

J = fa.resSearch()
print ''
print 'selected ', J
if fa.uncommitted(J):
	print 'uncommitted selected'
fa.autoLearn(J,printoutGenCode=True)
fa.doReadoutF1(J)

fa.displayNetwork()

