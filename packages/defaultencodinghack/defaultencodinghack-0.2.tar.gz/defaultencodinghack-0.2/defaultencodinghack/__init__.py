# Sigh.
import sys as oldsys
del oldsys.modules['sys']
import sys as newsys
newsys.setdefaultencoding('utf-8')
oldsys.modules['sys'] = oldsys
