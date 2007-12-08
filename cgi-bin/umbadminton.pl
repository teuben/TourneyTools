#! /usr/bin/perl -w
#
#  cgi-bin/umbadminton.pl:    process a badminton form and email 
#

use CGI qw(:standard);

$version = "14-sep-2003";
$q = CGI::new();

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
$tel       = $q->param("tel");
$sex       = $q->param("sex");
$email     = $q->param("email");
$ssn       = $q->param("ssn");
$type      = $q->param("type");

$comments    = $q->param("comments");

####    write report

#open(MAIL,"|mailx -s UMBADMINTON teuben\@astro.umd.edu");

$n = $#ms;

open(MAIL, ">/tmp/umbadminton.tmp.$$");
print MAIL "fname=",$fname,"\n";
print MAIL "lname=",$lname,"\n";
print MAIL "address=",$address,"\n";
print MAIL "city=",$city,"\n";
print MAIL "state=",$state,"\n";
print MAIL "zip=",$zip,"\n";
print MAIL "phone=",$tel,"\n";
print MAIL "sex=",$sex,"\n";
print MAIL "ssn=",$ssn,"\n";
print MAIL "type=",$type,"\n";
print MAIL "email=",$email,"\n";
#  comments= must be the last one, some scripts use it as a trigger!!
print MAIL "comments=",$comments;
close MAIL;
chmod 0666,"/tmp/umbadminton.tmp.$$";


####    report back to the form filler


print $q->header();
print hr, start_html;
print p("$fname, thanks for registration:");

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

print b("Now sending registration off....");
print hr, "-Peter Teuben.";
print end_html;


#  email me  when success

system("mail -s \"UMBADMINTON $fname $lname\" teuben\@astro.umd.edu  < /tmp/umbadminton.tmp.$$");
unlink "/tmp/umbadminton.tmp.$$";


