from grun import grun

grun("I'm a message box !")
grun("I'm a message error box !!")
grun("I'm a message box named !",name="jo")
assert grun("I'm a question : click YES ?")==True
assert grun("I'm a question : click NO ?")==False
assert not grun("I'm a question : CLOSE window ?")

