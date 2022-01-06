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
push (@INC,(fileparse($0))[1]);

use CGI;
require "lightsquid.cfg";
require "common.pl";

$co=new CGI;

$content=  "text/html";

$css=$co->param('css');if ($css ne "") {$content=  "text/css"; $file="$css.css";       }  
$png=$co->param('png');if ($png ne "") {$content= "image/png"; $file="images/$png.png";}  
$gif=$co->param('gif');if ($gif ne "") {$content= "image/gif"; $file="images/$gif.gif";}  
$jpg=$co->param('jpg');if ($jpg ne "") {$content="image/jpeg"; $file="images/$jpg.jpg";}  
CheckNewTPL($co->param('tpl'));

open F,"<","$tplpath/$templatename/$file" or MyDie("$!\n");
binmode F;
local $/;
$body=<F>;
close F;

binmode STDOUT;  
print "Content-Type: $content\n\n";
print $body;

__END__
2005-09-16 ADD : Inital release for v 1.6
2006-06-28 ADD : die -> MyDie
2006-06-28 ADD : &tpl= support
