from md5 import md5

def md5_hexdigest(self,s):
   """returns hexdigest of md5 sum"""

   return md5(str(s)).hexdigest()

