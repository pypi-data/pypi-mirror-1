##	Fonty Python Copyright (C) 2006, 2007, 2008, 2009 Donn.C.Ingle
import wx

def _(s):
	return s

class XXDialogSettings(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, _("Settings"), pos = wx.DefaultPosition)#, size =(450,-1))
		
		verticalSizer = wx.BoxSizer(wx.VERTICAL)

		self.nb = wx.Notebook(self, -1, style=0)
		self.PANE1= wx.Panel(self.nb, -1)
		self.PANE2 = wx.Panel(self.nb, -1)


		## The layout of PANE1 begins:
		font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)
		self.labelHeading = wx.StaticText(self, -1, _("Settings"))
		self.labelHeading.SetFont(font)

		self.label_1 = wx.StaticText(self.PANE1, -1, _("Sample text:"))
		self.inputSampleString = wx.TextCtrl(self.PANE1, -1, "abc", size = (200, -1)) 
		self.inputSampleString.SetFocus()
		
		self.label_2 = wx.StaticText(self.PANE1, -1, _("Point size:"))
		self.inputPointSize = wx.SpinCtrl(self.PANE1, -1, "")
		self.inputPointSize.SetRange(1, 500)
		self.inputPointSize.SetValue( 90 )#fpsys.config.points)
		
		self.label_3 = wx.StaticText(self.PANE1, -1, _("Page length:"))
		self.inputPageLen = wx.SpinCtrl(self.PANE1, -1, "")
		self.inputPageLen.SetRange(1, 5000) # It's your funeral!
		self.inputPageLen.SetValue( 10 ) #fpsys.config.numinpage) 
		self.inputPageLen.SetToolTip( wx.ToolTip( _("Beware large numbers!") ) )

		gridSizer = wx.FlexGridSizer( rows=3, cols=2, hgap=5, vgap=8 )
		gridSizer.Add(self.label_1, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		gridSizer.Add(self.inputSampleString, 1, wx.EXPAND )
		gridSizer.Add(self.label_2, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		gridSizer.Add(self.inputPointSize, 0 )
		gridSizer.Add(self.label_3, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		gridSizer.Add(self.inputPageLen, 0 )

		self.PANE1.SetSizer( gridSizer )
		#gridSizer.Fit()

		## Sept 2009 - Checkbox to ignore/use the font top left adjustment code
		self.chkAdjust = wx.CheckBox(self.PANE2, -1, _("Disable font top-left correction."))
		self.chkAdjust.SetValue( True )#fpsys.config.ignore_adjustments) 
		self.chkAdjust.SetToolTip( wx.ToolTip( _("Disabling this speeds font drawing up a fraction, but degrades top-left positioning.") ) )
		pane2sizer = wx.BoxSizer( wx.VERTICAL )#wx.FlexGridSizer( rows=2, cols=2, hgap=5, vgap=8 )
		pane2sizer.Add(self.chkAdjust, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )

		self.PANE2.SetSizer( pane2sizer )

		#box = wx.BoxSizer(wx.HORIZONTAL)
		#box.Add(verticalSizer, 1, flag = wx.ALL, border = 10)
		
		
		self.nb.AddPage( self.PANE1, _("Quick settings") )
		self.nb.AddPage( self.PANE2, _("Voodoo") )

		verticalSizer.Add( self.labelHeading, 0, wx.ALIGN_LEFT )
		verticalSizer.Add( (0,5), 0 )

		verticalSizer.Add( self.nb, 1, wx.EXPAND )
		verticalSizer.Add((0,10),0) #space between bottom of grid and buttons

		btnsizer = wx.StdDialogButtonSizer()
		
		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		btnsizer.Realize()
		
		verticalSizer.Add( btnsizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, border = 5)

		buffer=wx.BoxSizer( wx.HORIZONTAL )
		buffer.Add( verticalSizer, 1, border=10 )

		self.SetSizer( buffer )#box)		
		self.SetSizer( verticalSizer )#box)
		
		#box.Fit(self) # This triggers the sizers to do their thing.
		#verticalSizer.Fit(self) # This triggers the sizers to do their thing.
		#verticalSizer.SetSizeHints(self)
		self.Layout()






class DialogSettings(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, _("Settings"), pos = wx.DefaultPosition)#, size =(450,-1))
		
		verticalSizer = wx.BoxSizer(wx.VERTICAL)
		
		font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)
		self.labelHeading = wx.StaticText(self, -1, _("Settings"))
		self.labelHeading.SetFont(font)

		verticalSizer.Add( self.labelHeading, 0, wx.ALIGN_LEFT )
		verticalSizer.Add( (0,5), 0 )

		btnsizer = wx.StdDialogButtonSizer()
		
		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		btnsizer.Realize()
		
		verticalSizer.Add( btnsizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL)
		
		buffer=wx.BoxSizer( wx.HORIZONTAL )
		buffer.Add( verticalSizer, 0, wx.EXPAND | wx.ALL, border=60 )

		self.SetSizer( buffer )#box)		
		#buffer.SetSizeHints(self)
		buffer.Fit(self) # This triggers the sizers to do their thing.
		#self.Layout()


#######################

class DialogSettings(wx.Dialog):
	def __init__(self, parent):
		#-1 , "Settings", size = wx.DefaultSize, , 
		#	 style = wx.DEFAULT_DIALOG_STYLE):
		wx.Dialog.__init__(self, parent, -1, _("Settings"), pos = wx.DefaultPosition)#, size =(450,-1))
		
		verticalSizer = wx.BoxSizer(wx.VERTICAL)

		self.nb = wx.Notebook(self, -1, style=0)
		self.PANE1= wx.Panel(self.nb, -1)
		self.PANE2 = wx.Panel(self.nb, -1)


		## The layout of PANE1 begins:
		font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)
		self.labelHeading = wx.StaticText(self, -1, _("Settings"))
		self.labelHeading.SetFont(font)

		self.label_1 = wx.StaticText(self.PANE1, -1, _("Sample text:"))
		self.inputSampleString = wx.TextCtrl(self.PANE1, -1, fpsys.config.text, size = (200, -1)) 
		self.inputSampleString.SetFocus()
		
		self.label_2 = wx.StaticText(self.PANE1, -1, _("Point size:"))
		self.inputPointSize = wx.SpinCtrl(self.PANE1, -1, "")
		self.inputPointSize.SetRange(1, 500)
		self.inputPointSize.SetValue(fpsys.config.points)
		
		self.label_3 = wx.StaticText(self.PANE1, -1, _("Page length:"))
		self.inputPageLen = wx.SpinCtrl(self.PANE1, -1, "")
		self.inputPageLen.SetRange(1, 5000) # It's your funeral!
		self.inputPageLen.SetValue(fpsys.config.numinpage) 
		self.inputPageLen.SetToolTip( wx.ToolTip( _("Beware large numbers!") ) )

		gridSizer = wx.FlexGridSizer( rows=3, cols=2, hgap=5, vgap=8 )
		gridSizer.Add(self.label_1, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		gridSizer.Add(self.inputSampleString, 1, wx.EXPAND )
		gridSizer.Add(self.label_2, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		gridSizer.Add(self.inputPointSize, 0 )
		gridSizer.Add(self.label_3, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		gridSizer.Add(self.inputPageLen, 0 )

		pane1_buffer = wx.BoxSizer( wx.HORIZONTAL )
		pane1_buffer.Add( gridSizer, 1, wx.EXPAND | wx.ALL, border=10 )
		self.PANE1.SetSizer( pane1_buffer )

		## Sept 2009 - Checkbox to ignore/use the font top left adjustment code
		self.chkAdjust = wx.CheckBox(self.PANE2, -1, _("Disable font top-left correction."))
		self.chkAdjust.SetValue(fpsys.config.ignore_adjustments) 
		self.chkAdjust.SetToolTip( wx.ToolTip( _("Disabling this speeds font drawing up a fraction, but degrades top-left positioning.") ) )
		pane2sizer = wx.BoxSizer( wx.VERTICAL )#wx.FlexGridSizer( rows=2, cols=2, hgap=5, vgap=8 )
		pane2sizer.Add(self.chkAdjust, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )

		pane2_buffer = wx.BoxSizer( wx.HORIZONTAL )
		pane2_buffer.Add( pane2sizer, 1, wx.EXPAND | wx.ALL, border=10 )
		self.PANE2.SetSizer( pane2_buffer )
		
		#self.PANE2.SetSizer( pane2sizer )

		#box = wx.BoxSizer(wx.HORIZONTAL)
		#box.Add(verticalSizer, 1, flag = wx.ALL, border = 10)
		
		
		self.nb.AddPage( self.PANE1, _("Quick settings") )
		self.nb.AddPage( self.PANE2, _("Voodoo") )

		verticalSizer.Add( self.labelHeading, 0, wx.ALIGN_LEFT )
		verticalSizer.Add( (0,5), 0 )

		verticalSizer.Add( self.nb, 1, wx.EXPAND | wx.ALL )
		#verticalSizer.Add((0,10),0) #space between bottom of grid and buttons

		btnsizer = wx.StdDialogButtonSizer()
		
		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		btnsizer.Realize()
		
		verticalSizer.Add( btnsizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, border = 5)
	
		buffer=wx.BoxSizer( wx.HORIZONTAL )
		## To get border to work use wx.EXPAND | wx.ALL
		buffer.Add( verticalSizer, 1,wx.EXPAND | wx.ALL,  border=10 )

		self.SetSizer( buffer )#box)
		#box.Fit(self) # This triggers the sizers to do their thing.
		buffer.Fit(self) # This triggers the sizers to do their thing.
		#verticalSizer.SetSizeHints(self)
		self.Layout()






class MyApp(wx.App):
    def OnInit(self):
        dia = DialogSettings(None)
        dia.ShowModal()
        dia.Destroy()
        return True

app = MyApp(0)
app.MainLoop()

