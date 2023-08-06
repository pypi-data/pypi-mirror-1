#!/usr/local/bin/perl -w -I/home/gpk --
package m22;

sub ::transpose
{
 my ($a00, $a01, $a10, $a11) = @_;
 ($a00, $a10, $a01, $a11);
}


sub ::det
{
 my ($a00, $a01, $a10, $a11) = @_;
 $a00*$a11 - $a01*$a10;
}


sub ::inv
{
 my ($a00, $a01, $a10, $a11) = @_;
 my $d = det(@_);
 die "det($a00, $a01, $a10, $a11) = $d<= 0\n" if(!($d>0));
 ($a11/$d, -$a01/$d, -$a10/$d, $a00/$d);
}


sub ::mult
{
 die "Wrong args to mult: @_ \n" unless($#_ == 7);
 my ($a00, $a01, $a10, $a11, $b00, $b01, $b10, $b11) = @_;
 ($a00*$b00+$a01*$b10, $a00*$b01+$a01*$b11,
	$a10*$b00+$a11*$b10, $a10*$b01+$a11*$b11);
}


1;
