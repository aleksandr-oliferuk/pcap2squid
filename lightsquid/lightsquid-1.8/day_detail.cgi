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

print "Content-Type: text/html\n\n";

use File::Basename;
push (@INC,(fileparse($0))[1]);

use CGI;
require "lightsquid.cfg";
require "common.pl";


$co=new CGI;

#$year ="2004";
#$month="05";
#$day  ="01";
#$user ="#169";

$year      =$co->param('year');
$month     =$co->param('month');
$day       =$co->param('day');
$oversize  =$co->param('oversize');

InitTPL("day_detail",$co->param('tpl'));


$daypath="$reportpath/$year$month$day";

$workperiod="$day $MonthName[$month] $year";

($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat("$daypath");
($sec_,$min_,$hour_,$mday_,$mon_,$year_,$wday_,$yday_,$isdst_)=localtime($mtime);
$mon_++;$year_+=1900;

$worktmp=GetFeatures($daypath,"modification",sprintf("%02d:%02d",$hour_,$min_)." ::  $mday_ $MonthName[$mon_] $year_");

#forkaround for bug in version 1.7
$worktmp =~ m/(.*?\:\:\s+\S+)\s+(\S+)\s+(\S+)/;
if ($3 < 1900) {
  $preffix=$1;
  $year_=$3+1900;$month_=$2;
  if ($month_=~ m/MONTH(\d\d)/) {$month_=$1+1;} else {$month_=1;}
  $worktmp ="$preffix $MonthName[$month_] $year_";
}

$workperiod .= " (##MSG_UPDATE## :: $worktmp)" ;

$topsitesurl="topsites.cgi?year=$year&month=$month&day=$day";
$bigfilesurl="bigfiles.cgi?year=$year&month=$month&day=$day";

open FF,"<$daypath/.total";
$totaluser=<FF>;chomp $totaluser;$totaluser=~s/^user: //;
$totalsize=<FF>;chomp $totalsize;$totalsize=~s/^size: //;

$totalsize=1 if ($totalsize == 0);

$topsites_L="$topsitesurl";
$topsites_B="##MSG_TOP_SITES##";
$bigfiles_B="##MSG_BIG_FILES##";
if (-f "$daypath/.bigfiles") {
 $bigfiles_L="$bigfilesurl";
}

$overmsg="##MSG_OVERSIZE_HEAD## ".FineDec($perusertrafficlimit)." ##MSG_OVERSIZE_TAIL##";

GetGroup($daypath);

$N=0;
while (<FF>) {
  
  $N++;
  ($user,$size,$hit,$putpost)=split;


  next if ($oversize && ($size < $perusertrafficlimit));

  $percent     =sprintf("%2.1f",int($size*1000/$totalsize)/10);
  $printhit    =FineDec($hit);
  $printsize   =FineDec($size);
  $printputpost=FineDec($putpost);

  $putpostpercent=($putpost*100)/($size+1);
#  $printputpost .= " (".sprintf("%2.2f",$putpostpercent).")";

  $timeurl_L=URLEncode("user_time.cgi?year=$year&month=$month&day=$day&user=$user");
  $timeurl_B="##MSG_TIME_LINK##";

  $userurl_L=URLEncode("user_detail.cgi?year=$year&month=$month&day=$day&user=$user");
  $userurl_B="$user";

  $realname=GetRealName($daypath,$user);
#  $userurl_L =~ s/#/%23/;
  
  #no URLEncode here! # sign in url !!
  $usergroupurl_L="group_detail.cgi?year=$year&month=$month&day=$day#$hGroup{$user}";
  $usergroupurl_B=(defined $hGroup{$user})?"$hGroupName{$hGroup{$user}}":"?";

  $rowattr = ($N & 1)?$hTPLVARIABLE{oddattr}:$hTPLVARIABLE{evenattr};

  $overputpostattr=(($showputpost) && ($putpostpercent < $putpostwarninglevel))?$hTPLVARIABLE{putpostnormalattr}:$hTPLVARIABLE{putpostwarningattr};



  $tmp=$hTPL{user};
  $tmp=~s/##USERNUM##/$N/;
  $tmp=~s/##TIMEURL_L##/$timeurl_L/;
  $tmp=~s/##TIMEURL_B##/$timeurl_B/;
  $tmp=~s/##USERURL_L##/$userurl_L/;
  $tmp=~s/##USERURL_B##/$userurl_B/;
  $tmp=~s/##USERCONNECT##/$printhit/;
  $tmp=~s/##USERBYTES##/$printsize/;
  $tmp=~s/##USERPUTPOST##/$printputpost/;
  $tmp=~s/##USERPERCENT##/$percent/;
  $tmp=~s/##USERGROUPURL_L##/$usergroupurl_L/;
  $tmp=~s/##USERGROUPURL_B##/$usergroupurl_B/;
  $tmp=~s/##REALNAME##/$realname/;
  $tmp=~s/##ROWATTR##/$rowattr/;
  $tmp=~s/##OVERPUTPOSTATTR##/$overputpostattr/;

  $tpl{user} .= $tmp;

}

ReplaceTPL_URL(TOPSITESURL,$topsites_L,$topsites_B);
ReplaceTPL_URL(BIGFILESURL,$bigfiles_L,$bigfiles_B);
ReplaceTPL(DATE,$workperiod);
ReplaceTPL(OVERMSG,$overmsg);

ApplyTPL();
HideTPL("timereport") if ($timereport    == 0);
HideTPL("group")      if ($showgrouplink == 0);
HideTPL("overuser")   if ($oversize      == 0);
HideTPL("realname")   if ($userealname   == 0);
HideTPL("putpost")    if ($showputpost   == 0);

PrintTPL();

__END__
2004-12-18 ADD : Показываем дату и имя пользователя в скрипте
2005-04-14 ADD : usertrafficlimit support
2005-04-17 ADD : TemplateEngine
2005-05-01 ADD : Time Report Support
2005-08-30 ADD : Color Flipper
2005-10-01 ADD : _L,_B
2005-10-06 ADD : group column
2005-11-07 ADD : URLEncode for link
2006-06-28 ADD : &tpl= support
2006-07-05 ADD : PutPost added
2006-07-10 ADD : .features modification: parameter support
2007-01-10 FIX : fix for correct display update time broken in v1.7 (2007 -> 107)
