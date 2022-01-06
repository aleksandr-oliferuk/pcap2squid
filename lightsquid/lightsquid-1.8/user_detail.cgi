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

$year =$co->param('year');
$month=$co->param('month');
$day  =$co->param('day');
$user =$co->param('user');
$mode =$co->param('mode');

InitTPL("user_detail",$co->param('tpl'));

if      ($mode eq "month") {
  $workperiod="##MSG_WHOLE## ##MSG_MONTH## - $year $MonthName[$month]";
  $mask = "$year$month";
} elsif ($mode eq "year") {
  $workperiod="##MSG_WHOLE## ##MSG_YEAR## - $year";
  $mask = "$year";
} else {
  $workperiod="$day $MonthName[$month] $year";
  $mask = "$year$month$day";
  $mode = "day"
}

@datelist=sort glob "$reportpath/$mask*";

$calculatedtotal=0;
foreach $workday (sort @datelist) {
  GetRealName($workday,"?"); 
  GetGroup($workday);
  
  open FF,"<$workday/$user" || MyDie("can't open $daypath/$user");
  $totalsize=<FF>;chomp $totalsize;$totalsize=~s/total: //;

  while (<FF>) {
    ($site,$size,$hit)=split;
    $h{$site}{hit} +=$hit;
    $h{$site}{size}+=$size;
    $calculatedtotal+=$size
  }  
  close FF;
}


#---------
# check - exist current user in .bigfiles
# only in DAY mode
if ($mode eq "day") {
  open FF,"<$reportpath/$year$month$day/.bigfiles";

  while (<FF>) {
    ($buser,$btime,$bsize,$blink)=split;
    $flagbigfiles=1 if ($buser eq $user);
  }	     
  close FF;
}  

if ($flagbigfiles) {
    $bigfiles_B="##MSG_BIG_FILES_USER##";
    $bigfiles_L="bigfiles.cgi?year=$year&month=$month&day=$day&user=$user";
}
#---------


$N=0;
$total=0;
foreach $site (sort {$h{$b}{size} <=> $h{$a}{size}} keys %h)  {
  $N++;
  $hit=$h{$site}{hit};
  $size=$h{$site}{size};
  $total+=$size;
  $percent   =sprintf("%2.1f",int($size*1000/$calculatedtotal)/10);
  $printhit  =FineDec($hit);
  $printsize =FineDec($size);
  $printtotal=FineDec($total);

  $siteurl_L="http://$site";
  $siteurl_B="$site";

  $rowattr = ($N & 1)?$hTPLVARIABLE{oddattr}:$hTPLVARIABLE{evenattr};
  
  $tmp=$hTPL{site};
  $tmp=~s/##NUM##/$N/;
  $tmp=~s/##SITEURL_L##/$siteurl_L/g;
  $tmp=~s/##SITEURL_B##/$siteurl_B/g;
  $tmp=~s/##SITECONNECT##/$printhit/;
  $tmp=~s/##SITEBYTES##/$printsize/;
  $tmp=~s/##SITETOTAL##/$printtotal/;
  $tmp=~s/##SITEPERCENT##/$percent/;
  $tmp=~s/##ROWATTR##/$rowattr/;
  $tpl{site} .= $tmp;
  
}

$printtotalsize=FineDec($calculatedtotal);
	
$printuser="$user";
$printuser .= " (".GetRealName("?",$user).")" if ($userealname != 0);
      
ReplaceTPL(USER,$printuser);
ReplaceTPL(TOTAL,$printtotalsize);
ReplaceTPL(WORKPERIOD,$workperiod);
ReplaceTPL(GROUP,(defined $hGroup{$user})?"$hGroupName{$hGroup{$user}}":"?");
  

ReplaceTPL_URL(TIMEURL,"user_time.cgi?year=$year&month=$month&day=$day&user=$user","##MSG_TIME_LINK##");
ReplaceTPL_URL(BIGFILESURL,$bigfiles_L,$bigfiles_B);
      
ApplyTPL();
HideTPL("timereport") if (($timereport == 0) || ($mode ne "day"));
HideTPL("group")      if ($showgrouplink == 0);
PrintTPL();

__END__
2004-11-09 ADD : Total column, commulative total
2004-12-18 ADD : Показываем дату и имя пользователя в скрипте
2005-01-31 ADD : New Param (month=1) if, then show whole month user report, else only selected day
2005-04-14 FIX : in CONNECT column displayed size column
2005-04-17 ADD : TemplateEngine
2005-04-25 ADD : mode=year
2005-05-01 ADD : time report link
2005-08-30 ADD : Color Flipper
2005-09-08 ADD : if user exist in .bigfiles file, on top of report MESSAGE with link
2005-10-02 ADD : _L,_B
2005-11-01 ADD : Group name in header
2006-06-28 ADD : die -> MyDie
2006-06-28 ADD : &tpl= support
2006-09-13 ADD : add &user= in bigfiles URL
2006-11-20 ADD : /g for ##SITEURL_B## & ##SITEURL_L##, my need in some cases