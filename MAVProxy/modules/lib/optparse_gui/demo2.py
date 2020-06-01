import wx, os

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
        self.controls = {}
        self.browse_option_map = {}
        self.Centre()

    def panel(self, tab_name):
        '''return the panel for a named tab'''
        return self.panels[tab_name]

    def sizer(self, tab_name):
        '''return the sizer for a named tab'''
        return self.sizers[tab_name]

    def refit(self):
        '''refit after elements are added'''
        self.SetSizerAndFit(self.dialog_sizer)

    def _add_input(self, tab_name, label, ctrl, default=None, ctrl2=None):
        tab = self.panel(tab_name)
        box = wx.BoxSizer(wx.HORIZONTAL)
        labelctrl = wx.StaticText(tab, -1, label )
        box.Add(labelctrl, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        box.Add( ctrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5 )
        if ctrl2 is not None:
            box.Add( ctrl2, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )
        self.sizer(tab_name).Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.controls[label] = ctrl
        if default is not None:
            ctrl.Value = default

    def add_text(self, tab_name, label, default=None, width=300, height=100, multiline=False):
        '''added a text input line'''
        tab = self.panel(tab_name)
        if multiline:
            ctrl = wx.TextCtrl(tab, -1, "", size=(width,height), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        else:
            ctrl = wx.TextCtrl(tab, -1, "", size=(width,-1) )
        self._add_input(tab_name, label, ctrl, default)

    def add_filechooser(self, tab_name, label, default=None, width=300, directory=False):
        '''added a file input line'''
        tab = self.panel(tab_name)
        ctrl = wx.TextCtrl(tab, -1, "", size=(width,-1) )
        browse = wx.Button(tab, label='...')        
        wx.EVT_BUTTON(tab, browse.GetId(), self._on_select_path)
        self.browse_option_map[browse.GetId()] = label
        self._add_input(tab_name, label, ctrl, ctrl2=browse, default=default)

    def add_choice(self, tab_name, label, choices, default=None):
        '''added a choice input line'''
        tab = self.panel(tab_name)
        if default is None:
            default = choices[0]
        ctrl = wx.ComboBox(tab, -1, choices=choices,
                           value = default,
                           style = wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT )
        self._add_input(tab_name, label, ctrl, default)

    def add_image(self, tab_name):
        '''added a choice input line'''
        from MAVProxy.modules.lib import mp_widgets
        tab = self.panel(tab_name)
        ctrl = mp_widgets.ImagePanel(self, wx.EmptyImage(100,100))
        self._add_input(tab_name, 'image', ctrl, None)
        
    def _on_select_path(self, event):
        label = self.browse_option_map[event.GetId()]
        ctrl = self.controls[label]
        path = os.path.abspath(ctrl.Value)
        dlg = wx.FileDialog(self,
                            message = 'Select file for %s' % label,
                            defaultDir = os.path.dirname(path),
                            defaultFile = path)
        dlg_result = dlg.ShowModal()
        if wx.ID_OK != dlg_result:
            return
        ctrl.Value = dlg.GetPath()

#----------------------------------------------------------------------
class MyTabbedDlg(TabbedDialog):
    def __init__(self, parent):
        title = "Resize the dialog and see how controls adapt!"
        TabbedDialog.__init__(self, parent, ['TabOne', 'TabTwo'], title='Tab Test')

        self.add_text('TabOne', 'Foo label', 'blah') 
        self.add_text('TabTwo', 'Foo label2', 'blah foo!') 
        self.add_text('TabTwo', 'Multiline label', 'longer input', multiline=True) 
        self.add_choice('TabOne', 'Colour', ['Red','Green','Blue'])
        self.add_filechooser('TabOne', 'Filename')
        self.add_image('TabOne')
        self.refit()

    def OnButton(self, evt):
        self.EndModal(0)


#----------------------------------------------------------------------
class MyApp(wx.App):
    def OnInit(self):
        dlg = MyTabbedDlg(None)
        dlg.ShowModal()
        dlg.Destroy()
        return True

myapp = MyApp(redirect=False)
myapp.MainLoop()

