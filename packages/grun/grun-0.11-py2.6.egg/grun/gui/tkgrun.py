#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from Tkinter import *
    import tkMessageBox,tkFileDialog
except:
    from tkinter import *
    import tkinter.messagebox as tkMessageBox
    import tkinter.filedialog as tkFileDialog

TIMER=2000

import re
def stripTags(data):
    return re.compile(r'<.*?>').sub('', data)

import string
def beautifuler(s):
    s=stripTags(s)
    s="".join([i in string.uppercase and " %s"%i or i for i in list(s)])
    s=" ".join([word.capitalize() for word in s.replace("_"," ").split(" ")])
    return s.strip(" ")



class tkWin(Toplevel):
    def __init__(self,name,**k):
        Toplevel.__init__(self,border=4,**k)
        self.master.withdraw()  # hide real tk root
        self.title(name)
        #~ self.withdraw()

    def run(self):
        self.center()
        #~ self.deiconify()
        self.focus()
        self.wait_window()

    def focus(self):
        self.grab_set()
        self.focus_set()

    def center(self):
        self.update_idletasks()
        w= self["width"]!=0 and self["width"] or self.winfo_width()
        h= self["height"]!=0 and self["height"] or self.winfo_height()
        ws,hs = self.winfo_screenwidth(),self.winfo_screenheight()
        self.geometry('%dx%d+%d+%d' % (w, h, (ws/2) - (w/2), (hs/2) - (h/2)))
        #~ self.update_idletasks()


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def GuiInit(ico):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """ ico for *nix : "@/home/manatlan/Documents/python/glutPaint/data/arrow.xbm"
        ico for win : "file.ico"
    """
    pass
    #~ if ico is not None:
        #~ Tk().iconbitmap(ico)

        #~ bit=PhotoImage(file='/home/manatlan/Documents/www/manella.com/static/manella.gif',format='gif')
        #~ lb=Label(None,image=bit)
        #~ lb.grid()
        #~ TK.iconwindow(lb)


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def MessageBox(content,title,error=None):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    root=Tk()
    root.withdraw()  # hide real tk root
    if error:
        tkMessageBox.showerror(title,stripTags(content),parent=root)
    else:
        tkMessageBox.showinfo(title,stripTags(content),parent=root)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def QuestionBox(content,title):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #TODO: can't return None ;-(
    root=Tk()
    root.withdraw()  # hide real tk root
    return (tkMessageBox.askquestion(title,stripTags(content),parent=root)=="yes")


class tkBase(Frame):
    def __init__(self,name,lblMax=30,master=None,liste=None):
        Frame.__init__(self,master)
        l = Label(self,text=stripTags(name),anchor=E,width=lblMax)
        l.pack({"side": "left"},anchor=E)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gString(tkBase):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        tkBase.__init__(self,name,**k)

        self.v=StringVar()
        self.v.set(value or "")

        e = Entry(self,textvariable=self.v)
        e.pack({"side": "left"},expand=1,fill="x")
        self._e=e

    @property
    def value(self):
        return self.v.get()


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gPasswd(gString):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        gString.__init__(self,name,value,**k)
        self._e.config(show="*")

    @property
    def value(self):
        return self.v.get()

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gNumber(gString):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        gString.__init__(self,name,value is not None and str(value),**k)

    @property
    def value(self):
        v=self.v.get()
        return v and int(v)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gFile(gString):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        gString.__init__(self,name,value,**k)
        b = Button(self,text="...",command=self._sel)
        b.pack({"side": "left"})
    def _sel(self):
        v=tkFileDialog.askopenfilename()
        if v:
            self.v.set(v)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gFolder(gFile):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        gFile.__init__(self,name,value,**k)

    def _sel(self):
        v=tkFileDialog.askdirectory()
        if v:
            self.v.set(v)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gBool(tkBase):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        tkBase.__init__(self,name,**k)

        self.v=IntVar()
        self.v.set(value or False)

        e = Checkbutton(self,variable=self.v)
        e.pack({"side": "left"})

    @property
    def value(self):
        return self.v.get()


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gText(tkBase):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        tkBase.__init__(self,name,**k)

        self.v=StringVar()
        self.v.set(value or "")

        xscrollbar = Scrollbar(self, orient=HORIZONTAL,)
        xscrollbar.pack(side=BOTTOM, fill=X)

        yscrollbar = Scrollbar(self)
        yscrollbar.pack(side=RIGHT, fill=Y)

        e = Text(self,height=6,bg="white",wrap=NONE,
            xscrollcommand=xscrollbar.set,
            yscrollcommand=yscrollbar.set,
            )

        xscrollbar["command"] = e.xview
        yscrollbar["command"] = e.yview

        e.insert("1.0",value or "")
        e.pack({"side": "left"},expand=1,fill="both")
        self._e=e

    @property
    def value(self):
        return self._e.get("1.0",END)



#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gCheck(tkBase):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        list= "liste" in k and k["liste"] or []
        tkBase.__init__(self,name,**k)

        f=Frame(self)
        f.pack({"side":"left"},anchor=W)
        self._l=[]
        for i in list:
            b=IntVar()
            if value:
                if i in value: b.set(1)
            e=Checkbutton(f,text=str(i),variable=b,anchor=W,justify=LEFT)
            b.myvalue = i
            e.pack(anchor=W)
            self._l.append(b)

    @property
    def value(self):
        return [b.myvalue for b in self._l if b.get()]



#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gCombo(tkBase):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        list= "liste" in k and k["liste"] or []
        tkBase.__init__(self,name,**k)


        self.ol = list
        self.sl = [str(i) for i in list]

        self.variable = StringVar(self)
        self.variable.set( str(value) ) # default value

        w = OptionMenu(self, self.variable, *self.sl)
        w.pack({"side":"left"},anchor=W)

    @property
    def value(self):
        v=self.variable.get()
        if v in self.sl:
            idx = self.sl.index(v)
            return self.ol[idx]


class Popup(Menu):
    """
w.bind("<Button-3>", p.show)

b = Button(root, text="Quit", command=p.show)
    """
    def __init__(self,l,master=None):
        Menu.__init__(self,master, tearoff=0)
        self.bind( '<ButtonRelease-1>', self.testhide )

        def addMenus(x,l):
            #~ def _cb(parent,menu):
                #~ def __cb(*a):
                    #~ print a
                    #~ menu.unpost()
                #~ return __cb
            for n,c in l:
                if n is None or n.strip(" -") in ["","-"]:
                    x.add_separator()
                elif type(c) in (list,tuple):
                    m=Menu(x,tearoff=0)
                    #~ m.bind( '<Enter>', self.hide )
                    addMenus(m,c)
                    x.add_cascade(label=n,menu=m,command=c)
                else:
                    x.add_command(label=n,command=c)

        addMenus(self,l)

    def show(self,event=None):
        try:
            if event:
                x,y=event.x_root, event.y_root
            else:
                x,y=self.winfo_pointerx(),self.winfo_pointery()
            self.tk_popup(x,y,0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            #~ self.grab_release()
            pass

    def hide(self,event):
        self.quit()

    def testhide(self,event):
        if not (0<=event.x<=event.widget.winfo_width() and 0<=event.y<=event.widget.winfo_height()):
            # click is outside of the popup, so quit
            self.hide(event)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def PopApp(l,name,closeAfter=True):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    assert len(l)>0
    root=Tk()
    root.withdraw()
    root.ret=None

    def _cb(f): # callback method
        def __cb():
            g=GrunApp([f])
            g.run(name)
            root.quit()
            #~ if closeAfter:
                #~ root.quit()
            #~ else:
                #~ p.show()
        return __cb

    def _ss(s): # callback str
        def __cb():
            root.ret=s
            root.quit()
        return __cb


    def mkList(l):
        ll=[]
        for f in l:
            if f.__class__.__name__=="ExoFct":
                ll.append( (beautifuler(f.name),_cb(f)) )
            elif f is None or str(f).strip("- ") in ("","-"):
                ll.append( ("","") )    #separator
            elif type(f) == tuple:
                label,menus = f
                assert type(menus) in (list,tuple)
                ll.append( (label,mkList(menus)) )
            else:
                ll.append( (str(f),_ss(f)) )
        return ll

    ll=mkList(l)

    #~ ll.append( ("",""))
    #~ ll.append( ("Quit",root.quit))
    p=Popup(ll,master=root)
    p.show()
    root.mainloop()
    return root.ret

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def NotifyBox(txt,name):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    c="#FFFFEE"
    w=tkWin(name,borderwidth=30,background=c,width=400)
    w.master.after(TIMER,w.destroy)
    Label(w,text=txt,background=c).pack()
    w.run()

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class ProgressBox(object):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    MAX=30
    def __init__(self,gen,name):
        w=tkWin(name,borderwidth=20)
        self.w=w
        self._gen=gen
        self.l1 = Label(self.w,text="")
        self.l1.pack(fill="x")

        self.p1 = Label(self.w,width=0,bg="red",anchor=W,relief=SUNKEN)
        self.p1.pack({"side":"left"})
        self.p2 = Label(self.w,width=ProgressBox.MAX,anchor=W,relief=SUNKEN)
        self.p2.pack({"side":"left"})
        self.w.center()
        self.w.focus()

    def run(self):
        import time
        while 1:
            try:
                elt = self._gen.next()
            except StopIteration:
                break
            f,txt= type(elt)==tuple and elt or (elt,"Waiting")
            self.l1.config(text=txt)
            tp1 = int(f*ProgressBox.MAX)
            tp2 = ProgressBox.MAX - tp1
            self.p1.config(width=tp1)
            self.p2.config(width=tp2)
            self.w.update()
            time.sleep(0.1)
        self.w.destroy()
        #~ self.w.wait_window()
        #~ print dir(self.w)



#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class IconApp(object):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """ simulate IconApp as a PopApp ;-( """
    def __init__(self,methods,name,img):
        self._l=methods
        self._name=name
        print("IconApp can't work with Tk, simulating PopApp !")

    def run(self):
        PopApp(self._l,self._name,False)


class FnWin(tkWin):
    def __init__(self,name,fn,callback):
        t = "%s - %s" % (name,beautifuler(fn.name))
        tkWin.__init__(self,t,bd=4)

        if fn.doc:
            Label(self,text=stripTags(fn.doc)).pack(fill='x')

        # create widget with creator()
        self._wg=[]
        for arg in fn.args:
            obj=arg.create(self)
            obj.pack(fill="x")
            self._wg.append(obj)

        def _cb(f):
            def __cb():
                return callback(None,f)
            return __cb

        b=Button(self,text="Ok",width=16,command=_cb(self))
        b.pack()

        self._fn=fn
        self.ret=None

    def callfn(self,*a):
        """ call current method with form's fields """
        vals = [i.value for i in self._wg]
        self.ret = self._fn.call(*vals)
        return self.ret



#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class GrunApp(object):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,l):
        assert len(l)>0
        self.ret=None
        self._l=l

    def run(self,name,doc=None):
        self._name=name
        if len(self._l)>1:

            w=tkWin(name,width=200,borderwidth=4)

            if doc:
                d=Label(w,text=stripTags(doc))
                d.pack(fill='x')
            for f in self._l:

                def _cb(f):
                    def _kif():
                        return self._choose(f)
                    return _kif

                b=Button(w, text=beautifuler(f.name), command=_cb(f) ) #~ b.connect("clicked",self._choose,a,f)
                b.pack(fill='x')

            w.run()
            return self.ret
        else:
            return self._choose(self._l[0])


    def _choose(self,fn):
        if fn.args: # if args, present a form
            w=FnWin(self._name,fn,self._clickOK)
            #~ #=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|
            #~ if grun.autotest:
                #~ gobject.timeout_add(500,self._clickOK,None,w)
            #~ #=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|
            w.run()
            self.ret=w.ret
            w.destroy()
        else: # if no args, run imediatly
            #~ self.ret=w.callfn()
            self.ret=fn.call()
        return self.ret

    def _clickOK(self,w,winfn):
        self.ret=winfn.callfn()
        if self.ret is not None:
            winfn.destroy()


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class Clipboard(object):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,master=None):
        if master ==None:
            master = Tk()
            master.withdraw()
        self._master=master
    def clr(self):
        self._master.clipboard_clear()
    def set(self,v):
        assert isinstance(v,basestring)
        self.clr()
        self._master.clipboard_append(v)
    def get(self):
        return self._master.selection_get(selection="CLIPBOARD")


if __name__=="__main__":
    import os,sys
    p=sys.platform[:3]=="win" and "c:/python25/python.exe" or "python"
    os.system("%s ../../test.py"%p)
