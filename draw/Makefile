CFLAGS = -g  -DDOUBLE
FFLAGS = -g -C -u


TAR = Makefile drawplot.c makedraw.c draw.h  team.h
 
#

# PLROOT = /usr/lib/plplot
#PLROOT = $(NEMO)/local/plplot
#PLROOT = $(NEMO)/local/plplot-990122
#PLROOT = $(NEMO)/local/plplot-980318
PLROOT = /usr/local/plplot


# solaris
#EL = -L/usr/Local/lib/X11R6 -L/local/lib/X11R6 -L/opt/SUNWspro/lib -R /usr/Local/lib/X11R6:/local/lib/X11R6:/opt/SUNWspro/lib
# linux
EL = -L$(PLROOT)/lib -L/usr/X11R6/lib -L$(NEMOLIB)

#
L = $(NEMOLIB)/libnemo.a

# sunos4
#LIBS = -lnemo -lplplotfX -lX11  
# sunos5
#LIBS = $(EL) -lnemo -lplplotfX -lX11  -lsocket -lnsl
#INCS = -I$(NEMO)/local/include/plplot 
# linux: new PLPLOT
#LIBS = $(EL) -lnemo -lplplotdtk -lMatrix -ltk8.0 -ltcl8.0 -lX11 -ldl -lm
#LIBS = $(EL) -lnemo -lplplotftk -lMatrix -ltk8.0 -ltcl8.0 -lX11 -lvga -ldl -lm -lg2c
#LIBS = $(EL) -lnemo -lPltk -lMatrix -ltk8.0 -ltcl8.0 -lX11 -lvga -ldl -lm -lg2c
#
#LIBS = $(EL) -L$(NEMOLIB) -L/rh62/usr/lib -lnemo -lPltk -lX11 -lvga -ldl -lm -lg2c
INCS = -I$(PLROOT)/include -I$(PLROOT)/include/plplot -I$(NEMOINC) -I$(NEMOLIB)
LIBS = $(EL) -lnemo -lplplotd -lX11 -lgd -lpng -ljpeg -lz -ldl -lm -lg2c

OBJFILES=
BINFILES= makedraw drawplot
TESTFILES=

#	Define an extra SUFFIX for our .doc file
.SUFFIXES: .doc

.c.doc: $*
	$* help=t > $*.doc
	@echo "### Normally this $*.doc file would be moved to NEMODOC"
	@echo "### You can also use mkpdoc to move it over"

help:
	@echo "Badminton stuff"
	@echo " No more help to this date"

clean:
	rm -f core *.o *.a *.doc $(BINFILES) $(TESTFILES)

cleanlib:
	ar dv $(L) $(OBJFILES)
	ranlib $(L)

$(L):   $(LOBJFILES)
	echo "*** Now updating all members ***"
	ar ruv $(L) $?
	$(RANLIB) $(L)
	rm -f $?
				
lib:   $(L)

bin: $(BINFILES)

#	NEMO compile rules
.o.a:
	@echo "***Skipping ar for $* at this stage"

.c.o:
	$(CC) $(CFLAGS) $(INCS) -c $<

.c.a:
	$(CC) $(CFLAGS) $(INCS) -c $<

.c:
	$(CC) $(CFLAGS) $(INCS) -o $* $*.c $(BL) $(LIBS) $(AL) -lm

.o:
	$(CC) $(CFLAGS) $(INCS) -o $* $*.o $(BL) $(LIBS) $(AL) -lm
#

tar:
	tar cvf draws.tar $(TAR)


N=8
P=3
draw:
	nemoinp 1:$(N) format=player-%d  | makedraw - p=$(P)
