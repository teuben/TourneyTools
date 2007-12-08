#! /usr/bin/perl -w
#
#  cgi-bin/collopen.pl:    process a badminton form and email 
#

use CGI qw(:standard);

$version = "29-mar-2004";
$q = CGI::new();
$late = 0;

sub bail (msg) {
  print i("  Please go BACK using your browser, fix your form, and click on Register again");
  exit ;
}

$fname     = $q->param("fname");
$lname     = $q->param("lname");
$usab      = $q->param("usab");
$address   = $q->param("address");
$city      = $q->param("city");
$state     = $q->param("state");
$zip       = $q->param("zip");
$dphone    = $q->param("dphone");
$ephone    = $q->param("ephone");
$birthday  = $q->param("birthday");
$sex       = $q->param("sex");
$email     = $q->param("email");
$group     = $q->param("group");


$event[0]   = $q->param("event1");
$partner[0] = $q->param("partner1");


$event[1]   = $q->param("event2");
$partner[1] = $q->param("partner2");


$event[2]   = $q->param("event3");
$partner[2] = $q->param("partner3");


$event[3]   = $q->param("event4");
$partner[3] = $q->param("partner4");

$comments    = $q->param("comments");

####    write report

$n = $#ms;

open(MAIL, ">/tmp/dcopen.tmp.$$");
print MAIL "fname=",$fname,"\n";
print MAIL "lname=",$lname,"\n";
print MAIL "address=",$address,"\n";
print MAIL "city=",$city,"\n";
print MAIL "state=",$state,"\n";
print MAIL "zip=",$zip,"\n";
print MAIL "dphone=",$dphone,"\n";
print MAIL "ephone=",$ephone,"\n";
print MAIL "birthday=",$birthday,"\n";
print MAIL "sex=",$sex,"\n";
print MAIL "email=",$email,"\n";
print MAIL "group=",$group,"\n";
#
$count = 0;

if ($event[0] ne "none") { $count++; }
print MAIL "event1=",  $event[0],  "\n";
print MAIL "partner1=",$partner[0],"\n";

if ($event[1] ne "none") { $count++; }
print MAIL "event2=",  $event[1],  "\n";
print MAIL "partner2=",$partner[1],"\n";

if ($event[2] ne "none") { $count++; }
print MAIL "event3=",  $event[2],  "\n";
print MAIL "partner3=",$partner[2],"\n";

if ($event[3] ne "none") { $count++; } 
print MAIL "event4=",  $event[3],  "\n";
print MAIL "partner4=",$partner[3],"\n";

#
print MAIL "numevents=",$count,"\n";

# !!  comments= must be the last one, some scripts use it as a trigger!!
print MAIL "comments=",$comments;
close MAIL;
chmod 0666,"/tmp/dcopen.tmp.$$";


####    report back to the form filler


print $q->header();
print hr, start_html;
if ($late) {
  print b("Please be adviced you are formally to late to enter a new name. ");
  print b("Some ammendments are possible, but i cannot guarentee any results. ");
  print b("However, here's is what I'm going to try and send to the database:");
}
print p("$fname, here is your 2004 DC Open Registration Result:");
print p("Found $count events for you");

if (!$fname) {
  print b("You have not supplied your first name");
  &bail("no fname");
}

if (!$lname) {
  print b("You have not supplied your last name");
  &bail("no lname");
}

if (!$state) {
  print b("You have not supplied a state");
  &bail("no state");
}

if (!$sex) {
  print b("You have not supplied your gender");
  print i("  Go BACK, change and submit again");
  exit;
} 

if (!$email) {
  print b("You have not supplied your email");
  print i("  Go BACK, change and submit again");
  exit;
}

# $count = 0;
for ($i=0; $i<=$n; $i++) {
  if ($ms[$i] ne "none") { 
    $count++;
    print p("   $count: MS \n");
    if ($sex ne "m") { &bail("wrong sex"); }
  }
  if ($ws[$i] ne "none") { 
    $count++;
    print p("   $count: WS \n");
    if ($sex ne "f") { &bail("wrong sex"); }
  }

  if ($md[$i] ne "none") { 
    $count++;
    print p("   $count: MD w/ $dp[$i]\n");
    if ($sex ne "m") { &bail("wrong sex"); }
  }

  if ($wd[$i] ne "none") { 
    $count++;
    print p("   $count: WD w/ $dp[$i]\n");
    if ($sex ne "f") { &bail("wrong sex"); }
  }

  if ($xd[$i] ne "none") { 
    $count++;
    print p("   $count: XD w/ $xp[$i]\n");
  }
}

print b("Now sending registration off....");
print hr, "-Peter Teuben.";
print end_html;


#  email me  when success

system("mail -s \"COLLOPEN2004 $fname $lname\" teuben\@astro.umd.edu,teuben\@wam.umd.edu < /tmp/dcopen.tmp.$$");
#unlink "/tmp/dcopen.tmp.$$";


