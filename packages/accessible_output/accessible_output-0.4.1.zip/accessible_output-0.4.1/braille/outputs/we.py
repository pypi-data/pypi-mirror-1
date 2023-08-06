from pywintypes import com_error
import win32com.client

from main import OutputError, BrailleOutput

class WindowEyes (BrailleOutput):
 """Braille output which supports Window Eyes"""

 def __init__(self, *args, **kwargs):
  super(WindowEyes, self).__init__(*args, **kwargs)
  try:
   self.object = win32com.client.Dispatch("gwspeak.speak")
  except com_error:
   raise OutputError

 def canBraille(self):
  try:
   return win32gui.FindWindow("GWMExternalControl", "External Control") != 0 and super(WindowEyes, self).canSpeak()
  except:
   return False

 def braille (self, text):
  self.object.Display(text)
