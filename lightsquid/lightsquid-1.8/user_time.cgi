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
InitTPL("user_time",$co->param('tpl'));

if      ($mode eq "month") {
  $workperiod="##MSG_WHOLE## ##MSG_MONTH## - $year $MonthName[$month]";
  $mask = "$year$month";
} elsif ($mode eq "year") {
  $workperiod="##MSG_WHOLE## ##MSG_YEAR## - $year";
  $mask = "$year";
} else {
  $workperiod="$day $MonthName[$month] $year";
  $mask = "$year$month$day";
}

#@datelist=sort glob "$reportpath/$mask*";
@datelist=glob "$reportpath/$mask*";

$calculatedtotal=0;
foreach $workday (sort @datelist) {
  GetRealName($workday,"?");
  open FF,"<$workday/$user" || MyDie("can't open $workday/$user");
  $totalsize=<FF>;chomp $totalsize;$totalsize=~s/total: //;

  while (<FF>) {
    ($site,$size,$hit,@hlog)=split;
    $h{$site}{hit}  +=$hit;
    $h{$site}{size} +=$size;
    $calculatedtotal+=$size;

    for ($h=0;$h<24;$h++) {
      ($ttime,$tsize)=split /-/,$hlog[$h];
      $hsitetime{$site}[$h]+=$tsize;
      $htime[$h]+=$ttime;
      $hsize[$h]+=$tsize;
    }
  }  
  close FF;
}

$tmp=$hTPL{site};
$tmp=~s/##URL##/##MSG_TOTAL##/;
$tmp=~s/##NUM##//;
$tmp=~s/##ROWATTR##/$hTPLVARIABLE{totalattr}/;

$HH="00";
$total=0;
for ($h=0;$h<24;$h++) {
  $size = sprintf("%.1f",$hsize[$h]/(1024*1024));
  $size = "." if (0 == $hsize[$h]);
  $total+=$hsize[$h];
  $tmp=~s/##T$HH##/$size/;
  $HH++;
}    

$printsize =FineDec($total);
$tmp=~s/##URLSIZE##/$printsize/;
$tpl{site} .= $tmp;

$tmptotal=$tmp;

$N=0;
$Color=0;
$total=0;

foreach $site (sort {$h{$b}{size} <=> $h{$a}{size}} keys %h)  {
  $N++;
  $HH="00";
  $size=$h{$site}{size};
  
  next if ($N > $usertimelimit);
  
  $printsize =FineDec($size);
  
  $tmp=$hTPL{site};
  $tmp=~s/##URL##/$site/;
  for ($h=0;$h<24;$h++) {
    $size = sprintf("%.1f",$hsitetime{$site}[$h]/(1024*1024));
    $size = "." if (0 == $hsitetime{$site}[$h]);
    $tmp=~s/##T$HH##/$size/;
    $HH++;
  }  

  $rowattr = (++$Color & 1)?$hTPLVARIABLE{oddattr}:$hTPLVARIABLE{evenattr};

  $tmp=~s/##NUM##/$N/;
  $tmp=~s/##URLSIZE##/$printsize/;
  $tmp=~s/##ROWATTR##/$rowattr/;
  $tpl{site} .= $tmp;

}

if ($N > $usertimelimit) {
  $HH="00";
  $tmp=$hTPL{site};
  $tmp=~s/##URL##/\.\.\./;
  $ttt="...";
  for ($h=0;$h<24;$h++) {
    $tmp=~s/##T$HH##/$ttt/;
    $HH++;
  }    

  $rowattr = (++$Color & 1)?$hTPLVARIABLE{oddattr}:$hTPLVARIABLE{evenattr};

  $tmp=~s/##NUM##/\.\.\./;
  $tmp=~s/##URLSIZE##/\.\.\./;
  $tmp=~s/##ROWATTR##/$rowattr/;
  $tpl{site} .= $tmp;

  $printsize =FineDec($size);
  $HH="00";
  $tmp=$hTPL{site};
  $tmp=~s/##URL##/$site/;
  for ($h=0;$h<24;$h++) {
    $size = sprintf("%.1f",$hsitetime{$site}[$h]/(1024*1024));
    $size = "." if (0 == $hsitetime{$site}[$h]);
    $tmp=~s/##T$HH##/$size/;
    $HH++;
  }    

  $rowattr = (++$Color & 1)?$hTPLVARIABLE{oddattr}:$hTPLVARIABLE{evenattr};

  $tmp=~s/##NUM##/$N/;
  $tmp=~s/##URLSIZE##/$printsize/;
  $tmp=~s/##ROWATTR##/$rowattr/;
  $tpl{site} .= $tmp;
}

$tpl{site} .= $tmptotal;

$printtotalsize=FineDec($calculatedtotal);
	      
$printuser="$user";
$printuser .= " (".GetRealName("?",$user).")" if ($userealname != 0);

ReplaceTPL(USER,$printuser);
ReplaceTPL(WORKPERIOD,$workperiod);
      
ApplyTPL();
PrintTPL();
#print $template;

__END__
2005-05-01 ADD : Initial release
2005-08-30 ADD : Color flipper, total also at bottom of page
2005-09-07 FIX : Color flipper, if records > $usertimelimit
2005-10-02 ADD : _L,_B
2006-06-28 ADD : die -> MyDie
2006-06-28 ADD : &tpl= support
