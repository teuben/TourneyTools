#! /usr/bin/python
#
import cgi, sys, os, string, re
import ptt

version = "DCOPEN 5-dec-2007"

debug   = True
debug1  = False
late    = False
#late    = True
fee0    = 5           # initial reg fee
fee1    = 20          # fee per event
fee2    = 5           # late fee (after a certain date you can increase this)
maxev   = 3
emails  = "teuben@astro.umd.edu,teuben@verizon.net"
tournament = "DCOPEN 2008"

def get_form(key,default):
    global form
    if form.has_key(key):
        return form[key].value
    else:
        return default

def get_key(key,default=''):
    global form
    if form.has_key(key):
        return form[key].value.strip()
    else:
        return default

def get_keyi(key,default=0):
    return int(get_key(key,'0'))

def add_singles(idx):
    global pevents
    ekey = 'event%s' % idx
    pevents.append((get_key(ekey),'0'))

def add_doubles(idx):
    global pevents
    ekey = 'event%s' % idx
    pkey = 'partner%s' % idx
    pevents.append((get_key(ekey),get_key(pkey)))

def add_event(idx):
    global pevents
    ekey = 'event%s' % idx
    ckey = 'cat%s' % idx
    pkey = 'partner%s' % idx
    pevents.append((get_key(ekey),get_key(ckey),get_key(pkey)))

def find_partner(name):
    p1 = "joe"
    p2 = "ann"
#    return [p1,p2]
    return [p1]

def warning(text):
    print '<TABLE bgcolor="ffff77" border=><br>'
    print '<tr><td><br>'
    print "%s<br>" % text
    print '</td></tr><br>'
    
def error(text):
    print '<TABLE bgcolor="ff0000" border=><br>'
    print '<tr><td><br>'
    print "%s<br>" % text
    print '</td></tr><br>'

    
sys.stderr = sys.stdout
nbad       = 0

pid = os.getpid()
# pid = 99999          # for debug

form = cgi.FieldStorage()
print "Content-type: text/html\n"
print "This form is the new 2006 PTT written in python - Version %s<br>" % version
print "========================================================================<br>"

if late:
    error("The official deadline has passed, the entry will be submitted, but there is no guarentee for entry. Await an email")

#   initialize a person's record
data = {}

data['fname'] = get_form('fname','')
data['lname'] = get_form('lname','')

#print "First: %s  Last: %s" % (data['fname'],data['lname'])

# debug: what keys do we have
if debug1:
    print "Keys: ",form.keys()
    print "<br>"

fname = get_key('fname')
lname = get_key('lname')
sex   = get_key('sex')

address = get_key('address')
city    = get_key('city')
state   = get_key('state','ZZ').upper()
zip     = get_key('zip','00000')

dphone  = get_key('dphone')
ephone  = get_key('ephone')
cphone  = get_key('cphone')

tshirt  = get_key('tshirt')
# for U only
college = get_key('college')

usabnum  = get_key('usabnum')
usab     = get_key('usab','0')
# usabfee  = get_keyi('usabfee',0)
renew    = get_key('renew')
#family   = get_key('familyname')
club     = get_key('club')
bday    = get_key('birthday')
citizen = get_key('citizen')

email   = get_key('email')
# other   = get_key('other')
paid1 = get_key('paid')
if paid1.find('$') >= 0:
  # note, this still doesn't catch those that use "60$"
  paid = int(paid1[paid1.find('$')+1])
else:
  paid  = int(paid1)

print "Name: %s, %s [%s]<br>" % (lname,fname,sex)
print "Address: %s, %s, %s %s<br>" % (address,city,state,zip)
print "College: %s " % college
print "Club: %s " % club
print "Born: %s<br>" % bday
print "Phones: %s / %s / %s<br>" % (dphone,ephone,cphone)
print "Email: %s <br>" % (email)

if len(email)==0: 
    print "***You must provide an email contact ***<br>"
    nbad = nbad + 1

if len(email) > 0 and email.find('@') < 0:
    print "***Email seems badly formatted***<br>"
    nbad = nbad + 1

usabef=usab.split(',')
if len(usabef) != 2:
    usabfee = 0
else:    
    usabfee = int(usabef[1])

    

print "USAB: %s %s (renew: %s)[%s] fee=%d<br>" % (usabnum,usab,renew,club,usabfee)

if usab == '0':
    print "*** No USAB membership information<br>"
    nbad = nbad + 1

if usab == 'current,0':
    if usabnum == '0' or len(usabnum)==0:
        print "*** Bad USAB number: %s ; use -1 if you don't remember yours<br>" % usabnum
        nbad = nbad + 1
else:
    if len(renew)==0:
        print "*** Please specify if this is a renewal or not ***<br>"
        nbad = nbad + 1

#print "USABEF=%s %s<br>" % (usabef[0],usabef[1])

if len(tshirt) == 0:
    print "*** No t-shirt size given ***<br>"
    nbad = nbad + 1
    

#    accumulate the events somebody plays
pevents=[]
for i in ['1','2','3']:
    add_event(i)

print "events: %s<br>" % pevents

#    loop over events, and count how many valid this player has
n1=0  # n1 counts non-U level
n2=0  # n2 counts U-level
n=0
print "<br>"
for e in pevents:
    if e[0] != '0':
        n = n + 1
        print "Event%d: %s-%s " % (n,e[0],e[1])
        if e[1] == 'U':
	    n2 = n2 + 1
            if len(college) == 0:
                print "<br>*** no college given, needed for U levels ***"
                nbad = nbad + 1
	else:
	    n1 = n1 + 1
        if len(e[1]) == 0:
            print "<br>*** no category supplied for %s" % e[0]
            nbad = nbad + 1
        if e[0][1] == 'd':
            print "(Partner: %s)"  % e[2]
            if len(e[2]) == 0:
                print "<br>*** no partner name supplied : use REQ to request or TBA to announce later ***"
                nbad = nbad + 1
            found = find_partner(e[2])
            if len(found) == 0:
                print "<br>*** No matching partner names found in USAB database***"
            elif len(found) > 1:
                print "<br>*** Found %d matching partner names in USAB database***" % len(found)
                print found
        if e[0][0] == 'm' and sex != 'm':
            print "<br>*** bad gender selection for a Female ***"
            nbad = nbad + 1
        if e[0][0] == 'w' and sex != 'f':
            print "<br>*** bad gender selection for a Male ***"
            nbad = nbad + 1
        print "<br>"

if n > maxev:
    print "*** too many events selected, %d is the max ***<br>" % maxev
    nbad = nbad + 1
elif n==0:
    print "*** no events selected ***<br>" 
    nbad = nbad + 1
    
print "<br>"    

if n==1:            
    print "%s %s signed up for 1 event. <br>" % (fname,lname)
else:
    print "%s %s signed up for %d events. <br>" % (fname,lname,n)
if not late: 
    fee2 = 0
if fee2 > 0:
    dues = fee0+n*fee1+usabfee+fee2
    print "Total Fees:  $%d + %d * $%d + $%d + $%d (late fee) = $%d<br>" % (fee0,n,fee1,usabfee,fee2,dues)
else:
    dues = fee0+n*fee1+usabfee
    print "Total Fees:  $%d + %d * $%d + $%d = $%d<br>" % (fee0,n,fee1,usabfee,dues)
if dues==0:
    print "*** There is no free registration ***<br>"
    nbad = nbad + 1
if dues != paid:
    warning("Warning: your dues are %d but you say you paid %d<br>" % (dues,paid))
    print "You can either go BACK to the previous page and fix this, or we will settle this at the DC Open<br>"

if n1>0 and n2>0:
    warning("Warning: you have registered in a U as well as non-U level. Please be adviced that U-level is really meant for non-A/B/C/D level players from universities and colleges. Please consider changing your entries to reflect your level of play")
    
    
comments = get_key('comments')
print 'Your comments: %s<br>' % comments


if nbad > 0:
    print '<TABLE bgcolor="ff0000" border=><br>'
    print '<tr><td><br>'
    print "ERROR: *** %d Fatal errors, you cannot register with this information***<br>" % nbad
    print "find the lines marked with *** to find the errors<br>"
    print "please go back a page and try again<br>"
    print '</td></tr><br>'
else:
    print '<TABLE bgcolor="00ff00" border=><br>'
    print '<tr><td><br>'
    print "Thank You. Your form has been submitted for approval.<br>"
    print '</td></tr><br>'
    
    tmpname = '/tmp/dcopen%d.txt' % pid
    fp=open(tmpname,'w')
    fp.write("BEGIN=DCOPEN\n")
    fp.write("version=%s\n" % version)
    fp.write("tournament=%s\n" % tournament)
    fp.write("fname=%s\n" % fname)
    fp.write("lname=%s\n" % lname)
    fp.write("sex=%s\n" % sex)
    fp.write("birthday=%s\n" % bday)
    fp.write("citizen=%s\n" % citizen)
    fp.write("address=%s\n" % address)
    fp.write("city=%s\n" % city)
    fp.write("state=%s\n" % state)
    fp.write("zip=%s\n" % zip)
    fp.write("cphone=%s\n" % cphone)
    fp.write("dphone=%s\n" % dphone)
    fp.write("ephone=%s\n" % ephone)
    fp.write("email=%s\n" % email)
    fp.write("college=%s\n" % college)	
    fp.write("tshirt=%s\n" % tshirt)	
    fp.write("usab=%s\n" % usabef[0])    
    fp.write("usabnum=%s\n" % usabnum)    
    fp.write("renew=%s\n" % renew)
    fp.write("club=%s\n" % club)
    fp.write("usabfee=%s\n" % usabfee)    
    fp.write("latefee=%d\n" % fee2)
    fp.write("allfee=\n")
    fp.write("dues=%d\n" % dues)
    fp.write("paid=%d\n" % paid)
    fp.write("consent=0\n")
    n=0
    for e in pevents:
        if e[0] != '0':
            n=n+1
            fp.write("event%d=%s-%s\n" % (n,e[0],e[1]))
            if e[0][1] == 'd':
                fp.write("partner%d=%s\n" % (n,e[2]))
    fp.write("usabcomment=\n")
    fp.write("comments=%s\n" % comments)                
    fp.write("END=DCOPEN\n");                
    fp.close()
    cmd = "mail -s \"DCOPEN2008 %s %s\" %s < %s"  %   (fname,lname,emails,tmpname)
    e=os.system(cmd)
    if e==0:
        print "<br> Form has been processed and sent via email. You should get a confirmation.<br>"
        print "You can always go back to the previous page and re-submit your entry<br>"
	print "<B>Remember to send in your check and consent form by snail-mail before Dec 31!!!</B><br>"
    else:
        print "Some error occured in sending the registration via email...<br>"

#    print "<br><hr> Just to clarify, we're still testing this form, we're not open for business yet<br>"
#    print "Any comments/improvements etc. forward to Peter Teuben<br>"

    print "Please send any concerns to: teuben@astro.umd.edu<br>"
    os.system('date')
    # warning("this is an example warning")
    warning("NOTE: this version of the program has not checked the correct spelling of your doubles partner.")
