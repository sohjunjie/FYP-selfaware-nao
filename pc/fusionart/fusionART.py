from ARTfunc import *
import copy

FRACTION = 0.00001

class FusionART:
	def __init__(self,numspace=0,lengths=[],beta=[],alpha=[],gamma=[],rho=[],schema={}):
		self.codes=[]
		icode = {'F2':0, 'weights':[]}
		if len(schema) <= 0:
			self.activityF1=[[]]*numspace 
			if len(lengths) >= numspace:
				wght = []
				for k in range(len(self.activityF1)):
					self.activityF1[k] = [1]*lengths[k]	
					wght.append([1]*lengths[k])
				icode['weights'] = list(wght)
				self.codes.append(icode)
			if type(beta) is float:
				self.beta = beta
			if type(beta) is list:
				self.beta = list(beta)
			self.alpha = list(alpha)
			self.gamma = list(gamma)
			self.rho = list(rho)
			self.pmcriteria = [1.0]*numspace
			self.schema = {}
		else:
			self.schema = copy.deepcopy(schema)
			self.parseSchema(self.schema)
	
		self.lastChoice = []
		self.lastMatch = []
		self.lastActRho = []
		
		self.choiceAct = choiceActFuzzy
		self.compMatch = matchFuncFuzzy
		self.updWeight = []
		self.resonance = resonanceFuzzy
		self.matchVal = matchValFuzzy
		
		for k in range(len(self.activityF1)):
			self.updWeight.append(updWeightFuzzy)
		
		
	#not completely done---------------------------------------------------
	def parseSchema(self,schm={}):
		self.alpha = []
		self.beta = []
		self.gamma = []
		self.rho = []
		if len(schm) > 0:
			if 'codes' in schm:
				self.codes = copy.deepcopy(schm['codes'])
		if 'F1' in schm:
			if 'Fields' in schm['F1']:
				self.F1Fields = copy.deepcopy(schm['F1']['Fields'])
				for k in range(len(schm['F1']['Fields'])):
					if 'alpha' in self.F1Fields[k]:
						self.alpha.append(self.F1Fields[k]['alpha'])
					if 'beta' in self.F1Fields[k]:
						self.beta.append(self.F1Fields[k]['beta'])
					if 'gamma' in self.F1Fields[k]:
						self.gamma.append(self.F1Fields[k]['gamma'])
					if 'rho' in self.F1Fields[k]:
						self.rho.append(self.F1Fields[k]['rho'])
			if 'activityF1' in schm['F1']:
				self.activityF1 = copy.deepcopy(schm['F1']['activityF1'])
			else:
				if not hasattr(self,'activityF1'):
					if hasattr(self, 'F1Fields'):
						self.F1FieldsSetup(self.F1Fields)
					else:
						if 'numspace' in schm['F1']:
							if 'lengths' in schm['F1']:
								self.activityF1 = [[]]*schm['F1']['lengths']
								for k in range(len(self.activityF1)):
									self.activityF1[k] = [1]*schm['F1']['lengths'][k]
				buttUpAllF1()
		#else:
	#-----------------------------------------------------		
					

	def F1FieldsSetup(self, fschemas):
		actTmp = []
		schmTmp = []
		for k in range(len(fschemas)):
			fschema = initFieldSchema(fschemas[k])
			schmTmp.append(fschema)
			factivity = getActivityFromField(fschema)
			self.setActivityF1(factivity,kidx=k)
		self.F1Fields = schmTmp
		
	def buttUpAllF1(self):
		if hasattr(self,'F1Fields'):
			for k in range(len(self.F1Fields)):
				self.setActivityF1(getActivityFromField(self.F1Fields[k]),kidx=k)
	

	def updateF1bySchema(self,fschemas,refresh=False):
		for k in range(len(fschemas)):
			if 'name' in fschemas[k]:
				for kf in range(len(self.F1Fields)):
					if isSchemaWithAtt(self.F1Fields[kf],'name',fschemas[k]['name']):
						self.F1Fields[kf].update(fschemas[k])
						if refresh:
							self.F1Fields[kf] = refreshComplSchema(self.F1Fields[kf])
		self.buttUpAllF1()

	def updateF1byAttVal(self,attvals,kidx=-1,name=''):
		if kidx >= 0:
			self.F1Fields[kidx].update(setSchemabyAttVal(self.F1Fields[kidx],attvals))
		if len(name) > 0:
			for kf in range(len(self.F1Fields)):
				if isSchemaWithAtt(self.F1Fields[kf],'name',name):
					self.F1Fields[kf].update(setSchemabyAttVal(self.F1Fields[kf],attvals))
		self.buttUpAllF1()
		
	def updateF1byVals(self,vals,kidx=-1,name=''):
		if kidx >= 0:
			self.F1Fields[kidx].update(setValFieldSchema(self.F1Fields[kidx],vals))
		if len(name) > 0:
			for kf in range(len(self.F1Fields)):
				if isSchemaWithAtt(self.F1Fields[kf],'name',name):
					self.F1Fields[kf].update(setValFieldSchema(self.F1Fields[kf],vals))
		self.buttUpAllF1()
		#for k in range(len(vals)):
			

	
	def buttUpF1(self,fschema,kidx=-1,fname=''):
		if kidx >= 0:
			self.F1Fields[kidx].update(fschema)
		else:
			if len(fname)>0:
				for k in range(len(self.F1Fields)):
					if 'name' in self.F1Fields[k]:
						if self.F1Fields[k]['name'] == fname:
							self.buttUpF1(fschema,k)
							break
			else:
				for k in range(len(fschema)):
					self.buttUpF1(fschema[k],k)
		for k in range(len(self.F1Fields)):
			self.setActivityF1(getActivityFromField(self.F1Fields[k]),kidx=k)

	def TopDownF1(self,kidx=-1):
		F1f = []
		if (len(self.activityF1) > 0) and (len(self.F1Fields)>0):
			for k in range(len(self.activityF1)):
				c = False
				if 'compl' in self.F1Fields[k]:
					c = self.F1Fields[k]['compl']
				self.F1Fields[k].update(readOutVectSym(self.activityF1[k], c))
			F1f = copy.deepcopy(self.F1Fields)
		return F1f
	
	def setActivityF1(self,val,kidx=-1,iidx=-1):
		if kidx > -1:
			if iidx > -1:
				self.activityF1[kidx][iidx] = val
			else:
				self.activityF1[kidx] = list(val)
		else:
			self.activityF1 = list(val)
		
	
	def setActivityF2(self,val,jidx):
		self.codes[jidx]['F2'] = val 

	def setParam(self,param,value,k=-1):
		if param == "beta":
			if type(value) is float:
				self.beta = value
			if type(value) is list:
				if k>0:
					self.beta[k]=value
				else:
					self.beta=list(value)
		if param == "alpha":
			if k>0:
				self.alpha[k]=value
			else:
				self.alpha=list(value)
		if param == "gamma":
			if k>0:
				self.gamma[k]=value
			else:
				self.gamma=list(value)
		if param == "rho":
			if k>0:
				self.rho[k]=value
			else:
				self.rho=list(value)

	def compChoice(self):
		self.codes = attValList(list(self.choiceAct(self.activityF1,listAttVal(self.codes,'weights'),self.alpha,self.gamma,listAttVal(self.codes,'F2'))),self.codes,'F2')
			
	def compMatch(self, j, k):
		return self.matchFunc(self.activityF1[k],self.codes[j]['weights'][k])
		
	def expandCode(self):
		tw = []
		for k in range(len(self.activityF1)):
			tw.append([1]*len(self.activityF1[k]))
		self.codes.append({'F2':0, 'weights':list(tw)})
		
	def uncommitted(self,idx):
		for k in range(len(self.codes[idx]['weights'])):
			sumw = 0
			for i in range(len(self.codes[idx]['weights'][k])):
				sumw += self.codes[idx]['weights'][k][i]
			if sumw <= (len(self.codes[idx]['weights'][k])/2):
				return False
		return True
		
	def codeCompetition(self):
		maxact = -1
		c = -1
		for j in range(len(self.codes)):
			if self.codes[j]['F2'] > maxact:
				maxact = self.codes[j]['F2']
				if maxact > 0:
					c = j
		return c
		
	def doLearn(self,j):
		for k in range(len(self.activityF1)):
			for i in range(len(self.activityF1[k])):
				self.codes[j]['weights'][k][i] = self.updWeight[k](self.beta[k], self.codes[j]['weights'][k][i], self.activityF1[k][i])
				
				
	def doOverwrite(self,j):
		for k in range(len(self.activityF1)):
			self.codes[j]['weights'][k] = list(self.activityF1[k])
			
	def autoLearn(self,j,overwrite=False,printoutGenCode=False):
		if self.uncommitted(j):
			self.expandCode()
			if printoutGenCode:
				print 'new code ' + str(j) + ' is generated'
		if overwrite:
			self.doOverwrite(j)
		else:
			self.doLearn(j)
			if printoutGenCode:
				print 'code ' + str(j) + ' is updated'
			
	def doReadout(self,j,k,overwrite=True):
		for i in range(len(self.activityF1[k])):
			if overwrite:
				#self.activityF1[k][i] = self.weights[j][k][i]
				self.activityF1[k][i] = self.codes[j]['weights'][k][i]
			else:
				self.activityF1[k][i] = min(self.activity[k][i],self.codes[j]['weights'][k][i])
	
	def doReadoutF1(self,j,k=-1,overwrite=True):
		if k<0:
			for kf in range(len(self.activityF1)):
				self.doReadout(j,kf,overwrite)
		else:
			self.doReadout(j,k,overwrite)
		self.TopDownF1()
	
	def isResonance(self, j, rhos=[]):
		crhos = list(self.rho)
		if len(rhos)>0:
			crhos = list(rhos)
		if self.resonance(self.activityF1,self.codes[j]['weights'],chros):
			return True
		else:
			return False
			
	def rhotracking(m,fraction):
		return min(m+fraction,1)
	
	def resSearch(self,mtrack=[],rhos=[],F2filter=[]):
		resetcode = True
		J = -1
		crhos = self.rho
		if len(rhos)>0:
			crhos = list(rhos)
		self.compChoice()
		self.lastChoice = listAttVal(self.codes,'F2')
		while resetcode:
			resetcode = False
			J = self.codeCompetition()
			if J >= 0:
				matches = list(self.matchVal(self.activityF1,self.codes[J]['weights']))
				self.lastmatch = list(matches)
				if pmismatch(matches,self.pmcriteria):
					return J
				if(not mresonance(matches,crhos)) or (J in F2filter):
					self.activityF2[J] = 0
					self.codes[J]['F2'] = 0
					resetcode = True
					for m in range(len(mtrack)):
						if crhos[mtrack[m]] < matches[mtrack[m]]:
							crhos[mtrack[m]] = self.rhotracking(matches[mtrack[m]],FRACTION)
				self.lastActRho = list(crhos)
		return J
					
	def displayNetwork(self):
		for j in range(len(self.codes)):
			print 'Code: ' + str(j) + ' ' + str(self.codes[j])
		print '-----------------------------------------'
		print 'F1: ' + str(self.activityF1)
		
	def displayNetParam(self):
		print 'alpha: ' + str(self.alpha)
		print 'beta: '+ str(self.beta)
		print 'gamma: ' + str(self.gamma)
		print 'rho: ' + str(self.rho)

	def expandInput(self,idxs=[],quant=1):
		for q in range(quant):
			for i in range(len(idxs)):
				self.activityF1[idxs[i]].append(0)
				for j in range(len(self.weights)):
					self.weights[j][idxs[i]].append(1)



