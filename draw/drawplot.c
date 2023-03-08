/*
 *  drawplot:   plot a draw, with optional names, scores etc.
 *	
 *     12-oct-94        created for 1994 DC Open
 *	3-nov-95	minor mods for 1995 DC Open
 *     18-mar-95        additional match-id (match#, time) for a match [id]
 *                      after the match X/Y (or X-Y) notation
 *      6-mar-97   0.3  merge back in some older xedge= keyword from Seniors
 *	4-nov-97   0.4  top/bottom half option for 1997 DC Open
 *     11-nov-97   0.5  add USAB numbers via an 'id' file  (for singles ok now)
 *     14-nov-97   0.6  add winner for half!=0 case in the top draw
 *      7-may-98   0.7  allow the 2/1 bracket to be the 3rd place winner
 *			(from the shadow finals, between loosers of [1-2]/2)
 *      2-oct-99        ? some mucking at the airport ?
 *     26-oct-99   0.8  extract 1st or 2nd round loosers
 *      2-nov-99   0.9  use more liberal pattern matching
 *      8-nov-99   1.0c print shorter names for > 1st round
 *                      also fixed the bad MD-A bug when a lot of deep byes
 *     21-oct-00   1.0d some more bugs need to be fixed 
 *     20-oct-00        notice that plplot needs to be compiled in DOUBLE mode
 *      7-mar-02   1.1  follow IBF/USAB rules of placing seeds a little closer
 *     17-mar-02      a add timeslot=
 *     25-mar           fixed not showing finals, improve rr plot
 *      7-mar-23   1.2  plwid -> plwidth
 *      
 */

#include <nemo.h>
#include <plplot.h>
#include "draw.h"

string defv[] = {
    "in=\n          input data with the draw (optional)",
    "p=4\n          Draw depth (N=2**P is number of players) or -RR_players",
    "header=\n      Header on top of the draw",
    "cols=\n        Override column names (p+1) for each Round up to Winner",
    "dev=xwin\n	    PLPLOT Graphics device options",
    "o=\n           PLPLOT output filename",
    "ori=0\n        PLPLOT orientation (0=landscape 1=portrait)",
    "seeds=\n       seeds to print",
    "pmin=0\n       first column to draw horizontal lines for",
    "xedge=0,0\n    left and right fraction of plot to keep blank",
    "half=0\n       0=Full draw, 1=upper -1=lower half of draw",
    "id=\n          Filename with personal IDs to be tagged onto the left",
    "looser=\n      Show 1st or 2nd round loosers instead of plotting",
    "timeslot=\n    Optional lookup table of timeslot numbers",
    "plotid=t\n     Plot match ID and timeslot?",
    "VERSION=1.3\n  7-mar-2023 PJT",
    NULL,
};

string version="Plot a DRAW, with optional names and scores etc.";

string *burststring(string, string);
int     get_p(string);
int     parse_draw(string, int, int, Draw *, int, stream);
int     parse_rr(string, int, Team *, int, Draw *, stream);
void    plot_dd(string *, int,int,int, real,real, 
                  string, string *, int, Draw *, int, Player *, int *, int, bool);
void    print_dd(string, int, int, int, Draw *, int, Player *, int);
void    plot_rr(string *, int, int, real, real,
                string, Team *, int, Draw *, int *, bool);
int     draw_cmp(Draw *, Draw *);
int     get_player_id(int, Player *, char *);
int     player_eq(char *, char *);
int     player_is(char *);
string *parse_options();
string  abbrev(string);


#define MAXSEEDS     8
#define MAXLINELEN 256
#define MAXSLOT    256

nemo_main()
{
    int n, i, pmin, p = getiparam("p");
    Draw *draw;
    Team *team;
    Player *player;
    int maxdraw, ndraw, ne, maxplayer,nplayer;
    string header = getparam("header");
    string drawname = getparam("in");
    string *cols = NULL;
    string *plopts;
    int nseeds, seeds[MAXSEEDS+1];
    real xedge[2];
    int half=getiparam("half");
    int looser;
    stream tstr;
    bool Qid = getbparam("plotid");

    if (p==0) {
      // not implemented
      p = get_p(getparam("in"));
      if (p==0) error("Could not find drawdept p= in %s",getparam("in"));
    }

#if 0
    if (p>6)
	warning("Too many levels, cannot handle more than draws with 64");
#endif
    if (p<0) {              /* round robin */
        n = -p;
        team = (Team *) allocate(n*sizeof(Team));
        dprintf(0,"Round Robin with %d players\n",n);
    } else {                /* regular single elimitation draw */
        for (n=1, i=0; i<p; i++)
            n *= 2;
        dprintf(1,"Draw with maximum of %d players in the first round for p=%d\n",n,p);
    }
    if (hasvalue("cols"))
        cols = burststring(getparam("cols"),", \t");
    nseeds = nemoinpi(getparam("seeds"),seeds,MAXSEEDS);
    if (nseeds<0) error("Parsing seeds=%s",getparam("seeds"));
    seeds[nseeds]=0;    /* terminator of this array */
    pmin = getiparam("pmin");

    ne = nemoinpd(getparam("xedge"),xedge,2);
    if (ne < 0)
        error("bad xedge");
    else if (ne==1)
        xedge[1] = xedge[0];

    if (hasvalue("looser")) 
        looser=getiparam("looser");
    else
        looser=-1;
    if (hasvalue("timeslot"))
      tstr=stropen(getparam("timeslot"),"r");
    else
      tstr=NULL;


    plopts = parse_options();

    maxplayer = 128;
    player = (Player *) allocate(maxplayer*sizeof(Player));
    if (hasvalue("id")) {
        nplayer = parse_id(getparam("id"),maxplayer,player);
    } else
        nplayer = 0;
    
    if (p>0) {                  /* draw */

        maxdraw = 2*n-1;
                    /* cheat and allocate one more for winner in half mode */
        draw = (Draw *) allocate((maxdraw+1)*sizeof(Draw));
        ndraw = parse_draw(getparam("in"),p,maxdraw, draw, half, tstr);

	if (looser < 0)
          plot_dd(plopts,p,n,pmin,xedge[0],xedge[1],
                  header,cols,ndraw,draw,nplayer,player,seeds,half,Qid);
	else
	  print_dd(drawname,p,n,ndraw,draw,nplayer,player,looser);

    } else {                    /* round robin */

        maxdraw = (n*(n-1))/2;
        draw = (Draw *) allocate(maxdraw*sizeof(Draw));
        ndraw = parse_rr(getparam("in"),n,team, maxdraw,draw, tstr);
        plot_rr(plopts, p, n, xedge[0], xedge[1],
                header, team, ndraw, draw, seeds,Qid);
    }
}



static string plkeys[] = {
    "dev", "o", "ori", NULL,
};

string *parse_options()
{
    int i, n=0;
    string *sp, *opts;
    char tmp[128];

    
    for (i=0; plkeys[i]; i++)
        if (hasvalue(plkeys[i])) n++;
#if 0
	/* with options -o name etc. */
    n *= 2;
    sp = opts = (string *) allocate((n+1)*sizeof(string));
    for (i=0; plkeys[i]; i++) {
        if (!hasvalue(plkeys[i])) continue;
        sprintf(tmp,"-%s",plkeys[i]);
        sp[0] = strdup(tmp);
        sp++;
        sp[0] = strdup(getparam(plkeys[i]));
        sp++;
    }
    sp[0] = 0;
    for (i=0; opts[i]; i++) dprintf(1,"plopts: %s\n",opts[i]);
#else
	/* home brewn quick and dirty */
    opts = (string *) allocate((n+1)*sizeof(string));
    i = 0;
    opts[i++] = getparam("dev");
    opts[i++] = getparam("o");
    opts[i++] = getparam("ori");
#endif
    
    return opts;
}

int get_p(string fname)
{
  stream instr;
  char *cp, line[MAXLINELEN];
  string *words;
  int i, idx, len, nwords, count=0;

  instr = stropen(fname,"r");
  strclose(instr);
  return 0;
}


/*
 * List of ID's: (e.g. USAB numbers)
 *  Fname Lname ID
 *
 */
int parse_id (
    string fname,
    int maxplayer,
    Player *player
    )
{
    stream instr;
    char *cp, line[MAXLINELEN];
    string *words;
    int i, idx, len, nwords, count=0;

    if (fname==0 || *fname==0) return 0;
    instr = stropen(fname,"r");
    while (fgets(line,MAXLINELEN,instr) != NULL) {
        len = strlen(line);
        /* patch line, skip comments */
        if (line[len-1]=='\n') line[len-1]='\0';
        if (line[0]=='#' || line[0]==';' || line[0]=='!' || line[0]=='/') {
            continue;
        }
        if (count >= maxplayer) 
		warning("Too many entries; count=%d maxdraw=%d",
				count,maxplayer);
        words = burststring(line," \t");
        nwords = xstrlen(words,sizeof(string))-1;
        if (nwords < 1) continue;
        if (nwords < 3) error("%s: %d Need fname lname id",line,nwords);

        strcpy(player[count].name, words[0]);
	for (i=1; i<nwords-1; i++) {
            strcat(player[count].name, " ");
            strcat(player[count].name, words[i]);
        }
        strcpy(player[count].nick, words[nwords-2]);
        strcpy(player[count].id, words[nwords-1]);


        dprintf(2,"Player ID: %-32s %-16s %-16s\n",
                player[count].name,
                player[count].nick,
                player[count].id);

        count++;
    }
    dprintf(0,"Found %d ID players\n",count);
    return  count;
        
}



int parse_draw (
    string fname,
    int p,
    int maxdraw,
    Draw *draw,
    int half,
    stream tstr
    )
{
    stream instr;
    char *cp, *cp1, line[MAXLINELEN];
    string *words;
    int idx, idx1, len, nwords, count=0;
    int i1, i2, n = (maxdraw+1)/2;
    int x,y;
    bool keep;
    char *tslot[MAXSLOT+1];

    if (tstr) {
      dprintf(1,"Parsing timeslot lookup table\n");
      for (i1=0; i1<=MAXSLOT; i1++)
	tslot[i1] = 0;
      while (fgets(line,MAXLINELEN,tstr) != NULL) {
        len = strlen(line);
        /* patch line, skip comments */
        if (line[len-1]=='\n') line[len-1]='\0';
        if (line[0]=='#' || line[0]==';' || line[0]=='!' || line[0]=='/') {
            continue;
        }

        words = burststring(line," \t");
        nwords = xstrlen(words,sizeof(string))-1;
        if (nwords < 2) continue;

        idx = atoi(words[0]);
	if (idx > MAXSLOT) error("Not enough timeslots for %d",idx);
	tslot[idx] = strdup(words[1]);
      }
    }

    if (fname==0 || *fname==0) return 0;
    instr = stropen(fname,"r");
    while (fgets(line,MAXLINELEN,instr) != NULL) {
        len = strlen(line);
        /* patch line, skip comments */
        if (line[len-1]=='\n') line[len-1]='\0';
        if (line[0]=='#' || line[0]==';' || line[0]=='!' || line[0]=='/') {
            continue;
        }
        if (count >= maxdraw) warning("Too many entries; maxdraw=%d",maxdraw);
        words = burststring(line," \t");
        nwords = xstrlen(words,sizeof(string))-1;
        if (nwords < 1) continue;

        idx = 0;

        cp = words[idx];
        if (cp && isdigit(*cp)) {                /* we're expecting X/Y */
            draw[count].match = atoi(cp);
            cp = strchr(cp,'/');
            if (cp) {                           /* '/' found, so a real draw */
		i1 = draw[count].match;
		cp++;
		i2 = atoi(cp);
                if (half != 0) {
                    if (half > 0) {             /* upper half */
                        keep = (i1 <= (i2/2));
                        if (i1==1 && i2==1) keep=TRUE;
                    } else {                    /* lower half */
                        keep = (i1 > (i2/2));
                        if (i1==1 && i2==1) keep=FALSE; /* override: no winner */
                        if (keep) i1 -= i2/2;
                    }
                    if (keep) i2 /= 2;
                } else
                    keep = TRUE;
                if (keep) {
                    if (half==1 && i1==1 && i2==0) {
                        dprintf(1,"Slot %s: %d/%d \n",words[idx],i1,i2);
                        draw[count].match = maxdraw+1;      /* winner in TOP */
                    } else {
    		        if (i1<1 || i2 < 1 || i1 > n || i2 > n)
		            error("Slot %s: %d/%d parsing error or p=%d too small n=%d",
		            words[idx],i1,i2,p,n);
                        dprintf(1,"Slot %s: %d/%d \n",words[idx],i1,i2);
   		        draw[count].match = i1;
                        while (i2 < n) {
                            i2 *= 2;
                            draw[count].match += i2;
                        }
                    }
                }
	    }
            idx++;
        } else
            draw[count].match = count+1;

        if (!keep) continue;
#if 1
        cp = words[idx];
        if (cp && *cp == '[') {       /* got an optional match id */
            cp++;
            strcpy(draw[count].id,cp);

	    if (tstr && strchr(cp,',')) {    /* use lookup table */
	      cp1 = draw[count].id;
	      cp1 = strchr(cp1,',');
	      idx1 = atoi(cp1+1);
	      if (tslot[idx1]) {
		*cp1 = 0;
		strcat(draw[count].id," ");
		strcat(draw[count].id, tslot[idx1]);
	      }
	    }

            for(;;) {
                dprintf(1,"testing %s:",cp);
                while (*cp) cp++;
                cp--;
                dprintf(1,":found: %c\n",*cp);
                if (*cp == ']') break;      /* careful with infin. loop */
                cp = words[++idx];
                strcat(draw[count].id," ");
                strcat(draw[count].id,cp);
            }
            cp = draw[count].id;
            cp[strlen(cp)-1] = 0;
            dprintf(1,"GOT: (%s)\n",draw[count].id);
            idx++;
        } else {
            strcpy(draw[count].id,"");
        }
#endif
        cp = words[idx];
        if (cp && (isdigit(*cp) || *cp=='(' ||
                   strncmp(cp,"bye",3)==0 || strncmp(cp,"def",3)==0 ||
                   strncmp(cp,"BYE",3)==0 || strncmp(cp,"DEF",3)==0)) {
            strcpy(draw[count].result,cp);
            idx++;
        } else
            strcpy(draw[count].result," ");


	if (idx < nwords) {
            strcpy(draw[count].name,words[idx++]);
            for (;idx < nwords; idx++) {
                cp = words[idx];
                if (*cp=='#') break;
                strcat(draw[count].name," ");
                strcat(draw[count].name,cp);
            }
        } else
            strcpy(draw[count].name," ");

        dprintf(2,"%d %s %s\n",draw[count].match, draw[count].result,
            draw[count].name);
        count++;
    }

    if (count>0)
        qsort(draw,count,sizeof(Draw),draw_cmp);
    for (idx=0; idx<count; idx++)
        dprintf(1,"%d \"%s\": %s\n",draw[idx].match, draw[idx].result,
            draw[idx].name);
    
    return  count;
        
}

int parse_rr (
    string fname,
    int n,
    Team *team,
    int maxdraw,
    Draw *draw,
    stream tstr
    )
{
    stream instr;
    char *cp, *cp1, line[MAXLINELEN];
    string *words;
    int idx, idx1, len, nwords, count=0;
    int i1, i2;
    char *tslot[MAXSLOT+1];

    if (tstr) {
      dprintf(1,"Parsing timeslot lookup table\n");
      for (i1=0; i1<=MAXSLOT; i1++)
	tslot[i1] = 0;
      while (fgets(line,MAXLINELEN,tstr) != NULL) {
        len = strlen(line);
        /* patch line, skip comments */
        if (line[len-1]=='\n') line[len-1]='\0';
        if (line[0]=='#' || line[0]==';' || line[0]=='!' || line[0]=='/') {
            continue;
        }

        words = burststring(line," \t");
        nwords = xstrlen(words,sizeof(string))-1;
        if (nwords < 2) continue;

        idx = atoi(words[0]);
	if (idx > MAXSLOT) error("Not enough timeslots for %d",idx);
	tslot[idx] = strdup(words[1]);
      }
    }



    if (fname==0 || *fname==0) return 0;
    instr = stropen(fname,"r");
    while (fgets(line,MAXLINELEN,instr) != NULL) {
        len = strlen(line);
        /* patch line, skip comments */
        if (line[len-1]=='\n') line[len-1]='\0';
        if (line[0]=='#' || line[0]==';' || line[0]=='!' || line[0]=='/') {
            continue;
        }
        if (count >= maxdraw) warning("Too many entries; maxdraw=%d",maxdraw);
        words = burststring(line," \t");
        nwords = xstrlen(words,sizeof(string))-1;
        if (nwords < 1) continue;

        idx = 0;

        cp = words[idx];
        if (cp && isdigit(*cp)) {                /* we're expecting X or X-Y */
            i1 = atoi(cp);
            if (i1<1 || i1 > n) error("Bad person id (1..%d)",n);
            cp = strchr(cp,'-');
            if (cp) {           /* ok, we're at match level now ; count++ */
                cp++;
                i2 = atoi(cp);
                draw[count].u = i1;
                draw[count].d = i2;
                dprintf(1,"match %s (%d-%d)\n",words[idx],i1,i2);
                idx++;

                /* look for an (optional) match id */

                cp = words[idx];
                if (cp && *cp == '[') {       /* got an optional match id */
                    cp++;
                    strcpy(draw[count].id,cp);

		    if (tstr && strchr(cp,',')) {    /* use lookup table */
		      cp1 = draw[count].id;
		      cp1 = strchr(cp1,',');
		      idx1 = atoi(cp1+1);
		      if (tslot[idx1]) {
			*cp1 = 0;
			strcat(draw[count].id," ");
			strcat(draw[count].id, tslot[idx1]);
		      }
		    }


                    for(;;) {
                        dprintf(1,"testing %s:",cp);
                        while (*cp) cp++;
                        cp--;
                        dprintf(1,":found: %c\n",*cp);
                        if (*cp == ']') break;      /* careful with infin. loop */
                        cp = words[++idx];
                        strcat(draw[count].id," ");
                        strcat(draw[count].id,cp);
                    }
                    cp = draw[count].id;
                    cp[strlen(cp)-1] = 0;
                    dprintf(1,"GOT: %s\n",draw[count].id);
                    idx++;
                } else {
                    strcat(draw[count].id," ");
                }
                dprintf(1,"Match %d ID: %s\n",count+1,draw[count].id);
    
                /* look for a score or 'bye' or 'def' */

                cp = words[idx];
                if (cp && (isdigit(*cp) || *cp=='(' ||
                       strncmp(cp,"bye",3)==0 || strncmp(cp,"def",3)==0)) {
                    strcpy(draw[count].result,cp);
                    idx++;
                } else
                    strcpy(draw[count].result," ");
                dprintf(1,"Match %d score: %s\n",count+1,draw[count].result);

                /* look for the name of the winner (optional too) */

        	if (idx < nwords) {
                    strcpy(draw[count].name,words[idx++]);
                    for (;idx < nwords; idx++) {
                        cp = words[idx];
                        if (*cp=='#') break;
                        strcat(draw[count].name," ");
                        strcat(draw[count].name,cp);
                    }
                } else
                    strcpy(draw[count].name," ");

                count++;

            } else {            /* defining player/team names */
                idx++;
                cp = words[idx];
                strcpy(team[i1-1].name,cp);
                /* and catenate remaining parts of the name */
                idx++;
                while (idx<nwords) {
                    cp = words[idx];
                    if (*cp=='#') break;
                    strcat(team[i1-1].name," ");
                    strcat(team[i1-1].name,words[idx]);
                    idx++;
                } 
                dprintf(1,"player %s\n",team[i1-1].name);
            }
        } 
    }

    for (idx=0; idx<count; idx++)
        dprintf(1,"%d \"%s\": %s\n",draw[idx].match, draw[idx].result,
            draw[idx].name);
    
    return  count;
        
}

int draw_cmp(           /* helper function to sort a draw */
    Draw *i,
    Draw *j
    )
{
    return i->match - j->match;
}
    

/*                  plot a drop down draw - for up to 64 players */
void plot_dd (
    string *plopts,
    int p,
    int n,
    int pmin,
    real left_blank,
    real right_blank,
    string header,
    string *col,
    int ndraw,
    Draw *draw,
    int nplayer,
    Player *player,
    int *seeds,
    int half,
    bool Qid
    )
{
    PLFLT x, y, dx, dy, dx0, dy0, deltay, left, right;
    PLFLT xmin, xmax, ymin, ymax;
    int i, j, k, rank, nopts, slot=0, idx=0, pidx;
    char top[32], label[64], ver[80];

#if 0
    nopts = xstrlen(plopts,sizeof(string)) - 1;
    plParseInternalOpts(&nopts, plopts, PL_PARSE_FULL);
#endif    

    /* Get version number, just for kicks */

    plgver(ver);
    dprintf(1, "Plplot library version: %s\n",ver);


    if (*plopts[0]) plsdev(plopts[0]);          /* graphics name */
    if (*plopts[1]) plsfnam(plopts[1]);         /* graphics output file name */
    if (*plopts[2]) plsori(getiparam("ori"));   /* orientation */

    left = left_blank;
    right = right_blank;

    plinit();				/* initialize */
    pladv(0); 				/* advance to first page */
#if 1
    plvpor(0.0, 1.0, 0.0, 1.0);		/* set view port */
    plwind(0.0, 1.0, 0.0, 1.1);     /*   0-1 is for the draw 1-1.1 top labels */
#else
    xmin = 0.0;
    xmax = 1.0;
    ymin = 0.0;
    ymax = 1.0;
    plenv(xmin, xmax, ymin, ymax, 0, 0);
#endif
    plfontld(1);                    /* load the extended character set */

    plwidth(4);
    pljoin(0.0,0.0,0.0,1.0);
    pljoin(0.0,1.0,1.0,1.0);
    pljoin(1.0,1.0,1.0,0.0);
    pljoin(1.0,0.0,0.0,0.0);
    plwidth(1);    

    /* the draw: need p+1 columns */

    x = left;
    dx0 = dx = (1.0-left-right)/(float)(p+1);
    
    dy0 = dy = 1.0/(float)n;
    y = 1.0-0.5*dy;
    if (p<3)
        deltay = 0.05;      /* probably never happens */
    else if (p==3)
        deltay = 0.1;
    else if (p==4)
        deltay = 0.2;
    else if (p==5)
        deltay = 0.3;
    else if (p==6)
        deltay = 0.4;
    else
        deltay = 0.2;       /* should never happen */

    k = n;

    plwidth(3);
    plptex(0.5,1.08,1.0,0.0,0.5,header);
    plwidth(1);
    
    for (i=0; i<=p; i++) {              /* loop over all rounds */
                                /* i=0 is the first round; i=p final winner */
        if (col && col[i]) {
            strcpy(top,col[i]);
        } else {
            switch ( half==0 ? k : 2*k ) {
                case 1: strcpy(top,"Winner"); break;
                case 2: strcpy(top,"Finals"); break;
                case 4: strcpy(top,"Semis"); break;
                case 8: strcpy(top,"Quarters"); break;
                default:
                    switch(i) {
                        case 0: strcpy(top,"1st Round"); break;
                        case 1: strcpy(top,"2nd Round"); break;
                        case 2: strcpy(top,"3rd Round"); break;
                        default:sprintf(top,"%d. Round",i+1); break;
                    }
                    break;
            }
        }
        dprintf(1,"Column %d: %s\n",i+1,top);
        plschr(0.0,0.8);
        plptex(x+0.5*dx,1.03,1.0,0.0,0.5,top);
        plschr(0.0,1.0);
        
        for (j=0; j<k; j++) {           /* loop over all slots in a round */
            slot++;
            if (i>=pmin) {
                plwidth(3);
		if (pmin == 0 && i==0)
	            pljoin(0.0,y,x+dx*0.9,y);
		else
	            pljoin(x+dx*0.1,y,x+dx*0.9,y);
                plwidth(1);
                if (j%2) {      /* plot the 'arrows' for Diane */
                    pljoin(x+dx*0.9,y,x+dx*1.1,y+0.5*dy);
                    pljoin(x+dx*1.1,y+0.5*dy,x+dx*0.9,y+dy);
                                /* and try the numbers for Peter */
                    sprintf(top,"%d/%d",
				(half>=0 ? (j+1)/2 : (j+1)/2 + k/2),
				(half==0 ? k/2 :  k));
                    plschr(0.0,0.4);
                    plptex(x+dx,y+0.5*dy,dx,0.0,1.0,top);
                    plschr(0.0,1.0);
                }
            }
            if (idx<ndraw && draw[idx].match == slot) {
                plschr(0.0,0.5);
		if (i==pmin)                                            /* first column ? */
		    if (i==0) {				/* first round special */
                        if (nplayer > 0) {
                            pidx = get_player_id(nplayer,player,draw[idx].name);
                            if (pidx) {
                                strcpy(label,player[pidx-1].id);
                                strcat(label," ");
                                strcat(label,draw[idx].name);
                            } else
                                warning("No ID found for %s",draw[idx].name);
                            plptex(0.0,y+deltay*dy0,dx,0.0,0.0,label);      /* left flush */
                        } else
                            plptex(0.0,y+deltay*dy0,dx,0.0,0.0,draw[idx].name);  /* left flush */
                    } else
                        plptex(x,y+deltay*dy0,dx,0.0,0.0,draw[idx].name);       /* left flush */
                else
                    plptex(x+dx*0.5,y+deltay*dy0,dx,0.0,0.5,abbrev(draw[idx].name));  /* center */
                plfont(3);
                plschr(0.0,0.3);                
		if (Qid) {
		  dprintf(1,"ID: %s @ %g %g\n",draw[idx].id,x-dx*0.9,y);
		  plptex(x-dx*0.5,y,dx,0.0,1.0,draw[idx].id);
		}
                plptex(x+dx*0.5,y-deltay*dy0,dx,0.0,0.5,draw[idx].result);
                plfont(1);
                plschr(0.0,1.0);
                idx++;
            } else
                dprintf(1,"Empty match %d for idx=%d %s\n",
                        draw[idx].match,idx,draw[idx].name);
            y -= dy;
        }
        if (i<p) {
            k /= 2;
            x += dx;
            dy *= 2;
            y = 1.0 - 0.5*dy;
        }
    }

    dprintf(1,"Done at idx=%d match=%d/%d %s\n",
            idx,draw[idx].match,ndraw,draw[idx].name);
    if (draw[idx].match == 2*n) {
        if (half==1) {
            plschr(0.0,0.8);
            plptex(x+0.5*dx,0.1,1.0,0.0,0.5,"Winner");

            plschr(0.0,0.5);
            plptex(x+0.5*dx,0.05+deltay*dy0,1.0,0.0,0.5,abbrev(draw[idx].name));
            plfont(3);
            plschr(0.0,0.3);
            plptex(x+0.5*dx,0.05-deltay*dy0,1.0,0.0,0.5,draw[idx].result);
            plfont(1);
            plschr(0.0,1.0);
            idx++;
        } else
            warning("Cannot plot winner in other than top half");
    }
    

    if (seeds[0] > 0) {
        x = 0.75;
        y = 0.95;
        plschr(0.0,0.75);
        plptex(x,y,dx,0.0,0.0,"Seeded Players:");
        plschr(0.0,0.5);
        rank = 0;
        for (i=0; seeds[i] != 0; i++) {
            y -= 0.0625;
            idx = -1;
            for (j=0; j<ndraw; j++) {
                if (ABS(seeds[i]) == draw[j].match) {
                    idx = j;
                    break;
                }
            }
            if (seeds[i] > 0) rank++;
            if (idx >= 0) {
                sprintf(top,"%d. %s",rank,draw[idx].name);
            } else {
                sprintf(top,"%d. (slot %d)",i+1,seeds[i]);
                warning("Requested seed %d to be slot %d not found",i+1,seeds[i]);
            }
            plptex(x,y,dx,0.0,0.0,top);
        }
        plschr(0.0,1.0);
    }

    if (half != 0) {
        x = 0.925;
        y = (half < 0 ? 0.025 : 0.975);
        plptex(x,y,dx,0.0,0.0, (half < 0 ? "BOT" : "TOP"));
    }
    
    plend();
}


/*
 * print some things from a draw
 *  looser = 1,2        print the 1st or 2nd round loosers
 *  looser = 0          print current possible matches
 *                      and report# matches played in this event
 *                      or if all done, report winner

 */

void print_dd (
    string drawname,
    int p,
    int n,
    int ndraw,
    Draw *draw,
    int nplayer,
    Player *player,
    int looser
    )
{
    int i, j, k, rank, nopts, slot=0, idx=0, nmatch=0, pidx;
    char top[32], label[64], ver[80];
    Draw *u, *d, *w;

    /* In the first part of this routine we have:       */
    /* n     = number of players in the first round     */
    /* ndraw = number of entries in the draw, not counting BYE's and unplayed matches */

    dprintf(2,"# n=%d  ndraw=%d\n",n,ndraw);

    k = ndraw;
    for (i=0, slot=1; i<ndraw; i++, slot++) {        /* zero the remaining part of draw */
      while (slot < draw[i].match) {               /* since they have not been played */
            dprintf(2,"enlarge %d: %d BYE\n",i+1,slot);
            draw[k].name[0] = 0;
            draw[k].match = slot;
            k++;
            slot++;
       }
         dprintf(2,"        %d: %d %s\n",i+1,draw[i].match,draw[i].name);
    }

    /* BUG:  there is a bug here. If the drawsheet does not have dummy
       entries for the final parts of the draw, it will give those slot=0
       and get sorted out wrong in the next qsort()
    */

    ndraw = 2*n-1;          /* reset size, now that we have a full draw */
    qsort(draw,ndraw,sizeof(Draw),draw_cmp);

    for (i=0; i<ndraw; i++) {
        draw[i].pwin = 0;
        dprintf(2,"%d: %d %s\n",i+1,draw[i].match,draw[i].name);
    }

    if (looser > 0)         
        printf("# Players which lost %d matches in %s:\n",
                looser,getparam("in"));
    if (looser == 0)
        printf("# The following matches can be played in %s\n",drawname);

    idx = 0;   /*   try BUG 21-oct ???? */
    while (n > 1) {
            for (i=0; i<n; i+=2) {
                u = &draw[idx+i];       /* up */
                d = &draw[idx+i+1];     /* down */
                w = &draw[idx+n+i/2];   /* winner */
                if (player_is(u->name) && player_is(d->name)) {   /* both names known */
                   nmatch++;
                   dprintf(1,"Playing %s vs. %s  ; winner %s\n",
                        u->name, d->name, w->name);
                    if (player_is(w->name)==0) {
                        if (looser==0)
                            printf("%-8s %-10s %d/%d: %s vs. %s\n",
                                    w->id, drawname,
                                    i/2+1,n/2,
                                    u->name,d->name);
                    } else if (player_eq(u->name,w->name)) {   /* upper win */
                        w->pwin = u->pwin + 1;
                        if (d->pwin == looser-1)
                            printf("%s\n",d->name);
			if (looser==0 && n==2)
			  printf("%s: %s def. %s: %s \n", drawname, u->name, d->name, w->result);
                    } else if (player_eq(d->name,w->name)) {   /* lower win */
                        w->pwin = d->pwin + 1;
                        if (u->pwin == looser-1)
                            printf("%s\n",u->name);
			if (looser==0 && n==2)
			  printf("%s: %s def. %s: %s \n", drawname, d->name, u->name, w->result);
                    } else {				       /* mistake ? */
			dprintf(0,"u=%s d=%s w=%s: bad (n=%d i=%d idx=%d)\n",
				u->name,d->name,w->name,n,i,idx);
                        error("winner not one of two players");
		    }
                } else if (player_is(u->name)) {    /* only UPPER player */
                    w->pwin = u->pwin;
                    if (looser==0 && player_is(w->name)==0 && player_is(u->name))
                        printf("%-8s %-10s %d/%d: byeu %s \n",
                                    w->id, drawname,
                                    i/2+1,n/2, u->name);
                } else if (player_is(d->name)) {    /* only LOWER player */
                    w->pwin = d->pwin;
                    if (looser==0 && player_is(w->name)==0 && player_is(d->name))
                        printf("%-8s %-10s %d/%d: byed %s \n",
                                    w->id, drawname,
                                    i/2+1,n/2, d->name);
                } else if (player_is(w->name)==0) {
                    w->pwin = 0;
                } else {
                    if (looser > 0) {
                        error("should never occur, messed up draw %s @ %d %d",
                                   drawname,i,n);
		    }
		}
            }
            idx += n;
            n /= 2;
    }
        
    for (i=0; i<ndraw; i++) {
        dprintf(1,"%d: %d %s / %d\n",i+1,draw[i].match,draw[i].name,draw[i].pwin);
    }


    if (looser==0) printf("# Found %d matches in %s\n",nmatch+1,drawname);
}


/*             plot a round robin draw - doesn't work for > 4 players */
void plot_rr (
    string *plopts,
    int p,
    int n,
    real left_blank,
    real right_blank,
    string header,
    Team *team,
    int ndraw,
    Draw *draw,
    int *seeds,
    bool Qid
    )
{
    PLFLT x, y, dx, dy, dx0, dy0, deltay, left, right, drop = 0.035;
    int i, j, k, rank, nopts, slot=0, idx=0;
    int nx, ny, ix, iy, i1, i2;
    char top[32];

    if (*plopts[0]) plsdev(plopts[0]);          /* graphics name */
    if (*plopts[1]) plsfnam(plopts[1]);         /* graphics output file name */
    
    left = left_blank;
    right = right_blank;

    plinit();
    pladv(0);
    plvpor(0.0, 1.0, 0.0, 1.0);
    plwind(0.0, 1.0, 0.0, 1.1);     /*   0-1 is for the draw 1-1.1 top labels */
    plfontld(1);                    /* load the extended character set */

    plwidth(4);                       /* draw thick boundary */
    pljoin(0.0,0.0,0.0,1.0);
    pljoin(0.0,1.0,1.0,1.0);
    pljoin(1.0,1.0,1.0,0.0);
    pljoin(1.0,0.0,0.0,0.0);
    plwidth(1);  


    /* ok for 2, 3 or 4 teams in a RR */
    nx = 3;
    ny = 2;
        
    dx0 = dx = 1.0/(float)nx;
    dy0 = dy = 1.0/(float)ny;

    deltay = 0.05;

    plwidth(3);
    plptex(0.5,1.08,1.0,0.0,0.5,header);
    plwidth(1);

    plschr(0.0,0.8);
    plptex(0.5,1.03,1.0,0.0,0.5,"Round Robin");
    plschr(0.0,1.0);

    warning("Trying new plot for RR");

    for (iy=0; iy<ny; iy++) {
        y = 1.0 - (iy+1)*dy;
        for (ix=0; ix<nx; ix++) {
            x = 0.0 + ix*dx;
            if (ndraw==1) x += 0.5*dx;
	    if (ix==1) y-=drop;         /* the one in the middle must go down a little for long names */
            plwidth(3);
            pljoin(x+0.05*dx,y+0.75*dy,x+0.45*dx,y+0.75*dy);
            pljoin(x+0.05*dx,y+0.25*dy,x+0.45*dx,y+0.25*dy);
            pljoin(x+0.55*dx,y+0.50*dy,x+0.95*dx,y+0.50*dy);
            plwidth(1);
            pljoin(x+0.45*dx,y+0.75*dy,x+0.55*dx,y+0.50*dy);
            pljoin(x+0.45*dx,y+0.25*dy,x+0.55*dx,y+0.50*dy);

            plschr(0.0,0.5);
            plptex(x+dx*0.75,y+0.5*dy+deltay*dy0,dx,0.0,0.5,draw[slot].name);
            i1 = draw[slot].u-1;
            plptex(x+dx*0.25,y+0.75*dy+deltay*dy0,dx,0.0,0.5,team[i1].name);
            i2 = draw[slot].d-1;
            plptex(x+dx*0.25,y+0.25*dy+deltay*dy0,dx,0.0,0.5,team[i2].name);
            plfont(3);
            plschr(0.0,0.3);                
	    if (Qid)
	      plptex(x+dx*0.25,y+0.5*dy,dx,0.0,0.5,draw[slot].id);
            plptex(x+dx*0.75,y+0.5*dy-deltay*dy0,dx,0.0,0.5,draw[slot].result);
            plfont(1);
            plschr(0.0,1.0);

            slot++;
	    if (ix==1) y+=drop;         /* the one in the middle must go down a little for long names */
            if (slot >= ndraw) break;
        }
        if (slot >= ndraw) break;
    }

    if (seeds[0] > 0) {
        x = 0.75;
        y = 0.58;
        plschr(0.0,0.75);
        plptex(x,y,dx,0.0,0.0,"Seeded Players:");
        plschr(0.0,0.5);
        rank = 0;
        for (i=0; seeds[i] != 0; i++) {
            y -= 0.0625;
            rank++;
            idx = seeds[i]-1;
            sprintf(top,"%d. %s",rank,team[idx].name);
            plptex(x,y,dx,0.0,0.0,top);
        }
        plschr(0.0,1.0);
    }
    plend();
}

int get_player_id(int nplayer,Player *player, char *name)
{
    int i;

    for (i=0; i<nplayer; i++) {     /* dumb linear search */
        if (strncmp(player[i].name,name,strlen(player[i].name))==0) {
            dprintf(0,"PLAYER_ID: found %d for %s\n",i+1,name);
            return i+1;
        }
    }
    return 0;
}

int player_eq (char *a, char *b)
{
    char *cp, aa[64], bb[64];
    int i,n1, n2;

    for (cp=a, i=0; *cp; cp++) {
        if (isspace(*cp)) continue;     /* ignore spaces/tabs */
	if (isdigit(*cp)) continue;	/* numbers for scores */
	if (*cp == '-') continue;	/* dash (for scores)  */
	if (*cp == ',') continue;	/* , for scores */
        if (*cp == '(') break;          /* quit if (STATE) or (CLUB)  */
        aa[i++] = *cp;
    }   
    aa[i] = 0;                          /* terminate what we had copied */

    for (cp=b, i=0; *cp; cp++) {
        if (isspace(*cp)) continue;
	if (isdigit(*cp)) continue;	/* numbers for scores */
	if (*cp == '-') continue;	/* dash (for scores)  */
	if (*cp == ',') continue;	/* , for scores */
        if (*cp == '(') break;          /* quit if (STATE) or (CLUB)  */
        bb[i++] = *cp;
    }   
    bb[i] = 0;

    dprintf(1,"DEBUG: a=%s b=%s aa=%s bb=%s\n",a,b,aa,bb);

    n1 = strlen(aa);
    n2 = strlen(bb);
    if (n1==n2)
        return streq(aa,bb);


    return streq(aa,bb);
    
}

int player_is (char *a)
{
    char *cp, aa[64];
    int i,n1, n2;

    for (cp=a, i=0; *cp; cp++) {
        if (isspace(*cp)) continue;     /* ignore spaces/tabs */
	if (isdigit(*cp)) continue;	/* numbers for scores */
	if (*cp == '-') continue;	/* dash (for scores)  */
	if (*cp == ',') continue;	/* , for scores */
        if (*cp == '(') break;          /* quit if (STATE) or (CLUB)  */
        aa[i++] = *cp;
    }   
    aa[i] = 0;                          /* terminate what we had copied */

    return (strlen(aa) != 0);
}

/* 
 * Singles:
 *  long version of name:       First Middle Last (state)
 *  short version:              Last
 * Doubles:
 *  long version:               First1 Middle1 Last1 / First2 Middle2 Last2 (state/state)
 *  short:                      Last1 / Last2
 *
 * !!! Note we assume a space surrounds the names in a doubles team !!!
 */

string abbrev(string name)
{
    permanent char a[64];
    string *sp;
    char *slash, *ep, *bp;
    int i, is, ns;

    if (name == 0 || *name == 0) return name;

    sp =burststring(name," \t");
    if (sp[0] == 0 || *sp[0] == 0) return name;
    for (i=0, is=-1, ns=0; sp[i]; i++) {
        if (*sp[i] == '/') is = i;
        ns++;
    }
    slash = strchr(name,'/');


    if (slash) {                           /* doubles team */
        if (is < 0) {
            warning("Bad abbrev 1: %s",name); /* no space around '/' ?? */
            return name;
        }
        if (*sp[ns-1] == '(') ns--;
        if (is >= ns-1) {
            warning("Bad abbrev 2: %s",name); 
            return name;
        }                
        sprintf(a,"%s / %s",sp[is-1],sp[ns-1]);
        dprintf(2,"Abbrev doubles: %s => %s\n",name,a);
    } else {                               /* singles team */
        if (*sp[ns-1] == '(') ns--;
        if (ns<0) {
            warning("Bad abbrev 3: %s",name);
            return name;
        }
        strcpy(a,sp[ns-1]);
        dprintf(2,"Abbrev singles: %s => %s\n",name,a);
    }

    return a;
}
