#error Not used anymore
/*
 * team.h   definition of a team, for draws
 */


#define NAMELEN  64

typedef struct team {
    char name[64];
    int id;
    int rank;
    int region;
    int done;
} Team, *TeamPtr;
