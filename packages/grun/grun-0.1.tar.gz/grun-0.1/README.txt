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
