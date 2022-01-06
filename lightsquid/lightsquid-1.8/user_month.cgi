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

use File::Basename;
push( @INC, ( fileparse($0) )[1] );

use CGI;
require "lightsquid.cfg";
require "common.pl";

$co = new CGI;

$year  = $co->param('year');
$month = $co->param('month');
$user  = $co->param('user');
$mode  = $co->param('mode');

print "Content-Type: text/html\n\n";

InitTPL("user_month",$co->param('tpl'));

$workperiod = "$MonthName[$month] $year";
ReplaceTPL( WORKPERIOD, $workperiod );

$week_id=0;
$week_date=$date;

$average = 0;
$days    = 0;
$filter  = "$year$month";
@daylist = sort glob("$reportpath/$filter*");
@daylist = reverse @daylist;
foreach $daypath (@daylist ) {
    open FF, "<$daypath/.total";
    $tmp  = <FF>; $size = <FF>;
#    $daypath =~ m/(\d\d\d\d)(\d\d)(\d\d)/;

    $daypath  =~ m#$reportpath/(.*)#;
    $date=$1;
    $date =~ m/^(\d\d\d\d)(\d\d)(\d\d)/;
    $urldate="year=$1&month=$2&day=$3";
    
    $printdate= GetTxtDate($date);

    $weekday  = GetWeekDayDate($date);
    
    $weeksumtpl="";
    if ($weekday == 0) {
      $week_id++;
      $weeksumtpl="##WEEKSUM$week_id##";
      $weeksum[$week_id]=0;
    }

    $size="?";		

    while (<FF>) {
        ( $user_, $size_, $hit ) = split;
	next if ( $user_ ne  $user );
	$cumulative += $size_; 
	$size        = $size_;
    } 
    
    $weeksum[$week_id]+=$size if ($size ne "?");
    
    $printsize       =($size eq "?")?"?":FineDec($size);
    $printcumulative =FineDec($cumulative);

    $daydate_L =URLEncode("user_detail.cgi?$urldate&user=$user");  $daydate_B ="$printdate";

    $dayattr = ($weekday & 1 )?$hTPLVARIABLE{oddattr}:$hTPLVARIABLE{evenattr};
    $dayattr = $hTPLVARIABLE{sundayattr}   if ($weekday  == 0);
    $dayattr = $hTPLVARIABLE{saturdayattr} if (($weekday == 6) && ($weekendmode eq "both"));

	    
    $oversizeattr=(($perusertrafficlimit>0) && ($size > $perusertrafficlimit))?$hTPLVARIABLE{oversizedattr}:$hTPLVARIABLE{nooversizedattr};
	
    
    $tmp=$hTPL{day};
    $tmp=~s/##DAYDATE_L##/$daydate_L/;
    $tmp=~s/##DAYDATE_B##/$daydate_B/;
    $tmp=~s/##DAYBYTES##/$printsize/;
    $tmp=~s/##DAYCUMULATIVE##/$printcumulative/;
    $tmp=~s/##WEEKSUM##/$weeksumtpl/;
    $tmp=~s/##DAYATTR##/$dayattr/;
    $tmp=~s/##OVERSIZEATTR##/$oversizeattr/;
    $tpl{day} .= $tmp;
			      	        

    $days++;
    close FF;
}



$graphurl_L=URLEncode("graph.cgi?year=$year&month=$month&mode=user&user=$user");
$graphurl_B="##MSG_GRAPH_LINK##";

ReplaceTPL_URL(GRAPHURL,$graphurl_L,$graphurl_B);

ReplaceTPL(USER,$user);
ReplaceTPL(WORKPERIOD,$workperiod);
ReplaceTPL(TOTALBYTES,$printcumulative);

for ($i=0;$i<=$week_id;$i++) {
  ReplaceTPL("WEEKSUM$i",FineDec($weeksum[$i]));
}

ApplyTPL();
PrintTPL();

__END__
2005-10-06 ADD : Initial release
2006-06-28 ADD : &tpl= support
2006-07-01 ADD : RIC, add sunday highlight
