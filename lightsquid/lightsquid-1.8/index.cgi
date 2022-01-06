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

require "lightsquid.cfg";
require "common.pl";
use CGI;
use CGI::Carp qw (fatalsToBrowser);

$co=new CGI;

($tmp,$tmp,$tmp,$tmp,$mon,$tmpyear) = localtime;

$year =$co->param('year' ) || ($tmpyear+1900);
$month=$co->param('month') || sprintf("%02d",$mon+1);

InitTPL("index",$co->param('tpl'));

if ($month ne "all") {
    $workperiod=" $MonthName[$month] $year";
} else {
    $workperiod=" $year ";
    $month="";
}

#----------------------------------- find defined month & years
@days=sort glob("$reportpath/*");


foreach $day (@days) {
    if ($day =~ m/(\d\d\d\d)(\d\d)(\d\d)/) { 
	$yearhash {$1}=1;
    }    
    if ($day =~ m/$year(\d\d)(\d\d)/) { 
	$monthhash{$1}=1;
    }    
}

##  YEAR row ______________________________________________
@yearlist=sort keys %yearhash;
$yearcnt=$#yearlist+1;
if ($yearcnt == 0) {
    ErrPrintConfig("report folder '$reportpath' not contain any valid data! Please run lightparser.pl (and check 'report' folder content)");
    print "<hr>folder content:<br>";
    foreach $file (@days) {
        print "$file<br>";
    }

    exit;

}

$yearspan=12/$yearcnt;

foreach $yearname (sort keys %yearhash) {
    $yearselected=($yearname eq $year)?qq{$hTPLVARIABLE{yearselected}}:""; 
    $yearurl_L= qq(index.cgi?year=$yearname&month=all);
    $yearurl_B= qq($yearname);

    $yearoptionselected = ($yearname eq $year)?" selected":"";
    $yearoption = qq(<option$yearoptionselected>$yearname</option>);

    $tmp=$hTPL{year};
    $tmp=~s/##YEARCOLSPAN##/$yearspan/;
    $tmp=~s/##YEARSELECTED##/$yearselected/;
    $tmp=~s/##YEARURL_L##/$yearurl_L/;
    $tmp=~s/##YEARURL_B##/$yearurl_B/;
    $tmp=~s/##YEAROPTION##/$yearoption/;  
    $tpl{year} .= $tmp;
}

##  MONTH row ____________________________________________

$monthtmp="01";
for ($i=1;$i<=12;$i++) {
    $monthselected=($monthtmp eq $month)?qq{$hTPLVARIABLE{monthselected}}:"";

    $monthurl_L=(defined $monthhash{$monthtmp} )?"index.cgi?year=$year\&month=$monthtmp":"";
    $monthurl_B="$monthtmp";
    
    $monthtmp++;

    $tmp=$hTPL{month};
    $tmp=~s/##MONTHSELECTED##/$monthselected/;
    $tmp=~s/##MONTHURL_L##/$monthurl_L/;
    $tmp=~s/##MONTHURL_B##/$monthurl_B/;
    $tpl{month} .= $tmp;
}

## --

@days=sort glob("$reportpath/$year$month*"); @days=reverse @days;

foreach $daypath (@days) {
    open FF,"<$daypath/.total" || MyDie("can't open file $daypath/.total<br>"); 
    $user=<FF>;chomp $user;$user=~s/^user: //;
    $size=<FF>;chomp $size;$size=~s/^size: //;
    close FF;

    $overuser=GetFeatures($daypath,"overuser","?");
    $cachehit=GetFeatures($daypath,"cachehit%","?");
   
    $cachehittotal+=$cachehit;
      
    $daypath =~ m#$reportpath/(.*)#;
    $date=$1;

    $weekday=GetWeekDayDate($date);

    $average=($user != 0)?int($size/$user):0;

    $totalsize+=$size;
    $totalaverage+=$average;
    $totaluser+=$user;
    $totaloveruser+=$overuser;

    $printaverage=FineDec($average);
    $printsize   =FineDec($size);
    $printdate   =GetTxtDate($date);


    $date =~ m/^(\d\d\d\d)(\d\d)(\d\d)/;
   
    $urldate="year=$1&month=$2&day=$3";

    $daydate_L ="day_detail.cgi?$urldate";  $daydate_B ="$printdate";
    $daygroup_L="group_detail.cgi?$urldate";$daygroup_B="##MSG_GRP##";
   
    $overuser_L=(($overuser eq "?") || ($overuser == 0))?"":"$daydate_L&oversize=1";
    $overuser_B="$overuser"; 

    $dayattr = ($weekday & 1 )?$hTPLVARIABLE{oddattr}:$hTPLVARIABLE{evenattr};
    $dayattr = $hTPLVARIABLE{sundayattr} if ($weekday == 0);
    $dayattr = $hTPLVARIABLE{saturdayattr} if (($weekendmode eq "both") && ($weekday == 6));;

    $tmp=$hTPL{day};
    $tmp=~s/##DAYDATE_L##/$daydate_L/;
    $tmp=~s/##DAYDATE_B##/$daydate_B/;
    $tmp=~s/##DAYGROUP_L##/$daygroup_L/;
    $tmp=~s/##DAYGROUP_B##/$daygroup_B/;
 
    $tmp=~s/##DAYUSERS##/$user/;

    $tmp=~s/##DAYOVERUSERS_L##/$overuser_L/;
    $tmp=~s/##DAYOVERUSERS_B##/$overuser_B/;

    $tmp=~s/##DAYBYTES##/$printsize/;
    $tmp=~s/##DAYAVERAGE##/$printaverage/;
    $tmp=~s/##DAYCACHEHIT##/$cachehit/;
    
    $tmp=~s/##DAYATTR##/$dayattr/;
    
    $tpl{day} .= $tmp;
}

$days=($#days+1);
if ($days==0) {$days=0.00000001;} #;-), dirty hack

$printtotalsize       = FineDec($totalsize);
$printtotalaverage    = FineDec(int($totalaverage/$days));
$printaveragehit      = sprintf ("%3.2f",$cachehittotal/$days);
$printaverageuser     = int($totaluser/$days);
$printaverageoveruser = int($totaloveruser/$days);

$month="all" if ($month eq "");
$printtotalsize_L = "month_detail.cgi?year=$year&month=$month";
$printtotalsize_B = "$printtotalsize";

ReplaceTPL(WORKPERIOD,$workperiod);
ReplaceTPL(TOTAL_L,$printtotalsize_L);
ReplaceTPL(TOTAL_B,$printtotalsize_B);
ReplaceTPL(TOTALAVERAGE,$printtotalaverage);
ReplaceTPL(AVERAGEHIT,$printaveragehit);
ReplaceTPL(USERAVERAGE,$printaverageuser);
ReplaceTPL(OVERUSERAVERAGE,$printaverageoveruser);

ReplaceTPL_URL(  TOP_MONTH,"topsites.cgi?year=$year&month=$month&mode=month",    "##MSG_MONTH##");
ReplaceTPL_URL(  TOP_YEAR ,"topsites.cgi?year=$year&month=$month&mode=year" ,    "##MSG_YEAR##");
ReplaceTPL_URL(TOTAL_MONTH,"month_detail.cgi?year=$year&month=$month",           "##MSG_MONTH##");
ReplaceTPL_URL(TOTAL_YEAR ,"month_detail.cgi?year=$year&month=all",              "##MSG_YEAR##");
ReplaceTPL_URL(GROUP_MONTH,"group_detail.cgi?year=$year&month=$month&mode=month","##MSG_MONTH##");
ReplaceTPL_URL(GROUP_YEAR ,"group_detail.cgi?year=$year&mode=year",              "##MSG_YEAR##");
ReplaceTPL_URL(MONTH_GRAPH,"graph.cgi?year=$year&month=$month&mode=month",       "");

ApplyTPL();

HideTPL("monthtop") if ($month eq "all");
HideTPL("oversize") if ($showoversizelink == 0); 
HideTPL("group")    if ($showgrouplink == 0);
HideTPL("graph")    if ($graphreport == 0);

PrintTPL();

__END__
2004-09-01 FIX : show only month for current year ...
2004-12-18 ADD : if MODE == MONTH -> totalsize - link month_detail.cgi
2005-01-02 ADD : default - current year
2005-04-14 ADD : check empty report folder!
2005-04-17 ADD : Template Engine 
2005-04-19 ADD : error check, add .oversize & .cachehit field support 
2005-04-21 ADD : Template Engine, HIDE function
2005-04-22 ADD : move cahchehit -> .features
2005-05-01 ADD : TopSites & Total report box
2005-08-29 ADD : color flipper & sunday color,
2005-09-06 ADD : colorselected now defined in TPL file
2005-09-15 ADD : if month="all" then not show MONTH table at top, (also changed TPL file)
2005-10-01 ADD : now all URL in TPL (_L,_B), TPL also changed ;-)
2006-06-28 ADD : die -> MyDie
2006-06-28 ADD : &tpl= support
2006-09-13 ADD : error to browser
