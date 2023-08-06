try:
    from __main__ import USETK
except:
    USETK=False

if USETK is True:   # tk only !
    from tkgrun import GuiInit, MessageBox, QuestionBox, ProgressBox, NotifyBox, IconApp, PopApp, GrunApp, \
         gNumber, gFile, gFolder, gBool, gText, gPasswd, gString, gCombo, gCheck, \
         Clipboard
else: # gtk first else tk
    try:
        from gtkgrun import GuiInit, MessageBox, QuestionBox, ProgressBox, NotifyBox, IconApp, PopApp, GrunApp, \
             gNumber, gFile, gFolder, gBool, gText, gPasswd, gString, gCombo, gCheck, \
             Clipboard
    except:
        from tkgrun import GuiInit, MessageBox, QuestionBox, ProgressBox, NotifyBox, IconApp, PopApp, GrunApp, \
             gNumber, gFile, gFolder, gBool, gText, gPasswd, gString, gCombo, gCheck, \
             Clipboard

try:
    # try to override "NotifyBox" if pynotify is present !
    import pynotify
    def NotifyBox(s,title):
        pynotify.init(title)
        pynotify.Notification(title, s, 'info').show()
except:
    pass

import string
def beautifuler(s):
    s="".join([i in string.uppercase and " %s"%i or i for i in list(s)])
    s=" ".join([word.capitalize() for word in s.replace("_"," ").split(" ")])
    return s

class NameGuesser(object):
    def __init__(self,name):
        self.name = name
    def isType(self,typ):
        typ=typ.lower()
        l=self.name.lower().split("_")
        rest=[i for i in l if i!=typ] or [typ,]
        self.name = "_".join(rest)
        return typ in l


class ExoArg(object):
    def __init__(self,fn,name,default,value):
        self._fn=fn
        n=NameGuesser(name)
        self._liste=None

        if type(default) == list:   # type defined by its default value ! here a list defines a combo
            self._liste = default
            self._type = gCombo
            default ="" # clear defaut !!
        elif type(default) == tuple:    # type defined by its default value ! here a tuples defines a list of cbox
            self._liste = default
            self._type = gCheck
            default ="" # clear defaut !!
        else:
            if n.isType("int") or type(default) in (int,long):
                self._type=gNumber
            elif n.isType("file"):
                self._type=gFile
            elif n.isType("folder"):
                self._type=gFolder
            elif n.isType("bool") or type(default) == bool:
                self._type=gBool
            elif n.isType("text"):
                self._type=gText
            elif n.isType("passwd"):
                self._type=gPasswd
            else:
                self._type=gString

        self._realname = name           # real name
        self._name = n.name             # name without type defined inside
        self._value = value or default  # current value

    @property
    def name(self): return self._name   #name without type included
    @property
    def realname(self): return self._realname #real name
    @property
    def affname(self):
        if self.realname in self._fn.infos:
            return self._fn.infos[self.realname]
        else:
            return beautifuler(self.name)

    @property
    def value(self): return self._value

    def create(self,master=""):
        return self._type(self.affname, self._value,lblMax=self._fn.labelmax,liste=self._liste,master=master)

if __name__ == "__main__":
    #~ MessageBox("hello","ko")
    #~ print QuestionBox("heoo","k")
    assert gString("key",None).value==""
    assert gString("key","").value==""
    assert gString("key","val").value=="val"

    assert gNumber("key","12").value==12
    assert gNumber("key",1).value==1
    assert gNumber("key",0).value==0

    assert gBool("k",True).value
    assert gBool("k",1).value
    assert not gBool("k",False).value
    assert not gBool("k",0).value

    assert gCheck("ki",[1,3],liste=[1,2,3]).value == [1,3]
    assert gCheck("ki",None,liste=[1,2,3]).value == []
    assert gCombo("ki",2,liste=[1,2,3]).value == 2
    assert gCombo("ki",None,liste=[1,2,3]).value == None

    g=gString("key",None)
    if hasattr(g,"master"): g.master.withdraw() # tk specific : suppress root window
    #~ print dir(g)


    class F:    #Fake/Mock ExoFn
        def __init__(self,n,returns=False):
            self.name=n
            self.infos={}
            self.labelmax=20
            self.doc="doc "+n
            self.returns=returns
        def call(self,*a,**k):
            print( '%s.call() with : '%self.name,a,k )
            if self.returns:
                return 1

    fn=F("jim")
    fn.args=[
            ExoArg(fn,"name","marco","") ,
            ExoArg(fn,"passwd","toto",""),
            #~ ExoArg(fn,"text","toto",""),
    ]

    fn2=F("jim2",True)
    fn2.args=[
            ExoArg(fn2,"name","marc","") ,
            ExoArg(fn2,"passwd","toto",""),
    ]


    #~ g=GrunApp([fn,fn2])
    g=GrunApp([fn,])
    g.run("title")
    #~ from tkgrun import FnWin
    #~ def j(*a,**k):print a,k
    #~ FnWin("jo",fn,j).run()
