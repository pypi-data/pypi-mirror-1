

def containsBlackListedItem(s, bl):
   ""
   for bli in bl:
      if bli in s:
         return True
   return False

for l in open("test.rtf"):

   # get the part that contains the HTML tag
   htmlline = l[l.find("{"):l.find("}")+1].strip("\n\t\l\f\r ")
   if htmlline:
      # get actual tag
      tagline = htmlline[htmlline.find("<"):htmlline.find(">")+1].strip("\n\t\l\f\r ")
      if tagline:
         print tagline
      # get encoded HTML chars
      else:
         char = htmlline[htmlline.find("&"):htmlline.find(";")+1].strip("\n\t\l\f\r ")
         if char:
            print char

   contentline = l[l.find('}')+1:]
   words = []
   blacklist = ("\\htmlrtf","\\par","\\f","\\line","\\q","}\\","\highlight","\\cf")
   for word in contentline.split():
      if not containsBlackListedItem(word, blacklist):
            words.append(word.strip("\n\t\l\f\r "))
   print " ".join(words)