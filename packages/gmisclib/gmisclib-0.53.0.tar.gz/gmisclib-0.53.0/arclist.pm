#!/usr/local/bin/perl -w --

package arclist;
require 5.002;

my $iraf_shift = 1;	# Coordinates are in IRAF (1) origin, not FOCAS(0)

use parsedata;

sub get_coordfiles($)
{
 my $f = shift;
 my @cfl;
 open(AL, "<$f") or die "No open arclist=$f";
 my $x;
 while(defined($x=<AL>))	{
	my %a = ::parse($x);
	if(exists($a{arc}))	{
		push(@cfl, $a{arc});
	}
	elsif(exists($a{match}))	{
		push(@cfl, split(' ', $a{match}));
	}
 }
 close(AL);
 return @cfl;
}



sub read_coordfile($)
{
	my $coordfile = shift;
	my ($z, $rxyl, $rxye) = read_coordfile_all($coordfile);
	return ($z, @$rxyl);
}


sub read_coordfile_all($)
{
	my $coordfile = shift;
	my @xylist = ();
	my @xyexcl = ();
    	my $z_source = undef();

	open(COORD, "<$coordfile") or die "cannot open $coordfile: $! ";
	my $line;
	while (defined($line=<COORD>)) {
	    # Allow for comments:
	    chomp($line);
	    $line =~ s/#.*//;
	    next if($line =~ m'^\s*$');
	    if($line =~ m'^\s*z\s*=\s*(\w+)\s*#?'i)	{
		$z_source = $1;
		next;
	    }

	    if($line =~ m'^ POINT\(\s*([0-9eE.+-]+)\s*,\s*([0-9eE.+-]+)\s*\)')	{
		my ($x1, $y1) = ($1, $2);
	    	push @xylist, [$x1-$iraf_shift, $y1-$iraf_shift];
	    }
	    elsif($line =~ m'^-POINT\(\s*([0-9eE.+-]+)\s*,\s*([0-9eE.+-]+)\s*\)')	{
		my ($x1, $y1) = ($1, $2);
	    	push @xyexcl, [$x1-$iraf_shift, $y1-$iraf_shift];
		}
	    else	{
		my ($x1, $y1) = split(" ", $line);
	    	push @xylist, [$x1-$iraf_shift, $y1-$iraf_shift];
	    }
	}
 close(COORD);
 return ($z_source, \@xylist, \@xyexcl);
}





sub minx(@)
{
 my $rv = 1e30;
 my $r;
 foreach $r (@_)	{
	if($r->[0] < $rv)	{
		$rv = $r->[0];
		}
	}
 int($rv-0.6);
}


sub maxx(@)
{
 my $rv = -1e30;
 my $r;
 foreach $r (@_)	{
	if($r->[0] > $rv)	{
		$rv = $r->[0];
		}
	}
 int($rv+0.6);
}


sub miny(@)
{
 my $rv = 1e30;
 my $r;
 foreach $r (@_)	{
	if($r->[1] < $rv)	{
		$rv = $r->[1];
		}
	}
 int($rv-0.6);
}


sub maxy(@)
{
 my $rv = -1e30;
 my $r;
 foreach $r (@_)	{
	if($r->[1] > $rv)	{
		$rv = $r->[1];
		}
	}
 int(0.6+$rv);
}

1;
