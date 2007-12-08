#! /usr/bin/perl -w
#
#  cgi-bin/mbgg.pl:    process a badminton form and email 
#

use CGI qw(:standard);

$version = "19-apr-2005";
$q = CGI::new();
$late = 1;

sub bail (msg) {
  print i("  Please go BACK using your browser, fix your form, and click on Register again");
  exit ;
}

$fname     = $q->param("fname");
$lname     = $q->param("lname");
$address   = $q->param("address");
$city      = $q->param("city");
$state     = $q->param("state");
$zip       = $q->param("zip");
$dphone    = $q->param("dphone");
$ephone    = $q->param("ephone");
$cphone    = $q->param("cphone");
$email     = $q->param("email");

$player[0]  = $q->param("player1");
$event[0]   = $q->param("event1");
$age[0]     = $q->param("age1");
$partner[0] = $q->param("partner1");

$player[1]  = $q->param("player2");
$event[1]   = $q->param("event2");
$age[1]     = $q->param("age2");
$partner[1] = $q->param("partner2");

$player[2]  = $q->param("player3");
$event[2]   = $q->param("event3");
$age[2]     = $q->param("age3");
$partner[2] = $q->param("partner3");

$player[3]  = $q->param("player4");
$event[3]   = $q->param("event4");
$age[3]     = $q->param("age4");
$partner[3] = $q->param("partner4");

$player[4]  = $q->param("player5");
$event[4]   = $q->param("event5");
$age[4]     = $q->param("age5");
$partner[4] = $q->param("partner5");

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
print MAIL "cphone=",$cphone,"\n";
print MAIL "email=",$email,"\n";
#
$count = 0;

if ($player[0] ne "") { $count++; }
print MAIL "player1=", $player[0],  "\n";
print MAIL "event1=",  $event[0],  "\n";
print MAIL "age1=",    $age[0],    "\n";
print MAIL "partner1=",$partner[0],"\n";

if ($player[1] ne "") { $count++; }
print MAIL "player2=", $player[1],  "\n";
print MAIL "event2=",  $event[1],  "\n";
print MAIL "age2=",    $age[1],    "\n";
print MAIL "partner2=",$partner[1],"\n";

if ($player[2] ne "") { $count++; }
print MAIL "player3=", $player[2],  "\n";
print MAIL "event3=",  $event[2],  "\n";
print MAIL "age3=",    $age[2],    "\n";
print MAIL "partner3=",$partner[2],"\n";

if ($player[3] ne "") { $count++; } 
print MAIL "player4=", $player[3],  "\n";
print MAIL "event4=",  $event[3],  "\n";
print MAIL "age4=",    $age[3],    "\n";
print MAIL "partner4=",$partner[3],"\n";

if ($player[4] ne "") { $count++; } 
print MAIL "player5=", $player[4],  "\n";
print MAIL "event5=",  $event[4],  "\n";
print MAIL "age5=",    $age[4],    "\n";
print MAIL "partner5=",$partner[4],"\n";

#
print MAIL "players=",$count,"\n";

# !!  comments= must be the last one, some scripts use it as a trigger!!
print MAIL "comments=",$comments;
close MAIL;
chmod 0666,"/tmp/dcopen.tmp.$$";


####    report back to the form filler


print $q->header();
print hr, start_html;

print p("$fname, here is your 2005 MBGG Registration Result:");
print p("Found $count players for you");

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

for ($i=0; $i<=$count; $i++) {
  if ($player[$i] ne "") { 
    # print p("player=$player[$i] event=$event[$i] age=$age[$i]");
    if ($event[$i] eq "JA") {
      if ($age[$i] eq "") {
         &bail("no age for $player[$i]");
      }
    }
    if ($event[$i] eq "JB") {
      if ($age[$i] eq "") {
         &bail("no age for $player[$i]");
      }
    }
  }
}

print b("Now sending registration off....");
print p("the deadline for entry forms is: tuesday April 26, 2005");
print p("Anything after that you need to get in touch with Peter via email");
print p("and get a confirmation, or you should consider your entry invalid");
print p(" ");

print hr, "-Peter Teuben.";
print end_html;


#  email me  when success

system("mail -s \"MBGG2005 $fname $lname\" teuben\@astro.umd.edu,teuben\@wam.umd.edu,teuben58\@comcast.net < /tmp/dcopen.tmp.$$");
#unlink "/tmp/dcopen.tmp.$$";


