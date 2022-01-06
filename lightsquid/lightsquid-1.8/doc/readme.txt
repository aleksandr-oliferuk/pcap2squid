Light Squid  - light squid report parser and visualizer, generate sort of report

	light
	fast
	no database required
	no additional perl modules
        small disk usage
	template html - you can create you own look;
	
read install.txt for instalation instruction
read version.txt for new features

____________________________________________________________________________________
LightSquid generate various report type
       
       index.cgi show current year & month, also show all day with report data 
       
       Date  		  USERS  OVERSIZE  	BYTES  	 AVERAGE  	CACHE HIT %
       18 Apr 2005 [grp]   76       10     419 501 879   5 519 761	      5.11%
       17 Apr 2005 [grp]   23        6     321 906 050 	13 995 915            8.02%

       all hyperlink on page - do some report !
       link under TOTAL size - generate WHOLE MONTH report
       
       you may select another month
       you may select another year
       
       if you click any year - report period - whole year
       link under TOTAL size - generate WHOLE YEAR report
       
       hyperlink under date - show day statistic with user
       [grp] - show day statistic with additional group order
       (you may hide [grp] link in lightsquid.cfg)
       
       if enabled in config OVERSIZE - 
       show how many user exceed per day limit - under link - per user rport
       
   
       day_detail.cgi
       
       topsites link - generate list all sites (where walk all users)
       number limited in config gile
       you may order list by size or by hit
       also you may look [who] explore this site.
       
       bigfiles link - show user & link where url exceed config variable
       useful for check what user download
       
       also you may view user detail report ;-)
       total - cummulative summ
       
___________________________________________________________________________________
ip2name notes

        you have personal configuration, i don't know it ;-)
	
	some examples see in ip2name folder

____________________________________________________________________________________
file structure

	.htaccess		apache control file 

config file
-----------
	lightsquid.cfg		main config file
	group.cfg		group definition file for simple variant ;-))

log parser
----------
	lightparser.pl		access.log parser, generate report in `Report` folder
	

web part
--------
	index.cgi		date selector		
          month_detail.cgi      whole month report
	   day_detail.cgi	day info panel
  	   day_detail_grp.cgi	day info panel order by dep.
	     user_detail.cgi	user detail report
	       bigfiles.cgi	big files report
	       topsites.cgi     top sites report
	        whousesite.cgi  top site -> who use module
	common.pl		common subs (template engine and other)

	tpl\
	    base\		template engine templates ;-)


        ip2name\		example ip2name function
	