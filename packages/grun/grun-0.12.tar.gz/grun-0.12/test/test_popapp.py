USETK=True
from grun import grun

def action_without_return(string):
	""" this window should never quit when pressing 'ok' """
	print "string = ",string
	pass

def action_with_return(string):
	""" this window should quit when hitting 'ok' """
	return string

# tests popup of values (None is a separator)
assert grun( popup=["hello","kook",12,"","SELECT ME",None,"lll"] ) == "SELECT ME"
assert grun.popup( ["hello","kook",12,"","SELECT ME",None,"lll"] ) == "SELECT ME"

# tests popup of methods
grun( popup=[action_without_return, action_with_return,] )

# tests subpopup
print grun.popup(["Albert",("koko","jim,jo,jack".split(",")+[action_with_return,]),("koko","jim,jo,jack".split(","))])

# tests popup of methods and values mixed
print grun( popup=[action_without_return,"Hello",12,None, action_with_return,] )
