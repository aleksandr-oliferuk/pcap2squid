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

print "LightSquid lang file check utilite. compare your lang file with ENG file\n";

$lang=lc $ARGV[0];
$lang =~ s/\.lng//i;

if ($lang eq "") {
  print "usage check_lang LANG\n";
  print "      check_lang ru\n";
  exit (-1);
}

print "check \"$lang.lng\" file\n";

open F,"<eng.lng" or die "can't open language file eng.lng - $!\n";
while (<F>) {
 chomp;
 next if (/^#/);
 ($lname,$lvalue)=split /=/,$_,2;
 $hENG{$lname}=$lvalue;
}
close F;

open F,"<$lang.lng" or die "can't open language file $lang.lng - $!\n";
while (<F>) {
 chomp;
 next if (/^#/);
 ($lname,$lvalue)=split /=/,$_,2;
 $hFILE{$lname}=$lvalue;
}
close F;

foreach $key (sort keys %hENG) {
  unless (defined $hFILE{$key}) {
    $notdefined .= "\t$key\n";
  }
}
print "\nnot defined in $lang.lng:\n $notdefined\n" if ($notdefined ne "");

foreach $key (sort keys %hFILE) {
  unless (defined $hENG{$key}) {
    $mistype .= "\t$key\n";
  }
}
print "\nnot defined in eng.lng - mistype ?? :\n $mistype\n" if ($mistype ne "");



