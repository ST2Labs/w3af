'''
unhandled_bug_report.py

Copyright 2009 Andres Riancho

This file is part of w3af, w3af.Trac.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''

import gtk

from core.controllers.easy_contribution.sourceforge import SourceforgeXMLRPC
from core.controllers.easy_contribution.sourceforge import DEFAULT_USER_NAME, DEFAULT_PASSWD
from core.controllers.exception_handling.cleanup_bug_report import cleanup_bug_report
from core.ui.gtkUi.exception_handling.common_windows import (simple_base_window, report_bug_show_result,
                                                             dlg_ask_bug_info, dlg_ask_credentials)
from core.ui.gtkUi.constants import W3AF_ICON



class trac_bug_report(object):
    '''
    Class that models user interaction with Trac to report a bug.
    '''
    
    def __init__(self, tback='', fname=None, plugins=''):
        self.sf = None
        self.tback = tback
        self.fname = fname
        self.plugins = plugins
        self.autogen = False
    
    def report_bug(self):
        sf, summary, userdesc, email = self._info_and_login()
        rbsr = report_bug_show_result( self._report_bug_to_sf, [(sf, summary, userdesc, email),(sf, summary, userdesc, email),(sf, summary, userdesc, email),(sf, summary, userdesc, email),(sf, summary, userdesc, email), (sf, summary, userdesc, email),(sf, summary, userdesc, email),(sf, summary, userdesc, email),(sf, summary, userdesc, email),(sf, summary, userdesc, email),(sf, summary, userdesc, email),(sf, summary, userdesc, email),(sf, summary, userdesc, email)] )
        rbsr.run()
    
    def _info_and_login(self):
        # Do the login
        sf, email = self._login_sf()
        
        # Ask for a bug title and description
        dlg_bug_info = dlg_ask_bug_info()
        summary, userdesc = dlg_bug_info.run()
        
        return sf, summary, userdesc, email
        
    def _report_bug_to_sf(self, sf, summary, userdesc, email):
        '''
        Send bug to Trac.
        '''
        try:
            ticket_url, ticket_id = sf.report_bug(summary, userdesc, self.tback,
                                                  self.fname, self.plugins, self.autogen,
                                                  email)
        except:
            return None, None
        else:
            return ticket_url, ticket_id
    
    def _login_sf(self, retry=3):
        '''
        Perform user login.
        '''
        invalid_login = False
        email = None
        
        while retry:
            # Decrement retry counter
            retry -= 1
            # Ask for user and password, or anonymous
            dlg_cred = dlg_ask_credentials(invalid_login)
            method, params = dlg_cred.run()
            
            if method == dlg_ask_credentials.METHOD_SF:
                user, password = params
            
            elif method == dlg_ask_credentials.METHOD_EMAIL:
                # The user chose METHOD_ANON or METHOD_EMAIL with both these
                # methods the framework actually logs in using our default 
                # credentials
                user, password = (DEFAULT_USER_NAME, DEFAULT_PASSWD)
                email = params[0]

            else:
                # The user chose METHOD_ANON or METHOD_EMAIL with both these
                # methods the framework actually logs in using our default 
                # credentials
                user, password = (DEFAULT_USER_NAME, DEFAULT_PASSWD)
            
            sf = SourceforgeXMLRPC(user, password)
            login_result = sf.login()
            invalid_login = not login_result
            
            if login_result:
                break
            
        return (sf, email)
    

    

class bug_report_window(simple_base_window, trac_bug_report):
    '''
    The first window that the user sees when an exception is raised and
    it bubbles up until gtkUi's main.py or worse.
    
    Please note that in this case we're reporting ONE exception and then
    stopping the scan. Completely different from what you can see in
    handled.py . 
    '''
    
    MANUAL_BUG_REPORT = 'https://sourceforge.net/apps/trac/w3af/newticket'
    
    def __init__(self, title, tback, fname, plugins):
        # Before doing anything else, cleanup the report to remove any
        # user information that might be present.
        tback = cleanup_bug_report(tback)
        
        simple_base_window.__init__(self)
        trac_bug_report.__init__(self, tback, fname, plugins)
        
        # We got here because of an autogenerated bug, not because of the user
        # going to the Help menu and then clicking on "Report a bug"
        self.autogen = True
        
        # Set generic window settings
        self.set_modal(True)
        self.set_title(title)
        
        self.vbox = gtk.VBox()
        
        # the label for the title
        self.title_label = gtk.Label()
        self.title_label.set_line_wrap(True)
        label_text = _('\n<b>An unhandled exception was raised:</b>\n\n')
        self.title_label.set_markup(label_text)
        self.title_label.show()
        
        # A gtk.TextView for the exception
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.text_view = gtk.TextView()
        self.text_view.set_size_request(150, 250) 
        self.text_view.set_editable(False)
        self.text_view.set_wrap_mode(gtk.WRAP_CHAR)

        buffer = self.text_view.get_buffer()
        buffer.set_text(tback)
        
        sw.add(self.text_view)
        
        # the label for the rest of the message
        self.label = gtk.Label()
        self.label.set_line_wrap(True)
        label_text = _("<i>All this info is in a file called ") + fname + _(" for later review.</i>\n\n")
        label_text += _('If you wish, <b>you can contribute</b> to the w3af project and submit this')
        label_text += _(' bug to our bug tracking system from within this window.')
        label_text += _(' It\'s a simple <i>two step process</i>.\n\n')
        label_text += _('w3af will only send the exception traceback and the version information to')
        label_text += _(' Trac, no personal or confidential information is collected.\n\n')
        self.label.set_markup(label_text)
        self.label.show()
        
        self.vbox.pack_start(self.title_label, True, False)
        self.vbox.pack_start(sw, False, False)
        self.vbox.pack_start(self.label, True, False)
        
        # the buttons
        self.hbox = gtk.HBox()
        self.butt_send = gtk.Button(stock=gtk.STOCK_OK)
        self.butt_send.connect("clicked", self.report_bug)
        self.hbox.pack_start(self.butt_send, True, False)
        
        self.butt_cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.butt_cancel.connect("clicked", self._handle_cancel)
        self.hbox.pack_start(self.butt_cancel, True, False)
        self.vbox.pack_start(self.hbox, True, False)
        
        #self.resize(400,450)
        self.add(self.vbox)
        self.show_all()
        
        # This is a quick fix to get around the problem generated by "set_selectable"
        # that selects the text by default
        self.label.select_region(0, 0)
    
    def report_bug(self, widg):
        # Avoid "double clicking" in the OK button,
        self.butt_send.set_sensitive(False)
        
        # Report the bug
        trac_bug_report.report_bug(self)

    