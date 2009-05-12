#! /bin/env python
#
#  Badminton ELO Ranking
#  http://en.wikipedia.org/wiki/Elo_rating_system
#  http://www.chessrankings.com/theory.aspx
#  
#
# The datafile of matches should be formatted as follows:
# For singles
#    p1 p2 : s1 s2 s2 s2 s1 s2
# For doubles
#    p1 p2 p3 p4 : s1 s2 s2 s2 s1 s2
#


ptt_version = "$Revision$  $Date$"

import os,sys,time,math

def q(r,scale=400.0):
    """compute Q"""
    return math.pow(10.0,r/scale)

def expected(r1,r2):
    """compute change E
    E_1 based on R_1 and other player R_2
    """
    return 1.0 / (1.0 + q(r2-r1))

def rank(r,s,e,k):
    """compute new rank
    R'_a = R_a + K*(S_a-E_a)
    """
    return r+k*(s-e)

def s2s(s):
    """convert a linear score list to a set of pairs"""
    s1 =[]
    for i in range(len(s)/2):
        s1.append( (s[2*i],s[2*i+1]) )
    return s1


class Ranking(object):
    """read a score file"""
    def __init__(self,filename):
        # rank
        self.rank = {}
        # games
        self.games = []
        self.filename = filename
        fd = open(filename,'r')
        self.lines=fd.readlines()
        fd.close()
        print "Read %d lines from %s" % (len(self.lines),filename)
        # singles lines are P1 P2 S1-S2
        for line in self.lines:
            if line[0] == '#': continue
            words = line.strip().split(':')
            if len(words) != 2: continue
            players = words[0].split()
            scores  = words[1].split()
            if len(players) != 2 and len(players) != 4:
                print "Skipping bad players in line: ",line
                continue
            if len(scores)%2 == 1:
                print "Skipping bad score in line: ",line
                continue
            for p in players:
                if not self.rank.has_key(p): self.rank[p] = 1500
            s = []
            for si in scores:
                s.append(int(si))
            self.games.append( (players,s2s(s)) )
        #print 'RANK:',self.rank
        #print 'GAME:',self.games
    def reset(self,default=1500):
        for player in self.rank.keys():
            self.rank[player] = default
            # print 'Player: ',player,' Rank: ',self.rank[player]
    def final(self):
        for player in self.rank.keys():
            print 'Final Player: ',player,' Rank: ',self.rank[player]
    def try1(self,debug=False,k=100):
        for player in self.rank.keys():
            print 'Initialize Player: ',player,' Rank: ',self.rank[player]
        n = 0
        for game in self.games:
            n = n + 1
            player = game[0]
            score  = game[1]
            print player, score
            if len(player) == 2:
                # singles
                p1 = player[0]
                p2 = player[1]
                for s in score:
                    s1 = float(s[0])/(float(s[0]+s[1]))
                    s2 = 1.0-s1
                    r1 = self.rank[p1]
                    r2 = self.rank[p2]
                    e1 = expected(r1,r2)
                    e2 = expected(r2,r1)
                    r1_new = rank(r1,s1,e1,k)
                    r2_new = rank(r2,s2,e2,k)
                    self.rank[p1] = r1_new
                    self.rank[p2] = r2_new
                    if debug:
                        print "Singles %d: %s vs %s  :  %s %s" % (n,p1,p2,s[0],s[1])
                        print 'Rank: %.1f %.1f %.1f %.1f %f %f   %f %f' % (r1,r2,r1_new,r2_new,e1,e2,s1,s2)
                        print "Player %s: %.1f %.1f" % (p1,r1,r1_new)
                        print "Player %s: %.1f %.1f" % (p2,r2,r2_new)
            elif len(player) == 4:
                # doubles
                p1a = player[0]
                p1b = player[1]
                p2a = player[2]
                p2b = player[3]
                for s in score:
                    s1 = float(s[0])/(float(s[0]+s[1]))
                    s2 = 1.0-s1
                    r1a = self.rank[p1a]
                    r1b = self.rank[p1b]
                    r2a = self.rank[p2a]
                    r2b = self.rank[p2b]
                    r1 = (r1a+r1b)/2.0
                    r2 = (r2a+r2b)/2.0
                    e1 = expected(r1,r2)
                    e2 = expected(r2,r1)
                    r1_new = rank(r1,s1,e1,k)
                    r2_new = rank(r2,s2,e2,k)
                    self.rank[p1a] = r1a + (r1_new-r1)
                    self.rank[p1b] = r1b + (r1_new-r1)
                    self.rank[p2a] = r2a + (r2_new-r2)
                    self.rank[p2b] = r2b + (r2_new-r2)
                    if debug:
                        print "Doubles %d: %s %s vs. %s %s  : %s %s" % (n,p1a,p1b,p2a,p2b,s[0],s[1])
                        print 'Rank: %.1f %.1f %.1f %.1f %f %f   %f %f' % (r1,r2,r1_new,r2_new,e1,e2,s1,s2)
                        print "Player %s: %.1f %.1f" % (p1a,r1a,r1a + (r1_new-r1))
                        print "Player %s: %.1f %.1f" % (p1b,r1b,r1b + (r1_new-r1))
                        print "Player %s: %.1f %.1f" % (p2a,r2a, r2a + (r2_new-r2))
                        print "Player %s: %.1f %.1f" % (p2b,r2b, r2b + (r2_new-r2))


        for player in self.rank.keys():
            print 'Player: ',player,' Rank: ',self.rank[player]
            
##  there is no __main__ check and execute; this code is import'd and used

if __name__ == '__main__':
    if len(sys.argv) > 1:
        t = Ranking(sys.argv[1])
        t.try1()
        t.final()

