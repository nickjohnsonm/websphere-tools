import sys

# the following will add _ to the output for writing to disk

def shellquote(s):
   return s.replace("(","_").replace("|","_").replace("/","_").replace(")","_").replace("#","_")

# for each argument, run AdminConfig.  The item requires a * after it

for arg in sys.argv:
        star = (str("*"))
        name = (str(arg))
        my_list = [name , star]
        item = "".join(my_list) 
        source=AdminConfig.list('DataSource', item).split("\n")

# dump to disk the results

for i in source:
        filename = "/home/wasprod/scripts/dump/"
        file = open(filename + shellquote(str(i)) + ".txt" ,'w+')
        file.write(AdminConfig.showall(i))
        file.close
        continue

