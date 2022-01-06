#!/usr/bin/perl

print "LightSquid Config Checker, (c) 2005-9 Sergey Erokhin GNU GPL\n\n";

die "perl module File::Basename not found, please install !\n" if (!eval { require File::Basename });
use File::Basename;push (@INC,(fileparse($0))[1]);

die "can't access to lightsquid.cfg !!!\n" if (!eval { require "lightsquid.cfg" });
die "can't access to common.pl !!!\n"      if (!eval { require "common.pl" });

die "no: CGI.PM found, please install\n"   if (!eval { require CGI });

die "can't access to $logpath `access.log` file\ncheck \$logpath variable or privilege\n" unless (-f "$logpath/access.log");

die "Invalid access.log format or can't check format type ...\n" if (CheckLogType("$logpath/access.log"));

print "LogPath   : $logpath\n";
open F,"<$logpath/access.log"          or die "can't access to `access.log` file, check privilege\n";
close F;

print "reportpath: $reportpath\n";
die "can't found report folder `$reportpath`\nplease check \$reportpath variable, create if need\n" unless (-d "$reportpath");

open F,">$reportpath/test.txt"         or die "can't create file in $reportpath folder, check privilege\n";
close F;
unlink "$reportpath/test.txt";

print "Lang      : $langpath/$lang\n";
open F,"<$langpath/$lang.lng"          or die "can't open language file $langpath/$lang.lng, check \$lang variable\n";
close F;

print "Template  : $tplpath/$templatename\n";
open F,"<$tplpath/$templatename/index.html" or die "can't open template $tplpath/$templatename folder, check \$templatename variable\n";
close F;

print "Ip2Name   : $ip2namepath/ip2name.$ip2name\n";
open F,"<$ip2namepath/ip2name.$ip2name"     or die "can't open file $ip2namepath/ip2name.$ip2name file, check \$ip2name variable\n";
close F;

print "\n";

die "\$skipurl variable empty !, read documentation !!!\n" if ($skipurl eq "");

if ($graphreport) {
  die "no: GD.PM found, please install or set \$graphreport=0 to disable\n"   if (!eval { require GD });
  require GD;
  die "no: GD::Polygon modules, please install or set \$graphreport=0 to disable\n" if (!eval { my $poly1 = new GD::Polygon });
  die "no: GD trouble, please install or set \$graphreport=0 to disable\n" if (!eval {  $im = new GD::Image(720,480) });
  if ($ttffont ne "") {
    die "can't access to TTF font $font file, check \$font variable or set \$ttffont = \"\" to disable\n" unless (-f $ttffont);
    die "no: TTF support in GD, please install, or set \$ttffont = \"\" to disable\n" if (!eval { $im = new GD::Image(720,480) ;$im->stringFT(0,$ttffont,7,0.0,0,437,"Hello World") });
  } 
  die "Variable \$graphmaxuser should be >0 !!!\n" if ($graphmaxuser == 0);
  die "Variable \$graphmaxall should be >0 !!!\n"  if ($graphmaxall == 0);
}

#check $skipurl, warning if they contain . char
if ($skipurl =~ m/\./) {
	$tmp=$skipurl;
	$skipurl =~ s/\\\.//gs;
	if ($skipurl =~ m/\./) {
		print "WARNING: \$skipurl variable contain unescaped '.' char !!!\n";
		print "WARNING: if you use \. as regular expression metacharacter please use '' instead \"\" and escape . via \\\. \n";
		print "WARNING: \$skipurl now ->$tmp<\n"; 
	}
}

print "\nall check passed, now try access to cgi part in browser\n";

sub CheckLogType($) {
    my $LogFile = shift;
    my @a;
    my $EmulatedFormat1 = 0;
    my $EmulatedFormat2 = 0;
    my $NativeFormat1   = 0;
    my $NativeFormat2   = 0;
    my $TestedLine      = 0;
	my $ret				= 0;

	my @LogName;
	$LogName[0]			="Native";
	$LogName[1]			="Emulated";

	my $warning;
	
#    print "FILE: $LogFile\n";

	unless ( -z $LogFile ) {

		open FLOG, "<", "$LogFile";
		while (<FLOG>) {
			chomp;
			$line=$_;
			next if ( $line eq "" );
			$TestedLine++;

			@a = split /\s+/, $line;

			$NativeFormat1++ if ( ( $a[0]   = ~ m/\d+\.\d+/ ) and ( $a[1] =~ m/\d+/ ) and ( $a[4] =~ m/\d+/ ) );
			#      0         1          2        3           4   5
			#970313965.619 1249    denis.local TCP_MISS/200 2598 GET    http://www.emalecentral.com/tasha/thm_4374x013.jpg -     DIRECT/www.emalecentral.com image/jpeg
			# timestamp    elapsed host        type         size method url                                                  user  hierarechy                    type
			#1125191043.218      3 192.168.1.240 TCP_DENIED/403 1411 GET http://ar.atwola.com/image/93159194/icq - NONE/- text/html
			#1125191043.219      0 192.168.1.240 TCP_DENIED/403 1403 GET http://ar.atwola.com/file/adsEnd.js -     NONE/- text/html
			$NativeFormat2++ if ( ($#a == 9) );

			#emulated httpd log
			#      0      1 2       3                 4      5
			#192.168.3.40 - - [15/Apr/2005:11:46:35 +0300] "GET http://mail.yandex.ru/mboxjscript? HTTP/1.0" 200 2262 TCP_MISS :DIRECT

			$EmulatedFormat1++ if ( ( $a[3] = ~ m/\[\d{1,2}\// ) and ( $a[4] =~ m/\d{1,4}\]/ ) and ( $a[5] =~ m/\"/ ) );
#                                                   192.168.3.40           -     -     [15      /Apr     /2005  :11      :46      :35        +0300]       "GET http://mail.yandex.ru/mboxjscript? HTTP/1.0" 200 2262 TCP_MISS :DIRECT
			$EmulatedFormat2++ if ( $line =~ m/^(\d{1,3}\.){3}\d{1,3}\s+\S+\s+\S+\s\[\d{1,2}\/\S{1,3}\/\d{4}\:\d{1,2}\:\d{1,2}\:\d{1,2}\s[+-]\d{1,4}\] \".*\S+\:\S+$/);
		}
		close FLOG;

		if ( $TestedLine == 0 ) {
			die "WARNING: log file is empty!, can't check log file format !!!!!\n";
		}

		$n1 = Percent( $TestedLine, $NativeFormat1 );
		$n2 = Percent( $TestedLine, $NativeFormat2 );
		$e1 = Percent( $TestedLine, $EmulatedFormat1 );
		$e2 = Percent( $TestedLine, $EmulatedFormat2 );

		if ($debug) {
			 print "dbg: tested  : $TestedLine\n";
			 print "dbg: native1 : $NativeFormat1 :: $n1\n";
			 print "dbg: native2 : $NativeFormat2 :: $n2\n";
			 print "dbg: emulate1: $EmulatedFormat1 :: $e1\n";
			 print "dbg: emulate2: $EmulatedFormat2 :: $e2\n";
		}

		if ( $e1 > 90 ) {
			$detected = 1;
			$warning  = "Log format Look like CUSTOM log, Lightsquid can't parse this format! Please check documentation !" if ( $e2 < 60 );
		}
		if ( $n1 > 90 ) {
			$detected = 0;
			$warning  = "Log format Look like CUSTOM log, Lightsquid can't parse this format! Please check  documentation !" if ( $n2 < 60 ) ;
		}
	} else {
		$warning="log file is empty!, can't check log file format !!!!!\n";
	}
	
    if ( $detected != $squidlogtype ) {
		print "WARNING: \$squidlogtype=$squidlogtype in lightsquid.conf, it's mean expected log type is '$LogName[$squidlogtype]'\n";
        print "WARNING: but your access.log look like `$type`, please correct config file -> `\$squidlogtype=$detected`\n";
		$ret=1;
    }
    if ( $warning ne "" ) { $ret=1;print "WARNING: $warning\n"};
	return $ret;
}

sub Percent($$) {
    my $total = shift;
    my $val1  = shift;
    return sprintf( "%.2f", ( $val1 * 100 ) / $total );
}
