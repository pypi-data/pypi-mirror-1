#!/usr/local/bin/perl -w -I/home/gpk/bin --

package wnpp;
require 5.002;

use wnpp_combine;

my %cache;

sub expand_word($)
{
 my $w = shift;
 # print STDERR "INFO: Wnpp: $w\n";
 if(exists($cache{$w}))	{
	return @{$cache{$w}};
	}
 return wnpp_combine::expand_word($w);
}

1;
