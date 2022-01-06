#!/usr/bin/perl
#
# LightSquid Project (c) 2004-2009 Sergey Erokhin aka ESL
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# detail see in gnugpl.txt

#agregate site in user reports

#agregate function see in Aggregat() function
#you can combine garbage like i1.site.com,i2.site.com,i3.site.com -> site.com


#2008-12-18 Sergey Erokhin aka ESL.


use File::Find;
use Socket;

require "../../lightsquid.cfg";

$| = 1;

#in several cases squid doesn't resolve all ip to it's name, and leave several as ip
#if you set this variable to 1, script try to resolve ip 2 name
$TryToResolveIp=0;
#a lot of sites my be aggtrgated in this case, but it's my be very slooooooowwwwwwww.

my $oldsize=0;
my $newsize=0;
my $cmpfile=0;
my $totalfile=0;


print "Start Aggregate '$reportpath' folder (Y - for yes)?";
$answer=<STDIN>;
chomp $answer;
exit if ($answer ne "Y");

print "Let's go ...\n";

find({ wanted => \&process, no_chdir=>1 }, "$reportpath/");

print "totalfile: $totalfile\n";
print "compacted: $cmpfile\n";
print "OldSize  : $oldsize\n";
print "NewSize  : $newsize\n";
print "Saved    : ".($oldsize-$newsize)."\n";



sub process() {
	my $old;
	my $new;
	
	next if (m{\/\.});
	next unless (m{\/\d+\/});
#	print "$_\n";
	$old=-s $_;
	$new=ProcessUser($_);
	if ($new) {
		$oldsize+=$old;
		$newsize+=$new;
		$cmpfile++;
	}
	$totalfile++;
}

#total: 3483285
#www.mail.ru						2261579		483	0-3302 8-2248160 0-772 0-772 0-772 0-772 0-772 0-772 0-5485 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 0-0 

#return new size if modified
#or 0 if not modified;
sub ProcessUser($) {
	my $FileName=shift;
	my $Modified=0;
	my $total;
	my %hSite;
	my @tmp;
	my $site,$size,$hit,@time;
	my $ssite;
	my $ttime,$tsize;
	my $srclen=-s $FileName;
	my $dstlen=0;
	my $dstfile="";
	my $ret=0;
	
	open F,"<","$FileName" or die "can't open file >$FileName< - $!\n";
	
	$total=<F>; 
	die "Invalid file format >$FileName< - first line should be total: ....\n" unless ($total =~ m/total: \d+/io);
	
	$srclen+=length($total);
	
	while (<F>) {
		chomp;
		$line=$_;
		($ssite,$size,$hit,@time)=split;

		if ($TryToResolveIp) {
			$site=Aggregate(GetName($ssite));
		} else {
			$site=Aggregate($ssite) ;
		}
		
		$Modified=1 if ($ssite ne $site);

		$hSite{$site}{size}+=$size;
		$hSite{$site}{hit} +=$hit;

		for (my $h=0;$h<24;$h++) {
			($ttime,$tsize)=split /-/,$time[$h];
			$hSite{$site}{hsize}[$h]+=$tsize;
			$hSite{$site}{htime}[$h]+=$ttime;
		}
		
	}
	close F;
	
	if ($Modified) {
		my $t2=0;
		$dstfile=$total;
		foreach $site (sort {$hSite{$b}{size} <=>$hSite{$a}{size}} keys %hSite) {
			$dstfile.=sprintf ("%-29s %12s %10s\t",$site,$hSite{$site}{size},$hSite{$site}{hit});
			for ( $h = 0 ; $h < 24 ; $h++ ) {
				$dstfile.=sprintf("%d-%s ", $hSite{$site}{htime}[$h]+0,$hSite{$site}{hsize}[$h]+0);
			}
			$dstfile.="\n";
			$t2+=$hSite{$site}{size};
		}
		
		
		$total =~ m/total: (\d+)/io;
		if ($1 != $t2) {
			print "WARNING !!!!! size mismatch !!!!!\n";
		}
		
		open F,">","$FileName" or die "can't create dst file\n";
		print F $dstfile;
		close F;

#		$dstlen+=length($dstfile);
#		print "$FileName\t";
#		print "\tsrclen: $srclen\tdstlen=$dstlen\t(";
#		print -s "$FileName.patch";
#		print ")\n";  
		 $ret=-s $FileName; #return new size ...
	}
	return $ret;
}

sub GetName($) {
	my $site=shift;
	my $ret=$site;

	if ($site =~ m/\d+\.\d+\.\d+\.\d+/) {
		print "$site -> ";		 
		unless (defined $hhIP{$site}) {
			my $ia=inet_aton($site);
			$ret=gethostbyaddr($ia, AF_INET);
			$ret=$site if ($ret eq "");
			$hhIP{$site}=$ret;
		}
		$ret=$hhIP{$site};
		print "$ret\n";		 
 	}
 	return $ret;
}

sub Aggregate($) {
 	my	$site=shift;
 	if (1) {
		$site=~ s{(.*?)\.vkontakte\.ru}{vkontakte\.ru}o;
		$site=~ s{(.*?)\.vkadre\.ru}{www\.vkadre\.ru}o;
		$site=~ s{(.*?)\.top\.list\.ru}{1\.top\.list\.ru}o;
		$site=~ s{(.*?)\.myspacecdn\.com}{www\.myspacecdn\.com}o;
		$site=~ s{(.*?)\.youtube\.com}{www\.youtube\.com}o;
		$site=~ s{(.*?)\.imageshack\.us}{www\.imageshack\.us}o;
		$site=~ s{(.*?)\.photobucket\.com}{www\.photobucket\.com}o;
		$site=~ s{u\d+\.eset\.com}{updates\.eset\.com}o;
		$site=~ s{ts\d+\.eset\.com}{updates\.eset\.com}o;
		$site=~ s{89\.202\.157\.13[5-9]}{updates\.eset\.com}o;
		$site=~ s{(.*?)\.depositfiles\.com}{www\.depositfiles\.com}o;
		$site=~ s{(.*?)\.odnoklassniki\.ru}{www\.odnoklassniki\.ru}o;
		$site=~ s{(.*?)\.facebook\.com}{www\.facebook\.com}o;
		$site=~ s{download\d+\.avast\.com}{download\.avast\.com}o;
		$site=~ s{.\d+\.radikal\.ru}{cdn\.radikal\.ru}o;
		$site=~ s{.*?\.foto\.radikal\.ru}{cdn\.foto\.radikal\.ru}o;
		$site=~ s{khm\d+\.google.com}{maps\.google\.com}o;
		$site=~ s{kh\d+\.google.com}{maps\.google\.com}o;
		$site=~ s{mt\d+\.google.com}{maps\.google\.com}o;
		$site=~ s{tbn\d+\.google.com}{tbn\.google\.com}o;
		$site=~ s{mlt\d+\.google.com}{mlt\.google\.com}o;
		$site=~ s{(.*?)\.ifolder\.ru}{www\.ifolder\.ru}o;
		$site=~ s{(.*?)\.mystat-in\.net}{www\.mystat-in\.net}o;
		$site=~ s{(.*?)\.photosight\.ru}{www\.photosight\.ru}o;
		$site=~ s{(.*?)\.mylivepage\.com}{www\.mylivepage\.com}o;
		$site=~ s{(.*?)\.imagevenue\.com}{www\.imagevenue\.com}o;
		$site=~ s{(.*?)\.adskape\.ru}{www\.adskape\.ru}o;
		$site=~ s{(.*?)\.tbn\.ru}{www\\.tbn\.ru}o;
		$site=~ s{(.*?)\.fotki\.com}{www\.fotki\.com}o;
		$site=~ s{(.*?)\.deviantart\.com}{www\.deviantart\.com}o;
		$site=~ s{(.*?)\.rutube\.ru}{rutube\.ru}o;
#		$site=~ s{(.*?)\.}{www\.}o;
#		$site=~ s{(.*?)\.}{www\.}o;
#		$site=~ s{(.*?)\.}{www\.}o;
#		$site=~ s{(.*?)\.}{www\.}o;
#		$site=~ s{(.*?)\.}{www\.}o;
#		$site=~ s{(.*?)\.}{www\.}o;
#		$site=~ s{(.*?)\.}{www\.}o;
#		$site=~ s{(.*?)\.}{www\.}o;
#		$site=~ s{(.*?)\.}{www\.}o;
#		$site=~ s{(.*?)\.}{www\.}o;
#		$site=~ s{(.*?)\.}{www\.}o;
	}
	return $site;
}
