import csv

csvfile = open("tali.csv", "r")
reader = csv.reader( csvfile, delimiter=',', quotechar='"')
contacts = {}

for row in reader:
    name = ''
    if not row[1] == '': name =  row[1]
    if not row[3] == '': name =  row[3]
    if (not row[1] == '') and (not row[3] == ''): name = row[1] + " " +row[3]
   
 
    if name in contacts:
        if not row[13] == '': contacts[name].append(row[13])
    else:
        if not row[13] == '': contacts[name] = [ row[13] ]
    if name in contacts:
        if not row[14] == '': contacts[name].append(row[14])
        if not row[28] == '': contacts[name].append(row[28])

out = open('out.txt','w')

title = '"Title","First name","Middle name","Last name","Suffix","Job title","Company","Birthday","SIP address","Push-to-talk","Share view","User ID","Notes","General mobile","General phone","General e-mail","General fax","General video call","General web address","General VOIP address","General P.O.Box","General extension","General street","General postal/ZIP code","General city","General state/province","General country/region","Home mobile","Home phone","Home e-mail","Home fax","Home video call","Home web address","Home VOIP address","Home P.O.Box","Home extension","Home street","Home postal/ZIP code","Home city","Home state/province","Home country/region","Business mobile","Business phone","Business e-mail","Business fax","Business video call","Business web address","Business VOIP address","Business P.O.Box","Business extension","Business street","Business postal/ZIP code","Business city","Business state/province","Business country/region",""'
row_fmt = '"","%(name)s","","","","","","","","","","","%(phone1)s","%(phone2)s","","","","","","","","","","","","","","%(phone3)s","","","","","","","","","","","","","","","","","","","","","","","","","","","",""'
out.write(title +"\n")
for a in contacts:
    l = list (set(contacts[a]))
    row = { 'name': a, 'phone1':l[0] , 
            'phone2': '' if (len(l) < 2) else l[1] , 
            'phone3': '' if (len(l) < 3) else l[2]}
    out.write( row_fmt %  row + "\n")
print contacts["Voice Mail"]