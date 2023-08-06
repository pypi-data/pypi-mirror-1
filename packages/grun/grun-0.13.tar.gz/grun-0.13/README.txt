Turn yours methods in GUI forms !!!
===================================
A simple example, turn your methods into gui forms ::

    from grun import grun

    @grun
    def my_window( name, passwd, cookie=["1 day","1 week","1 month"] ):
        '''Hello, I'm the method's doc

        name:    Login
        passwd:  Password
        cookie:  How long ?
        '''
        if name == passwd:
            return True
        else:
            grun("Set login == password !")

    print my_window(cookie="1 day")

will display :

.. image:: http://www.manatlan.com/files/grun.png

Works on Linux/BSD, Windows and Mac using Tk framework (or pygtk when available)

See `more infos <http://www.manatlan.com/page/grun>`_

Version 0.1X:
  - fix: gtk number-widget wasn't initialized when value was None
  - tk iconapp simulate now a grunapp (not a popup'app anymore)

Version 0.12 (2009/10/03):

  - tk popup should work as expected on win32 (no more tk.mainloop) !!!!!!!
  - tk winform should focus on first entry now (seems not work on win ?!)
  - popup/popapp actions wich return something returns it after grun.popup

Version 0.11 (2009/10/01):

  - clipboard manager available grun.clipboard
  - better shortcut grun.popup()
  - better shortcut grun.form()
  - popup menu works with any types of value
  - popup menu support submenu too !
  - tk: text widget with usable scrollbars now
  - tk: fix in msgbox (always of type error)
  - tk: home-made-combobox, replaced by Tk.OptionMenu
  - tk: better simulation of tk popapp/popupmenu (no more 'close' entry)

Version 0.1 (2009/09/28): Initial Public Release
