#!/usr/local/bin/perl -w -I/home/gpk/bin --

package wnpp_combine;

use wnpp_local;
use wnpp_rules;
use wnpp_wn;

$nospace = 1;

sub expand_word($)
{
my $w = shift;
# print STDERR "INFO: wnpp_combine: $w\n";

my @o = wnpp_rules::expand_word($w);
if($#o >= 0)	{
	return @o;
	}

@o = wnpp_local::expand_word($w);
push @o, wnpp_wn::expand_word($w);

return normalize_probabilities(@o);
}


sub normalize_probabilities(@)
{
	my $sum = 0;
	my $x;
	foreach $x (@_)	{
		if(exists($x->{p}))	{
			$sum += $x->{p};
			}
		else	{
			$sum += 1;
			$x->{p} = 1;
			}
		}

	foreach $x (@_)	{
		$x->{p} /= $sum;
		}

	return @_;
}

1;
