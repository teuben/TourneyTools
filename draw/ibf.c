/*
 *  ibf (makedraw):   make a draw, starting from a ranked list of teams
 *
 *	0.1	12-oct-1994			peter teuben
 *	0.2	 2-oct-1999	cleanup for DC Open 99
 *      0.3     26-oct-1999     also allow finishing random draw (full=t)
 *      0.4     31-oct-1999     more work on the 9...16 places
 *      0.5      2-nov-1999     allow randomize on some levels
 *	0.6      4-nov-1999     optonial add match IDs to matches per round
 *                              
 * Todo: seeding rules for 16, 32, 64 draws
 */

#include <nemo.h>
#include "draw.h"

string defv[] = {
    "p=4\n          level depth ; 2**n is number of players ",
    "VERSION=0.6a\n 4-nov-99 PJT",
    NULL,
};

string usage="Make a drop down draw from a (ranked) list of players";




static int *byes[] = {
    {1},
    {0},
    {1,2,5},
    {1,6},
    {1},
    {0},
    {1,2,3,4,7,8,9},
    {1,2,3,8,9,10},
    {1,2,3,8,11},
    {1,4,9,12},
    {1,4,13},
    {1,14},
    {1},
    {-1},
};




nemo_main()
{
    int n, i, i0, idx, p = getiparam("p");
    int nid, mid, midx, matchid[10];
    char smatchid[32];
    Team *team, *w, zero;
    stream outstr;
    int nteam, slot;
    int seed, nrandom;
    int *bs, e;


    for (e=3, bs = byes; *bs[0] >= 0; bs++, e++) {
        printf("e=%d bye(1)=%d\n",e,bs[0]);
    }
}
