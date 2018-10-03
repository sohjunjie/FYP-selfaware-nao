import copy

#choiceFuncFuzzy: calculate the choice function for a node j
#given input xc, a weight vector wjc, alphac as learning rate, and gammac for contribution parameter as list of parameters
#return the activation value of node j
def choiceFuncFuzzy(xc,wjc,alphac,gammac):
	tj = 0
	for k in range(len(xc)):
		tp = 0
		btm = alphac[k]
		for i in range(len(xc[k])):
			tp += min(xc[k][i],wjc[k][i])
			btm += wjc[k][i]
		tj += gammac[k] * (float(tp)/float(btm))
	return tj

#choiceActFuzzy: calculate the choice function for the entire F2
#given input xc, all weights wc, alphac, and gammac
#return the vector of F2
def choiceActFuzzy(xc,wc,alphac,gammac,F2=[]):
	if(len(F2)<len(wc)):
		F2 = [0.0]*len(wc)
	for j in range(len(wc)):
		F2[j] = choiceFuncFuzzy(xc,wc[j],alphac,gammac)
	return F2

#actReadoutFuzzy: readout the template with Fuzzy AND
#wj is the template (weights) to readout to xold
#returning xnew as the new readout vector
def actReadoutFuzzy(xold,wj):
	xnew = []
	for i in range(len(xold)):
		xnew[i] = min(xold[i],wj[i])
	return xnew
	
#matchFuncFuzzy: Fuzzy match function of weight vector wjck with vector xck
#return the match value
def matchFuncFuzzy(xck,wjck):
	m = 0.0
	denominator = 0.0
	for i in range(len(xck)):
		m += min(xck[i],wjck[i])
		denominator += xck[i]
	if denominator <= 0:
		return 1.0
	return m/denominator
  
#matchValFuzzy: Fuzzy match of  weights wjc with fields xc
#returning the list of match value for every field
def matchValFuzzy(xc,wjc):
	mF1 = []
	if len(xc) > 0:
		mF1 = [0.0]*len(xc)
		for k in range(len(xc)):
			mF1[k] = matchFuncFuzzy(xc[k],wjc[k])
	return mF1

#resonanceFuzzy: given fields xc, weights wjc, and vigilances rho
#check wether it is in resonance condition or not
#return True (resonance) or False (not in resonance)
def resonanceFuzzy(xc,wjc,rho):
	matched = True
	for k in range(len(xc)):
		if matchFuncFuzzy(xc[k],wjc[k]) < rho[k]:
			matched = False
	return matched
	

def updWeightFuzzy(rate, weight, input):
	return (1- rate)*weight + rate*min(weight,input)
	
			
#mresonance: check if given the match values and rhos. it's in resonance
#return True or False
def mresonance(ms,rho):
	for k in range(len(ms)):
		if ms[k] < rho[k]:
			return False
	return True
		
#pmismatch: check if given matching criteria mcriteria, it's in perfect mismatch.
#return True or False
def pmismatch(match,mcriteria):
	for k in range(len(match)):
		if match[k] < mcriteria[k]:
			return False
	return True
	
#genComplementVect: generate complement-coded vector from a vector val
#return a new complement coded vector as a list
def genComplementVect(val):
	compl = [1-i for i in val]
	ccode = val + compl
	return list(ccode)
	
#genActivityVect: generate activity vector given a vector val that can be complemented or not (compl)
#return a new activity vector as a list
def genActivityVect(val,compl=False):
	if(compl):
		return genComplementVect(val)
	return list(val)
	
#readOutVectSym: readout a structure of input/output field (in JSON) given an activity vector which can be complemented (compl)
#return a (JSON) structure of in input/output field {'val': <vector values>, 'vcompl':<complement of val if specified>} 
def readOutVectSym(activity, compl=False):
	if(compl):
		ilen = len(activity)//2
		v = activity[0:ilen]
		c = activity[ilen:ilen*2]
		vc = {'val':v, 'vcompl':c}
		return vc
	return {'val':list(activity)}

def readOutVectSchema(activity, fschema):
	c = False
	if 'compl' in fschema:
		c = fschema['compl']
	return 
	if(compl):
		ilen = len(activity)//2
		v = activity[0:ilen]
		c = activity[ilen:ilen*2]
		vc = {'val':v, 'vcompl':c}
		return vc
	return {'val':list(activity)}

#readOutVectAttribs: readout a structure of input/output field (JSON) with attribute, given an activity vector
#return a (JSON) structure of input/output field {'attval': <dictionary of attribute-value of the field>, 'attcompl':<dictionary of the complement of attribute-value of the field>, 'compl':indicate if the values are complemented}
def readOutVectAttribs(activity, compl=False, attr=[]):
	afield = {}
	afield['attval'] = {}
	afield['compl'] = compl
	if compl:
		afield['compl'] = True
		afield['attcompl'] = {}
		ilen = len(activity)/2
		if len(attr)>0:
			for i in range(len(attr)):
				afield['attval'][attr[i]] = activity[i]
				afield['attcompl'][attr[i]] = activity[i+ilen]
		else:
			for i in range(ilen):
				afield['attval'][i] = activity[i]
				afield['attcompl'][i] = activity[i+ilen]
	else:
		afield['compl'] = False
		if len(attr)>0:
			for i in range(len(attr)):
				afield['attval'][attr[i]] = activity[i]
		else:
			for i in range(len(activity)):
				afield['attval'][i] = activity[i]
	return afield

#initField: initialized a field structure given the length of the field vector or the list of attributes
#return a (JSON) structure of a field {'name': <optional name of the field>, 'compl':<indicate complemented>','val':<value vector>, 'vcompl':<complemented value vector>} 
def initField(fname='',fcompl=False,flen=0,fattr=[]):
	fld = {}
	if len(fname)>0:
		fld['name']=fname
	fld['compl']=fcompl
	if len(fattr)>0:
		flen = len(fattr)
		fld['attrib'] = list(fattr)
	fld['val']=[1.0]*flen
	if fld['compl']:
		fld['vcompl'] = [1.0]*flen
	return fld
	

#initField: initialized a field structure given the field schema specification in fschema
#return a (JSON) structure of a field {'name': <optional name of the field>, 'compl':<indicate complemented>','val':<value vector>, 'vcompl':<complemented value vector>} 
def initFieldSchema(fschema):
	uschema = copy.deepcopy(fschema)
	fname = ''
	attrib = []
	cmpl = False
	if 'name' in fschema:
		fname = fschema['name']
	if 'compl' in fschema:
		cmpl = fschema['compl']
	if 'attrib' in fschema:
		attrib = list(fschema['attrib'])
	if 'val' in fschema:
		uschema.update(initField(fname,fcompl=cmpl,flen=len(fschema['val']),fattr=attrib))
	else:
		uschema.update(initField(fname,fcompl=cmpl,fattr=attrib))
	return uschema

#getActivityFromField: generate activity vector (maybe complemented) given a field structure or schema
#return the activity vector based on the field schema
def getActivityFromField(fschema):
	act = []
	if 'compl' in fschema:
		if fschema['compl']:
			if 'vcompl' in fschema:
				act = fschema['val'] + fschema['vcompl']
			else:
				c = [1-i for i in fschema['val']]
				act = fschema['val'] + c
		else:
			act = list(fschema['val'])
	else:
		act = list(fschema['val'])
	return act
	

#setValFieldSchema: set a value/values of a schema based on an index in the list (optional)
#return the schema with the updated value/values
def setValFieldSchema(fschema,val,vcom=[],idx=-1):
	uschema = copy.deepcopy(fschema)
	if idx>=0:
		uschema['val'][idx] = val
		if not type(vcom) == list:
			if 'vcompl' in uschema:
				uschema['vcompl'][idx] = vcom
	else:
		uschema['val'] = list(val)
	if uschema['compl']:
		if len(vcom)>0:
			uschema['vcompl'] = list(vcom)
		else:
			uschema['vcompl'] = [(1-i) for i in uschema['val']]
	return uschema
	
#setValAttrFieldSchema: set a value/values of a schema based on the attribute of the value
#return the schema with the updated value/values
def setValAttrFieldSchema(fschema,val,att):
	uschema = copy.deepcopy(fschema)
	idx = -1
	if 'attrib' in fschema:
		idx = uschema['attrib'].index(att)
	else:
		idx = att
	uschema = setValFieldSchema(uschema,val,idx=idx)
	return uschema
	

def setSchemabyAttVal(fschema,attval):
	uschema = copy.deepcopy(fschema)
	if 'attrib' in fschema:
		for att in attval.keys():
			if att in fschema['attrib']:
				idx = fschema['attrib'].index(att)
				uschema = setValFieldSchema(uschema,attval[att],idx=idx)
	return uschema
	

def isSchemaWithAtt(fschema,att,val):
	if att in fschema:
		if fschema[att] == val:
			return True
	return False

def refreshComplSchema(fschema):
	uschema = copy.deepcopy(fschema)
	if 'compl' in uschema:
		if uschema['compl']:
			for a in range(len(uschema['val'])):
				uschema['vcompl'][a] = 1 - uschema['val'][a]
	return uschema


def listAttVal(dlist, attr):
	rlist = []
	for i in range(len(dlist)):
		rlist.append(dlist[i][attr])
	return rlist
	
def attValList(olist,dlist,attr):
	for i in range(len(olist)):
		dlist[i][attr] = olist[i]
	return dlist
