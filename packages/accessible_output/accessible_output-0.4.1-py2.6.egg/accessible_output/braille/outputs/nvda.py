from ctypes import windll
from accessible_output import paths

from main import OutputError, BrailleOutput

class NVDA (BrailleOutput):
 """Brailler which supports The NVDA screen reader"""

 def __init__(self, *args, **kwargs):
  try:
   self.dll = windll.LoadLibrary(paths.root('lib\\nvdaControllerClient32.dll'))
  except:
   raise OutputError

 def braille(self, text, *args, **kwargs):
  self.dll.nvdaController_brailleMessage(unicode(text))

 def canBraille(self):
  try:
   return self.dll.nvdaController_testIfRunning() == 0 and super(NVDA, self).canSpeak()
  except:
   return False

