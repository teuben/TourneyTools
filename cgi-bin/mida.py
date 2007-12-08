#! /usr/bin/python
#
#  process a MidAtlantic style registration form
#

import cgi, sys, os, string, re
import ptt

version = "MIDA 2-nov-2007"
debug   = True
debug1  = False
late    = False
fee0    = 0           # initial reg fee
fee1    = 25          # fee per event
fee2    = 5           # late fee (after a certain date you can increase this)
maxev   = 3
emails  = "teuben@astro.umd.edu,teuben@verizon.net"

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
# pid = 99999

form = cgi.FieldStorage()
print "Content-type: text/html\n"
print "This form is the new 2006 PTT written in python - Version %s<br>" % version
print "========================================================================<br>"

# debug: what keys do we have
if debug1:
    print "Keys: ",form.keys()
    print "<br>"

fname = get_key('fname')
lname = get_key('lname')
sex   = get_key('sex')

usabnum  = get_key('usabnum')
usab     = get_key('usab','0')
usabfee  = get_keyi('usabfee',0)
renew    = get_key('renew')
family   = get_key('familyname')

address = get_key('address')
city    = get_key('city')
state   = get_key('state','ZZ').upper()
zip     = get_key('zip','00000')

bday    = get_key('birthday')
citizen = get_key('citizen')
dphone  = get_key('dphone')
ephone  = get_key('ephone')
cphone  = get_key('cphone')
email   = get_key('email')
# other   = get_key('other')

print "Name: %s, %s [%s]<br>" % (lname,fname,sex)
print "Address: %s, %s, %s %s<br>" % (address,city,state,zip)
print "Born: %s<br>" % bday
print "Phones: %s / %s / %s<br>" % (dphone,ephone,cphone)
print "Email: %s <br>" % email

if len(email)==0:
    error("***You must provide an email contact ***")
    nbad = nbad + 1


if len(email) > 0 and email.find('@') < 0:
    error("***Email seems badly formatted***")
    nbad = nbad + 1

print "USAB: %s %s (renew: %s)[%s] fee=%d<br>" % (usabnum,usab,renew,family,usabfee)


if usab == '0':
    error("*** No USAB membership information")
    nbad = nbad + 1

if usab == 'current':
    if usabnum == '0' or len(usabnum)==0:
        error("*** Bad USAB number<br>")
        nbad = nbad + 1
else:
    if len(renew)==0:
        error("*** Please specify if this is a renewal or new ***<br>")
        nbad = nbad + 1
    
if usab == 'family' and len(family) == 0:
    error("*** No family name given for the USAB Family membership ***")
    nbad = nbad + 1



if debug1:
    # this is the old retrieval method, we don't need it anymore
    events = {}
    possible_events=['1','2','3','4','5','3s','4s','5s']
    for e in possible_events:
        ev='event%s' % e
        events[ev] = get_key(ev)
        print "%s: %s<br>" % (ev,events[ev])	

    partners={}
    possible_partners=['3','4','5','3s','4s','5s']
    for p in possible_partners:
        pa='partner%s' % p
        partners[pa] = get_key(pa)
        print "%s: %s<br>" % (pa,partners[pa])

#   new method to accumulate the events somebody plays

pevents=[]
for i in ['1','2']:
    add_singles(i)
for i in ['3','4','5','3s','4s','5s']:
    add_doubles(i)

#    loop over events, and count how many valid this player has
n=0
print "<br>"
for e in pevents:
    if e[0] != '0':
        n = n + 1
        print "Event%d: %s " % (n,e[0])
        if e[0][1] == 'd':
            print "(Partner: %s)"  % e[1]
            if len(e[1]) == 0:
                warning("<br>*** no partner name supplied : use REQ to request or TBA to announce later ***")
                nbad = nbad + 1
        if e[0][0] == 'm' and sex != 'm':
            error("<br>*** bad gender selection for a Female ***")
            nbad = nbad + 1
        if e[0][0] == 'w' and sex != 'f':
            error("<br>*** bad gender selection for a Male ***")
            nbad = nbad + 1
        print "<br>"

if n > maxev:
    error("*** too many events selected, %d is the max ***<br>" % maxev)
    nbad = nbad + 1
elif n==0:
    error("*** no events selected ***<br>" )
    nbad = nbad + 1
    
print "<br>"    

if n==1:            
    print "%s %s signed up for 1 event. <br>" % (fname,lname)
else:
    print "%s %s signed up for %d events. <br>" % (fname,lname,n)
if fee2 > 0:
    dues = fee0+n*fee1+usabfee+fee2
    print "Total Fees:  $%d + %d * $%d + $%d + $%d (late fee) = $%d<br>" % (fee0,n,fee1,usabfee,fee2,dues)
else:
    dues = fee0+n*fee1+usabfee
    print "Total Fees:  $%d + %d * $%d + $%d = $%d<br>" % (fee0,n,fee1,usabfee,dues)
if dues==0:
    error("*** There is no free registration ***<br>")
    nbad = nbad + 1
    
comments = get_key('comments')
print 'Your comments: %s<br>' % comments


if nbad > 0:
    error("ERROR: *** %d Fatal errors, you cannot register ***<br>" % nbad)
else:
    tmpname = '/tmp/mida%d.txt' % pid
    fp=open(tmpname,'w')
    fp.write("BEGIN=MIDA\n");
    fp.write("version=%s\n" % version);
    fp.write("fname=%s\n" % fname)
    fp.write("lname=%s\n" % lname)
    fp.write("sex=%s\n" % sex)
    fp.write("citizen=%s\n" % citizen)
    fp.write("address=%s\n" % address)
    fp.write("city=%s\n" % city)
    fp.write("state=%s\n" % state)
    fp.write("zip=%s\n" % zip)
    fp.write("cphone=%s\n" % cphone)
    fp.write("dphone=%s\n" % dphone)
    fp.write("ephone=%s\n" % ephone)
    fp.write("email=%s\n" % email)
    fp.write("usab=%s\n" % usab)    
    fp.write("usabnum=%s\n" % usabnum)    
    fp.write("renew=%s\n" % renew)
    fp.write("family=%s\n" % family)
    fp.write("usabfee=%s\n" % usabfee)    
    fp.write("latefee=%d\n" % fee2)
    fp.write("allfee=\n")
    fp.write("dues=%d\n" % dues)
    n=0
    for e in pevents:
        if e[0] != '0':
            n=n+1
            fp.write("event%d=%s\n" % (n,e[0]))
            if e[0][1] == 'd':
                fp.write("partner%d=%s\n" % (n,e[1]))
    fp.write("comments=%s\n" % comments)                
    fp.write("END=MIDA\n");                
    fp.close()
    cmd = "mail -s \"MIDA2006 %s %s\" %s < %s"  %   (fname,lname,emails,tmpname)
    e=os.system(cmd)
    if e==0:
        print "<br> Form has been processed and sent via email<br>"
        print "You can always go back to the previous page and re-submit your entry<br>"
	print "<B>Remember to send in your check and consent form by snail-mail before Nov 2!!!</B><br>"
    else:
        print "Some error occured in sending the registration via email...<br>"

#    print "<br><hr> Just to clarify, we're still testing this form, we're not open for business yet<br>"
#    print "Any comments/improvements etc. forward to Peter Teuben<br>"

    print "Please send any concerns to: teuben@astro.umd.edu<br>"
    os.system('date')
