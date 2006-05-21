#

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
                if words[0] == 'Z-Release':
                    cnt2 = cnt2 + 1
                    inside = False
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
                    insert(player,words,'Partner-MXD_A-B', 'xp-A')

                    insert(player,words,'MS_C-D',          'ms-C')
                    insert(player,words,'WS_C-D',          'ws-C')
                    insert(player,words,'MD_C-D',          'md-C')
                    insert(player,words,'WD_C-D',          'wd-C')
                    insert(player,words,'MXD_C-D',         'xd-C')                
                    insert(player,words,'Partner_C-D',     'dp-C')
                    insert(player,words,'Partner_MXD_C-D', 'xp-C')

                    insert(player,words,'MS_SENIOR',         'ms-S')
                    insert(player,words,'WS_SENIOR',         'ms-S')
                    insert(player,words,'MD_SENIOR',         'md-S')
                    insert(player,words,'WD_SENIOR',         'wd-S')
                    insert(player,words,'MXD_SENIOR',        'xd-S')
                    insert(player,words,'Partner_SENIOR',    'dp-S')
                    insert(player,words,'Partner_MXD_SENIOR','xp-S')

                    insert(player,words,'BS_JUNIOR',         'ms-J')
                    insert(player,words,'WS_JUNIOR',         'ms-J')
                    insert(player,words,'GD_JUNIOR',         'md-J')
                    insert(player,words,'GD_JUNIOR',         'wd-J')
                    insert(player,words,'MXD_JUNIOR',        'xd-J')
                    insert(player,words,'Partner_JUNIOR',    'dp-J')
                    insert(player,words,'Partner_MXD_JUNIOR','xp-J')
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

    def showcat(self):
        for c in self.cat:
            print "ms-%s  ws-%s  md-%s  wd-%s  xd-%s" % (c,c,c,c,c)


    def map(self):
        print "      MS   WS   MD   WD   XD "
        for c in self.cat:
            for e in ['ms' 'ws' 'md' 'wd' 'xd']:
                print "%-3s:  %2d   %2d   %2d   %2d   %2d" % (c,self.sum[c]['ms'],self.sum[c]['ws'],self.sum[c]['md'],self.sum[c]['wd'],self.sum[c]['xd'])
                

    def list(self,key):
        if key[1] == 'd':
            self.doubles(key)
        else:
            self.singles(key)

    def singles(self,key):
        """created a list of a singles entries:
        singles(players,key), e.g.  singles(p,'ms-A')
        """
        n = 0
        for player in self.players:
            if player.has_key(key):
                n = n+1
                print "%2d: %s %s (%s)" % (n,player['fname'],player['lname'],player['state'])
        e=key[0:2]
        c=key[3:4]
        self.sum[c][e] = n

    def doubles(self,key1,key2=None):
        """created a list of a doubles entries
        doubles(players,key1,key2), e.g. doubles(p,'md-A','dp-A')
        """
        n = 0
        if key2 == None:
            if key1[2] == '-':
                if key1[0] == 'x':
                    key2 = 'xp-' + key1[3]
                else:
                    key2 = 'dp-' + key1[3]
        for player in self.players:
            player[0] = 0
        for player in self.players:
            if player.has_key(key1):
                if player[0] == 0:
                    n = n+1
                    show = 1
                else:
                    show = 0
                player[0] = 1                
                partner = '???'
                if player.has_key(key2): partner = player[key2]
                if show:
                    print "%2d: %s %s (%s) %s" % (n,player['fname'],player['lname'],player['state'],partner)
                else:
                    print  "  : %s %s (%s) %s" % (player['fname'],player['lname'],player['state'],partner)
                p1 = self.player1(partner)
                if len(p1):
                    p1[0] = 1
                    partner = '???'
                    if p1.has_key(key2): partner = p1[key2]
                    print "  : %s      %s %s (%s)" % (partner,p1['fname'],p1['lname'],p1['state'])
        e=key1[0:2]
        c=key1[3:4]
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
        return {}

    def listall(self):
        for cat in self.cat:
            for event in ['ms','ws','md','wd','xd']:
                key = event+'-'+cat
                print "Event: %s" % key
                self.list(key)

# p = parse1('njopen')
# p = parse2('seniors2002')
# p = parse3('dcopen06')

# r = Registration('njopen')
