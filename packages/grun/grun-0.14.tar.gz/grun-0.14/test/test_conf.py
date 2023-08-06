
from grun import grun

cfg=grun()
assert not cfg.delete()
assert not cfg.has_key("a")
assert cfg["unknown"]==None
assert not cfg, "cfg should be new"
cfg["a"]=12
assert cfg.has_key("a")
assert cfg.keys()==['a',]
assert cfg["a"]==12, "cfg hasn't be configured ?!"
assert not cfg.exists
cfg.save()
assert cfg.exists

del cfg
cfg=grun()
assert cfg.has_key("a")
assert cfg["a"]==12, "persistance don't work ?!"
assert cfg.exists
assert cfg.delete()
assert cfg["a"]==12, "cfg file has been deleted, but content should be here !"
assert not cfg.exists

del cfg
cfg=grun()
assert not cfg, "cfg should be new again"

cfg=grun(name="aeff")
cfg["b"]=13
assert not cfg.exists
cfg.save()
assert cfg.exists

del cfg
cfg=grun(name="aeff")
assert cfg["b"]==13, "persistance don't work"
assert cfg.exists
cfg.delete()
assert not cfg.exists
del cfg

print "grun config ok"
