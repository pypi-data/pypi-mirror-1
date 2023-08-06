from accessible_output.output import OutputError, AccessibleOutput
from ctypes import windll

class SystemAccess (AccessibleOutput):
 """Supports Brailling to System Access."""
 def __init__(self, *args, **kwargs):
  super(SystemAccess, self).__init__(*args, **kwargs)
  try:
   self.dll = windll.SAAPI32
  except:
   raise OutputError

 def braille(self, text):
  self.dll.SA_BrlShowTextW(unicode(text))

 def canBraille(self):
  try:
   return self.dll.SA_IsRunning() and super(SystemAccess, self).canSpeak()
  except:
   return False
