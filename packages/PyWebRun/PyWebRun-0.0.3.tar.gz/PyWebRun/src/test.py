import wx

class MyFrame(wx.Frame):
	def __init__(self, parent, id, title, icon):
		wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition,
			style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)
		
		self.SetBackgroundColour(wx.WHITE)
		self.SetSize((200, 100))
		self.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_GIF))
		self.Centre()

def main(**params):
	print "HELLO!"
	
	# **params from gui.py:
	# "cache" object
	# "parent" frame
	icon = params["cache"].getFile("http://localhost:8000/gui.gif")
	
	frame = MyFrame(params["parent"], -1, "HELLO! Test", icon)
	frame.Show(True)
