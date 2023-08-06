#! /usr/bin/perl
#
# Script from RECIA : http://recia.fr

use Net::IPAddress;
use Getopt::Long;

my $ip;
my $help;
my $number;


GetOptions (
            "ip=s" => \$ip,
            "number=i" => \$number,
            "help" =>\$help,
            "verbose" =>\$verbose
);


my $usage = "
USAGE:-i [-h|--help]
 
PARAMS :    -i                  IP
            -n                  Nombres d'adresses MAC <257
 
OPTIONS :
            -h or --help         print this help
            -v or --verbose      Verbose
 
";

if ( $help || ! $ip || $number > 256 ) {
        print $usage;
        exit(0);
}

$number = 1 if (! $number);

my $hex_ip = sprintf('%X',ip2num($ip));
$hex_ip="0$hex_ip" if length($hex_ip) == 7 ;

while ($number) {
        $number--;
        $number_hex = sprintf('%X',$number);
        $number_hex="0$number_hex" if length($number_hex) == 1 ;
        $macaddress="40:".$number_hex.":".substr($hex_ip,0,2).":".substr($hex_ip,2,2).":".substr($hex_ip,4,2).":".substr($hex_ip,6,2);
        print $macaddress."\n";
}
