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

$year        =$co->param('year');
$month       =$co->param('month');
$day         =$co->param('day');
$filteruser  =$co->param('user');

InitTPL("bigfiles",$co->param('tpl'));

$n=1;

$total=0;

$workperiod=" $day $MonthName[$month] $year";

open FF,"<$reportpath/$year$month$day/.bigfiles" || MyDie("cant' open .bigfile");

$N=0;
while (<FF>) {
 ($user,$time,$size,$link)=split;

 if ($filteruser ne "") {
   next unless ($filteruser eq $user);
 };

 $N++;

 $total+=$size;
 $printsize=FineDec($size);

 $rowattr = ($N & 1)?$hTPLVARIABLE{oddattr}:$hTPLVARIABLE{evenattr};

 $url_L=URLEncode("user_detail.cgi?year=$year&month=$month&day=$day&user=$user");
 $url_B="$user";

 $url_L =~ s/#/%23/;

 $tmp=$hTPL{bigfile};
 $tmp=~s/##BFILENUM##/$N/;
 $tmp=~s/##BFILETIME##/$time/;
 $tmp=~s/##BFILEUSER_L##/$url_L/;
 $tmp=~s/##BFILEUSER_B##/$url_B/;
 $tmp=~s/##BFILESIZE##/$printsize/;
 $tmp=~s/##BFILELINK##/$link/;
 $tmp=~s/##ROWATTR##/$rowattr/; 
 $tpl{bigfile} .= $tmp;
}

close FF;

$printsize=FineDec($total);
$tmp=$hTPL{bigfile};
$tmp=~s/##BFILENUM##/ /;
$tmp=~s/##BFILETIME##/ /;
$tmp=~s/##BFILEUSER_L##//;
$tmp=~s/##BFILEUSER_B##/TOTAL/;
$tmp=~s/##BFILESIZE##/$printsize/;
$tmp=~s/##BFILELINK##/ /;
$tmp=~s/##ROWATTR##/$hTPLVARIABLE{total}/; 
$tpl{bigfile} .= $tmp;


ReplaceTPL(DATE,$workperiod);
		
ReplaceTPL(REPORTUSER,$filteruser);
ApplyTPL();
HideTPL("reportuser") if ($filteruser eq "");
PrintTPL();

__END__
2004-09-09 ADD : skip all files starting with .
2005-04-17 ADD : TemplateEngine
2005-07-01 ADD : TOTAL size
2005-08-30 ADD : Color flipper
2005-09-08 ADD : user now URL to day_detail for user
2005-10-01 ADD : _L,_B
2005-11-07 ADD : URL_Encode
2006-06-28 ADD : die -> MyDie
2006-06-28 ADD : &tpl= support
2006-09-13 ADD : &user= filter by USER
