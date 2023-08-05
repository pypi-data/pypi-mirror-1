import re, sys
import wx
import cache

CACHE_DIR = "cache"

sys.path.append(CACHE_DIR)
cache = cache.Cache(CACHE_DIR, "cache.db")

HELP = '''\
press KEY_DOWN or KEY_UP to navigate in commands history

help      this help
help CMD  specific command help
run       run .py on web or local
clear     the console
'''

HELP_RUN = '''\
run URL | MODULE

Examples:
run http://localhost:8000/test.py
run a7e2cc2218ad211dcb9a2444553540000
'''

#Redirect stdout and stderr on GUI
class Log:
	BUFFER = 32000 #wxTextCtrl  size limit
	def __init__(self, textCtrl):
		self.textCtrl = textCtrl
		sys.stdout = sys.stderr = self

	def write(self, text):
		#if over limit, clear the log
		if len(self.textCtrl.GetValue() + text) > self.BUFFER:
			self.textCtrl.Clear()
		#add new stdout or stderr
		self.textCtrl.AppendText(text)

#frame for "PyWebRun - Python Web Runner"
class MyFrame(wx.Frame):
	def __init__(self, parent, id, title, app):
		wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition,
			style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)

		self.app = app #main application
		fnt = wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL)
		
		#commands field
		self.comboBox = wx.ComboBox(self, -1, "", choices=[""], style=wx.TE_PROCESS_ENTER)
		self.comboBox.SetFont(fnt)
		self.comboBox.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
		self.comboBox.SetBackgroundColour("#EEEEEE")

		#redirected stdout and stderr
		app.textCtrlLog = wx.TextCtrl(self, -1, 'Type "help" and press ENTER\n', style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
		app.textCtrlLog.SetFont(fnt)
		app.textCtrlLog.SetBackgroundColour("#EEEEEE")

		#commands field layout
		bxTop = wx.BoxSizer(wx.HORIZONTAL)
		bxTop.Add(self.comboBox, 1, wx.ALIGN_BOTTOM)
		
		#main layout
		bxMain = wx.BoxSizer(wx.VERTICAL)
		bxMain.Add(bxTop, 1, wx.EXPAND|wx.ALL, 20)
		bxMain.Add(app.textCtrlLog, 2, wx.EXPAND)
		
		#frame
		self.SetSizer(bxMain)
		self.SetBackgroundColour(wx.WHITE)
		self.SetSize((600, 400))
		self.SetIcon(wx.Icon("gui.gif", wx.BITMAP_TYPE_GIF))
		self.Centre()
		
	#when press ENTER pn commands field
	def OnTextEnter(self, event):
		cmd = self.comboBox.GetValue()
		cmd = cmd.strip()
		if cmd == "":
			return
		
		print "cmd> " + cmd 
		#if new command append on comboBox (for the history)
		if cmd != self.comboBox.GetString(1):
			self.comboBox.Insert(cmd, 1)
		#select the first always empty
		self.comboBox.SetSelection(0)
		
		#command parser
		cmdS = re.split("\s", cmd, 1)
		if "help" == cmdS[0]:
			if len(cmdS) == 1:
				print HELP
			elif "run" == cmdS[1]:
				print HELP_RUN
			else:
				print "No help for: " + cmdS[1]
		elif "run" == cmdS[0]:
			if len(cmdS) == 1:
				print "No URL or module"
			#if run URL over HTTP
			elif cmdS[1].startswith("http://"):
				mod = cache.getModule(cmdS[1])
				exec "reload(mod)"
				exec "mod.main(parent=self, cache=cache)"
			#if run module
			else:
				exec "import %s as mod" % cmdS[1]
				exec "reload(mod)"
				exec "mod.main(parent=self, cache=cache)"
		elif "clear" == cmdS[0]:				
				self.app.textCtrlLog.Clear()
		else:
			print "No command: " + cmdS[0]
		
class MyApp(wx.App):

	def OnInit(self):
		self.textCtrlLog = None
	
		frame = MyFrame(None, -1, "PyWebRun - Python Web Runner", self)
		frame.Show(True)
		self.SetTopWindow(frame)

		return True

app = MyApp(0)
Log(app.textCtrlLog)
app.MainLoop()