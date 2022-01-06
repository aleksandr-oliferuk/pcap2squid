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

require "lightsquid.cfg";
require "common.pl";

if (!eval { require GD }) {
	print "Content-Type: text/html\n\n";
	MyDie("LightSquid can't show graphics report ...<br>GD-GRAPH library is unavailable, please install it or set \$graphreport=0 in lightsquid.cfg for disable graphics ...")
}

use GD;

use CGI;
use CGI::Carp qw (fatalsToBrowser);

$co = new CGI;

$year  = $co->param('year');
$month = $co->param('month');
$user  = $co->param('user');
$mode  = $co->param('mode');
$png   = $co->param('png');

$mminy=60-50;
$mmaxy=420-50;

my @MAP;

sub fixnum($) {
    my $num = shift;

    if ( $num >= 1000 * 1024 * 1024 * 1024 ) { return sprintf( "%3.1fT", $num / ( 1024 * 1024 * 1024 * 1024 ) ); }
    if ( $num >= 1000 * 1024 * 1024 )        { return sprintf( "%3.1fG", $num / ( 1024 * 1024 * 1024 ) ); }
    if ( $num >= 1024 * 1024 )               { return sprintf( "%3dM", int( $num / ( 1024 * 1024 ) ) ); }
    return sprintf( "%3dK", int( $num / (1024) ) );
} ## end sub fixnum($)

sub GetY($) {
    my $value    = shift;
    my $all      = $mmaxy - 30;
    my $diapazon = 5;
    my $indep    = $all / $diapazon;

    my $tmp = $all / $max;

    if ( $max < $value ) { $value = $max; }

    my $y = $mmaxy - $value * $tmp;

    return int($y);
} ## end sub GetY($)

sub bar($$) {
    my $day   = shift;
    my $value = shift;

    my $xx = 44 + $day * 20;

    $value = 1 if ( $value == 0 );

    $maxaverage+=$value;
    $maxaverageday++;

    my $y = GetY($value);
        
    # add data for MAP structure
    if ($png == 0) {
	my $xx2=$xx+17;
	my $yy2=$mmaxy+5;
	$MAP[$day]="$xx, $y, $xx2,$yy2";
        $maxcntr++ if ( $value > $max );
	return;
    }

    $im->filledRectangle( $xx, $y, $xx + 11, $mmaxy + 5, $bcolor3 );    # main BAR

    my $poly1 = new GD::Polygon;
    $poly1->addPt( $xx + 7,  $y - 5 );
    $poly1->addPt( $xx,      $y );                                      # top 3d polygon
    $poly1->addPt( $xx + 11, $y );
    $poly1->addPt( $xx + 17, $y - 5 );
    $im->filledPolygon( $poly1, $bcolor1 );

    my $poly2 = new GD::Polygon;
    $poly2->addPt( $xx + 17, $y - 5 );
    $poly2->addPt( $xx + 11, $y );                                      # right 3d BAR
    $poly2->addPt( $xx + 11, $mmaxy + 6 );
    $poly2->addPt( $xx + 17, $mmaxy );
    $im->filledPolygon( $poly2, $bcolor2 );

    #text box
    if ( $value < $max ) { $textcolor = $dimgray; $boxcolor = $goldenrod; }
    else { $textcolor = $white; $boxcolor = $red; }

    $im->line( $xx + 8, $y - 2, $xx + 8, $y - 10, $dimgray );
    $im->filledRectangle( $xx - 2, $y - 20, $xx + 18, $y - 10, $boxcolor );
    $im->rectangle( $xx - 2, $y - 20, $xx + 18, $y - 10, $goldenrod2 );

    $im->string( gdTinyFont, $xx - 1, $y - 19, fixnum($value), $textcolor );

    undef $poly1;
    undef $poly2;
} ## end sub bar($$)

sub InitGraph() {

    # allocate some colors
    $white      = $im->colorAllocate( 255, 255, 255 );
    $red        = $im->colorAllocate( 255,   0,   0 );
    $lavender   = $im->colorAllocate( 230, 230, 250 );
    $white      = $im->colorAllocate( 255, 255, 255 );
    $gray       = $im->colorAllocate( 192, 192, 192 );
    $silver     = $im->colorAllocate( 211, 211, 211 );
    $black      = $im->colorAllocate(   0,   0,   0 );
    $blue       = $im->colorAllocate(  35,  35, 227 );
    $dimgray    = $im->colorAllocate( 105, 105, 105 );
    $darkblue   = $im->colorAllocate(   0,   0, 139 );
    $goldenrod  = $im->colorAllocate( 234, 234, 174 );
    $goldenrod2 = $im->colorAllocate( 207, 181,  59 );

    %colors = (
	blue 	=> [ [  62,  80, 167 ], [  40,  51, 101 ], [  57,  73, 150 ] ],
	green	=> [ [ 120, 166, 129 ], [  84, 113,  82 ], [ 158, 223, 167 ] ],
	yellow	=> [ [ 185, 185,  10 ], [ 111, 111,  10 ], [ 166, 166,  10 ] ],
	brown	=> [ [  97,  45,  27 ], [  60,  30,  20 ], [  88,  41,  26 ] ],
	red	=> [ [ 185,  10,  10 ], [ 111,  10,  10 ], [ 166,  10,  10 ] ],
	orange	=> [ [ 255, 233, 142 ], [ 220, 163,  72 ], [ 255, 198, 107 ] ],
    );

    ${bcolor.$_} = $im->colorAllocate( @{ $colors{$barcolor}[$_-1] } ) for (1..3);

    $im->rectangle( 0, 0, 719, $mmaxy + 39, $dimgray );    #border
    $im->filledRectangle( 60, $mminy, 700, $mmaxy, $silver );    #main area

    $poly1 = new GD::Polygon;                                    #left 3d border
    $poly1->addPt( 50, $mminy + 5 );
    $poly1->addPt( 50, $mmaxy + 5 );
    $poly1->addPt( 60, $mmaxy );
    $poly1->addPt( 60, $mminy );
    $im->filledPolygon( $poly1, $gray );

    $poly2 = new GD::Polygon;                                    #down 3d border
    $poly2->addPt( 60,  $mmaxy );
    $poly2->addPt( 50,  $mmaxy + 5 );
    $poly2->addPt( 690, $mmaxy + 5 );
    $poly2->addPt( 700, $mmaxy );
    $im->filledPolygon( $poly2, $gray );

    $im->line( 50,  $mminy + 5, 50,  $mmaxy + 10, $black );      #black outer
    $im->line( 45,  $mmaxy + 5, 690, $mmaxy + 5,  $black );
    $im->line( 50,  $mmaxy + 5, 60,  $mmaxy,      $black );
    $im->line( 60,  $mmaxy,     60,  $mminy,      $black );
    $im->line( 700, $mminy,     700, $mmaxy,      $black );
    $im->line( 690, $mmaxy + 5, 700, $mmaxy,      $black );

    $im->line( 60, $mmaxy, 700, $mmaxy, $black );

    #bottom border grid
    for ( $x = 70 ; $x <= 680 ; $x += 20 ) { $im->line( $x, $mmaxy + 5, $x, $mmaxy + 8, $dimgray ); }

    #print days
    $weekday=GetWeekDayDate("$year$month"."01");
    $x = 65;
    for ( $i = 1 ; $i <= 31 ; $i++ ) {
        $color=$dimgray;
        $color=$red if ($weekday==0);
	$color=$red if (($weekday==6) && ($weekendmode eq "both"));	
	$weekday++;
	$weekday=0 if ($weekday==7);

        $im->string( gdSmallFont, $x - 1, $mmaxy + 8, sprintf( "%02d", $i ), $color );

        $x += 20;
    } ## end for ( $i = 1 ; $i <= 31...

    #legend
    #50M   show line and value at value 50mb
    #50M-  show only line
    #50M.  skip this value

    #MONTH
    $gridvalues{month} = [ "50M-", "100M", "150M-", "200M", "250M-", "300M", "350M-", "400M", "450M-", "500M", "550M.", "600M", "700M", "800M", "900M", "1G", "2G", "3G", "4G", "5G", "6G", "7G", "8G", "9G" , "10G" , "15G" , "20G", "25G", "30G" ];

    #USER
    $gridvalues{user} = [ "5M", "10M", "15M", "20M", "25M", "30M", "35M", "40M", "45M", "50M", "55M", "60M.", "70M", "80M.", "90M", "1G", "2G", "3G", "4G", "5G" ];

    $hh{"K"} = 1024;
    $hh{"M"} = 1024 * 1024;
    $hh{"G"} = 1024 * 1024 * 1024;
    $hh{"T"} = 1024 * 1024 * 1024 * 1024;

    for ( $i = 0 ; $i < $#{ $gridvalues{$mode} } + 1 ; $i++ ) {
        $gridvalues{$mode}[$i] =~ m/(\d*)(\D)([\.-])?/;

        $flag = $3;
        next if ( $flag eq "." );

        $v = $1 * $hh{$2};
        $y = GetY($v) - 5;

        next if ( $v > $max );

        $im->line( 60, $y, 700, $y, $dimgray );

        $im->line( 50, $y + 5, 60, $y, $dimgray );
        $im->line( 47, $y + 5, 50, $y + 5, $dimgray );

        next if ( $flag eq "-" );

        $im->string( gdSmallFont, 21, $y - 2, fixnum($v), $dimgray );
    } ## end for ( $i = 0 ; $i < $#{...

    #axis name
    $im->stringUp( gdLargeFont, 20 - 15, 248 - 9, "BYTES", $dimgray );
    $im->string( gdLargeFont, 330 + 15, $mmaxy + 20, "DAYS", $dimgray );
} ## end sub InitGraph($$$)


####################################################################################

if ( $mode eq "user" )  { $max = $graphmaxuser; $varname="graphmaxuser";}
if ( $mode eq "month" ) { $max = $graphmaxall;  $varname="graphmaxall";}

$max=1 if ($max == 0); #div0 protection

if ( $png == 1 ) {
    print "Content-type: image/png\n\n";
    # create a new image
    $im = new GD::Image( 720, $mmaxy + 40 );
    InitGraph();
} else {
    print "Content-Type: text/html\n\n";

    InitTPL("graph",$co->param('tpl'));
    $workperiod = "$MonthName[$month] $year";
    ReplaceTPL( WORKPERIOD, $workperiod );

    $graphicsurl = "graph.cgi?png=1\&year=$year\&month=$month\&mode=$mode";
    $graphicsurl .= "\&user=$user" if ( $mode eq "user" );
    ReplaceTPL( GRAPHICSURL, URLEncode($graphicsurl) );

    if ( $mode eq "month" ) {
        $txtmode = "##MSG_WHOLE## ##MSG_MONTH##";
    }
    else {
        $txtmode = "##MSG_USER## \"$user\"";
    }
    ReplaceTPL( MODE, $txtmode );
}


$average = 0;
$days    = 0;
$filter  = "$year$month";
@daylist = glob("$reportpath/$filter*");
foreach $daypath ( sort @daylist ) {
    open FF, "<$daypath/.total";
    $tmp  = <FF>;
    $size = <FF>;
    chomp $size;
    $size    =~ s/^size: //;
    $daypath =~ m/(\d\d\d\d)(\d\d)(\d\d)/;

    if ( $mode eq "month" ) {
        bar( $3, $size );
        $average += $size;
    }
    elsif ( $mode eq "user" ) {
        while (<FF>) {
            ( $user_, $size, $hit ) = split;
            if ( $user_ eq $user ) { bar( $3, $size ); $average += $size; }
        }
    } ## end elsif ( $mode eq "user" )
    $days++;
    close FF;
} ## end foreach $daypath ( sort @daylist)

if ( $png == 1 ) {

    #average bar
    if ( $days > 0 ) {
        $y = GetY( int( $average / $days ) );
        $im->line( 60, $y, 700, $y, $red );
        $im->line( 56, $y + 2, 60, $y, $red );

    } ## end if ( $days > 0 )

    binmode STDOUT;

    # Convert the image to PNG and print it on standard output
	print eval {$im->png} || $im->gif; #use gif if png not supported by libgd (Konstantin M. Mefodichev)

} ## end if ( $png == 1 )
else {
  
    $url=($mode eq "user")?"user_detail.cgi":"day_detail.cgi";
    $url.=qq(?year=$year&month=$month);
    $url.=($mode eq "user")?"\&user=$user":"";
    $url = URLEncode($url);
    		
    $day="00";
    for ($i=1;$i<$#MAP+1;$i++) {
	$day++;
	$tmp=$hTPL{imagemap};
        $tmp=~s/##MAPURL##/$url\&day=$day/;
        $tmp=~s/##MAPCOORD##/$MAP[$i]/;
	$tpl{imagemap} .= $tmp;    	
    }

    ReplaceTPL( IMGMAP, $imgmap );


    $maxaverage /= ($maxaverageday+1);
    ReplaceTPL( VARVALUE,sprintf("%1.2f",int(($maxaverage+($maxaverage*0.30))/(1024*1024*1024/10)+1)/10));
    ReplaceTPL( VARNAME,$varname);
    HideTPL("warning") if ($maxcntr < 7);

    ApplyTPL();
    PrintTPL();

} ## end else [ if ( $png == 1 )

__END__
2005-11-07 ADD : some HW perl trick
2005-11-07 ADD : url encode
2006-06-28 ADD : &tpl= support
2006-09-05 ADD : warning and recomended max value
2006-09-13 ADD : error to browser
2006-11-23 ADD : FIX recomendation warning
2008-11-28 FIX : try to use gif if png not supported by libgd
			   : div0 protection added
2008-12-14 FIX : No more err500 in browser if no GD is installed
           ADD : Terabyte support ;)			
