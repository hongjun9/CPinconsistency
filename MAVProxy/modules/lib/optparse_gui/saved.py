'''
A drop-in replacement for optparse ( "import optparse_gui as optparse" )
Provides an identical interface to optparse(.OptionParser),
But displays an automatically generated wx dialog in order to enter the
options/args, instead of parsing command line arguments
'''

import os
import sys
import re
import optparse

import wx

__version__ = 0.1
__revision__ = '$Id$'

class TabbedDialog(wx.Dialog):
    def __init__(self, parent, tab_names, title='Title', size=wx.DefaultSize):
        wx.Dialog.__init__(self, parent, -1, title,
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.tab_names = tab_names
        self.notebook = wx.Notebook(self, -1, size=size)
        self.panels = {}
        self.sizers = {}
        for t in tab_names:
            self.panels[t] = wx.Panel(self.notebook)
            self.notebook.AddPage(self.panels[t], t)
            self.sizers[t] = wx.BoxSizer(wx.VERTICAL)
            self.panels[t].SetSizer(self.sizers[t])
        self.dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        self.dialog_sizer.Add(self.notebook, 1, wx.EXPAND|wx.ALL, 5)
        self.Centre()

    def panel(self, tab_name):
        '''return the panel for a named tab'''
        return self.panels[tab_name]

    def sizer(self, tab_name):
        '''return the sizer for a named tab'''
        return self.sizers[tab_name]

    def ReFit(self):
        '''refit after elements are added'''
        self.SetSizerAndFit(self.dialog_sizer)

class OptparseDialog( TabbedDialog ):
    '''The dialog presented to the user with dynamically generated controls,
    to fill in the required options.
    Based on the wx.Dialog sample from wx Docs & Demos'''
    def __init__(
            self,
            option_parser, #The OptionParser object
            parent = None,
            ID = 0,
            title = 'Optparse Dialog',
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.DEFAULT_DIALOG_STYLE,
            name = 'OptparseDialog',
        ):
        TabbedDialog.__init__(self, parent, option_parser.tab_names, title='Tab Test')
        provider = wx.SimpleHelpProvider()
        wx.HelpProvider_Set(provider)

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)

        sizer = self.sizer(option_parser.tab_names[0])
        tab = self.panel(option_parser.tab_names[0])

        panel1 = tab
        panel1_sizer = sizer
        text = wx.TextCtrl(panel1, -1, "Hi!", size=(400,90), style=wx.TE_MULTILINE)
        button1 = wx.Button(panel1, -1, "I only resize horizontally...")
        panel1_sizer.Add(text, 1, wx.EXPAND|wx.ALL, 10)
        panel1_sizer.Add(button1, 0, wx.EXPAND|wx.ALL, 10)


        self.option_controls = {}

        top_label_text = '%s %s' % ( option_parser.get_prog_name(),
                                     option_parser.get_version() )
        label = wx.StaticText(tab, -1, top_label_text)
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.browse_option_map = {}

        # Add controls for all the options
        for option in option_parser.option_list:
            if option.dest is None:
                continue

            if option.help is None:
                option.help = u''

            print('tab_name=%s' % option.tab_name)

            sizer = self.sizer(option.tab_name)
            tab = self.panel(option.tab_name)
            
            box = wx.BoxSizer(wx.HORIZONTAL)
            if 'store' == option.action:
                label = wx.StaticText(tab, -1, option.dest )
                label.SetHelpText( option.help )
                box.Add( label, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )

                if 'choice' == option.type:
                    if optparse.NO_DEFAULT == option.default:
                        option.default = option.choices[0]
                    ctrl = wx.ComboBox(
                        tab, -1, choices = option.choices,
                        value = option.default,
                        style = wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT
                    )
                else:
                    if 'MULTILINE' in option.help:
                        ctrl = wx.TextCtrl( tab, -1, "", size=(300,100), style = wx.TE_MULTILINE|wx.TE_PROCESS_ENTER )
                    else:
                        ctrl = wx.TextCtrl( tab, -1, "", size=(300,-1) )

                    if ( option.default != optparse.NO_DEFAULT ) and \
                       ( option.default is not None ):
                        ctrl.Value = unicode( option.default )

                box.Add( ctrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5 )

                if option.type in ['file', 'directory']:
                    browse = wx.Button(tab, label='...')
                    browse.SetHelpText( 'Click to open %s browser' % (option.type) )
                    self.browse_option_map[browse.GetId()] = option, ctrl
                    wx.EVT_BUTTON(tab, browse.GetId(), self.OnSelectPath)
                    box.Add( browse, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )

            elif option.action in ( 'store_true', 'store_false' ):
                ctrl = wx.CheckBox( tab, -1, option.dest, size = ( 300, -1 ) )
                box.Add( ctrl, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )
            else:
                raise NotImplementedError('Unknown option action: %s' % repr( option.action ) )

            ctrl.SetHelpText( option.help )
            sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

            self.option_controls[ option ] = ctrl

        # Add a text control for entering args
        box = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText(tab, -1, 'args' )
        label.SetHelpText( 'This is the place to enter the args' )

        self.args_ctrl = wx.TextCtrl( tab, -1, '', size = ( -1, 100 ),
                            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER )
        self.args_ctrl.SetHelpText(
'''Args can either be separated by a space or a newline
Args the contain spaces must be entered like so: "arg with sapce"
'''
        )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        box.Add( self.args_ctrl, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )

        sizer.Add( box , 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        line = wx.StaticLine(tab, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(tab)
            btnsizer.AddButton(btn)

        btn = wx.Button(tab, wx.ID_OK)
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(tab, wx.ID_CANCEL)
        btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        sizer.Fit(tab)
        self.ReFit()

    def OnSelectPath(self, event):
        option, ctrl = self.browse_option_map[event.GetId()]
        path = os.path.abspath(ctrl.Value)
        if option.type == 'file':
            dlg = wx.FileDialog(self,
                                message = 'Select file for %s' % (option.dest),
                                defaultDir = os.path.dirname(path),
                                defaultFile = path)
        elif option.type == 'directory':
            if os.path.isfile (path):
                path = os.path.dirname (path)
            dlg = wx.DirDialog(self,
                               message = 'Select directory for %s' % (option.dest),
                               defaultPath = path)
        else:
            raise NotImplementedError('option.type')
        dlg_result = dlg.ShowModal()
        if wx.ID_OK != dlg_result:
            return
        ctrl.Value = dlg.GetPath()
##        import open_py_shell;open_py_shell.open_py_shell( locals() )

    def _getOptions( self ):
        option_values = {}
        for option, ctrl in self.option_controls.iteritems():
            option_values[option] = ctrl.Value

        return option_values

    def _getArgs( self ):
        args_buff = self.args_ctrl.Value
        args = re.findall( r'(?:((?:(?:\w|\d)+)|".*?"))\s*', args_buff )
        return args

    def getOptionsAndArgs( self ):
        '''Returns the tuple ( options, args )
        options -  a dictionary of option names and values
        args - a sequence of args'''

        option_values = self._getOptions()
        args = self._getArgs()
        return option_values, args

class UserCancelledError( Exception ):
    pass

class Option (optparse.Option):
    SUPER = optparse.Option
    TYPES = SUPER.TYPES + ('file', 'directory')

class OptionParser( optparse.OptionParser ):
    SUPER = optparse.OptionParser

    def __init__( self, *args, **kwargs ):
        if 'option_class' not in kwargs:
            kwargs['option_class'] = Option
        self.current_tab = None
        self.SUPER.__init__( self, *args, **kwargs )
        self.tab_names = []

    def parse_args( self, args = None, values = None ):
        '''
        multiprocessing wrapper around _parse_args
        '''
        from multiprocessing import Process, Queue
        q = Queue()
        p = Process(target=self._parse_args, args=(q, args, values))
        p.start()
        ret = q.get()
        p.join()
        return ret

    def add_tab(self, tab_name):
        '''add a tab for the following options'''
        self.current_tab = tab_name
        self.tab_names.append(tab_name)

    def add_option(self, *args, **kwargs):
        self.SUPER.add_option(self, *args, **kwargs)
        self.option_list[-1].tab_name = self.current_tab

    def _parse_args( self, q, args, values):
        '''
        This is the heart of it all - overrides optparse.OptionParser.parse_args
        @param arg is irrelevant and thus ignored,
               it is here only for interface compatibility
        '''
        if wx.GetApp() is None:
            self.app = wx.App( False )

        # preprocess command line arguments and set to defaults
        option_values, args = self.SUPER.parse_args(self, args, values)
        for option in self.option_list:
            if option.dest and hasattr(option_values, option.dest):
                default = getattr(option_values, option.dest)
                if default is not None:
                    option.default = default

        dlg = OptparseDialog( option_parser = self, title=self.get_description() )

        if args:
            dlg.args_ctrl.Value = ' '.join(args)

        dlg_result = dlg.ShowModal()
        if wx.ID_OK != dlg_result:
            raise UserCancelledError( 'User has canceled' )

        if values is None:
            values = self.get_default_values()

        option_values, args = dlg.getOptionsAndArgs()

        for option, value in option_values.iteritems():
            if ( 'store_true' == option.action ) and ( value is False ):
                setattr( values, option.dest, False )
                continue
            if ( 'store_false' == option.action ) and ( value is True ):
                setattr( values, option.dest, False )
                continue

            if option.takes_value() is False:
                value = None

            option.process( option, value, values, self )

        q.put((values, args))

    def error( self, msg ):
        wx.MessageDialog( None, msg, 'Error!', wx.ICON_ERROR ).ShowModal()
        return self.SUPER.error( self, msg )


################################################################################

def sample_parse_args():
    usage = "usage: %prog [options] args"
    if 1 == len( sys.argv ):
        option_parser_class = OptionParser
    else:
        option_parser_class = optparse.OptionParser

    parser = option_parser_class( usage = usage, version='0.1' )
    parser.add_option("-f", "--file", dest="filename", default = r'c:\1.txt',
                      help="read data from FILENAME")
    parser.add_option("-t", "--text", dest="text", default = r'c:\1.txt',
                      help="MULTILINE text field")
    parser.add_option("-a", "--action", dest="action",
                      choices = ['delete', 'copy', 'move'],
                      help="Which action do you wish to take?!")
    parser.add_option("-n", "--number", dest="number", default = 23,
                      type = 'int',
                      help="Just a number")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose",
                      help = 'To be or not to be? ( verbose )' )

    (options, args) = parser.parse_args()
    return options, args

def sample_parse_args_issue1():
    usage = "usage: %prog [options] args"
    option_parser_class = OptionParser

    parser = option_parser_class( usage = usage, version='0.1' , description = 'OptParse Demo')
    parser.add_tab('Tab One')
    parser.add_option("-f", "--file", dest="filename", default = r'c:\1.txt',
                      type = 'file',
                      help="read data from FILENAME")
    parser.add_option("-t", "--text", dest="text", default = r'c:\1.txt',
                      help="MULTILINE text field")

    parser.add_tab('Tab Two')
    parser.add_option("-a", "--action", dest="action",
                      choices = ['delete', 'copy', 'move'],
                      help="Which action do you wish to take?!")
    parser.add_option("-n", "--number", dest="number", default = 23,
                      type = 'int',
                      help="Just a number")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose",
                      help = 'To be or not to be? ( verbose )' )

    (options, args) = parser.parse_args()
    return options, args

def main():
    options, args = sample_parse_args_issue1()
    print 'args: %s' % repr( args )
    print 'options: %s' % repr( options )

if '__main__' == __name__:
    main()
