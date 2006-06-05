#
#  Peter's Tourney Toolkit - a set of python modules
#  to process badminton registration forms and prepare
#  event lists for ranking
#
#  History:
#  This work is based on the earlier awk/grep/sed/csh scripts
#  that have been used pre-2006.
#  First tested on Seniors 2006 and NJ Open 2006, both June 2006.
#
#  $Id$
#

ptt_version = "$Revision$

import os

class Registration(object):
    """Registration starts from an email folder that contains some kind of
    set of keyword=value pairs for each player. It is normally the output
    of the web form where the players registered. 

    You will however need to know which style this folder is in.

    We now have three:
    d = Registration('dcopen06',1)        old dcopen style
    s = Registration('seniors2002,2)      seniors style
    n = Registration('njopen',3)          eric miller's style
    """
    def __init__(self,filename,method):
        self.method = method
        self.filename = filename
        self.reload()
        os.system('date')
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
        else:
            print "Unimplemented method %d" % self.method

    def reset(self):
        self.sum = {}
        for c in self.cat:
            self.sum[c] = {}
            for e in ['ms', 'ws', 'md', 'wd', 'xd']:
                self.sum[c][e] = 0

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
                    insert(player,words,'D-City',          'city')
                    insert(player,words,'D-state',         'state')
                    insert(player,words,'E-zip',           'zip')
                    insert(player,words,'F-phone',         'phone')
                    insert(player,words,'H-E-Mail',        'email')
                    insert(player,words,'Z-comments',      'comments')

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
                    insert(player,words,'WS_SENIOR',          'ms-S')
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
        for c in self.cat:
            print "ms-%s  ws-%s  md-%s  wd-%s  xd-%s" % (c,c,c,c,c)

    def map(self):
        print ""
        print "Summary of tournament: %s" % self.filename
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

    def conflicts(self):
        """identify various conflicts:
        - men in doubles events with women partners
        - players in doubles with no partner
        """
        print "Searching for conflicts:"

    def sort1(self):
        def cmpfunc(a,b):
            name_a = a['lname'] + ' ' + a['fname'] 
            name_b = b['lname'] + ' ' + b['fname'] 
            if name_a == name_b: return 0
            if name_a <  name_b: return -1
            if name_a >  name_b: return 1
            return 0
        self.players.sort(cmpfunc)
            
    def list1(self):
        """list of all players and their events"""
        n = 0
        for player in self.players:
            n = n + 1
            name = "%-15s, %-15s (%s)" % (player['lname'],player['fname'],player['state'])
            events = ""
            for cat in self.cat:
                for event in ['ms','ws','md','wd','xd']:
                    key = event+'-'+cat
                    if player.has_key(key):
                        events = events + " " + key
            print "%3d: %-30s: %s" % (n,name,events)
        
            
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
        for player in self.players:
            if player.has_key(key):
                n = n+1
                print "%2d: %s %s (%s)" % (n,player['fname'],player['lname'],player['state'])
                sex = player['sex'][0]
                if self.bad_sex(sex,need_sex): print "###: Warning, %s is wrong sex (should be %s)?" % (sex,need_sex)
        e=key[0:2]
        c=key[3:4]
        self.sum[c][e] = n

    def doubles(self,key,debug=True):
        """created a list of a doubles entries
        doubles(players,key1), e.g. doubles(p,'md-A')
        key:     md-XXX, wd-XXX, xd-XXX
        """
        n = 0
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
                            print "%2d:: %s %s / %s (%s)" % (n,player['fname'],player['lname'],partner,state)
                        else:
                            print "%2d:: %s / %s %s (%s)" % (n,partner,player['fname'],player['lname'],state)
                else:
                    print "  : %s %s / %s - no partner found!" % (player['fname'],player['lname'],partner)
                    if partner != "???" and partner != "need" and partner != "REQ":
                        self.missing.append(partner)
                    
                
        e=key[0:2]
        c=key[3:]
        self.sum[c][e] = n

    def player2(self,fname,lname):
        for player in self.players:
            if player['fname']==fname and player['lname']==lname:
                return player
        return {}

    def player1(self,name):
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
        return {}

