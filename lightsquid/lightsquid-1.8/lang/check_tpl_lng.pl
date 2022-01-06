#/bin/perl

$lang=lc $ARGV[0];
$lang =~ s/\.lng//i;
$lang="eng" if ($lang eq "");

$tpl=lc $ARGV[1];
$tpl="base" if ($tpl eq "");

sub ReadTPL() {
  my @filename=glob("../tpl/$tpl/*.html");
  my $body;
  local $/;
  foreach $name (@filename) {
#    print "name: $name\n";
    open FF,"<","$name" or die "can't open file $name\n";
    $body=<FF>;
    close FF;
    while ($body =~ m/##(MSG.*?)##/gs) {
#      print "\t$1\n";;
      $hMSG{$1}+=$1;
      $hFILE{$1}{$name}=1;
    }
  }
}

sub ReadCGI() {
  my @filename=glob("../*.cgi");
  my $body;
  local $/;
  foreach $name (@filename) {
#    print "name: $name\n";
    open FF,"<","$name" or die "can't open file $name\n";
    $body=<FF>;
    close FF;
    while ($body =~ m/##(MSG.*?)##/gs) {
#      print "\t$1\n";;
      $hMSG{$1}+=$1;
      $hFILE{$1}{$name}=1;
    }
  }
}

$hMSG{"MSG_MONTH01"}=$hMSG{"MSG_MONTH02"}=$hMSG{"MSG_MONTH03"}=$hMSG{"MSG_MONTH04"}=1;
$hMSG{"MSG_MONTH05"}=$hMSG{"MSG_MONTH06"}=$hMSG{"MSG_MONTH07"}=$hMSG{"MSG_MONTH08"}=1;
$hMSG{"MSG_MONTH09"}=$hMSG{"MSG_MONTH10"}=$hMSG{"MSG_MONTH11"}=$hMSG{"MSG_MONTH12"}=1;


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
 $hLNG{$lname}=$lvalue;
}
close F;

ReadTPL();
ReadCGI();

print "Check 1, all defination in templates must be in LNG file ...\n";
foreach $msg (sort keys %hMSG) {
  unless (defined $hLNG{$msg}) {
    print "\"$msg\" (en:\"$hENG{$msg}\") used in \n";
    foreach $file (sort keys %{$hFILE{$msg}}) {
         print "\t\t\t$file\n";
         $cnt1++;
    }
  } 
}
print "passed, All OK\n"            if ($cnt1 == 0);
print "failed, $cnt1 error found\n" if ($cnt1 != 0);

print "\nCheck 2, check unused defination in LNG file ...\n";
foreach $msg (sort keys %hLNG) {
  unless (defined $hMSG{$msg}) {
    print "\"$msg\" defined, but not use\n";
    $cnt2++;
  } 
}
print "passed, All OK\n"            if ($cnt2 == 0);
print "failed, $cnt2 error found\n" if ($cnt2 != 0);
