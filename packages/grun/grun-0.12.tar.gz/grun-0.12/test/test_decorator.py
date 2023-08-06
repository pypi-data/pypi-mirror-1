from grun import grun
grun.autotest=True

@grun
def form1(txt):
	""" this window should close on "Ok" (coz return something) \n !!! PRESS OK  !!!"""
	print "form1 action, txt=",txt
	return True

@grun
def form2(txt):
	""" this window should never close on "Ok" (coz return nothing)"""
	print "form2 action, txt=",txt

@grun
def form3(txt):
	""" this window/form should be filled (coz called with params)"""
	print "form3 - action, txt=",txt
	return True

@grun
def form4(txt="default value"):
	""" this window/form should be filled (coz has a default value )"""
	print "form4 - action, txt=",txt
	return True

@grun
def form5():
	""" you shouldn't see this window (coz no args)"""
	print "form5 - action"

assert form1() == True
assert form2() == None
form4()
form3(txt="test1")
form3("test2")

form5()
grun( form5 )()		# note that a decorated method can be called thru grun() too, no trouble !

