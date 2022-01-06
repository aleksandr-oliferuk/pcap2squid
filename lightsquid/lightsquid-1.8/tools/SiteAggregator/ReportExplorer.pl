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

# "Service" script for "SiteAggregator.pl"
# script generate several statistic from you "Report" folder
# for detecting "Garbage" domain
# you can use this information for extending "Aggregator" function in "SiteAggregator.pl"


#2008-12-18 Sergey Erokhin aka ESL.

use File::Find;
require "../../lightsquid.cfg";


find({ wanted => \&process, no_chdir=>1 }, "$reportpath/");

sub process() {
  next if (m{\/\.});
  next unless (m{\/\d+\/});
#  print "$_\n";
  GetFileContent($_);
}

sub GetFileContent($) {
	my $file=shift;
	open F,"<$file" or die "can't open '$file'";
	<F>; #skip total
	while (<F>) {
		($site,@other)=split;

		if (0) {
			$site=~ s{(.*?)\.vkontakte\.ru}{www\.vkontakte\.ru}o;
			$site=~ s{(.*?)\.top\.list\.ru}{1\.top\.list\.ru}o;
			$site=~ s{(.*?)\.myspacecdn\.com}{www\.myspacecdn\.com}o;
			$site=~ s{(.*?)\.youtube\.com}{www\.youtube\.com}o;
			$site=~ s{(.*?)\.imageshack\.us}{www\.imageshack\.us}o;
			$site=~ s{(.*?)\.photobucket\.com}{www\.photobucket\.com}o;
			$site=~ s{u\d+\.eset\.com}{updates\.eset\.com}o;
			#		$site=~ s{(.*?)\.}{www.}o;
			#		$site=~ s{(.*?)\.}{www.}o;
		}

		if ($site =~ m{((.*)\.)?(.*?)\.(.*?)$}) {
			$l1="$3.$4";
			$l2=$2;
			
			$l2="." if ($l2 eq "");
			$hDOMAIN{$l1}{$l2}++;
			
		}else{
			print "ERR? :: $site\n";
		}
	}
	close F;
}

foreach $l1 (sort keys %hDOMAIN) {
    $subdomain=0;
	foreach $l2 (sort  {$hDOMAIN{$l1}{$b} <=> $hDOMAIN{$l1}{$a}} keys %{$hDOMAIN{$l1}}) {
		$subdomain++;
	}
	$hSub{$l1}=$subdomain;
}

foreach $l1 (sort {$hSub{$b} <=> $hSub{$a}} keys %hSub) {
	next if ($hSub{$l1}<50);
	print "$l1\t$hSub{$l1}\n";
}

foreach $l1 (sort {$hSub{$b} <=> $hSub{$a}} keys %hDOMAIN) {
	next if ($hSub{$l1}<50);
	print "$l1 ($hSub{$l1})\n";
	foreach $l2 (sort  {$hDOMAIN{$l1}{$b} <=> $hDOMAIN{$l1}{$a}} keys %{$hDOMAIN{$l1}}) {
		print "\t\t$l2\t$hDOMAIN{$l1}{$l2}\n";
	}
}
