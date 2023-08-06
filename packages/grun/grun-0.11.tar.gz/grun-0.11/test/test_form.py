from grun import grun
grun.autotest=True

# all widows should close when hitting "ok"


grun( form=("name","bool_isMale"), doc="form (empty) is a tuple")()
grun( form=["name","bool_isMale"], doc="form (empty) is a list")()
grun( form="name, bool_isMale", doc="form (empty) is a string (with commas)")()
grun( form="name bool_isMale", doc="form (empty) is a string (with spaces)")()
grun( form="name", doc="form (empty) should be named 'kiki'",name="kiki")()

grun( form=[("name",""),("bool_isMale",True)], doc="isMale is true")()
grun( form="name, address",doc="name and address should be empty")()
grun( form="name, address",doc="name and address should be filled")("marc","3st jack")
grun( form="name, address",doc="name and address should be filled again")("marc",address="3st jack")

assert grun( form="name",doc="Just press OK")(name="toto") ==[("name","toto")]
assert grun( form="",doc="You shouldn' see that window !!!")() == []

assert grun( form=[("jo",list("abc")),], doc="just press ok")("c") == [("jo","c")]

grun.form( "nom,prenom" )(nom="stuart")
