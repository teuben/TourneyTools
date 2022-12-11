/*
 * draw.h   definition of a single draw entry
 */


#define NAMELEN  64

typedef struct draw {
    char name[NAMELEN];     /* name and optional state of player/team */
    char id[NAMELEN];       /* optional ID string in [] in the input file */
    char result[NAMELEN];   /* optional result this player arrived here */
    int u, d;               /* IDs of the two players (up and down) */
    int pwin;               /* previous wins for this player/match */
    int match;              /* ? */
} Draw, *DrawPtr;

typedef struct team {
    char name[NAMELEN];     /* name and optional state of player/team */
    int id;                 /* id */
    int rank;
    int region;
    int slot;               /* linear, construed to be 1..(2**p-1) */
} Team, *TeamPtr;

typedef struct player {
    char name[NAMELEN];		/* full name */
    char nick[NAMELEN];		/* short nickname for in later draws */
    char id[NAMELEN];		/* some id (usually USAB number) */
} Player, *PlayerPtr;
