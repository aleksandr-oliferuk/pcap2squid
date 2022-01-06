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

$NotInGroupID="00";
$NotInGroupName="##MSG_NOT_IN_GROUP##";


$co=new CGI;

$year =$co->param('year');
$month=$co->param('month');
$day  =$co->param('day');
$mode =$co->param('mode') || "day";

InitTPL("group_detail",$co->param('tpl'));

if ($mode eq "month") {
    $workperiod="##MSG_WHOLE## ##MSG_MONTH## - $year $MonthName[$month]";
    $mask = "$year$month*";
} elsif ($mode eq "year") {
    $workperiod="##MSG_WHOLE## ##MSG_YEAR## - $year";
    $mask = "$year*";
} else {
    $mode="day";
    $workperiod="$day $MonthName[$month] $year";
    $mask = "$year$month$day";
}

#additional info in DAY mode
if ($mode eq "day") {
    ($dev,$ino,$mode_,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat("$reportpath/$mask");
    ($sec_,$min_,$hour_,$mday_,$mon_,$year_,$wday_,$yday_,$isdst_)=localtime($mtime);
    $mon_++;$year_+=1900;
    $workperiod .= " (##MSG_UPDATE## :: ".sprintf("%02d:%02d",$hour_,$min_)." ::  $mday_ $MonthName[$mon_] $year_)";

    $topsitesurl="topsites.cgi?year=$year&month=$month&day=$day";
    $bigfilesurl="bigfiles.cgi?year=$year&month=$month&day=$day";

    $topsites_L="$topsitesurl";
    $topsites_B="##MSG_TOP_SITES##";
    $bigfiles_B="##MSG_BIG_FILES##";
    if (-f "$reportpath/$mask/.bigfiles") {
	 $bigfiles_L="$bigfilesurl";
     }
}    

@datelist=sort glob "$reportpath/$mask*";

$totalsize=0;
foreach $workday (sort @datelist) {
    GetGroupFile($workday);
    GetRealName($workday,"?");
    
    open FF,"<$workday/.total" or MyDie("can't open file $workday/.total<br>");
    $user=<FF>;#chomp $user;$user=~s/^user: //;
    $size=<FF>;#chomp $size;$size=~s/^size: //;
    
    while (<FF>) {
	$N++;
	($user,$size,$hit)=split;
	$hUserTotal{$user}+=$size;
	$hUserTotalHit{$user}+=$hit;
	$totalsize+=$size;
    }
    close FF
}

#----------------------------------------------------------------------------------
#numerate user position in all list & add NOT IN GROUP
$N=0;
foreach $user (sort {$hUserTotal{$b} <=> $hUserTotal{$a}} keys %hUserTotal) {
    $N++;
    $hUserPosition{$user}=$N;
    unless (exists $hUserGroup{$user}) {
        #GetGroupFile - not clear
	$hGroupByUser{$NotInGroupID}{$user}=1;
	$hUserGroup  {$user}{$NotInGroupID}=$NotInGroupID;  
    }
}

#----------------------------------------------------------------------------------
#calculate TotalSize by group (all user in group sum)

foreach $grp (sort keys %hGroupByUser) {
    foreach $user (sort keys %{$hGroupByUser{$grp}}) {
        next unless (defined $hUserTotal{$user}); #skip if user not use internet
        $hGroupTotalSize{$grp}+=$hUserTotal{$user};
    }
}

#-----------------------------------------------------------------------------------

#out: group list ordered by size
$N=0;
foreach $grp (sort {$hGroupTotalSize{$b}<=>$hGroupTotalSize{$a}} keys %hGroupName) {
    next if (0 == $hGroupTotalSize{$grp});
    $size     =$hGroupTotalSize{$grp};
#    print "$hGroupName{$grp} -> $percent ->$size\n";

    $N++;
    $gprintsize=FineDec($size);
    $depurl_L="#$grp";
    $depurl_B="$hGroupName{$grp}";
    $gpercent  =sprintf("%2.1f",int($size*1000/$totalsize)/10);
	
    $rowattr = ($N & 1)?$hTPLVARIABLE{oddattr}:$hTPLVARIABLE{evenattr};
	  
    $tmp=$hTPL{grouplist};
    $tmp=~s/##GROUPLISTNUM##/$N/;
    $tmp=~s/##GROUPLISTNAMEURL_L##/$depurl_L/;
    $tmp=~s/##GROUPLISTNAMEURL_B##/$depurl_B/;
    $tmp=~s/##GROUPLISTBYTES##/$gprintsize/;
    $tmp=~s/##GROUPLISTPERCENT##/$gpercent/;
    $tmp=~s/##GROUPROWATTR##/$rowattr/;
    $tpl{grouplist} .= $tmp;
}

$row=0;
#foreach $grp (sort {$hGroupTotalSize{$b}<=>$hGroupTotalSize{$a}} keys %hGroupByUser) {
foreach $grp (sort keys %hGroupByUser) {
    next if (0 == $hGroupTotalSize{$grp});
#    print "$grp -> $hGroupName{$grp} -> $hGroupTotalSize{$grp}\n";

    
    $groupstarturl_L="$grp";
    $groupstarturl_B="$hGroupName{$grp}";
    
    $tmp=$hTPL{groupstart};
    $tmp=~s/##GROUPSTARTURL_L##/$groupstarturl_L/;
    $tmp=~s/##GROUPSTARTURL_B##/$groupstarturl_B/;
    $tpl{user} .= $tmp;    
    
    foreach $user (sort {$hUserTotal{$b} <=> $hUserTotal{$a}} keys %{$hGroupByUser{$grp}}) {
        next unless (defined $hUserTotal{$user}); #skip if user not use internet
#	print "\t$hUserPosition{$user}. $user\t$hUserTotal{$user}\n";

	$row++;
	
	$url_B="$user";

	$realname=GetRealName($daypath,$user);
  

        if ($mode eq "day") {
	    $url_L="user_detail.cgi?year=$year&month=$month&day=$day&user=$user";
	} elsif ($mode eq "month") {
	    $url_L="user_detail.cgi?year=$year&month=$month&day=$day&user=$user&mode=month";
	} else {
	    $url_L="";
	}
	$url_L = URLEncode($url_L);

        $size     =$hUserTotal{$user};
	$printhit =FineDec($hUserTotalHit{$user});
        $printsize=FineDec($size);
	$percent  =sprintf("%2.1f",int($size*1000/$totalsize)/10);
	$N        =$hUserPosition{$user};
	    

	$timeurl_L=URLEncode("user_time.cgi?year=$year&month=$month&day=$day&user=$user");
        $timeurl_B="##MSG_TIME_LINK##";	
	
	$rowattr = ($row & 1)?$hTPLVARIABLE{oddattr}:$hTPLVARIABLE{evenattr};
    
	$tmp=$hTPL{user};
        $tmp=~s/##USERNUM##/$N/;
	$tmp=~s/##USERURL_L##/$url_L/;
	$tmp=~s/##USERURL_B##/$url_B/;
	$tmp=~s/##REALNAME##/$realname/;
	$tmp=~s/##TIMEURL_L##/$timeurl_L/;
	$tmp=~s/##TIMEURL_B##/$timeurl_B/;
	$tmp=~s/##USERDEP##/$grp/;
	$tmp=~s/##USERCONNECT##/$printhit/;
	$tmp=~s/##USERBYTES##/$printsize/;
	$tmp=~s/##USERPERCENT##/$percent/;
	$tmp=~s/##ROWATTR##/$rowattr/;
	$tpl{user} .= $tmp;
    }


    $gprintsize=FineDec($hGroupTotalSize{$grp});
    $gpercent  =sprintf("%2.1f",int($hGroupTotalSize{$grp}*1000/$totalsize)/10);
    
    $tmp=$hTPL{groupend};
    $tmp=~s/##GROUPENDBYTES##/$gprintsize/;
    $tmp=~s/##GROUPENDPERCENT##/$gpercent/;
    $tpl{user} .= $tmp    
}

#generate HTML
ReplaceTPL_URL(TOPSITESURL,URLEncode($topsites_L),$topsites_B);
ReplaceTPL_URL(BIGFILESURL,URLEncode($bigfiles_L),$bigfiles_B);
ReplaceTPL(DATE,$workperiod);

ApplyTPL();

HideTPL("dayinfo") if ($mode ne "day");
HideTPL("timereport") if (($timereport == 0) or ($mode ne "day"));
HideTPL("realname")      if ($userealname == 0);

PrintTPL();

__END__
2005-11-07 ADD : URLEncode
2006-06-28 ADD : die -> MyDie
2006-06-28 ADD : &tpl= support
