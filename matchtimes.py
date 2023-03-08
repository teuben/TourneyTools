#! /bin/env python
#
#  matchtimes:    time estimates for scheduling a complex tournament 
#
#  Jan 2009 - Peter Teuben


# mt0 = matchtime for first rounds
# mt1 = match time for quarters and semis
# mt2 = match time for finals
# (30,35,40) are Chris Lawrence's guidelines
# use (1,1,1) if you want number of matches, not minutes needed

mt0 = 30
mt1 = 35
mt2 = 40

def round_robin(n, mt=30):
    """amount of time needed for RR of N players, MT in minutes"""
    return ((n*(n-1))/2)*mt

def single_elimination(n):
    """amount of time needed for N players to finish a single elimination"""
    if n<0: return round_robin(-n)
    nm = n-1
    if nm < 1: return 0
    sum = mt2
    nm  = nm - 1
    if nm < 1: return sum
    if nm < 7: return sum + nm*mt1
    sum = sum + 6 * mt1
    nm = nm - 6
    sum = sum + nm * mt0
    return sum

def double_elimination(n):
    """amount of time needed for N players to finish a single elimination"""
    if n<0: return round_robin(-n)
    return single_elimination(n) + single_elimination(n/2)
    
def round_robin(n, mt=30):
    """amount of time needed for RR of N players, MT in minutes"""
    return ((n*(n-1))/2)*30
    

def dcopen2009(t0=30,t1=35,t2=40):
    """match times for 2009"""
    global mt0,mt1,mt2
    mt0 = t0
    mt1 = t1
    mt2 = t2
    #
    hours = [23-17, 23-9, 16-9]
    court = 9
    #
    total = 0
    print("Hours:      ",hours)
    print("Match times:",mt0,mt1,mt2)
    for h in hours:
        total = total + h
    cm = total*court*60
    print("Total %2d hours on %2d courts: %d court minutes" % (total,court,cm))

    #
    a = [32, 16, 32, 16, 32]
    c = [32, 16, 32, 16, 32]
    s = [32,  0, 16,  4,  8]
    sum = 0
    for cat in a+c+s:
        sum = sum + double_elimination(cat)
    print("Total power of 2:           ",sum)
    a = [33, 10, 36, 13, 32]
    c = [46, 15, 44, 14, 41]
    s = [23,  1, 15,  4,  8]
    sum = 0
    for cat in a+c+s:
        sum = sum + double_elimination(cat)
    print("Total too much:             ",sum)
    a = [33, 10, 35, 11, 25]
    c = [46, 15, 40, 12, 29]
    s = [23,  1, 13,  3,  5]
    sum = 0
    for cat in a+c+s:
        sum = sum + double_elimination(cat)
    print("Total about right:          ",sum)
    

def pjt():
    dcopen2009(30,35,40)
    dcopen2009(1,1,1)
