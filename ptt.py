#
#  Peter's Tourney Toolkit - a set of python modules
#  to process badminton registration forms and prepare
#  event lists for ranking
#
#  History:
#  This work is based on the earlier awk/grep/sed/csh scripts
#  that have been used pre-2006.
#  First tested on Seniors 2006 and NJ Open 2006, both June 2006.
#  Continued with MIDA06 and DCOPEN07
#
#  $Id$
#
#  todo:
#     check if an entry doesn't have the same person twice
#     check if a name is a single name, no last name, if it's checked properly and flagged if not there
#     not very good (in non-=debug mode) in finding mis-registered accross events
#     not very good in detecting multiple event1='s
#     under the pressure of MIDA time, lots of horrible things added last days
#     REQ also can show up for singles in output
#     cannot have 2 the same names.... infamous Wei Wang dcopen06
#     fix if $$ is 20.00, has to be integer
#     doesn't deal with person A and B that both signed up with C
#     money defintions are in too many routines, so when changed, not same
#        so needs to be normalized
#     players_money needs an option to allow forcing +30 if no USAB1, but for final USAB0 sufficient
#        this way we do conservative at registration,but relaxed name fit for USAB/final report

ptt_version = "$Revision$  $Date$"

import os,sys,time

def request(name):
    """return true if the name if some form of a name is needed or coming
    """
    if name == "REQ" or name == "Req" or name == "request": return True
    if name == "TBA" or name == "Tba": return True
    if name == "need": return True
    return False


class Eopen(object):
    """ 
    open an event list (could be csv for TP or simple ascii list)
    """
    def __init__(self,name,TPout,basedir='events.d'):
        self.basedir = basedir
        # os.mkdir(basedir)
        if TPout:
            file = basedir + '/' + name + ".csv"
        else:
            file = basedir + '/' + name + ".list"
        self.fd = open(file,'w')
    def write(self,s):
        self.fd.write(s)
    def close(self):
        self.fd.close()

class USAB0(object):
    """Manage a USAB list. Currently the format contains the following columns,
    that can be accessed by the array self.players[]:
     0 'MemberID',
     1 'LastName',
     2 'Firstname',
     3 'Initial',
     4 'Address_1',
     5 'Address_2',
     6 'City',
     7 'State',
     8 'ZIP',
     9 'Country',
    10 'PhoneHome',
    11 'PhoneWork',
    12 'Email',
    13 'Gender',
    14 'DOB',
    15 'Club', 
    16 'EXP'
    Used for MidAtlantic 2007
    """
   
    def __init__(self,filename):
        self.filename = filename
        fd = open(filename,'r')
        self.lines=fd.readlines()
        fd.close()
        print "Read %d lines from %s" % (len(self.lines),filename)
        self.players=[]
        count = 0
        for l in self.lines:
            p = l.strip()
            if count==0:
                self.id=p.split('\t')
                print "Header:",self.id
            else:
                id = p.split('\t')
                id[0] = int(id[0])
                self.players.append(id)
                while len(id) < 17:
                    id.append(" ")
            count = count + 1
    def count(self):
        print len(self.players)
    def findbyname(self,name):
        """enter a name, first or last name
        Note names must be all in upper case
        """
        names = name.split()
        found=[]
        if len(names)==3:
            # this is kludgy, we assume western style  'Fname1 Fname2 Lname'
            # though Spanish could be 'Fname Lname1 Lname2'
            fname=names[0] + ' ' + names[1]
            lname=names[2]
            for i in self.players:
                if fname==i[2] and lname==i[1]:
                    found.append(i)
        elif len(names)==2:
            for i in self.players:
                if names[0]==i[2] and names[1]==i[1]:
                    found.append(i)
            if len(found)==0:
                # try last name alone
                for i in self.players:
                    if names[1]==i[1]:
                        found.append(i)
                if len(found) > 1:
                    # first name doesn't match well? The "JAMES LI WEN CHEH" case
                    found2=[]
                    for f in found:
                        print f
                        if len(f[2])==0: continue
                        f1=f[2].split()[0]
                        n1=len(f1)
                        if names[0] == f[2][0:n1]:
                            found2.append(f)
                    found = found2
        elif len(names)==1:
            for i in self.players:
                if names[0]==i[1]:
                    found.append(i)
            for i in self.players:
                if names[0]==i[2]:
                    found.append(i)
        else:
            print "Cannot find names like : ",name
        if len(found) > 1:
            all = []
            for i in found:
                print "%s %s" % (i[2],i[1])
            return []
        return found
    def findbyusab(self,usab):
        """enter a USAB number, e.g. 132, 400857"""
        for i in self.players:
            if usab==i[0]:
                return i
        return []
    def findusabfromname(self,name):
        """find a USAB number and expiration date, e.g. 132, 400857
        integer and string are returned
        """
        i = self.findbyname(name)
        if len(i) > 0:
            return (i[0][0],i[0][16])
        return (0,0)
            
            
class USAB1(object):
    """Manage a USAB list. Currently the format contains the following columns,
    that can be accessed by the array self.players[]:
     0 'MemberID',
     1 'Name',
     2 'Firstname',
     3 'Middlename',
     4 'Address',
     5 'Address2',
     6 'City',
     7 'State',
     8 'Postalcode',
     9 'Country',
    10 'PhoneHome',
    11 'PhoneWork',
    12 'Email',
    13 'Gender',
    14 'DOB',
    15 'Club', 
    16 'EXP'
    Used for MidAtlantic 2006
    """
   
    def __init__(self,filename):
        self.filename = filename
        fd = open(filename,'r')
        self.lines=fd.readlines()
        fd.close()
        print "Read %d lines from %s" % (len(self.lines),filename)
        self.players=[]
        count = 0
        for l in self.lines:
            p = l.strip()
            if count==0:
                self.id=p.split('\t')
                print "Header:",self.id
            else:
                id = p.split('\t')
                id[0] = int(id[0])
                self.players.append(id)
                while len(id) < 17:
                    id.append(" ")
            count = count + 1
    def count(self):
        print len(self.players)
    def findbyname(self,name):
        """enter a name, first or last name
        Note names must be all in upper case
        """
        names = name.split()
        found=[]
        if len(names)==3:
            fname=names[0] + ' ' + names[1]
            lname=names[2]
            for i in self.players:
                if fname==i[2] and lname==i[1]:
                    found.append(i)
        elif len(names)==2:
            for i in self.players:
                if names[0]==i[2] and names[1]==i[1]:
                    found.append(i)
        elif len(names)==1:
            for i in self.players:
                if names[0]==i[1]:
                    found.append(i)
            for i in self.players:
                if names[0]==i[2]:
                    found.append(i)
        else:
            print "Cannot find names like : ",name
        if len(found) > 1:
            all = []
            for i in found:
                print "%s %s" % (i[2],i[1])
            return []
        return found
    def findbyusab(self,usab):
        """enter a USAB number, e.g. 132, 400857"""
        for i in self.players:
            if usab==i[0]:
                return i
        return []
    def findusabfromname(self,name):
        """find a USAB number and expiration date, e.g. 132, 400857
        integer and string are returned
        """
        i = self.findbyname(name)
        if len(i) > 0:
            return (i[0][0],i[0][16])
        return (0,0)
            
            
class USAB2(object):
    """Manage a USAB2 list. Currently the format contains the following columns,
    0 FIRST_NAME,
    1 LAST_NAME,
    2 LABEL,
    3 TYPE,
    4 NUMBER,
    5 EXP,
    6 ADDRESS_1,
    7 ADDRESS_2,
    8 CITY,
    9 STATE,
    10 ZIP,
    11 BIRTHDATE
    Used for DC Open 2007
    """
   
    def __init__(self,filename):
        self.filename = filename
        fd = open(filename,'r')
        self.lines=fd.readlines()
        fd.close()
        print "Read %d lines from %s" % (len(self.lines),filename)
        self.players=[]
        count = 0
        for l in self.lines:
            p = l.strip()
            if count==0:
                self.id=p.split(',')
                print "Header:",self.id
            else:
                id = p.split(',')
                if len(id[4]) > 0:
                    id[4] = int(id[4])
                else:
                    # bad empty USAB's
                    # print id
                    id[4] = 0
                self.players.append(id)
                while len(id) < 17:
                    id.append(" ")
            count = count + 1
    def count(self):
        print len(self.players)
    def findbyname(self,name):
        """enter a name, first or last name
        Note names must be all in upper case
        """
        names = name.split()
        found=[]
        if len(names)==3:
            fname=names[0] + ' ' + names[1]
            lname=names[2]
            for i in self.players:
                if fname==i[0] and lname==i[1]:
                    found.append(i)
        elif len(names)==2:
            for i in self.players:
                if names[0]==i[0] and names[1]==i[1]:
                    found.append(i)
        elif len(names)==1:
            for i in self.players:
                if names[0]==i[1]:
                    found.append(i)
            for i in self.players:
                if names[0]==i[0]:
                    found.append(i)
        else:
            print "Cannot find names like : ",name
        if len(found) > 1:
            all = []
            for i in found:
                print "%s %s" % (i[0],i[1])
            return []
        return found
    def findbyusab(self,usab):
        """enter a USAB number, e.g. 132, 400857"""
        for i in self.players:
            if usab==i[4]:
                return i
        return []
    def findusabfromname(self,name):
        """find a USAB number and expiration date, e.g. 132, 400857
        integer and string are returned
        """
        i = self.findbyname(name)
        if len(i) > 0:
            return (i[0][4],i[0][5])
        return (0,0)
            
            
class USAB3(object):
    """Manage a USAB list. Currently the format contains the following columns,
    that can be accessed by the array self.players[]:
    0  LastName         1
    1  <nothing>
    2  FirstName        2
    3  MiddleInitial	3
    4  Comp	
    5  Date Of Birth	14
    6  USAB #	        0
    7  Sex	        13
    8  Address1	        4
    9  Address2	        5
    10  City	        6
    11 State	        7
    12 Zip	          8
    13 Expiration Date    16
    Used for DC Open 2009 - new database , but extracted still?

    ---old---
     0 'MemberID',         1 'Name',     2 'Firstname',     3 'Middlename',     4 'Address',     5 'Address2',     6 'City',
     7 'State',            8 'Postalcode',     9 'Country',    10 'PhoneHome',    11 'PhoneWork',    12 'Email',    13 'Gender',
    14 'DOB',    15 'Club',     16 'EXP'

    """
   
    def __init__(self,filename):
        self.filename = filename
        fd = open(filename,'r')
        self.lines=fd.readlines()
        fd.close()
        print "Read %d lines from %s" % (len(self.lines),filename)
        self.players=[]
        count = 0
        for l in self.lines:
            p = l.strip().upper()
            if count==0:
                self.id=p.split('\t')
                print "Header:",self.id
            else:
                id = p.split('\t')
                id[6] = int(id[6])
                while len(id) < 17:
                    id.append(" ")
                self.players.append(id)
            count = count + 1
    def count(self):
        print len(self.players)
    def findbyname(self,name):
        """enter a name, first or last name
        Note names must be all in upper case
        """
        names = name.split()
        found=[]
        if len(names)==3:
            fname=names[0] + ' ' + names[1]
            lname=names[2]
            for i in self.players:
                if fname==i[2] and lname==i[0]:
                    found.append(i)
        elif len(names)==2:
            for i in self.players:
                if names[0]==i[2] and names[1]==i[0]:
                    found.append(i)
        elif len(names)==1:
            for i in self.players:
                if names[0]==i[0]:
                    found.append(i)
            for i in self.players:
                if names[0]==i[2]:
                    found.append(i)
        else:
            print "Cannot find names like : ",name
        if len(found) > 1:
            all = []
            for i in found:
                print "%s %s" % (i[2],i[1])
            return []
        return found
    def findbyusab(self,usab):
        """enter a USAB number, e.g. 132, 400857"""
        for i in self.players:
            if usab==i[6]:
                return i
        return []
    def findusabfromname(self,name):
        """find a USAB number and expiration date, e.g. 132, 400857
        integer and string are returned
        """
        i = self.findbyname(name)
        if len(i) > 0:
            return (i[0][6],i[0][13])
        return (0,0)
            
            
class USAB4(object):
    """Manage a USAB/NGB list. 
       Currently the format contains the following columns,
       that can be accessed by the array self.players[]:
    0  LastName         
    1  FirstName        
    2  MiddleInitial	
    8  Date Of Birth	
    12 NGB # (USAB)     
    13 Sex	        
    15 Address1	        
    17 City	        
    18 State	        
    19 Zip	        
    24 Expiration Date  
    Used for DC Open 2010 - new RailStation database 

    """
   
    def __init__(self,filename):
        self.filename = filename
        fd = open(filename,'r')
        self.lines=fd.readlines()
        fd.close()
        print "Read %d lines from %s" % (len(self.lines),filename)
        self.players=[]
        count = 0
        for l in self.lines:
            p = l.strip().upper()
            if count==0:
                self.id=p.split('\t')
                print "Header:",self.id
            else:
                id = p.split('\t')
                if len(id[12]) > 0:
                    id[12] = int(id[12])
                else:
                    id[12] = 0
                # while len(id) < 17:
                #    id.append(" ")
                self.players.append(id)
            count = count + 1
    def count(self):
        print len(self.players)
    def findbyname(self,name):
        """enter a name, first or last name
        Note names must be all in upper case
        """
        names = name.split()
        found=[]
        if len(names)==3:
            fname=names[0] + ' ' + names[1]
            lname=names[2]
            for i in self.players:
                if fname==i[2] and lname==i[0]:
                    found.append(i)
        elif len(names)==2:
            for i in self.players:
                if names[0]==i[2] and names[1]==i[0]:
                    found.append(i)
        elif len(names)==1:
            for i in self.players:
                if names[0]==i[0]:
                    found.append(i)
            for i in self.players:
                if names[0]==i[2]:
                    found.append(i)
        else:
            print "Cannot find names like : ",name
        if len(found) > 1:
            all = []
            for i in found:
                print "%s %s" % (i[2],i[1])
            return []
        return found
    def findbyusab(self,usab):
        """enter a USAB number, e.g. 132, 400857"""
        for i in self.players:
            if usab==i[12]:
                return i
        return []
    def findusabfromname(self,name):
        """find a USAB number and expiration date, e.g. 132, 400857
        integer and string are returned
        """
        i = self.findbyname(name)
        if len(i) > 0:
            return (i[0][12],i[0][24])
        return (0,0)
            
            
        
class Registration(object):
    """Registration starts from an email folder that contains some kind of
    set of keyword=value pairs for each player. It is normally the output
    of the web form where the players registered.

    You will however need to know which style this folder is in.

    We now have several:
    d = Registration('dcopen06',1)        pjt's old dcopen style
    s = Registration('seniors2002,2)      pjt's old seniors style
    n = Registration('njopen',3)          eric miller's old style (at least for njopen)
    m = Registration('mida',5)            pjt's new MIDA style
    

    A note on nomenclature:
    We enforce the use of the following abbreviations for the categories:   ms, ws, md, wd, xd (lower case!)
    But the letter(s) designating the categories can be choosen freely by the parser() routine. Typical
    examples are:   A, C, J, S, U17, U15, S35, S40, S45 etc.
    The 'event' is then made up of a category and level, e.g.   'ms-S'

    """
    def __init__(self,filename,method,cat):
        self.method = method
        self.filename = filename
        self.cat = cat
        self.reload()
        print "  [Using software PTT %s]" % ptt_version
        print ""
        os.system('date')
        self.ctime = time.ctime()
    def reload(self):
        if self.method==1:
            """old dcopen"""
            self.parse1(self.filename)
        elif self.method==2:
            """old seniors"""
            self.parse2(self.filename)
        elif self.method==3:
            """eric miller's njopen"""
            self.parse3(self.filename)
        elif self.method==4:
            """eric miller's njopen"""
            self.parse4(self.filename)
        elif self.method==5:
            """new MIDA"""
            self.parse5(self.filename)
        else:
            print "Unimplemented method %d" % self.method

    def reset(self):
        self.sum = {}
        for c in self.cat:
            self.sum[c] = {}
            for e in ['ms', 'ws', 'md', 'wd', 'xd']:
                self.sum[c][e] = 0

    # --------------------------------------------------------------------------------
    
    def parse5(self,file):
        """parser for MIDA 2006, DCOPEN 2007, MIDA 2007, DCOPEN 2008, DCOPEN 2009"""
        def insert(player,words,keyform,key):
            if words[0] == keyform:
                player[key] = words[1].strip()
        def inserte(event,words,keyform):
            if words[0] == keyform and len(words[1])>0:
                event[key] = words[1]
        self.filename = file
        #   mida
        # self.cat = ['A', 'B', 'S']
        #   dcopen
        #self.cat = ['A', 'C', 'S']
        self.players = []
        self.reset()
        f = open(file,'r')
        a = f.readlines()
        f.close()       
        cnt1 = 0
        cnt2 = 0
        inside = False
        for l in a:
            line = l.strip()
            words = line.split('=')
            if len(words) > 0:
                if words[0] == 'BEGIN':
                    cnt1 = cnt1 + 1
                    inside = True
                    player={}
                    event={}
                    raw=[]
                    player['id'] = cnt1
                if words[0] == 'END':
                    cnt2 = cnt2 + 1
                    inside = False
                    # max 5 events
                    player['entry'] = raw
                    # print player
                    for number in ['1','2','3','4','5']:
                        keye = 'event'+number
                        keyp = 'partner'+number
                        if event.has_key(keye):
                            if  event[keye] == 'none': continue
                            new_key = event[keye]
                            player[new_key] = 1
                            cat = new_key[3:]
                            if new_key[1] == 'd':
                                if new_key[0] == 'm' or new_key[0] == 'w':
                                    new_key = 'dp-' + cat
                                elif new_key[0] == 'x':
                                    new_key = 'xp-' + cat
                                else:
                                    new_key = '?p-' + cat
                                partner = '???'
                                if event.has_key(keyp):
                                    partner = event[keyp]
                                player[new_key] = partner
                    # insert(player,['state','XX'],'state','state')
                    # fix such that usba has a value if it doesn't have one
                    if len(player['usab']) == 0:
                        player['usab'] = '0'
                    if len(player['usab']) > 6:
                        print "%s %s USAB# too long: %s" % (player['fname'],player['lname'],player['usab'])
                    self.players.append(player)
                if inside:
                    if words[0] != 'BEGIN':
                        raw.append(line)
                    #                    file        internal
                    insert(player,words,'fname',     'fname')
                    insert(player,words,'lname',     'lname')
                    insert(player,words,'sex',       'sex')
                    insert(player,words,'city',      'city')
                    insert(player,words,'address',   'address')
                    insert(player,words,'state',     'state')
                    insert(player,words,'zip',       'zip')
                    insert(player,words,'birthday',  'birthday')
                    insert(player,words,'usabnum',   'usab')
                    insert(player,words,'usab',      'usabmem')
                    insert(player,words,'cphone',    'cphone')
                    insert(player,words,'dphone',    'dphone')
                    insert(player,words,'ephone',    'ephone')
                    insert(player,words,'email',     'email')
                    insert(player,words,'club',      'club')
                    insert(player,words,'paid',      'dues')
                    insert(player,words,'tshirt',    'tshirt')
                    insert(player,words,'consent',   'consent')
                    insert(player,words,'latefee',   'latefee')
                    insert(player,words,'usabfee',   'usabfee')
                    insert(player,words,'usabcomment',   'usabcomment')
                    # search for up to 6 events (though they can't play 6 of course)
                    for number in ['1','2','3','4','5', '6']:
                        for thing in ['event', 'partner']:
                            key   = thing+number
                            inserte(event,words,key)
        if cnt1==cnt2:
            print "Found %d players in %s" % (cnt1,file)
        else:
            print "Terrible, found %d starting frames and %d ending" % (cnt1,cnt2)

    # --------------------------------------------------------------------------------
    
    def parse4(self,file):
        """parser for Eric's 2006 YMCA round robin doubles"""
        def insert(player,words,keyform,key):
            if words[0] == keyform:
                player[key] = words[1].strip()
        def insert1(player,words,keyform,key,val):
            if words[0] == keyform:
                player[key] = val
        self.filename = file
        self.cat = ['A', 'B', 'C', 'S', 'J']
        self.players = []
        self.reset()
        f = open(file,'r')
        a = f.readlines()
        f.close()
        cnt1 = 0
        cnt2 = 0
        inside = False
        for l in a:
            line = l.strip()
            words = line.split(':')
            if len(words) > 0:
                if words[0] == '0-Subject':
                    # New Jersey Open Registration Form Entry
                    cnt1 = cnt1 + 1
                    inside = True
                    player={}
                if words[0] == 'z-z-end':
                    cnt2 = cnt2 + 1
                    inside = False
                    q = self.player2(player['fname'],player['lname'])
                    if len(q) > 0:
                        print "###: Warning : player %s %s already registered" % (player['fname'],player['lname'])
                    if not player.has_key('state'):
                        player['state'] = '??'
                    if not player.has_key('sex'):
                        player['sex'] = '?'
                    self.players.append(player)
                if inside:
                    insert(player,words,'A-firstname',     'fname')
                    insert(player,words,'A-lastname',      'lname')
                    insert(player,words,'A-nickname',      'nick')
                    insert(player,words,'A-usab-no',       'usab')
                    insert(player,words,'A-age',           'age')
                    insert(player,words,'A-birthdate',     'bday')
                    insert(player,words,'B-org',           'org')
                    insert(player,words,'C-Street1',       'street')
                    insert(player,words,'C-Street2',       'street2')
                    insert(player,words,'D-city',          'city')
                    insert(player,words,'D-state',         'state')
                    insert(player,words,'E-zip',           'zip')
                    insert(player,words,'F-phone',         'phone')
                    insert(player,words,'H-E-Mail',        'email')
                    insert(player,words,'Z-comments',      'comments')
                    insert1(player,words,'WOMENS',      'sex','f')
                    insert1(player,words,'MENS',        'sex','f')
                    


                    insert(player,words,'RR_Doubles_A',    'md-A')
                    insert(player,words,'RR_Doubles_B',    'md-B')
                    insert(player,words,'RR_Doubles_C',    'md-C')

                    insert(player,words,'Partner_ABC',     'dp-A')
                    insert(player,words,'Partner_ABC',     'dp-B')
                    insert(player,words,'Partner_ABC',     'dp-C')

                    insert(player,words,'RR_MXDDoubles_A', 'xd-A')
                    insert(player,words,'RR_MXDDoubles_B', 'xd-B')
                    insert(player,words,'RR_MXDDoubles_C', 'xd-C')

                    insert(player,words,'Partner_MXD',     'xp-A')
                    insert(player,words,'Partner_MXD',     'xp-B')
                    insert(player,words,'Partner_MXD',     'xp-C')

        if cnt1==cnt2:
            print "Found %d players in %s" % (cnt1,file)
        else:
            print "Terrible, found %d starting frames and %d ending" % (cnt1,cnt2)

    # --------------------------------------------------------------------------------
    
    def parse3(self,file):
        """parser for njopen"""
        def insert(player,words,keyform,key):
            if words[0] == keyform:
                player[key] = words[1].strip()
        self.filename = file
        self.cat = ['A', 'C', 'S', 'J']
        self.players = []
        self.reset()
        f = open(file,'r')
        a = f.readlines()
        f.close()
        cnt1 = 0
        cnt2 = 0
        inside = False
        for l in a:
            line = l.strip()
            words = line.split(':')
            if len(words) > 0:
                if words[0] == '0-Subject':
                    # New Jersey Open Registration Form Entry
                    cnt1 = cnt1 + 1
                    inside = True
                    player={}
                if words[0] == 'z-Thanks':
                    cnt2 = cnt2 + 1
                    inside = False
                    q = self.player2(player['fname'],player['lname'])
                    if len(q) > 0:
                        print "###: Warning : player %s %s already registered" % (player['fname'],player['lname'])
                    if not player.has_key('state'):
                        player['state'] = '??'
                    if not player.has_key('sex'):
                        player['sex'] = '?'
                    self.players.append(player)
                if inside:
                    insert(player,words,'A-firstname',     'fname')
                    insert(player,words,'A-lastname',      'lname')
                    insert(player,words,'A-nickname',      'nick')
                    insert(player,words,'A-usab-no',       'usab')
                    insert(player,words,'gender',          'sex')
                    insert(player,words,'A-age',           'age')
                    insert(player,words,'A-birthdate',     'bday')
                    insert(player,words,'B-org',           'org')
                    insert(player,words,'C-Street1',       'street')
                    insert(player,words,'C-Street2',       'street2')
                    insert(player,words,'D-city',          'city')
                    insert(player,words,'D-state',         'state')
                    insert(player,words,'E-zip',           'zip')
                    insert(player,words,'F-phone',         'phone')
                    insert(player,words,'H-E-Mail',        'email')
                    insert(player,words,'Z-comments',      'comments')

                    # todo:  if somebody has a Partner, might need to tag it also as to play!!!

                    insert(player,words,'MS_A-B',          'ms-A')
                    insert(player,words,'MD_A-B',          'md-A')
                    insert(player,words,'WS_A-B',          'ws-A')
                    insert(player,words,'WD_A-B',          'wd-A')
                    insert(player,words,'MXD_A-B',         'xd-A')
                    insert(player,words,'Partner_A-B',     'dp-A')
                    insert(player,words,'Partner_MD_A-B',  'dp-A')
                    insert(player,words,'Partner_WD_A-B',  'dp-A')
                    insert(player,words,'Partner_MXD_A-B', 'xp-A')

                    insert(player,words,'MS_C-D',          'ms-C')
                    insert(player,words,'WS_C-D',          'ws-C')
                    insert(player,words,'MD_C-D',          'md-C')
                    insert(player,words,'WD_C-D',          'wd-C')
                    insert(player,words,'MXD_C-D',         'xd-C')
                    insert(player,words,'Partner_C-D',     'dp-C')
                    insert(player,words,'Partner_MD_C-D',  'dp-C')
                    insert(player,words,'Partner_WD_C-D',  'dp-C')
                    insert(player,words,'Partner_MXD_C-D', 'xp-C')

                    insert(player,words,'MS_SENIOR',          'ms-S')
                    insert(player,words,'WS_SENIOR',          'ws-S')
                    insert(player,words,'MD_SENIOR',          'md-S')
                    insert(player,words,'WD_SENIOR',          'wd-S')
                    insert(player,words,'MXD_SENIOR',         'xd-S')
                    insert(player,words,'Partner_SENIOR',     'dp-S')
                    insert(player,words,'Partner_MXD_SENIOR', 'xp-S')

                    insert(player,words,'BS_JUNIORS',         'ms-J')
                    insert(player,words,'GS_JUNIORS',         'ws-J')
                    insert(player,words,'BD_JUNIORS',         'md-J')
                    insert(player,words,'GD_JUNIORS',         'wd-J')
                    insert(player,words,'MXD_JUNIORS',        'xd-J')
                    insert(player,words,'Partner_JUNIORS',    'dp-J')
                    insert(player,words,'Partner_MXD_JUNIORS','xp-J')
        if cnt1==cnt2:
            print "Found %d players in %s" % (cnt1,file)
        else:
            print "Terrible, found %d starting frames and %d ending" % (cnt1,cnt2)

    def parse2(self,file):
        """parser for seniors2002"""
        def insert(player,words,keyform,key):
            if words[0] == keyform:
                player[key] = words[1]
        self.filename = file
        self.cat = ['1','2','3','4','5','6','7','8','9','10']
        self.players = []
        self.reset()
        f = open(file,'r')
        a = f.readlines()
        f.close()
        print 'Found %d lines in %s' % (len(a),file)
        cnt1 = 0
        cnt2 = 0
        inside = False
        for l in a:
            line = l.strip()
            words = line.split('=')
            if len(words) > 0:
                if words[0] == 'fname':
                    cnt1 = cnt1 + 1
                    inside = True
                    player={}
                if words[0] == 'comments':
                    cnt2 = cnt2 + 1
                    inside = False
                    self.players.append(player)
                if inside:
                    insert(player,words,'fname',     'fname')
                    insert(player,words,'lname',     'lname')
                    insert(player,words,'usab',      'usab')
                    insert(player,words,'sex',       'sex')
                    insert(player,words,'state',     'state')

                    for level in ['1','2','3','4','5','6','7','8','9','10']:
                        for cat in ['ms','ws','md','wd','xd','dp','xp']:
                            key   = cat+level
                            event = cat+'-'+level
                            if len(words[1]) > 0:
                                insert(player,words,key,event)

        if cnt1==cnt2:
            print "Found %d players in %s" % (cnt1,file)
        else:
            print "Terrible, found %d starting frames and %d ending" % (cnt1,cnt2)
            
    # --------------------------------------------------------------------------------            

    def parse1(self,file):
        """parser for dcopen06, and probably any dcopen up until 2006"""
        def insert(player,words,keyform,key):
            if words[0] == keyform:
                player[key] = words[1]
        def inserte(event,words,keyform):
            if words[0] == keyform and len(words[1])>0:
                event[key] = words[1]
        self.filename = file
        self.cat = ['A','C','S','M']
        self.players = []
        self.reset()
        f = open(file,'r')
        a = f.readlines()
        f.close()
        print 'Found %d lines in %s' % (len(a),file)
        cnt1 = 0
        cnt2 = 0
        inside = False
        for l in a:
            line = l.strip()
            words = line.split('=')
            if len(words) > 0:
                if words[0] == 'fname':
                    cnt1 = cnt1 + 1
                    inside = True
                    player={}
                    event={}
                if words[0] == 'comments':
                    cnt2 = cnt2 + 1
                    inside = False
                    for number in ['1','2','3']:
                        keye = 'event'+number
                        keyc = 'cat'+number
                        keyp = 'partner'+number
                        if event.has_key(keye):
                            if  event[keye] == 'none': continue
                            cat = '?'
                            if event.has_key(keyc): cat = event[keyc]
                            new_key = event[keye]+'-'+cat
                            player[new_key] = 1
                            if new_key[1] == 'd':
                                if new_key[0] == 'm' or new_key[0] == 'w':
                                    new_key = 'dp-' + cat
                                elif new_key[0] == 'x':
                                    new_key = 'xp-' + cat
                                else:
                                    new_key = '?p-' + cat
                                partner = '???'
                                if event.has_key(keyp):
                                    partner = event[keyp]
                                player[new_key] = partner
                    self.players.append(player)
                if inside:
                    insert(player,words,'fname',     'fname')
                    insert(player,words,'lname',     'lname')
                    insert(player,words,'usab',      'usab')
                    insert(player,words,'sex',       'sex')
                    insert(player,words,'state',     'state')
                    for number in ['1','2','3']:
                        for thing in ['event', 'cat', 'partner']:
                            key   = thing+number
                            inserte(event,words,key)

        if cnt1==cnt2:
            print "Found %d players in %s" % (cnt1,file)
        else:
            print "Terrible, found %d starting frames and %d ending" % (cnt1,cnt2)

    # --------------------------------------------------------------------------------

    def showcat(self):
        """show all categories for this registration in a matrix
        something like:
        ms-A ws-A md-A wd-A xd-A
        ms-C ws-C md-C wd-C xd-C
        """
        for c in self.cat:
            print "ms-%s  ws-%s  md-%s  wd-%s  xd-%s" % (c,c,c,c,c)

    def map(self):
        print ""
        print "Summary of number of entries in tournament: %s" % self.filename
        print "      ms   ws   md   wd   xd "
        # for e in ['ms' 'ws' 'md' 'wd' 'xd']:
        sum = [0,0,0,0,0]
        n = [0,0,0,0,0]
        for c in self.cat:
            n[0] = self.sum[c]['ms']
            n[1] = self.sum[c]['ws']
            n[2] = self.sum[c]['md']
            n[3] = self.sum[c]['wd']
            n[4] = self.sum[c]['xd']
            nsum = n[0] + n[1] + n[2] + n[3] + n[4]
            for i in range(5):
                sum[i] = sum[i] + n[i]
            print "%-3s:  %2d   %2d   %2d   %2d   %2d   |  %3d" % (c,n[0],n[1],n[2],n[3],n[4], nsum)
        sumall = sum[0]+sum[1]+sum[2]+sum[3]+sum[4]
        print "     ---  ---  ---  ---  ---   | ---" 
        print "     %3d  %3d  %3d  %3d  %3d   |  %3d" % (sum[0],sum[1],sum[2],sum[3],sum[4], sumall)
        print "Number of payments: %d" % (sum[0]+sum[1]+2*sum[2]+2*sum[3]+2*sum[4])

    def match_count(self,p=2):
        def mp(n,p):
            if n<2: return 0
            if p==1:
                return n-1
            elif p==2:
                return (3*n)/2-2
            elif p==3:
                return 2*n-4
        print ""
        print "Number of expected paired up matches in tournament: %s" % self.filename
        print "Assuming elimination level %d" % p
        print "      ms   ws   md   wd   xd "
        # for e in ['ms' 'ws' 'md' 'wd' 'xd']:
        sum = [0,0,0,0,0]
        n = [0,0,0,0,0]
        for c in self.cat:
            n[0] = mp(self.sum[c]['ms'],p)
            n[1] = mp(self.sum[c]['ws'],p)
            n[2] = mp(self.sum[c]['md'],p)
            n[3] = mp(self.sum[c]['wd'],p)
            n[4] = mp(self.sum[c]['xd'],p)
            nsum = n[0] + n[1] + n[2] + n[3] + n[4]
            for i in range(5):
                sum[i] = sum[i] + n[i]
            print "%-3s:  %2d   %2d   %2d   %2d   %2d   |  %3d" % (c,n[0],n[1],n[2],n[3],n[4], nsum)
        sumall = sum[0]+sum[1]+sum[2]+sum[3]+sum[4]
        print "     ---  ---  ---  ---  ---   | ---" 
        print "     %3d  %3d  %3d  %3d  %3d   |  %3d" % (sum[0],sum[1],sum[2],sum[3],sum[4], sumall)
        print "  (warning: as long as REQ partners have not been matched up, this match count is too large)"

    def conflicts(self):
        """identify various conflicts:
        - men in doubles events with women partners
        - players in doubles with no partner
        """
        print "Searching for conflicts:"

    def overlap(self,cat):
        if len(cat) != 2:
            print "Cannot do overlap for %s" % cat
        print "Checking overlap in %s :" % cat
        for p in self.players:
            for c in  ['ms', 'ws', 'md', 'wd', 'xd']:
                key1 = c + '-' + cat[0]
                key2 = c + '-' + cat[1]
                if p.has_key(key1) and p.has_key(key2):
                    print "###: Player %s %s overlapping %s and %s" % (p['fname'],p['lname'],key1,key2)

    def states(self,out=sys.stdout):
        """Show state statistics.
        Optionally a filename can be given, defaults to screen"""
        if out!=sys.stdout:
            out=open(out,"w")
        out.write("Participants per state: \n")
        count={}
        for p in self.players:
            state = p['state']
            if count.has_key(state):
                count[state] = count[state] + 1
            else:
                count[state] = 1
        for state in count.keys():
            out.write("%s : %d\n" % (state,count[state]))
        if out!=sys.stdout:
            out.close()

    def need(self):
        print "Checking for need partners:" 
        for p in self.players:
            for l in self.cat:
                for c in  ['md', 'wd', 'xd']:
                    key = c + '-' + l
                    if p.has_key(key):
                        partner = '???'
                        if c == 'xd':
                            key1 = 'xp-' + l
                        else:
                            key1 = 'dp-' + l
                        if p.has_key(key1):
                            partner = p[key1]
                        if request(partner):
                            player = "%s %s" % (p['fname'],p['lname'])
                            print "###: %s  =>  %-20s    w/ %s" % (key,player,partner)

    def sort1(self):
        """Sort players alphabetically"""
        def cmpfunc(a,b):
            name_a = a['lname'] + ' ' + a['fname'] 
            name_b = b['lname'] + ' ' + b['fname'] 
            if name_a == name_b: return 0
            if name_a <  name_b: return -1
            if name_a >  name_b: return 1
            return 0
        self.players.sort(cmpfunc)

    def sort2(self):
        """Sort players by their waiting list"""
        def cmpfunc(a,b):
            name_a = a['lname'] + ' ' + a['fname'] 
            name_b = b['lname'] + ' ' + b['fname'] 
            if name_a == name_b: return 0
            if name_a <  name_b: return -1
            if name_a >  name_b: return 1
            return 0
        self.players.sort(cmpfunc)

    def show1(self,name):
        """find a player. you can give just the first name, last name, or both."""
        p = self.player1(name)
        if len(p) == 0:
            print "No player found"
            return
        print "%s %s (%s) %s" % (p['fname'],p['lname'],p['state'],p['sex'][0])
        for cat in self.cat:
            for event in ['ms','ws','md','wd','xd']:
                key = event+'-'+cat
                if p.has_key(key):
                    if key[1]=='d':
                        key1 = self.partner_key(key)
                        if p.has_key(key1):
                            partner = p[key1]
                        else:
                            partner = '???'
                    else:
                        partner = ""
                    print "%s : %s" % (key,partner)
            
    def list1(self,out=sys.stdout,missing=True):
        """list of all players and their events.
        Optionally a filename can be given, defaults to screen"""
        n = 0
        if out!=sys.stdout:
            out=open(out,"w")
        out.write("Status: %s\n" % self.ctime)
        out.write("%s\n" % "Participants: ");
        tshirt={}
        for player in self.players:
            n = n + 1
            name = "%-15s, %-15s (%s)" % (player['lname'],player['fname'],player['state'])
            events = ""
            sex = player['sex']
            for cat in self.cat:
                for event in ['ms','ws','md','wd','xd']:
                    key = event+'-'+cat
                    if player.has_key(key):
                        events = events + " " + key
                        # check for REQ
                        if event == 'xd':
                            key1='xp-'+cat
                        else:
                            key1='dp-'+cat
                        if player.has_key(key1):
                            if request(player[key1]):
                                events = events + " (" + player[key1] + ")"
            out.write("%3d: %-30s %s: %s\n" % (n,name,sex[0],events))
            if len(events) > 0:
                s = player['tshirt']
                if tshirt.has_key(s):
                    tshirt[s] = tshirt[s] + 1
                else:
                    tshirt[s] = 1
        tsum = 0
        print "T-shirt size count for all playing participants:"
        for s in tshirt.keys():
            tsum = tsum +tshirt[s] 
            print "%-10s : %3d  %3d" % (s,tshirt[s],tsum)
        print "------------------------------------------------"
        if missing:
            if len(self.missing) > 0:
                out.write("===Missing and/or mis-spelled players:\n");
                old = ""
                count = 0
                for i in self.missing:
                    if i != old:
                        count = count + 1
                        out.write("%3d: %s\n" % (count,i))
                    old = i
                    print ""
            else:
                out.write("===Not checked for missing players yet:\n");
                
                
        if out!=sys.stdout:
            out.close()

    def list1_email(self,out=sys.stdout):
        """list of all players and their events.
        Optionally a filename can be given, defaults to screen"""
        n = 0
        if out!=sys.stdout:
            out=open(out,"w")
        out.write("Status: %s\n" % self.ctime)
        out.write("%s\n" % "Participants: ");
        for player in self.players:
            n = n + 1
            name = "%-15s, %-15s (%s)" % (player['lname'],player['fname'],player['state'])
            events = ""
            sex = player['sex']
            email = player['email']
            k=0
            for cat in self.cat:
                for event in ['ms','ws','md','wd','xd']:
                    key = event+'-'+cat
                    if player.has_key(key):
                        events = events + " " + key
                        k = k + 1
            for i in range(k,4):
                events = events + "     "
            out.write("%3d: %-30s %s: %s    : %s\n" % (n,name,sex[0],events, email))
                
        if out!=sys.stdout:
            out.close()
        
    def list1_booklet(self,out=sys.stdout):
        """list of all players + state, for the booklet"""
        n = 0
        if out!=sys.stdout:
            out=open(out,"w")
        for player in self.players:
            n = n + 1
            name = "%s, %s (%s)" % (player['lname'],player['fname'],player['state'])
            out.write("%s\n" % name)
                   
        if out!=sys.stdout:
            out.close()
            
                   
            
    def list1_money(self,out=sys.stdout,Qusab=False):
        """list of all players and their events.
        Optionally a filename can be given, defaults to screen"""
        n = 0
        if out!=sys.stdout:
            out=open(out,"w")
        out.write("Status: %s\n" % self.ctime)
        if Qusab:
            out.write("Participants:                     (state)sex  USAB0      USAB1      status      $$$\n");
            #         .  1: Agavinate      , Guitar          (NY) f: 202341+    0          :   0 :
        else:
            out.write("Participants: \n");
        sum1 = 0
        sum2 = 0
        sum3 = 0
        sum4p = 0
        sum4n = 0
        for player in self.players:
            n = n + 1
            name = "%-15s, %-15s (%3s)" % (player['lname'],player['fname'],player['state'])
            events = ""
            sex = player['sex']
            email = player['email']
            dues = int(player['dues'])
            #dues = 0
            # 'usab0' is the one from the USAB database, 'usab' is the one the player claimed
            usab  = player['usab']
            usab0 = player['usab0']
            usabexp = player['usabexp']
            usabfee = int(player['usabfee'])
            usabmem = player['usabmem']
            latefee = int(player['latefee'])
            usabcomment = player['usabcomment']
            club = player['club']
            k=0
            for cat in self.cat:
                for event in ['ms','ws','md','wd','xd']:
                    key = event+'-'+cat
                    if player.has_key(key):
                        events = events + " " + key
                        k = k + 1
            for i in range(k,3):
                events = events + "     "
            # dcopen::topay1=5+20*k
            # mida::topay1=25*k
            if k>0:
                topay1=5+20*k
            else:
                topay1=0
            topay2=0
            if usab0=="0" or usab0 == 0:
                if usabfee > 0:
                    topay2=usabfee
                else:
                    if len(player['uinfo']) == 0:
                        topay2 = 30
                    else:
                        topay2 = 0
                if k==0: topay2=0
            if usabfee > 0:
                topay2 = usabfee
            out.write("%3d: %-30s %s:" % (n,name,sex[0]))
            if not Qusab:
                out.write(" %s :" % events)
            out.write(" %-10s %-10s %-10s %-10s: %3d :" % (usab,usab0,usabexp,usabmem,usabfee))
            if Qusab:
                out.write(" %s" % usabcomment)
            else:
                out.write(" %3d - %3d - %3d - %3d = %3d  " % (dues,topay1,topay2,latefee,dues-topay1-topay2-latefee))
            if not Qusab:
                out.write(" %s" % club)
            out.write("\n")
            # FIGURE THIS OUT
            # sum1 = sum1 + topay2
            if usabfee > 0:
               sum1 = sum1 + usabfee
            sum2 = sum2 + dues
            sum3 = sum3 + latefee
            d = dues-topay1-topay2-latefee
            if d>0:
                sum4p = sum4p + d
            else:
                sum4n = sum4n - d
        if Qusab:
            out.write("===\n TOTAL USAB sum=%d\n" % sum1)
        else:
            out.write("===\n TOTAL sum_dues=%d     USAB sum=%d  TOURNEY sum=%d LATE=%d\n" % (sum2,sum1,sum2-sum1,sum3))
            out.write(" TOTAL sum4p=%d   sum4n=%d \n" % (sum4p,sum4n))
        if out!=sys.stdout:
            out.close()
        
                   
            
    def list2_1(self,u,out=sys.stdout):
        """list of all players, city, state and USAB number.. meant for the USAB1"""
        n = 0
        ngood = 0
        if out!=sys.stdout:
            out=open(out,"w")
        out.write("Participants and USAB membership: \n");
        for player in self.players:
            n = n + 1
            city='???'
            usab='?'
            if player.has_key('city'): city = player['city']
            if player.has_key('usab'): usab = player['usab']
            name = "%-15s, %-15s " % (player['lname'],player['fname'])
            place = "%-20s %2s" % (city,player['state'])
            uname = player['fname'] + ' ' + player['lname']
            (findu,exp) = u.findusabfromname(uname.upper())
            player['usabexp'] = exp
            player['usab0'] = findu
            # findu = int(findu)
            if usab>0 and findu>0 and usab==findu:
                ngood=ngood + 1
                star = "*"
            else:
                star = " "
            out.write("%3d: %s %s :%s: %-10s : %-10s  %s\n" % (n,name,place,star,usab,findu,exp))
            # print "DEBUG: %d %d %s" % (usab,findu,star)
        if out!=sys.stdout:
            out.close()
        
            
    def list2(self,u,out=sys.stdout):
        """list of all players, city, state and USAB number.. meant for the USAB2"""
        n = 0
        ngood = 0
        if out!=sys.stdout:
            out=open(out,"w")
        out.write("Participants and USAB membership: \n");
        for player in self.players:
            n = n + 1
            city='???'
            if player.has_key('city'): city = player['city']
            if player.has_key('usab'): 
                usab = player['usab']
                u_info = u.findbyusab(int(usab))
                if len(u_info) > 0:
                    uplayer = u_info[2] + ' ' + u_info[0] 
                else:
                    uplayer = ' '
            else:
                usab = '?'
                u_info = []
                uplayer = ' '
                

                
            name = "%-15s, %-15s " % (player['lname'],player['fname'])
            place = "%-20s %2s" % (city,player['state'])
            uname = player['fname'] + ' ' + player['lname']
            (findu,exp) = u.findusabfromname(uname.upper())
            player['usabexp'] = exp
            player['usab0'] = findu
            player['uinfo'] = u_info

            # findu = int(findu)
            if usab>0 and findu>0 and usab==findu:
                ngood=ngood + 1
                star = "*"
            else:
                star = " "
            out.write("%3d: %s %s :%s: %-10s : %-10s  %s  [%s]\n" % (n,name,place,star,usab,findu,exp,uplayer))
            # print "DEBUG: %d %d %s" % (usab,findu,star)
        if out!=sys.stdout:
            out.close()

    def email(self,efile,subject,stop_id=0):
        for player in self.players:
            fname = player['fname']
            lname = player['lname']
            email = player['email']
            my_id = player['id']
            if len(email) > 0:
                f1 = open(efile)
                f0 = open('email.tmp','w')
                f0.write("Dear %s %s \n    (or person responsible for his/her entry):" % (fname,lname))
                for line in f1.readlines():
                    f0.write(line)
                for line in player['entry']:
                    f0.write("%s\n" % line)
                f0.close()
                print "%d: %s" % (my_id,email)
                subject1 = "%s %s %s" % (subject,player['fname'],player['lname'])
                print "%s" % subject1
                cmd = "mail -s \"%s\" %s < email.tmp" % (subject1,email)
                print "CMD: ",cmd
                time.sleep(0.2)
                #os.system('ls -l email.tmp')
                os.system(cmd)
            if my_id == stop_id:
                break

    def list3(self,out=sys.stdout,verbose=True):
        """list of all players, and their emails"""
        if out!=sys.stdout:
            out=open(out,"w")
        for player in self.players:
            if player.has_key('email'):
                email = player['email']
                if len(email) > 0:
                    name = "%s %s" % (player['fname'],player['lname'])
                    if verbose:
                        out.write('"%s" <%s>' % (name,email))
                    else:
                        out.write("   "+email+",")
        if out!=sys.stdout:
            out.close()

    def list4(self,out=sys.stdout, replicate=0, formfeed=False):
        """Registration list, library card  style
        replicate = number of times a record is repeated per page
        formfeed = formfeed after each player?
        """
        if out!=sys.stdout:
            out=open(out,"w")
        for player in self.players:
            out.write("%-15s, %-15s" % (player['lname'],player['fname']))
            out.write("                                   %s\n" % player['lname'])
            out.write("---------------  ---------------\n");
            out.write("Address:      %s\n" % (player['address']))
            out.write("City,State:   %s, %s\n" % (player['city'],player['state']))
            usab  = player['usab']
            usab0 = player['usab0']
            usabfee = int(player['usabfee'])
            dues = int(player['dues'])
            #dues = 0
            latefee = int(player['latefee'])
            usabexp = player['usabexp']
            out.write("USAB#: Given:  %s       Found:  %s   w/Exp: %s\n" % (usab,usab0,usabexp))
            out.write("\n");
            out.write("Events:\n");

            k=0
            for cat in self.cat:
                for event in ['ms','ws','md','wd','xd']:
                    key = event+'-'+cat
                    if player.has_key(key):
                        k = k + 1
                        if key[1]=='d':
                            if key[0]=='x':
                                pkey = 'xp-'+cat
                            else:
                                pkey = 'dp-'+cat
                            out.write("%s : %s\n" % (key,player[pkey]))
                        else:
                            out.write("%s\n" % key)
            # DCOPEN: 5+20k   MIDA:   25*k
            if k>0:
                topay1=5+20*k
            else:
                topay1=0
            #topay1=25*k
            topay2=0
            if usab0=="0" or usab0 == 0:
                if usabfee > 0:
                    topay2=usabfee
                else:
                    topay2=30
            if usabfee > 0:
                topay2 = usabfee
            out.write("\n");
            out.write("Paid:     %d " % dues)
            if dues==0 and latefee==0:
                out.write("        (Adding $5 late fee for no payment present yet)\n")
                latefee = 5
            out.write("USAB fee: %d\n" % usabfee)
            out.write("Due:      %d    =   %d (entry) + %d (usab) + %d (late) - %d (paid)\n" % (topay1+topay2+latefee-dues,topay1,topay2,latefee,dues))
            out.write("Consent:  %s\n"  % player['consent'])

            out.write("______________  \n\n");
            for line in player['entry']:
                out.write("    %s\n" % line)
            out.write("_____________________________________________________________\n\n")
            
        if out!=sys.stdout:
            out.close()
        
    def list4usab(self,out=sys.stdout):
        """Registration list for new/renewing USAB members
        """
        if out!=sys.stdout:
            out=open(out,"w")
        count = 0
        for player in self.players:
            usabfee = int(player['usabfee'])
            if usabfee == 0: continue
            count = count + 1
            out.write("%-15s, %-15s                             %d\n" % (player['lname'],player['fname'],count))
            out.write("%s\n" % (player['address']))
            out.write("%s, %s %s\n" % (player['city'],player['zip'],player['state']))
            out.write("C-phone: %s   D-phone: %s  E-phone: %s\n" % (player['cphone'],player['dphone'],player['ephone']))
            out.write("Email: %s\n" % player['email'])
            out.write("Sex: %s     Birthday: %s\n" % (player['sex'],player['birthday']))
            usab  = player['usab']
            usab0 = player['usab0']
            dues = int(player['dues'])
            #dues = 0
            usabexp = player['usabexp']
            usabmem = player['usabmem']

            out.write("USAB: %s   Found:  %s   w/Exp: %s\n" % (usab,usab0,usabexp))
            out.write("\n");

            out.write("USAB fee: %d    (%s)\n" % (usabfee,usabmem))
            out.write("_____________________________________________________________\n\n")
            
        if out!=sys.stdout:
            out.close()
        
    def list4card(self,out=sys.stdout):
        """Red Registration card
        """
        if out!=sys.stdout:
            out=open(out,"w")
        count = 0
        for player in self.players:
            usabfee = int(player['usabfee'])
            count = count + 1
            out.write("%-15s, %-15s                          %d\n\n" % (player['lname'],player['fname'],count))
            out.write("%s, %s\n" % (player['city'],player['state']))
            usab  = player['usab']
            usab0 = player['usab0']
            dues = int(player['dues'])
            usabexp = player['usabexp']
            usabmem = player['usabmem']

            out.write("Paid: %s\n" % dues)
            out.write("USAB: %s   Found:  %s   w/Exp: %s\n" % (usab,usab0,usabexp))
            out.write("\n");

            out.write("USAB fee: %d    (%s)\n" % (usabfee,usabmem))
            out.write("_____________________________________________________________\n\n")
            
        if out!=sys.stdout:
            out.close()
        
    def list5(self,u,out=sys.stdout):
        """Database dump in csv format for the TP program"""
        def all_events(n,lines):
            """lines is a set of lines that contain event1=, partner1=.... 3"""
            out=[]
            for i in range(n):
                out.append(["",""])
            for l in lines:
                kv=l.split("=")
                if kv[0]=="event1":
                    out[0][0]=kv[1]
                if kv[0]=="event2":
                    out[1][0]=kv[1]
                if kv[0]=="event3":
                    out[2][0]=kv[1]
                if kv[0]=="partner1":
                    out[0][1]=kv[1]
                if kv[0]=="partner2":
                    out[1][1]=kv[1]
                if kv[0]=="partner3":
                    out[2][1]=kv[1]
                    
            return out
        if out!=sys.stdout:
            out=open(out,"w")
        header=[]
        header.append("USAB")
        header.append("USABref")
        header.append("lname")
        header.append("fname")
        header.append("sex")
        header.append("address")
        header.append("city")
        header.append("state")
        header.append("zip")
        header.append("cphone")
        header.append("dphone")
        header.append("ephone")
        header.append("email")
        header.append("event1")
        header.append("partner1")
        header.append("event2")
        header.append("partner2")
        header.append("event3")
        header.append("partner3")
        for h in header:
            out.write("\"%s\"," % h)
        out.write("\"country\"\n")
        for player in self.players:
            out.write("\"%s\"," % player["usab"])
            out.write("\"%s\"," % player["usab0"])
            out.write("\"%s\"," % player["lname"])
            out.write("\"%s\"," % player["fname"])
            out.write("\"%s\"," % player["sex"])
            out.write("\"%s\"," % player["address"])
            out.write("\"%s\"," % player["city"])
            out.write("\"%s\"," % player["state"])
            out.write("\"%s\"," % player["zip"])
            out.write("\"%s\"," % player["cphone"])
            out.write("\"%s\"," % player["dphone"])
            out.write("\"%s\"," % player["ephone"])
            out.write("\"%s\"," % player["email"])
            events = all_events(3,player['entry'])
            for i in [0,1,2]:
                out.write("\"%s\"," % events[i][0])
                out.write("\"%s\"," % events[i][1])
            # out.write("\"%s\"," % player["event1"])            
            out.write("\"usa\"\n")
        if out!=sys.stdout:
            out.close()
            
    def listall(self,debug=False,csv=False):
        """loop over all events in the tournament and list them.
        to do just one, use list(event)
        """
        print "=== LISTALL: "
        self.missing=[]
        for cat in self.cat:
            for event in ['ms','ws','md','wd','xd']:
                key = event+'-'+cat
                print "Event:: %s" % key
                self.list(key,debug,csv)
        print "=== Missing entries from: "
        self.missing.sort()
        old = ""
        count = 0
        for i in self.missing:
            if i != old:
                count = count + 1
                print "%3d: %s" % (count,i)
            old = i
        print ""
        np = len(self.players)
        print "Expecting a total of %d + %d = %d players" % (np,count,np+count)
            

    def list(self,key,debug=False, TPout=False):
        """list a single event
        key:    ms-XXX, ws-XXX, md-XXX, wd-XXX, xd-XXX
        debug:  useful before making the lists
        TPout:  useful if CSV lists are needed
        """
        if key[1] == 'd':
            self.doubles(key,debug,TPout)
        else:
            self.singles(key,debug,TPout)

    def wlistall(self,debug=False):
        """loop over all events in the tournament with waitlisting
        to do just one, use list(event)
        """
        print "=== WLISTALL: "
        self.missing=[]
        for cat in self.cat:
            for event in ['ms','ws','md','wd','xd']:
                key = event+'-'+cat
                print "Event:: %s" % key
                self.wlist(key,debug)
                key = event+'-'+cat+'w'
                print "Event:: %s" % key
                self.wlist(key,debug)
        print "=== Missing entries from: "
        self.missing.sort()
        old = ""
        count = 0
        for i in self.missing:
            if i != old:
                count = count + 1
                print "%3d: %s" % (count,i)
            old = i
        print ""
        np = len(self.players)
        print "Expecting a total of %d + %d = %d players" % (np,count,np+count)
            

    def wlist(self,key,debug=False):
        """list a single event
        key:    ms-XXX, ws-XXX, md-XXX, wd-XXX, xd-XXX
        debug:  useful before making the lists
        TPout:  useful if CSV lists are needed
        """
        if key[1] == 'd':
            self.wdoubles(key,debug)
        else:
            self.wsingles(key,debug)

    def bad_sex(self,sex,need_sex):
        """check genders
        sex:       'm' or 'f'
        need_sex   'm' or 'w'
        """
        if sex=='m' and need_sex=='m': return False
        if sex=='f' and need_sex=='w': return False
        return True

    def TP0(self):
        """header for TP player entry list"""
        line='"MemberID","Name","Firstname","State"\n'
        return line

    def TP1(self,player):
        """Tournament Program player output"""
        if player==0:
            line = '"0","NULL","NULL","NULL"'
        else:
            #line = '"%s","%s","%s","%s"' % (player['usab'],player['lname'],player['fname'],player['state'])
            line = '"%s","%s","%s","%s"' % (player['id'],player['lname'],player['fname'],player['state'])
        return line

    def singles(self,key,debug=True,TPout=False):
        """created a list of a singles entries:
        singles(players,key), e.g.  singles(p,'ms-A')
        key:  ms-XXX
              ws-XXX
        """
        n = 0
        need_sex = key[0]
        ev = Eopen(key,TPout)
        if TPout:    # write a header for the CSV file
            ev.write(self.TP0())
        for player in self.players:
            if player.has_key(key):
                n = n+1
                print "%3d: %s %s (%s) # %d" % (n,player['fname'],player['lname'],player['state'],player['id'])
                if TPout:
                    ev.write("%s\n" % self.TP1(player))
                else:
                    ev.write("%s %s (%s)\n" % (player['fname'],player['lname'],player['state']))
                sex = player['sex'][0]
                if self.bad_sex(sex,need_sex): print "###: Warning, %s is wrong sex (should be %s) for %s %s?" % (sex,need_sex,player['fname'],player['lname'])
        e=key[0:2]
        c=key[3:4]
        self.sum[c][e]  = n
        ev.close()

    def wsingles(self,key,debug=True):
        """created a list of a singles entries for wait listing
        singles(players,key), e.g.  singles(p,'ms-A')
        key:  ms-XXX
              ws-XXX
              "MemberID","Name","Firstname","State"
        """
        def sortwsingles(a,b):
            if a[1]<b[1]: return -1
            if a[1]>b[1]: return  1
            if a[1]==b[1]: return 0
        lout=[]
        TPout=True
        ev = Eopen(key,TPout)
        for player in self.players:
            if player.has_key(key):
                sout = "%s %s (%s) # %d" % (player['fname'],player['lname'],player['state'],player['id'])
                lout.append((sout,player['id']))
        lout.sort(sortwsingles)
        n = 0
        for l in lout:
            n = n + 1
            print "%3d: %s" % (n,l[0])
            ev.write("%s\n" % l[0])
        ev.close()

    def partner_key(self,key):
        if key[1] == 'd':
            if key[0] == 'x':
                return 'xp-' + key[3:]
            else:
                return 'dp-' + key[3:]
        else:
            return "### Illegal partner key for %s" % key

    def doubles(self,key,debug=True,TPout=False):
        """created a list of a doubles entries
        doubles(players,key1), e.g. doubles(p,'md-A')
        key:     md-XXX, wd-XXX, xd-XXX
        """
        n   = 0
        n1f = 0
        n1m = 0
        n2  = 0
        ev = Eopen(key,TPout)
        need_sex = key[0]
        if key[0] == 'x':
            mixed = True
            key2 = 'xp-' + key[3:]
        else:
            mixed = False
            key2 = 'dp-' + key[3:]
        # set this tag to 0 if we've not seen this person
        for player in self.players:
            player[0] = 0
        m_needy_players = []
        f_needy_players = []
        if TPout:    # write a header for the CSV file
            ev.write(self.TP0())
        # loop over all players, and see if they play in "key"
        for player in self.players:
            if player.has_key(key):
                sex = player['sex'][0]
                if not mixed and self.bad_sex(sex,need_sex): print "###: Warning, %s is wrong sex (should be %s)?" % (sex,need_sex)
                if player[0] == 0:
                    n = n+1
                    show = 1
                else:
                    show = 0
                player[0] = 1                
                partner = '???'
                if player.has_key(key2): partner = player[key2]
                if debug:
                    if show:
                        print "%2d: %s %s (%s) %s" % (n,player['fname'],player['lname'],player['state'],partner)
                    else:
                        print  "  : %s %s (%s) %s" % (player['fname'],player['lname'],player['state'],partner)
                p1 = self.player1(partner)
                if len(p1):
                    # partner found
                    p1[0] = 1
                    partner2 = '???'
                    if p1.has_key(key2): partner2 = p1[key2]
                    if debug: print "  : %s      %s %s (%s)" % (partner2,p1['fname'],p1['lname'],p1['state'])
                    if show:
                        n2 = n2 + 1
                        s1 = player['state']
                        s2 = p1['state']
                        if s1 == s2:
                            state = s1
                        else:
                            if mixed and sex=='m':
                                state = s1+'/'+s2
                            else:
                                state = s2+'/'+s1
                        # the next line should be the final and only line for printout in the final correct version
                        # the others are all for debugging and otherwise "should never happen" if all is well in the db
                        rank1 = player['id']
                        rank2 = p1['id']
                        if mixed and sex=='m':
                            s = "%s %s / %s (%s) # %d/%d" % (player['fname'],player['lname'],partner,state,rank1,rank2)
                        else:
                            s = "%s / %s %s (%s) # %d/%d" % (partner,player['fname'],player['lname'],state,rank1,rank2)
                        print "%2d:: %s" % (n,s)
                        if TPout:
                            if mixed and sex=='m':
                                ev.write("%s\n" % self.TP1(player))
                                ev.write("%s\n" % self.TP1(p1))
                            else:
                                ev.write("%s\n" % self.TP1(p1))
                                ev.write("%s\n" % self.TP1(player))
                        else:
                            ev.write("%s\n" % s)
                    if not debug and partner2 == '???':
                        print "### Missing partner (usually entered in different event)"
                else:
                    # partner not found
                    if debug:
                        print "  : %s %s / %s - no partner found!" % (player['fname'],player['lname'],partner)
                    if not request(partner):
                        self.missing.append(partner)
                        n2 = n2 + 1
                        if not debug:
                            s = "%s %s / %s (%s) ** not reg ** " % (player['fname'],player['lname'],partner,player['state'])
                            print "%2d:: %s" % (n,s)
                            if TPout:
                                ev.write("%s\n" % self.TP1(player))
                                ev.write("%s\n" % self.TP1(0))
                            else:
                                ev.write("%s\n" % s)
                    else:
                        s = "%s %s (%s) # %d" % (player['fname'],player['lname'],player['state'],player['id'])
                        if sex=='m':
                            m_needy_players.append(s)
                            n1m = n1m + 1
                        else:
                            f_needy_players.append(s)
                            n1f = n1f + 1
                        if TPout:
                            ev.write("%s\n" % self.TP1(player))  
                            ev.write("%s\n" % self.TP1(0))
                        else:
                            ev.write("%-40s    **REQ**\n" % s)
        if len(m_needy_players)+len(f_needy_players) > 0:
            print "== Partners Requested in %s by: =============" % key
            for np in f_needy_players+m_needy_players:
                print np
            print "============================================="

        e=key[0:2]
        c=key[3:]
        if mixed:
            self.sum[c][e] = n2 + min(n1m,n1f)
        else:
            self.sum[c][e] = n2 + max(n1m,n1f)/2

    def wdoubles(self,key,debug=True):
        """created a list of a doubles entries for the waitlist
        doubles(players,key1), e.g. doubles(p,'md-A')
        key:     md-XXX, wd-XXX, xd-XXX
        """
        def sortwdoubles(a,b):
            """ (s,r1,r2) """
            def max(x,y):
                if x>y: return x
                return y
            ra = max(a[1],a[2])
            rb = max(b[1],b[2])
            if ra < rb : return -1
            if ra > rb : return  1
            if ra == rb: return  0
        lout=[]
        n   = 0
        n1f = 0
        n1m = 0
        n2  = 0
        need_sex = key[0]
        if key[0] == 'x':
            mixed = True
            key2 = 'xp-' + key[3:]
        else:
            mixed = False
            key2 = 'dp-' + key[3:]
        # set this tag to 0 if we've not seen this person
        for player in self.players:
            player[0] = 0
        m_needy_players = []
        f_needy_players = []
        # loop over all players, and see if they play in "key"
        for player in self.players:
            if player.has_key(key):
                sex = player['sex'][0]
                if not mixed and self.bad_sex(sex,need_sex): print "###: Warning, %s is wrong sex (should be %s)?" % (sex,need_sex)
                if player[0] == 0:
                    n = n+1
                    show = 1
                else:
                    show = 0
                player[0] = 1                
                partner = '???'
                if player.has_key(key2): partner = player[key2]
                if debug:
                    if show:
                        print "%2d: %s %s (%s) %s" % (n,player['fname'],player['lname'],player['state'],partner)
                    else:
                        print  "  : %s %s (%s) %s" % (player['fname'],player['lname'],player['state'],partner)
                p1 = self.player1(partner)
                if len(p1):
                    # partner found
                    p1[0] = 1
                    partner2 = '???'
                    if p1.has_key(key2): partner2 = p1[key2]
                    if debug: print "  : %s      %s %s (%s)" % (partner2,p1['fname'],p1['lname'],p1['state'])
                    if show:
                        n2 = n2 + 1
                        s1 = player['state']
                        s2 = p1['state']
                        if s1 == s2:
                            state = s1
                        else:
                            if mixed and sex=='m':
                                state = s1+'/'+s2
                            else:
                                state = s2+'/'+s1
                        # the next line should be the final and only line for printout in the final correct version
                        # the others are all for debugging and otherwise "should never happen" if all is well in the db
                        rank1 = player['id']
                        rank2 = p1['id']
                        if mixed and sex=='m':
                            s = "%s %s / %s (%s) # %d/%d" % (player['fname'],player['lname'],partner,state,rank1,rank2)
                        else:
                            s = "%s / %s %s (%s) # %d/%d" % (partner,player['fname'],player['lname'],state,rank1,rank2)
                        lout.append((s,rank1,rank2))
                    if not debug and partner2 == '???':
                        print "### Missing partner (usually entered in different event)"
                else:
                    # partner not found
                    if debug:
                        print "  : %s %s / %s - no partner found!" % (player['fname'],player['lname'],partner)
                    if not request(partner):
                        self.missing.append(partner)
                        n2 = n2 + 1
                        if not debug:
                            s = "%s %s / %s (%s) ** not reg ** " % (player['fname'],player['lname'],partner,player['state'])
                            lout.append((s,999,999))
                    else:
                        s = "%s %s (%s) # %d" % (player['fname'],player['lname'],player['state'],player['id'])
                        if sex=='m':
                            m_needy_players.append(s)
                            n1m = n1m + 1
                        else:
                            f_needy_players.append(s)
                            n1f = n1f + 1
                        # print "%-40s    **REQ**" % s
        lout.sort(sortwdoubles)
        n = 0
        for l in lout:
            n = n + 1
            print "%3d: %s" % (n,l[0])
        if len(m_needy_players)+len(f_needy_players) > 0:
            print "== Partners Requested in %s by: =============" % key
            for np in f_needy_players+m_needy_players:
                print np
            print "============================================="

    def player2(self,fname,lname):
        for player in self.players:
            if player['fname']==fname and player['lname']==lname:
                return player
        return {}

    def player1(self,name):
        """find the first player that matches the name; some freedom in choosing Fname, Lname or both
        """
        for player in self.players:
            if player['fname']==name or player['lname']==name:
                return player
        names = name.split()
        if len(names) == 2:
            for player in self.players:
                if player['fname']==names[0] and player['lname']==names[1]:
                    return player
        if len(names) == 3:
            fname = names[0] + ' ' + names[1]
            lname = names[2]
            for player in self.players:
                if player['fname']==fname and player['lname']==lname:
                    return player
            fname = names[0]
            lname = names[1] + ' ' + names[2]
            for player in self.players:
                if player['fname']==fname and player['lname']==lname:
                    return player
        if len(names) == 4:
            print "### Name with 4 words???: " % names
        # having arrived here, no exact match was found, should try partial
        return {}
    def dump_all(self):
        for player in self.players:
            print player



##  there is no __main__ check and execute; this code is import'd and used
