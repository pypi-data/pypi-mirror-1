#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk,gtk
pygtk.require('2.0')
import types
import os
import gobject
import time

TIMER=2000

import string
def beautifuler(s):
    s="".join([i in string.uppercase and " %s"%i or i for i in list(s)])
    s=" ".join([word.capitalize() for word in s.replace("_"," ").split(" ")])
    return s.strip(" ")

_img=None
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def GuiInit(ico):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    global _img
    if ico is None:
        ico = gtk.STOCK_EXECUTE

    if os.path.isfile(ico):
        gtk.window_set_default_icon_from_file(ico)
    else:
        gtk.window_set_default_icon_name(ico)

    _img=ico

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def NotifyBox(s,title):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    a=App(title)
    print dir(a)
    a.set_border_width(30)
    l=gtk.Label(s)
    a.set(l)
    gobject.timeout_add(TIMER,a.quit)
    a.run()



class MyLabel(gtk.Label):
    def __init__(self,t=None):
        gtk.Label.__init__(self,t or "")
        self.set_line_wrap(True)
        self.set_selectable(True)
        self.set_use_markup(True)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def MessageBox(data,title=None,error=None):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    if error:
        icon=gtk.STOCK_DIALOG_ERROR
    else:
        icon=gtk.STOCK_DIALOG_INFO
    parent=None
    dialog = gtk.Dialog(title, parent, 0,
            (gtk.STOCK_OK, gtk.RESPONSE_OK)
            )
    dialog.set_default_response(gtk.RESPONSE_OK)


    hbox = gtk.HBox(False, 8)
    hbox.set_border_width(8)
    dialog.vbox.pack_start(hbox, False, False, 0)

    stock = gtk.image_new_from_stock(
            icon,
            gtk.ICON_SIZE_DIALOG)
    hbox.pack_start(stock, False, False, 0)

    table = gtk.Table(2, 2)
    table.set_row_spacings(4)
    table.set_col_spacings(4)
    hbox.pack_start(table, True, True, 0)

    label = MyLabel(data)
    table.attach(label, 0, 2, 0, 1)

    dialog.show_all()

    dialog.run()
    dialog.destroy()
    while gtk.events_pending():      # *!*
        gtk.main_iteration(False)


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def QuestionBox (label, title=None):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    parent=None
    buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK)

    dialog = gtk.Dialog (title, parent, 0, buttons)
    dialog.set_default_response(gtk.RESPONSE_OK)
    dialog.set_has_separator (False)
    dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)

    hbox = gtk.HBox(False, 8)
    hbox.set_border_width(8)
    dialog.vbox.pack_start(hbox, False, False, 0)

    stock = gtk.image_new_from_stock(
            gtk.STOCK_DIALOG_QUESTION,
            gtk.ICON_SIZE_DIALOG)
    hbox.pack_start(stock, False, False, 0)

    table = gtk.Table(2, 2)
    table.set_row_spacings(4)
    table.set_col_spacings(4)
    hbox.pack_start(table, True, True, 0)

    label = MyLabel(label)
    table.attach(label, 0, 2, 0, 1)

    dialog.show_all()
    response = dialog.run()

    if response == gtk.RESPONSE_OK:
        ret= True
    elif response == gtk.RESPONSE_CANCEL:
        ret= False
    else:
        ret = None
    dialog.destroy()
    while gtk.events_pending():      # *!*
        gtk.main_iteration(False)

    return ret

class App(gtk.Window):
    def __init__(self,title):
        gtk.Window.__init__(self)
        self.set_border_width(4)
        self.set_transient_for(None)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_title(title)
        self._hb = gtk.VBox()
        self.add(self._hb)
        self.connect('delete-event', self.quit)
        self._l=[]

    def set(self,o,ex=True,padding=2):
        self.pack(o,ex,True,padding)

    def pack(self,*a):
        self._hb.pack_start(*a)
        o=a[0]
        if not isinstance(o,MyLabel):
            self._l.append(o)

    def run(self):
        self.set_focus_child(self._l[0])
        self.show_all()
        gtk.main()

    def quit(self,widget=None,a=None):
        self.hide()
        gtk.main_quit()

    def waitevents(self):
        # http://www.async.com.br/faq/pygtk/index.py?req=show&file=faq23.020.htp
        time.sleep(0.1)
        while gtk.events_pending():      # *!*
            gtk.main_iteration(False)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class IconApp(gtk.StatusIcon):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,methods,name,img):
        """
        img: a file or a stock icon (gtk.* or string)
        """
        global _img
        gtk.StatusIcon.__init__(self)
        self._methods = methods
        self.connect('activate', self.popup_menu_cb)
        self.connect('popup-menu', self.popup_menu_cb)
        self.set_tooltip(name or NAME)
        if img is None:
            #TODO: set the windowed default icon
            img = _img

        if os.path.isfile(img):
            self.set_from_file(img)
        else:
            if gtk.stock_lookup(img):
                self.set_from_stock(img)
            else:
                print( "bad grun icon '%s', set the default one !" % str(img) )
                self.set_from_stock(gtk.STOCK_EXECUTE)

        #TODO: gardefou pour pas que l'icon soit vide !!!!!!!!!!!! (pas visible alors)
        self._name=name

    def run(self):
        self.set_visible(True)
        gtk.main()

    def quit(self,*a):
        self.set_visible(False)
        gtk.main_quit()

    def popup_menu_cb(self,*a):
        if len(a)==3:
            w,button,time =a
        else:
            w,button,time=a[0],1,0

        if button==1 and len(self._methods)==1:
            self.choose(None,self._methods[0])
        else:
            menu = gtk.Menu()
            for fn in self._methods:
                menuItem = gtk.ImageMenuItem(beautifuler(fn.name))
                menuItem.connect('activate', self.choose, fn)
                menu.append(menuItem)
            menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
            menuItem.connect('activate', self.quit)
            menu.append(menuItem)

            menu.show_all()
            menu.popup(None, None, None, 3, time)

    def choose(self,w,fn):
        f=FnWin(self._name,fn,self.clickOK)
        if fn.args:
            f.run()
        else:
            f.callfn()

    def clickOK(self,w,winfn):
        r=winfn.callfn()
        if r is not None:
            winfn.quit()


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class ProgressBox(App):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,gen,name):
        App.__init__(self,name)
        self._g=gen
        self._t=MyLabel()
        self._t.set_selectable(False)
        self.set(self._t)
        self._pb=gtk.ProgressBar()
        self.set(self._pb)
        gobject.idle_add(self._do)

    def _do(self):
        try:
            elt = self._g.next()
            f,txt= type(elt)==tuple and elt or (elt,"Waiting")
            assert type(float(f))==float,"first param is not a float"
            assert isinstance(txt,basestring),"second param is not a string"
            self._pb.set_fraction(float(f))
            self.waitevents()
            self._t.set_label(txt)
            self.waitevents()
            return 1
        except StopIteration:
            self.quit()
            return 0
        except Exception,m:
            print "ERROR",m
            self.quit()
            return 0


class GtkBase(gtk.HBox):
    def __init__(self,name,lblMax=30,**k):
        gtk.HBox.__init__(self)
        l=MyLabel( name )
        l.set_width_chars(lblMax)
        l.set_alignment(1,0.5)
        self.pack_start( l, False,True,4 )
        self.l=l
        self.lbl=name
    def set(self,obj):
        self.pack_end( obj,True,True )


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gString(GtkBase):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        GtkBase.__init__(self,name,**k)
        self._e=gtk.Entry()
        self._e.set_text(value and str(value) or "")
        self.set( self._e )
        self.set_focus_chain([self._e,])
    @property
    def value(self):
        return self._e.get_text()

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gCombo(GtkBase):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        list= "liste" in k and k["liste"] or []
        GtkBase.__init__(self,name,**k)
        l = gtk.ListStore(str,object)
        for i in list:
            l.append((str(i),i))
        self._e=gtk.ComboBox(l)
        if value in list:
            self._e.set_active(list.index(value))
        cell=gtk.CellRendererText()
        self._e.pack_start(cell,True)
        self._e.add_attribute(cell,"text",0)
        self.set( self._e )
        self.set_focus_chain([self._e,])
    @property
    def value(self):
        l=self._e.get_model()
        idx=self._e.get_active()
        if not idx<0:
            return l[idx][1]

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gCheck(GtkBase):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        list= "liste" in k and k["liste"] or []
        GtkBase.__init__(self,name,**k)

        h=gtk.VBox()
        for i in list:
            b = gtk.CheckButton(str(i))
            b.realValue = i
            if i in (value or []):
                b.set_active( True )
            else:
                b.set_active( False )
            h.add(b)

        self.set( h )
        self._h=h
        self.set_focus_chain([h,])
    @property
    def value(self):
        return [i.realValue for i in self._h.get_children() if i.get_active()]


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gPasswd(gString):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        gString.__init__(self,name,value,**k)
        self._e.set_visibility(False)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gText(GtkBase):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        GtkBase.__init__(self,name,**k)
        sw=gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self._e=gtk.TextView()
        sw.add(self._e)
        b=gtk.TextBuffer()
        b.set_text(value is not None and str(value) or "")
        self._e.set_buffer(b)
        self.pack_end( sw,True,True)
        self.set_focus_chain([self._e,])
    @property
    def value(self):
        b=self._e.get_buffer()
        start = b.get_start_iter()
        end = b.get_end_iter()
        return b.get_text(start,end,False)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gBool(GtkBase):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        GtkBase.__init__(self,name,**k)
        self._e=gtk.CheckButton()
        self._e.set_active(value and True or False)
        self.set( self._e )
        self.set_focus_chain([self._e,])
    @property
    def value(self):
        return self._e.get_active()

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gNumber(gString):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        gString.__init__(self,name,str(value),**k)

    @property
    def value(self):
        v=self._e.get_text()
        return v and int(v)

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gFile(GtkBase):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self,name,value,**k):
        GtkBase.__init__(self,name,**k)
        hb=gtk.HBox()
        self._e=gtk.Entry()
        self._e.set_text(value and str(value) or "")
        hb.pack_start( self._e,True,True )
        b=gtk.Button("...")
        b.connect("clicked",self.click)
        hb.pack_end( b,False,False )
        self.set(hb)
        self.set_focus_chain([hb])
    def click(self,*a):
        dialog=gtk.FileChooserDialog(self.lbl,None,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        dialog.set_default_response (gtk.RESPONSE_OK)
        if self.value: dialog.set_current_folder( os.path.dirname(self.value) )
        r=dialog.run()
        if r == gtk.RESPONSE_OK:
            self._e.set_text(dialog.get_filename())
        dialog.destroy()
    @property
    def value(self):
        return self._e.get_text()

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class gFolder(gFile):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def click(self,*a):
        dialog=gtk.FileChooserDialog(self.lbl,None,gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        dialog.set_default_response (gtk.RESPONSE_OK)
        if self.value: dialog.set_current_folder( self.value )
        r=dialog.run()
        if r == gtk.RESPONSE_OK:
            self._e.set_text(dialog.get_filename())
        dialog.destroy()
    @property
    def value(self):
        return self._e.get_text()


class FnWin(App):
    def __init__(self,name,fn,callback):
        """ create a winform for the method fn, with a callback on button OK"""
        App.__init__(self, "%s - %s" % (name,beautifuler(fn.name)))
        if fn.doc:
            l=MyLabel(fn.doc)
            self.pack(l,False,True,2)
        else:
            l=None
        self._elts=[]

        sw=gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

        vb=gtk.VBox()
        sw.add_with_viewport(vb)
        vp=sw.get_children()[0]

        self.pack(sw,True,True,2)

        wx,wy=0,0
        for arg in fn.args:
            e=arg.create()
            vb.pack_start(e,False,False,2)
            self._elts.append(e)

        hb=gtk.HButtonBox()
        hb.set_layout(gtk.BUTTONBOX_END)
        b=gtk.Button(gtk.STOCK_OK)
        b.set_use_stock(True)
        b.connect("clicked",callback,self)
        hb.add(b)
        self.pack(hb,False,False,2)

        # resize SW/viewport
        vb.show_all() # !important, to be able to get size_request !!!
        wx,wy= vb.size_request()
        wy+=3
        wx+=20
        sw.set_size_request(wx,min(wy,400))
        if wy>400:
            vp.set_shadow_type(gtk.SHADOW_IN)
        else:
            vp.set_shadow_type(gtk.SHADOW_NONE)

        self._fn=fn
        self.ret=None

    def callfn(self,*a):
        """ call current method with form's fields """
        vals = [i.value for i in self._elts]
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
            a=App( name )
            if doc:
                d=MyLabel(doc)
                a.set( d )
            for f in self._l:
                b=gtk.Button( beautifuler(f.name) )
                b.connect("clicked",self._choose,a,f)
                #~ b.set_tooltip(f.doc)
                a.set(b)
            a.set_default_size(200,50)
            a.run()
            return self.ret
        else:
            return self._choose(None,None,self._l[0])


    def _choose(self,widget,win,fn):
        w=FnWin(self._name,fn,self._clickOK)
        if fn.args: # if args, present a form
            #~ #=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|
            #~ if grun.autotest:
                #~ gobject.timeout_add(500,self._clickOK,None,w)
            #~ #=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|
            w.run()
            self.ret=w.ret
        else: # if no args, run imediatly
            self.ret=w.callfn()
        return self.ret

    def _clickOK(self,w,winfn):
        self.ret=winfn.callfn()
        if self.ret is not None:
            winfn.quit()


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
class Clipboard(object):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def __init__(self):
        self.__cbc = gtk.Clipboard(selection="CLIPBOARD")
    def clr(self):
        self.__cbc.clear()
    def get(self):
        return self.__cbc.wait_for_text()
    def set(self,v):
        assert isinstance(v,basestring)
        self.clr()
        self.__cbc.set_text(v)
        self.__cbc.store()


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def PopApp(l,name):
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    assert len(l)>0

    class PopMenu(gtk.Menu):
        def __init__(self,l):
            gtk.Menu.__init__(self)

            for fn in l:
                if fn.__class__.__name__=="ExoFct":
                    menuItem = gtk.ImageMenuItem(beautifuler(fn.name))
                    menuItem.connect('activate', self.selectAction, fn)
                elif fn is None or str(fn).strip("- ") in ("","-"):
                    menuItem=gtk.SeparatorMenuItem()
                elif type(fn)== tuple:  #submenu
                    assert len(fn)==2
                    assert isinstance(fn[0],basestring)
                    assert type(fn[1]) in [tuple,list]
                    label,menus = fn
                    sm = PopMenu(menus)

                    menuItem=gtk.ImageMenuItem(label)
                    menuItem.set_submenu(sm)
                else:
                    menuItem = gtk.ImageMenuItem(str(fn))
                    menuItem.connect('activate', self.selectElement, fn)
                self.append(menuItem)
            self.show_all()

        def selectAction(self,w,f):
            g=GrunApp([f])
            PopMenu.ret =g.run(name)
            gtk.main_quit()

        def selectElement(self,w,f):
            PopMenu.ret = f
            gtk.main_quit()

        def show(self):
            PopMenu.ret=None
            p.popup(None, None, None, 1, 0)
            gtk.main()
            return PopMenu.ret

    p=PopMenu(l)
    p.connect("deactivate",gtk.main_quit)

    #~ menu.append(gtk.SeparatorMenuItem())
    #~ menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
    #~ menuItem.connect('activate', gtk.main_quit)
    #~ menu.append(menuItem)

    return p.show()

if __name__=="__main__":
    import os,sys
    p=sys.platform[:3]=="win" and "c:/python25/python.exe" or "python"
    os.system("%s ../../test.py"%p)


