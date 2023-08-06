#!/usr/local/bin/perl -w --

package findpath;

sub find($)
{
	my $f = shift;
	die if(!defined($f) or $f eq '');
	my $d;
	foreach $d (split(':', $ENV{'PATH'})) {
		my $p = "$d/$f";
		if( -x $p ) {
			return $p;
		}
	}
	return undef();
}

1;
