from grun import grun

def action_without_return(string):
	""" this window should never quit when pressing 'ok' """
	print("string = ",string)
	pass

def action_with_return(string):
	""" this window should quit when hitting 'ok' """
	print( "string = ",string)
	return 0

def action_without_arguments():
	""" You should not see this windows !!!!"""
	print( "i'm the action without args")

grun( (action_without_return, action_with_return,action_without_arguments) )

