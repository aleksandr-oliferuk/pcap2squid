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

# Show mont user list

print "Content-Type: text/html\n\n";

use File::Basename;
push (@INC,(fileparse($0))[1]);

use CGI;
require "lightsquid.cfg";
require "common.pl";


$co=new CGI;

$year =$co->param('year');
$month=$co->param('month');
InitTPL("month_detail",$co->param('tpl'));

if ($month ne "all") {
  $workperiod="$MonthName[$month] $year";
  $filter="$year$month";
  $mode="month";
  $modename="##MSG_MONTH##";
} else {
  $workperiod="##MSG_WHOLE## $year ##MSG_YEAR##";
  $filter="$year";
  $mode="year";
  $modename="##MSG_YEAR##";
}

@daylist=glob("$reportpath/$filter*");

foreach $daypath (sort @daylist) {
  open FF,"<$daypath/.total";
  
  GetRealName($daypath,"?"); # init realname for day
  
  $totaluser=<FF>;chomp $totaluser;$totaluser=~s/^user: //;
  $totalsize=<FF>;chomp $totalsize;$totalsize=~s/^size: //;

  $grandtotalsize+=$totalsize;
  $grandtotaluser+=$totaluser;

  while (<FF>) {

    ($user,$size,$hit)=split;

    $h{$user}{size}+=$size;
    $h{$user}{hit}+=$hit;
  }  
  close FF;
}
# 

$cummulative=0;
$N=0;
foreach $user (sort {$h{$b}{size}<=>$h{$a}{size}} keys 	%h) {
    $N++;	
    $percent  =sprintf("%2.1f",int($h{$user}{size}*1000/$grandtotalsize)/10);
    $printhit =FineDec($h{$user}{hit});
    $printsize=FineDec($h{$user}{size});

    $cummulative+=$h{$user}{size};
    $printcummulativesize=FineDec($cummulative);



    $timeurl_L=URLEncode("user_time.cgi?year=$year&month=$month&user=$user&mode=$mode");
    $timeurl_B="##MSG_TIME_LINK##";
    
    $graphurl_L=URLEncode("graph.cgi?year=$year&month=$month&mode=user&user=$user");
    $graphurl_B="##MSG_GRAPH_LINK##";

    $userurl_L=URLEncode("user_detail.cgi?year=$year&month=$month&user=$user&mode=$mode");
    $userurl_B="$user";

    $realname=GetRealName($daypath,$user);
  
    $usermonthurl_L=URLEncode("user_month.cgi?year=$year&month=$month&user=$user");
    $usermonthurl_B="##MSG_USER_MONTH##";

    $rowattr = ($N & 1)?$hTPLVARIABLE{oddattr}:$hTPLVARIABLE{evenattr};

    $tmp=$hTPL{user};
    $tmp=~s/##USERNUM##/$N/;
    $tmp=~s/##USERURL_L##/$userurl_L/;
    $tmp=~s/##USERURL_B##/$userurl_B/;
    $tmp=~s/##TIMEURL_L##/$timeurl_L/;
    $tmp=~s/##TIMEURL_B##/$timeurl_B/;
    $tmp=~s/##GRAPHURL_L##/$graphurl_L/;
    $tmp=~s/##GRAPHURL_B##/$graphurl_B/;
    $tmp=~s/##USERMONTHURL_L##/$usermonthurl_L/;
    $tmp=~s/##USERMONTHURL_B##/$usermonthurl_B/;
    $tmp=~s/##REALNAME##/$realname/;
    $tmp=~s/##USERCONNECT##/$printhit/;
    $tmp=~s/##USERBYTES##/$printsize/;
    $tmp=~s/##USERPERCENT##/$percent/;
    $tmp=~s/##ALLUSERTOTAL##/$printcummulativesize/;
    $tmp=~s/##ROWATTR##/$rowattr/;
    $tpl{user} .= $tmp;
}
		
ReplaceTPL(DATE,$workperiod);
ReplaceTPL(WHOLEPERIOD,$modename);

ApplyTPL();
HideTPL("timereport")  if ($timereport == 0);
HideTPL("graphreport") if (($graphreport == 0) || ($mode ne "month"));
HideTPL("monthreport") if ($mode ne "month");
HideTPL("realname")       if ($userealname == 0);
PrintTPL();

__END__
2004-12-18     : init version
2004-12-22     : add cummulative sum column
2005-01-31     : Add link User -> user month stat
2005-04-17 ADD : TemplateEngine
2005-04-19 ADD : Add skip .name: fields in .total
2005-04-25 ADD : now support YEAR report, tpl fix.
2005-05-01 ADD : time report support
2005-08-30 ADD : Color Flipper
2005-10-02 ADD : _L,_B
2005-10-06 ADD : user_month report link
2005-11-07 ADD : URLEncode
2006-06-28 ADD : &tpl= support

