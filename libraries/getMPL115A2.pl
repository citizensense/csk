#!/usr/bin/perl
use strict;

my $I2CSET = "/usr/sbin/i2cset";
my $I2CGET = "/usr/sbin/i2cget";

system("$I2CSET -y 1 0x60 0x12 0x01");
&shortsleep(0.1);
#----- padc -----#
my $address_0 = `$I2CGET -y 1 0x60 0x00 w`;
while ( $address_0 eq "" ) {
    $address_0 = `$I2CGET -y 1 0x60 0x00 w`;
}
chomp($address_0);
my $padc = hex(substr($address_0,4,2).substr($address_0,2,2)) >> 6;
#print "0x00: $address_0\n";
#print "Padc = $padc\n";
#----- tadc -----#
my $address_2 = `$I2CGET -y 1 0x60 0x02 w`;
while ( $address_2 eq "" ) {
    $address_2 = `$I2CGET -y 1 0x60 0x02 w`;
}
chomp($address_2);
my $tadc = hex(substr($address_2,4,2).substr($address_2,2,2)) >> 6;
#print "0x02: $address_2\n";
#print "Tadc = $tadc\n";
#----- a0 -----#
my $address_4 = `$I2CGET -y 1 0x60 0x04 w`;
while ( $address_4 eq "" ) {
    $address_4 = `$I2CGET -y 1 0x60 0x04 w`;
}
chomp($address_4);
my $a0 = hex(substr($address_4,4,2).substr($address_4,2,2));
#print "0x04: $address_4\n";
$a0 = &get_frac($a0,3,0);
#print "a0: ",$a0,"\n";
#----- b1 -----#
my $address_6 = `$I2CGET -y 1 0x60 0x06 w`;
while ( $address_6 eq "" ) {
    $address_6 = `$I2CGET -y 1 0x60 0x06 w`;
}
chomp($address_6);
my $b1 = hex(substr($address_6,4,2).substr($address_6,2,2));
#print "0x06: $address_6\n";
$b1 = &get_frac($b1,13,0);
#print "b1: ",$b1,"\n";
#----- b2 -----#
my $address_8 = `$I2CGET -y 1 0x60 0x08 w`;
while ( $address_8 eq "" ) {
    $address_8 = `$I2CGET -y 1 0x60 0x08 w`;
}
chomp($address_8);
my $b2 = hex(substr($address_8,4,2).substr($address_8,2,2));
#print "0x08: $address_8\n";
$b2 = &get_frac($b2,14,0);
#print "b2: ",$b2,"\n";
#----- c12 -----#
my $address_a = `$I2CGET -y 1 0x60 0x0a w`;
while ( $address_a eq "" ) {
    $address_a = `$I2CGET -y 1 0x60 0x0a w`;
}
chomp($address_a);
my $c12 = hex(substr($address_a,4,2).substr($address_a,2,2));
#print "0x0a: $address_a\n";
$c12 = &get_frac($c12,22,2);
#print "c12: ",$c12,"\n";
my $Pcomp = $a0 + ($b1 + $c12 * $tadc) * $padc + $b2 * $tadc;
my $PhPa = ((65/1023) * $Pcomp + 50) * 10;
printf "%6.1f\n",$PhPa;

exit 0;

sub get_frac {
    my ($val,$fracbits,$zero) = @_;
    my $valsign = 1;
    if ($val & 0x8000) {
	$valsign = -1; # sign
	$val = ~$val + 1;
    }
    $val = $val >> $zero if ($zero);
    my $valfrac = 0;
    my $mask = 0x0001;
    for (my $i=$fracbits;$i>0;$i--) {
	$valfrac += 1/(2**$i) if ($val & $mask);
	$mask <<= 1;
    }
    my $valint = ($val & 0x7fff) >> $fracbits;

    return $valsign * ($valint + $valfrac);
}

sub shortsleep {
    my $s = shift;
    select(undef,undef,undef,$s);    
}

__END__
