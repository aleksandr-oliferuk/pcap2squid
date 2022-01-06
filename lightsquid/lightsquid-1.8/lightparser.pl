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

#parse access.log
# make per user report in 'report' direcotry

#usage: lightparse.pl {param}
#if param omit				 - parse full access.log file
#	today					 - only current day
#	yesterday				 - yesterday
#	data in format YYYYMMDD	 - parse day
#	access.log.{\d}.{gz|bz2} - parse file (for process archived)

# function prototypes
sub MakeReport();
sub InitSkipUser();
sub getLPS($$);
sub LockLSQ();
sub UnLockLSQ();
sub LOCKREMOVER();

use File::Basename;
use Time::Local;

push (@INC,(fileparse($0))[1]);

require "lightsquid.cfg";
require "common.pl";

#include ip2name function
require "ip2name/ip2name.$ip2name";

$SIG{INT} = \&LOCKREMOVER;	# traps keyboard interrupt
my $lockfilepath	  ="$lockpath/lockfile";

my $skipurlcntr		  = 0;
my $skip4xxcntr		  = 0;
my $skipfilterdatecntr= 0;

my $firstrun	= 1;
my $totallines	= 0;
my $parsedlines = 0;
my $daylines	= 0;

my $catname	  ="cat";
my $filename  ="access.log";

undef $workday;

exit unless (LockLSQ()); #Lock LSQ (block multiple instance)

if ($skipurl eq "") {
   $skipurl = "skipurl MUST be defined!!!";
   print "WARNING !!! \$skipurl is empty\n";
}	

($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime;
$month=sprintf("%02d",$mon+1);;
	  
my $filterdatestart=0;
my $filterdatestop =timelocal(59,59,23,31,12-1,2020-1900)+1000;

$fToday=1 if ($ARGV[0] eq "today");
$fToday=1 if ($ARGV[0] eq "yesterday");

if ($fToday) {
   ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime;

   $filterdate=sprintf("%04d%02d%02d",$year+1900,$mon+1,$mday);;
   $filterdatestart=timelocal( 0, 0, 0,$mday,$mon,$year);
   $filterdatestop =timelocal(59,59,23,$mday,$mon,$year);
   print ">>> filter today: $filterdate\n" if ($debug);
}

if ($ARGV[0] eq "yesterday") {
   $filterdatestart=$filterdatestart-(24*60*60);
   $filterdatestop =$filterdatestop -(24*60*60);
   ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($filterdatestart);
   $filterdate=sprintf("%04d%02d%02d",$year+1900,$mon+1,$mday);;
   print ">>> filter yesterday: $filterdate\n" if ($debug);
}

if ($ARGV[0] =~ m/^(\d\d\d\d)(\d\d)(\d\d)$/) {
   $filterdate=$ARGV[0];
   $filterdatestart=timelocal( 0, 0, 0,$3,$2-1,$1);
   $filterdatestop =timelocal(59,59,23,$3,$2-1,$1);
   print ">>> filter date:	$filterdate\n" if ($debug);
}

if ($ARGV[0] =~ m/access\.log\.(\d)/) {
   $filename=$ARGV[0];
   $catname="zcat" if ($ARGV[0] =~ m/\.gz$/);
   $catname="bzcat" if ($ARGV[0] =~ m/\.bz2$/);
}

print ">>> use file :: $logpath/$filename\n" if ($debug);
#open FF, "$logpath\\$filename" || die "can't access log file\n";
open FF, "$catname $logpath/$filename|" || die "can't access log file\n";

InitSkipUser();

StartIp2Name();

undef %bigfile; $bigfilecnt=0;
while (<FF>) {
	chomp;
	$totallines++;

	if (0 == $squidlogtype) {
	   #squid native log
	   #970313965.619 1249	  denis.local TCP_MISS/200 2598 GET	   http://www.emalecentral.com/tasha/thm_4374x013.jpg -		DIRECT/www.emalecentral.com image/jpeg
	   # timestamp	  elapsed host		  type		   size method url													user  hierarechy					type

	   #speed optimization for FILTERDATE mode
	   $Ltimestamp=substr $_,0,11;
	   if ($Ltimestamp<$filterdatestart or $Ltimestamp>$filterdatestop) {
		  print ">>>> skipDafteFilter URL $Lurl\n$_" if ($debug2 >= 2 );
		  $skipfilterdatecntr++;
		  next;
	   };

	   ($Ltimestamp,$Lelapsed,$Lhost,$Ltype,$Lsize,$Lmethod,$Lurl,$Luser,$Lhierarchy,$Lconttype,@Lrest)=split;
	   ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($Ltimestamp);
	   $mon++; #fix, month start from 0
	   $date  =sprintf("%04d%02d%02d",$year+1900,$mon,$mday);

	   #check row with invalid record
	   if ( ($#Lrest >= 0) && ($#Lrest < 4) ) { 
		  $str=$_;
		  #maybe two concatenated record (first - truncated)
	  if ($str =~ m/(\d+\.\d+\s+\d+\s+(\d{1,3}\.){3}\d{1,3}\s+\w+\/\d+\s+\d+\w+\s+\S+\s+\S+\s+\S+\s+\w+\/\S+\s(-|([a-zA-Z\-]+\/[a-zA-Z\-]+)))$/) {
			$newstr=$1;
			($Ltimestamp,$Lelapsed,$Lhost,$Ltype,$Lsize,$Lmethod,$Lurl,$Luser,$Lhierarchy,$Lconttype)=split /\s+/,$newstr;
		  } else {
			# maybe source url contain SPACES, try concatenate ...
			while ($#Lrest != -1) {
			   $Lurl.="_$Luser";$Luser=$Lhierarchy;$Lhierarchy=$Lconttype;$Lconttype=shift @Lrest;
			}
			#do some sanity check
		unless (($Lhierarchy =~ m/\w+\/\S+/) and ($Lconttype =~ m/-|([a-zA-Z\-]+\/[a-zA-Z\-]+)/)) {
			   $notrecoveredlines++;
		   next;
			}
		  }
		  $recoveredlines++;
	   }
	} else {
	   #emulated httpd log
	   #192.168.3.40 - - [15/Apr/2005:11:46:35 +0300] "GET http://mail.yandex.ru/mboxjscript? HTTP/1.0" 200 2262 TCP_MISS :DIRECT
	   #192.168.3.40 - - [15/Apr/2005:11:46:35 +0300] "GET http://css.yandex.ru/css/mail/search.js HTTP/1.0" 200 4199 TCP_HIT:NONE
	   #192.168.3.12 -		 -		 [15/Apr/2005:11:46:35 +0300] "CONNECT aero.lufthansa.com:443 HTTP/1.0" 200 35992 TCP_MISS:DIRE
	   # ($Lhost,	  $Luser,$Luser2,$Ldate,			   $u2,	  $Lmethod,$Lurl,				  $u3,	   $Ltype,$Lsize,$u4)=split
 
	   ($Lhost,$Luser,$Luser2,$Ldate,$u2,$Lmethod,$Lurl,$u3,$Ltype,$Lsize,$u4)=split;
	   
	   $Ldate =~ m#^\[(\d\d)/(...)/(\d\d\d\d):(\d\d):(\d\d):(\d\d)#;
	   $mday=$1;$mon=$month2dec{$2};$year=$3-1900;
	   $hour=$4;$min=$5;$sec=$6;

	   $date  =sprintf("%04d%02d%02d",$year+1900,$mon,$mday);
	   if ($filterdate) {
		  if ($date ne $filterdate) {
			 print ">>>> skipDafteFilter URL $Lurl\n$_" if ($debug2 >= 2 );
			 $skipfilterdatecntr++;
			 next;
		  };
	   }
	   
	   if (($Luser eq "-") && ($Luser2 ne "-")) {
		 $Luser = $Luser2;
	   }
	   
	   $u4 =~ m/(.*?)\s?:(.*)/;
	   $Ltype = "$1/$Ltype";
	}  #if ($squidlogtype)
	
	if ($year < 2000-1900) { ; #invalid record
	   print ">>>> skipn Bad Year  $Lurl\n$_" if ($debug2 >= 1 );
	   $skipbadyear++;
	   next;
	}

	#skip intranet
	if ($Lurl =~ m/$skipurl/o) {
	  print ">>>> skipURL $Lurl\n$_" if ($debug2 >= 2 );
	  $skipurlcntr++;
	  next;
	};

	# skip Access denied records (TODO: report)
	if ($Ltype =~ m#DENIED#io) {
	  $skipDenied++;
	  print ">>>> skipDenied $Ltype\n$_" if ($debug2 >= 2);
	  next;
	};
	
	if ($Ltype =~ m/HIT/) {
	  $CacheHIT+=$Lsize;
	} else {
	  $CacheMISS+=$Lsize;
	}

	$parsedlines++;
	
	if ($date ne $workday) { # close prev day, prepare for new
	  if ($firstrun) {
		undef $firstrun;
		$workday=$date;
	  } else {
		MakeReport();
		undef %totalsize; undef %sitesize; undef %sitehit;undef %totalhit;undef %totalputpost;
	undef %hashhost;undef %hashname;
		undef %bigfile; $bigfilecnt=0;
	undef %sitetime;undef %sitetimesize;
		$daylines=0;
		$workday=$date;
	$sqlreq=0;
	$CacheHIT=0;$CacheMISS=0;
	  }
	}
	$daylines++;

	$user=lc $Luser;
 
	$user = Ip2Name($Lhost,$user,$Ltimestamp);

	next if (defined $hSkipUser{$user});

	#simplified some common banner system & counters
	$url=$Lurl;
	$url =~ s/([a-z]+:\/\/)??.*\.(spylog\.com)/$1www.$2/o;
	$url =~ s/([a-z]+:\/\/)??.*\.(yimg\.com)/$1www.$2/o;
	$url =~ s/([a-z]+:\/\/)??.*\.(adriver\.ru)/$1www.$2/o;
	$url =~ s/([a-z]+:\/\/)??.*\.(bannerbank\.ru)/$1www.$2/o;
	$url =~ s/([a-z]+:\/\/)??.*\.(mail\.ru)/$1www.$2/o;
	$url =~ s/([a-z]+:\/\/)??.*\.(adnet\.ru)/$1www.$2/o;
	$url =~ s/([a-z]+:\/\/)??.*\.(rapidshare\.de)/$1www.$2/o;
	$url =~ s/([a-z]+:\/\/)??.*\.(rapidshare\.com)/$1www.$2/o;

	$url =~ s/([a-z]+:\/\/)??.*\.(vkontakte\.ru)/$1www.$2/o;
	$url =~ s/([a-z]+:\/\/)??.*\.(odnoklasniki\.ru)/$1www.$2/o;


	#extract site name
	if ($url =~ m/([a-z]+:\/\/)??([a-z0-9\-]+\.){1}(([a-z0-9\-]+\.){0,})([a-z0-9\-]+){1}(:[0-9]+)?\/(.*)/o) {
	   $site=$2.$3.$5;
	} else {
	   $site=$Lurl;
	}

	
	$site=$Lurl if ($site eq "");

	$totalsize	  {$user}		+=$Lsize;
	$totalhit	  {$user}		++;
	$totalputpost {$user}		+=$Lsize if (($Lmethod eq "PUT") or ($Lmethod eq "POST"));
	$sitesize	  {$user}{$site}+=$Lsize;
	$sitehit	  {$user}{$site}++;
	
	$sitetime	  {$user}{$site}[$hour]+=$Lelapsed;
	$sitetimesize {$user}{$site}[$hour]+=$Lsize;
	
	#.bigfile support
	if ($Lsize > $bigfilelimit) {
		$bigfile [$bigfilecnt]{date}=sprintf("%02d:%02d:%02d",$hour,$min,$sec);
		$bigfile [$bigfilecnt]{link}=$Lurl;
		$bigfile [$bigfilecnt]{size}=$Lsize;
		$bigfile [$bigfilecnt]{user}=$user;
		$bigfilecnt++;
	}
}

MakeReport();
StopIp2Name();
UnLockLSQ();

if ($debug) {
	$worktime = ( time() - $^T );
	print "run TIME: $worktime sec\n";
	print "LightSquid parser statistic report\n\n";
	printf( "	   %10u lines processed (average %.2f lines per second)\n",
		$totallines, getLPS( $worktime, $totallines ) );
	printf( "	   %10u lines parsed\n",				  $parsedlines );
	printf( "	   %10u lines recovered\n",				  $recoveredlines );
	printf( "	   %10u lines notrecovered\n",			  $notrecoveredlines );
	printf( "	   %10u lines skiped by bad year\n",	  $skipbadyear );
	printf( "	   %10u lines skiped by date filter\n",	  $skipfilterdatecntr );
	printf( "	   %10u lines skiped by Denied filter\n", $skipDenied );
	printf( "	   %10u lines skiped by skipURL filter\n", $skipurlcntr );

	if ( $parsedlines == 0 ) {
		print "\nWARNING !!!!, parsed 0 lines from total : $totallines\n";
		print "please check confiuration !!!!\n";
		print "may be wrong log format selected ?\n";
	}

}



# The END ---------------------------------------------------------

##Subroutines
# return Line Per Second value (check 0 values and correct)
sub getLPS($$) {
  my $time=shift;
  my $lines=shift;
  $time||=1;
  $lines||=1;
  return ($lines/$time);
}

sub MakeReport() {
	#generate report
	#use global var 

	return if ($daylines < 2);

	print ">>> Make Report $workday ($daylines - log line parsed)\n" if ($debug);

	$reppath="$reportpath/$workday";

	unless ( -d $reppath )
	{
	  mkdir $reppath, 0755 or die "Can't create dir '$reppath': $!";
	}

	open TOTALFILE,">$reppath/.total" || die "can't create file	 $reppath/.total - $!";

	$tmp="";$tmpsize=0;$tmpuser=0;$tmpoveruser=0;

	foreach $tuser (sort {$totalsize{$b} <=> $totalsize{$a}} keys %totalsize) {
#		   $tmp.="$tuser\t$totalsize{$tuser}\t$totalhit{$tuser}\t$totalputpost{$tuser}\n";
	  $totalputpost{$tuser}+=0; #prevent empty value
	  $tmp.=sprintf("%-20s %15s %15s %15s\n",$tuser,$totalsize{$tuser},$totalhit{$tuser},$totalputpost{$tuser});
	  $tmpuser++;
	  $tmpsize+=$totalsize{$tuser};
	  $tmpoveruser++ if ($totalsize{$tuser} >= $perusertrafficlimit);

	  open REPFILE,">$reppath/$tuser" || die "can't create file	 $reppath/$tuser - $!";

	  print REPFILE "total: $totalsize{$tuser}\n";

	  foreach $tsite (sort {$sitesize{$tuser}{$b} <=> $sitesize{$tuser}{$a}} keys %{$sitesize{$tuser}} ) {
		  printf REPFILE ("%-29s %12s %10s\t",$tsite,$sitesize{$tuser}{$tsite},$sitehit{$tuser}{$tsite});
	  if ($timereport != 0) {
			for ($hour=0;$hour<24;$hour++) {
		printf REPFILE ("%d-%s ",int($sitetime{$tuser}{$tsite}[$hour]/3600),$sitetimesize{$tuser}{$tsite}[$hour]+0);
		}
	  }
		  print REPFILE "\n";
	  }
	  close REPFILE;
	}

	$CacheMISS=1 if ($CacheMISS == 0);

	print TOTALFILE "user: $tmpuser\n";
	print TOTALFILE "size: $tmpsize\n";

	print TOTALFILE "$tmp";
	close TOTALFILE;

	my ($sec_,$min_,$hour_,$mday_,$mon_,$year_,$wday_,$yday_,$isdst_) = localtime;$mon_++;$year_+=1900;
	my $moddate=sprintf("%02d:%02d",$hour_,$min_)." ::	$mday_ $MonthName[$mon_] $year_";

	open FILE,">$reppath/.features" || die "can't create file  $reppath/.features - $!";
	print FILE "overuser: $tmpoveruser\n";
	print FILE "cachehit%: ".sprintf("%3.2f",($CacheHIT*100)/($CacheHIT+$CacheMISS))."\n";
	print FILE "cachehit: $CacheHIT\n";
	print FILE "cachemiss: $CacheMISS\n";
	print FILE "cacheall: ".($CacheHIT+$CacheMISS)."\n";
	print FILE "modification: $moddate\n";
	close FILE;

	unlink "$reppath/.bigfiles";
	if ($bigfilecnt != 0) {
	  open MAXFILE,">$reppath/.bigfiles" || die "can't create file	$reppath/.bigfiles - $!";
	  for ($i=0;$i<$bigfilecnt;$i++) {
		print MAXFILE "$bigfile[$i]{user}\t$bigfile[$i]{date}\t$bigfile[$i]{size}\t$bigfile[$i]{link}\n";
	  }
	  close MAXFILE;
	}

	#create list of user that use more than $perusertrafficlimit bytes
	unlink "$reppath/.overuser";
	if ($tmpoveruser) {
		open OVERFILE,">","$reppath/.overuser" || die "can't create file  $reppath/.overuser - $!";
		foreach $tuser (sort {$totalsize{$b} <=> $totalsize{$a}} keys %totalsize) {
			print OVERFILE "$tuser\t$totalsize{$tuser}\n" if ($totalsize{$tuser} >= $perusertrafficlimit);
		}
		close OVERFILE;
	}
	
	CreateGroupFile($reppath);
	CreateRealnameFile($reppath);
}

sub InitSkipUser() {
 open F,"<$cfgpath/skipuser.cfg";
 while (<F>) {
   chomp;
   next if (/^#/);
   $hSkipUser{$_}=1;
 }
 close F;
}
# Lock support
sub LockLSQ() {
   if (-f "$lockfilepath") {
	  #read data from `lockfile`
	  print STDERR "Warning, `$lockfilepath` exist, maybe anoter process running !\n";
	  open FF,"<","$lockfilepath" or die "can't read lock file `$lockfilepath`\n";
	  $pid=<FF>;chomp $pid;$pid =~ s/PID: //;
	  $ts =<FF>;chomp $ts ;$ts	=~ s/Timestamp: //;
	  close FF;
	  #check timedelta
	  $tsdelta=time - $ts;
	  print STDERR "LockPID : $pid\n" ;
	  print STDERR "tsdelta : $tsdelta second(s) (maxlocktime: $maxlocktime)\n";

	  return 0 if ($tsdelta<$maxlocktime);

	  print STDERR "OLD lock file ignored and removed!\n";
	  UnLockLSQ();
   } 

   open FF,">","$lockfilepath" or die "can't create lock file `$lockfilepath`\n";
   print FF "PID: $$\n";
   $ts=time;
   print FF "Timestamp: $ts\n";
   print FF "Creation time: ".localtime($ts)."\n";
   close FF;

   return 1;
}

sub UnLockLSQ() {
  unlink $lockfilepath or die "can't remove lock file `$lockfilepath`\n";
}

sub LOCKREMOVER() {
   print "INT happents, remove LOCK\n";
   UnLockLSQ();
   exit;
}

__END__
2004-04-23		: initial version
2004-09-01 FIX	: error in parse invalid file
2004-09-09 ADD	: add create .bigfile file contain links greater $bigfilelimit
2004-11-08 ADD	: skip 4xx records (dirty :-() TODO: do error report
2004-11-09 ADD	: use DB only if not define user name...
2005-04-13 ADD	: LightSquid publication cleanup
2005-04-14 ADD	: $debug and $debug2 variable for generate statistic
				: if parsed lines = 0 print WARNING
2005-04-17 ADD	: add support fot HTTPDlike log file
2005-04-19 ADD	: add .bz2 support
				: add cache hit calculationn (if Ltype contain HIT - hit else - MISS), wrong ??
				: add oversized user calculation
2005-04-20 ADD	: .features file added, with additional info		   
2005-04-22 FIX	: httpdlike parser bug;
	   	   FIX	: mkdir 655 -> mkdir 755
2005-04-30 ADD	: Rewrite archive support, now support access.log.{D},access.log.{D}.gz,access.log.{D}.bz2
		   ADD	: time report
2005-05-03 FIX	: fix wrong .features file output
2005-05-12 FIX	: empty line report only if $debug
		   FIX	: date filter now ^\d\d\d\d\d\d\d\d$ ...	   
2005-11-21 FIX	: cosmetical changes
2006-07-02 ADD	: try recovery some type of broken log record (url contain spaces, two concatenated record)
				: fix negative number in user file (printf -%d <2g $u <4g), now use simple print
2006-07-05 ADD	: Put & Post addet into .total file
2006-07-10 ADD	: SkipUser support
				: GetNameByIP -> IP2NAME (see doc)
				: $cfgpath in config
				: .features modification: parameter support
2006-07-29 ADD	: add LOCKing, for prevent multiple LightSquid parser instance ...
		   ADD	: improve SKIP speed for native squid log format (more that 3 time !!!!)
		   ADD	: report line per second speed LPS in debug report
2006-11-23 FIX	: Yet another printf trouble in time report fixed
2007-01-05 FIX	: Wrong modification data writen in .features
2008-11-28 NEW	: Odnoklasniki & Vkontakte agregator added
		   FIX	: Perl 5.10 fix. in several cases incorrect name was used, but size calculated correctly.
2009-06-30 NEW	: .overuser support