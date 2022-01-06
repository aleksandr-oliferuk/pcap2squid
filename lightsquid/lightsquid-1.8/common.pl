#!/usr/bin/perl
#
# LightSquid Project (c) 2004-2005 Sergey Erokhin aka ESL
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# detail see in gnugpl.txt

use Time::Local;

#month name
@MonthName = (00,
              "##MSG_MONTH01##","##MSG_MONTH02##","##MSG_MONTH03##","##MSG_MONTH04##",
              "##MSG_MONTH05##","##MSG_MONTH06##","##MSG_MONTH07##","##MSG_MONTH08##",
              "##MSG_MONTH09##","##MSG_MONTH10##","##MSG_MONTH11##","##MSG_MONTH12##",
             );
							

# ------------------------------------------- common funcion
sub FineDec($)
{
  my $val=shift;
  my $ret=$val;
  
  if ($DecOutType eq "class") {
    if    ($val>=1000*1024*1024) {$ret=sprintf("%3.1f G",$val/(1024*1024*1024));}
    elsif ($val>=     1024*1024) {$ret=sprintf("%3.1f M",$val/(     1024*1024));}
    else  {                       $ret=$val;}
  }
  $ret =~ s/(\d{1,3})(?=(?:\d\d\d)+(?!\d))/$1$decdelimiter/gx;
  return $ret;
}

sub GetTxtDate($) {
  my $date = shift;
  $date =~ m/^(\d\d\d\d)(\d\d)(\d\d)/;
  return "$3 $MonthName[$2] $1";
}

sub GetWeekDayDate($) {
  my $date = shift;
  $date =~ m/^(\d\d\d\d)(\d\d)(\d\d)/;
  my $wday= (localtime(timelocal(0,0,0,$3,$2-1,$1)))[6];
  return $wday;
}

$hFeatures{0}=1;
# -------------------------------------------- .features support
sub GetFeatures($$$) {
  my $path=shift;
  my $featuresname=shift;
  my $featuresdefault=shift;
  my $fname;
  my $fval;
  
  unless (defined $hFeatures{$path}{__init__}) {
    open Fftr,"<$path/.features";
    while (<Fftr>) {
      chomp;
      ($fname,$fval)=split /\s/,$_,2;
      $fname =~ s/://;
      $hFeatures{$path}{$fname}=$fval;
    }
    close Fftr;
    $hFeatures{$path}{__init__}=1;
  }
  $fval=(defined $hFeatures{$path}{$featuresname})?$hFeatures{$path}{$featuresname}:$featuresdefault;
  return $fval;
}

# -------------------------------------------- .realname support
#read .realname file
#in : FilePath, UserID
#out: realname, or ? if not userid in file
sub GetRealName($$) {
  my $path=shift;
  my $userid=shift;
  my $fuid;
  my $fullname;
  my $fval;
  
  unless (defined $hRealName{$path}{__init__}) {
    open Fftr,"<$path/.realname";
    while (<Fftr>) {
      next if (m/^#/);
      next if (m/^\s+$/);
      chomp;
      ($fuid,$fullname)=split /\s/,$_,2;
      $fuid =~ s/://;
      $hRealName{$fuid}=$fullname;
    }
    close Fftr;
    $hRealName{__init__}=1;
  }
  $fval=(defined $hRealName{$userid})?$hRealName{$userid}:"?";
  return $fval;
}

# -------------------------------------------- Templates support
$RequiredTPLVersion="1.7";


sub InitTPL($) {
 InitLANG("eng");
 InitLANG($lang);
 my $tmp=$/;
 my $tplname=shift;
 my $newtpl=shift;

 CheckNewTPL($newtpl);

 undef $/;
 open F,"<$tplpath/$templatename/$tplname.html" or MyDie("can't open template file $tplpath/$templatename/$tplname.html - $!\n");
   $template=<F>;
 close F;
 
 #check version
 $template =~ m/<!-- LightSquid TPL v(.*) -->/;
 if ($RequiredTPLVersion > $1) {
   print "<HR>WARNING!!! ::  Your Template ($templatename) version: $1 , Required $RequiredTPLVersion. Update template. <HR>";
 }

 while ($template =~ s/<!--\s\[\[\s(.*?)\sstart-->(.*?)<!--\s\]\]\s\1\send-->/<!--###tpl_$1###-->/s) {
  $hTPL{$1}=$2;
 }

 #get VARIABLEs from TPL
 while ($template =~ s/<!--\s?VARIABLE\s+(.*?)\s+(.*?)\s+-->//s) {
  $hTPLVARIABLE{$1}=$2;
 }

 $/=$tmp;
 
 my $meta=qq(<META HTTP-EQUIV="REFRESH" CONTENT="600">\n).
          qq(<META HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE">\n).
          qq(<META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">\n).
          qq(<META HTTP-EQUIV="CACHE-CONTROL" CONTENT="post-check=0,pre-check=0">\n).
          qq(<META HTTP-EQUIV="CACHE-CONTROL" CONTENT="max-age=0">\n).
          qq(<meta http-equiv="expires" content="0">\n).
          qq(<meta http-equiv="Last-Modified" content=").gmtime(time).qq( GMT">\n);
 ReplaceTPL(META,$meta);
}

sub CheckNewTPL($) {
 my $newtpl=shift;

 if ($newtpl) {
   $templatename=$newtpl;
   ReplaceSTRING(".cgi\\?",".cgi\?tpl=$newtpl\&");
 }
}

sub ReplaceSTRING($$) {
  my $name=shift;
  my $value=shift;
  $hTPLreplaceString{$name}=$value;
}

sub ReplaceTPL($$) {
  my $name=shift;
  my $value=shift;
  $hTPLreplace{$name}=$value;
}

sub ReplaceTPL_URL($$$) {
  my $name=shift;
  my $value_L=shift;
  my $value_B=shift;
  $hTPLreplace{"$name"."_L"}=$value_L;
  $hTPLreplace{"$name"."_B"}=$value_B;
}

sub ApplyTPL() {
  my $tpl;
  
  #replace repeatable block 
  foreach $tpl (keys %hTPL) {  
    $template =~ s/(<!--###tpl_$tpl###-->)/$tpl{$tpl}/;
  }

  $template =~ s/##COPYRIGHT##/$COPYRIGHT/;

  #replace string
  foreach $name (keys %hTPLreplace) {
    $template =~ s/##$name##/$hTPLreplace{$name}/gs;
  }

  #replace string pass 2
  foreach $name (keys %hTPLreplace) {
    $template =~ s/##$name##/$hTPLreplace{$name}/gs;
  }

  foreach $name (keys %hTPLreplaceString) {
    $template =~ s/$name/$hTPLreplaceString{$name}/gs;
  }

}

sub HideTPL($) {
    #remove section <!-- HIDE $hidename start --> DELETED SECTION <!-- HIDE $hidename end -->
    my $hidename=shift;
    $template =~ s/<!--\sHIDE $hidename\sstart\s?-->.*?<!--\sHIDE $hidename\send\s?-->//gs;
}

sub PrintTPL() {
    
    #delete EMPTY url link (href="")
    $template =~ s/<a\s+href=\"\">(.*?)<\/a>/$1/gi;

    #delete not used HIDE field
    $template =~ s/<!--\sHIDE \S+\sstart\s?-->//gs;
    $template =~ s/<!--\sHIDE \S+\send\s?-->//gs;

    #delete TPL version
    $template =~ s/<!-- LightSquid TPL \S+ -->//gs;
    #delete empty spaces in lines
    $template =~ s/(^\s*$)//mg;
    print $template;
}

# -------------------------------------------- Localization support
sub InitLANG($) {
 my $langname=shift;
 my $lname;
 my $lvalue;
 open F,"<$langpath/$langname.lng" or MyDie("can't open language file $langpath/$langname.lng - $!\n");
 while (<F>) {
  chomp;
  next if (/^#/);
  ($lname,$lvalue)=split /=/,$_,2;
#  $hTPLreplace{$lname}=$lvalue;
  ReplaceTPL($lname,$lvalue);
 }
 close F;
}
## Group routines --------------------------------------
sub GetGroup($) {
    my $path=shift;
    my @a;
    open F,"<$path/.group";
    while (<F>) {
        next if (m/^#/);
        next if (m/^s+$/);
        chomp;
        ($username_,$groupid_,$groupname_)=split /\s+/,$_,3;
        if   ($showgroupid) { $hGroupName{$groupid_}="$groupid_. $groupname_" }
	else                { $hGroupName{$groupid_}="$groupname_" };
        $hGroup{$username_}=$groupid_;
    }
    close F;
}

sub GetGroupFile($) {
    my $path=shift;
    my @a;
    open F,"<$path/.group";
    while (<F>) {
        next if (m/^#/);
        next if (m/^s+$/);
        chomp;
        ($username_,$groupid_,$groupname_)=split /\s+/,$_,3;
        if   ($showgroupid) { $hGroupName{$groupid_}="$groupid_.  $groupname_" }
	else                { $hGroupName{$groupid_}="$groupname_" };

        #esli v groupe est' etot chelovek to =1
        $hGroupByUser{$groupid_}{$username_}=1;

        #esli user whodit w gruppu, to hash =1;
        $hUserGroup{$username_}{$groupid_}=$groupid_;
    }
    close F;
    $hGroupName{$NotInGroupID}="$NotInGroupName";
    $hGroupName{$NotInGroupID}="$NotInGroupID. $NotInGroupName" if ($showgroupid);
}

#
$COPYRIGHT="<font size=\"-1\"><b><center><a href=\"http://lightsquid.sf.net\">LightSquid v1.8</a> (c) Sergey Erokhin AKA ESL</center></b></font>";

##-----------------------------------------------------
# Encoding and decoding. WebIn.pm
# (c) Dmitry  Koterov <koterov at cpan dot org>, http://www.dklab.ru
sub URLEncode { my ($s)=@_; $s=~s/([^;\/?:@&=+\$,A-Za-z0-9\-_.!~*'()])/sprintf("%%%02X",ord $1)/sge; return $s }
sub URLDecode { my ($s)=@_; $s=~tr/+/ /; $s=~s/%([0-9A-Fa-f]{2})/chr(hex($1))/esg; return $s }

sub ErrPrintConfig($) {
    my $msg=shift;
    print "<b>LigthSquid diagnostic.</b><br>";
    print "<b>Error :</b> <font color='RED'>$msg</font><br>";
    print "<b>Please check config file !</b><hr>";
    print "<table border=1>";
    print "<tr bgcolor='gray'><td><b>Variable</b></td><td><b>value</b></td></tr>";
    print "<tr><td>\$tplpatph<d><td>$tplpath</td></tr>";
    print "<tr><td>\$templatename<d><td>$templatename</td></tr>";
    print "<tr><td>\$langpatph<d><td>$langpath</td></tr>";
    print "<tr><td>\$langname<d><td>$lang</td></tr>";
    print "<tr><td>\$reportpath</td><td>$reportpath</td></tr>";
    print "<tr><td>Access to '$reportpath' folder</td><td><b><font color=";
    print ((-d "$reportpath")?"GREEN>yes":"RED>NO !!!!!!!!!!!!");
    print "<font></b></td></tr>";
    print "<tr><td>\$graphreport<d><td>$graphreport</td></tr>";
    print "</table>";
}

sub MyDie($) {
  my $msg=shift;
  ErrPrintConfig($msg);
  exit;
}

1;    
__END__
2005-06-06 ADD :: FineDec, add "class" output type
2005-08-29 ADD :: GetWeekDayDate, and use Time::Local
2005-10-01 ADD :: add ReplaceTPL_URL, & PrintTPL, and fix -w warning
2005-10-03 ADD :: Check TPL version. warning if < $RequiredTPLVersion
2005-11-21 ADD :: insert Group routines
2006-06-28 ADD :: better error handling, die replaced by MyDie.
2006-06-28 ADD :: &tpl= support
2006-11-20 ADD :: add $showgroupid support
