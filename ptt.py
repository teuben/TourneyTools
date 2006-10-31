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

ptt_version = "$Revision$  $Date$"

import os,sys,time

class Eopen(object):
    def __init__(self,name,basedir='events.d'):
        self.basedir = basedir
        # os.mkdir(basedir)
        file = basedir + '/' + name + ".list"
        self.fd = open(file,'w')
    def write(self,s):
        self.fd.write(s)
    def close(self):
        self.fd.close()

class USAB(object):
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
                id[0] = int(id[0])
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
        if len(names)==2:
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
    def findbusabfromname(self,name):
        """enter a USAB number, e.g. 132, 400857"""
        i = self.findbyname(name)
        if len(i) > 0:
            return i[0][0]
        return 0
            
            
        
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
    def __init__(self,filename,method):
        self.method = method
        self.filename = filename
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
        """parser for MIDA 2006 """
        def insert(player,words,keyform,key):
            if words[0] == keyform:
                player[key] = words[1].strip()
        def inserte(event,words,keyform):
            if words[0] == keyform and len(words[1])>0:
                event[key] = words[1]
        self.filename = file
        self.cat = ['A', 'B', 'S']
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
                if words[0] == 'END':
                    cnt2 = cnt2 + 1
                    inside = False
                    # max 5 events
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
                    self.players.append(player)
                if inside:
                    insert(player,words,'fname',     'fname')
                    insert(player,words,'lname',     'lname')
                    insert(player,words,'sex',       'sex')
                    insert(player,words,'state',     'state')
                    # search for 6 events (though they can't play 6 of course)
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
                return 0
        print ""
        print "Number of expected matches in tournament: %s" % self.filename
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
                        if partner == "need" or partner == "???" or partner == "REQ" or partner == "TBA" or partner == "request":
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
            out.write("%3d: %-30s %s: %s\n" % (n,name,sex[0],events))
        if missing:
            if len(self.missing) > 0:
                out.write("===Missing players:\n");
                old = ""
                count = 0
                for i in self.missing:
                    if i != old:
                        count = count + 1
                        out.write("%3d: %s\n" % (count,i))
                    old = i
                    print ""
            else:
                out.write("===No missing players yet:\n");
                
                
        if out!=sys.stdout:
            out.close()
        
            
    def list2(self,out=sys.stdout):
        """list of all players, city, state and USAB number.. meant for the USAB"""
        n = 0
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
            out.write("%3d: %s %s : %s\n" % (n,name,place,usab))
        if out!=sys.stdout:
            out.close()
        
            
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
        
    def listall(self,debug=False):
        """loop over all events in the tournament and list them.
        to do just one, use list(event)
        """
        self.missing=[]
        for cat in self.cat:
            for event in ['ms','ws','md','wd','xd']:
                key = event+'-'+cat
                print "Event:: %s" % key
                self.list(key,debug)
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
            

    def list(self,key,debug=False):
        """list a single event
        key:  ms-XXX, ws-XXX, md-XXX, wd-XXX, xd-XXX
        """
        if key[1] == 'd':
            self.doubles(key,debug)
        else:
            self.singles(key,debug)

    def bad_sex(self,sex,need_sex):
        """check genders
        sex:       'm' or 'f'
        need_sex   'm' or 'w'
        """
        if sex=='m' and need_sex=='m': return False
        if sex=='f' and need_sex=='w': return False
        return True

    def singles(self,key,debug=True):
        """created a list of a singles entries:
        singles(players,key), e.g.  singles(p,'ms-A')
        key:  ms-XXX
              ws-XXX
        """
        n = 0
        need_sex = key[0]
        ev = Eopen(key)
        for player in self.players:
            if player.has_key(key):
                n = n+1
                print "%2d: %s %s (%s)" % (n,player['fname'],player['lname'],player['state'])
                ev.write("%s %s (%s)\n" % (player['fname'],player['lname'],player['state']))
                sex = player['sex'][0]
                if self.bad_sex(sex,need_sex): print "###: Warning, %s is wrong sex (should be %s) for %s %s?" % (sex,need_sex,player['fname'],player['lname'])
        e=key[0:2]
        c=key[3:4]
        self.sum[c][e] = n
        ev.close()

    def partner_key(self,key):
        if key[1] == 'd':
            if key[0] == 'x':
                return 'xp-' + key[3:]
            else:
                return 'dp-' + key[3:]
        else:
            return "### Illegal partner key for %s" % key

    def doubles(self,key,debug=True):
        """created a list of a doubles entries
        doubles(players,key1), e.g. doubles(p,'md-A')
        key:     md-XXX, wd-XXX, xd-XXX
        """
        n = 0
        ev = Eopen(key)        
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
        needy_players = []
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
                    p1[0] = 1
                    partner2 = '???'
                    if p1.has_key(key2): partner2 = p1[key2]
                    if debug: print "  : %s      %s %s (%s)" % (partner2,p1['fname'],p1['lname'],p1['state'])
                    if show:
                        s1 = player['state']
                        s2 = p1['state']
                        if s1 == s2:
                            state = s1
                        else:
                            state = s1+'/'+s2
                        # the next line should be the final and only line for printout in the final correct version
                        # the others are all for debugging and otherwise "should never happen" if all is well in the db
                        if mixed and sex=='m':
                            s = "%s %s / %s (%s)" % (player['fname'],player['lname'],partner,state)
                        else:
                            s = "%s / %s %s (%s)" % (partner,player['fname'],player['lname'],state)
                        print "%2d:: %s" % (n,s)
                        ev.write("%s\n" % s)
                else:
                    if debug:
                        print "  : %s %s / %s - no partner found!" % (player['fname'],player['lname'],partner)
                    if partner != "???" and partner != "need" and partner != "REQ" and partner != "TBA":
                        self.missing.append(partner)
                        if not debug:
                            s = "%s %s / %s (%s) ** not reg ** " % (player['fname'],player['lname'],partner,player['state'])
                            print "%2d:: %s" % (n,s)
                            ev.write("%s\n" % s)
                    else:
                        s = "%s %s (%s)" % (player['fname'],player['lname'],player['state'])
                        needy_players.append(s)
                        ev.write("%-40s    **REQ**\n" % s)
        if len(needy_players) > 0:
            print "== Partners Requested in %s by: =============" % key
            for np in needy_players:
                print np
            print "============================================="

        e=key[0:2]
        c=key[3:]
        self.sum[c][e] = n

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



##  there is no __main__ check and execute; this code is import'd and used
