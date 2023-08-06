#!/usr/local/bin/perl -w -I/home/gpk/bin --

use expint;	# Local part of exponential integration.
require 5.002;

package integrate_exp;

# integrates exp(f(x))

sub integrate($$$$$)
{
 my ($f, $range_low, $range_high, $nmin, $farg) = @_;

 my @x;
 my $i;
 for($i=0; $i<$nmin; $i++)	{
	my $x = (0.5+$i)*($range_high-$range_low)/$nmin + $range_low;
	push @x, $x;
	}
 return integratea($f, $range_low, $range_high, \@x, $farg);
}


sub integratea2($$$$$)
{
 my ($f, $range_low, $range_high, $rxy, $farg) = @_;
 my $r;
 my @x;
 foreach $r (@$rxy)	{
	push @x, $r->[0];
	}
 return integratea($f, $range_low, $range_high, \@x, $farg);
}



sub integratea($$$$$)
{
 my ($f, $range_low, $range_high, $rx, $farg) = @_;

 # print STDERR "n=$#$rx\n";
 my @xy;
 my $x;
 foreach $x (@$rx)	{
	my $y = &$f($x, $farg);
	# print STDERR "x=$x, y=$y\n";
	push @xy, [$x, $y];
	}
 # print STDERR "n=$#xy\n";
 my ($pass, $lastsum);
 for($pass = 0; ; $pass++)	{
	my $i;
	# print STDERR "in loop n=$#xy\n";
	my @s = sort { $a->[0] <=> $b->[0]; } @xy;
	# print STDERR "s.n=$#s\n";
	my $max = $s[0]->[1];
	for($i=1; $i<=$#s; $i++)	{
		# print STDERR "i=$i s= $s[$i]->[0], $s[$i]->[1]\n";
		if($max < $s[$i]->[1])	{
			$max = $s[$i]->[1];
			}
		}
	my $sum = integrate_fixed_guts($range_low, $range_high, @s);
	if($pass>5 || ($pass>1 && $sum<1.001*$lastsum && $sum>0.999*$lastsum)) {
		return $sum;
		}
	# print STDERR "s.n=$#s\n";
	my @extra1;
	for($i=1; $i<$#s; $i++)	{
		my $ex_x = expint::parabx($s[$i-1]->[0], $s[$i-1]->[1],
							$s[$i]->[0], $s[$i]->[1],
							$s[$i+1]->[0], $s[$i+1]->[1]);
		my $ex_y = expint::paraby($s[$i-1]->[0], $s[$i-1]->[1],
							$s[$i]->[0], $s[$i]->[1],
							$s[$i+1]->[0], $s[$i+1]->[1]);
		my $dm = ($s[$i-1]->[0] - $s[$i]->[0]) * ($i==1 ? 1 : 0.75);
		my $dp = ($s[$i+1]->[0] - $s[$i]->[0]) * ($i==$#s ? 1 : 0.75);
		my $ox = $ex_x - $s[$i]->[0];
		my $yl1 = $s[$i]->[1] + 0.2/($pass+1);
		my $yl2 = defined($max) ? $max + 0.1/($pass+1) : $yl1;
		my $yl3 = $s[$i]->[1] - 0.2/($pass+1);
		if($ox > $dm  &&  $ox < $dp && abs($ox)>0.01*($dp-$dm)
				&&  ($ex_y > $yl1  || $ex_y>$yl2 || $ex_y<$yl3))	{
			my $y = &$f($ex_x, $farg);
			# print STDERR "push ex1, $ex_x, $y\n";
			push @extra1, [$ex_x, $y];
			}
		}
	@s = sort { $a->[0] <=> $b->[0]; } (@s, @extra1);
	# print STDERR "3 s.n=$#s\n";
	my @extra2;
	for($i=1; $i<$#s; $i++)	{
		my $lp = $s[$i-1]->[1]
				+ ($s[$i+1]->[1] - $s[$i-1]->[1])
				  * ($s[$i]->[0] - $s[$i-1]->[0])
				  / ($s[$i+1]->[0] - $s[$i-1]->[0]);
		if(abs($lp - $s[$i]->[1]) > 0.5/($pass + 1))	{
			my $xt1 = 0.67*$s[$i]->[0] + 0.33*$s[$i+1]->[0];
			push @extra2, [$xt1, &$f($xt1, $farg)];
			# print STDERR "push ex2, $xt1\n";
			my $xt2 = 0.67*$s[$i]->[0] + 0.33*$s[$i-1]->[0];
			push @extra2, [$xt2, &$f($xt2, $farg)];
			# print STDERR "push ex2, $xt2\n";
			}
		}
	@s = sort { $a->[0] <=> $b->[0]; } (@s, @extra2);
	my @extra3;
	if($s[1]->[0] - $s[0]->[0] > $s[0]->[0]-$range_low)	{
		my $xt = 0.5*$s[0]->[0] + 0.5*$range_low;
		push @extra3, [$xt, &$f($xt, $farg)];
		# print STDERR "push ex3, $xt\n";
		}
	if($s[$#s]->[0] - $s[$#s - 1]->[0] > $range_high - $s[$#s]->[0])	{
		my $xt = 0.5*$s[$#s]->[0] + 0.5*$range_high;
		push @extra3, [$xt, &$f($xt, $farg)];
		# print STDERR "push ex3, $xt\n";
		}
	@xy = (@s, @extra3);

	my $ne = $#extra1 + 1 + $#extra2 + 1 + $#extra3 + 1;
	if($ne == 0  && $pass>2)	{
		return $sum;
		}
	if($ne > 0  || !defined($lastsum))	{
		$lastsum = $sum;
		}
	}
 return undef();
}



# This integrates from a fixed set of [x y] measurements.
# It does not assume that the data is sorted or anything.
sub integrate_fixed($$@)
{
	my ($range_low, $range_high, @s) = @_;
	my @ss = sort {$a->[0] <=> $b->[0]; } @s;
	die if($ss[0]->[0] > $ss[$#ss]->[0]);
	my $i;
	for($i=0; $i<=$#ss && $ss[0]->[0]<$range_low; $i++)	{
		shift @ss;
	}
	for($i=$#ss; $i>=0 && $ss[$#ss]->[0]>$range_high; $i++)	{
		pop @ss;
	}
	return integrate_fixed_guts($range_low, $range_high, @ss);
}


# We assume that the things to integrate are sorted, and are all
# between range_low and range_high.
sub integrate_fixed_guts($$@)
{
	my ($range_low, $range_high, @s) = @_;

	my $sum = 0;
	my $i;
	for($i=1; $i<$#s; $i++)	{
		my $tmp = expint::localint($s[$i-1]->[0], $s[$i-1]->[1],
						$s[$i]->[0], $s[$i]->[1],
						$s[$i+1]->[0], $s[$i+1]->[1]);
		# print STDERR "Summing around $s[$i]->[0], $s[$i]->[1] increments $sum by $tmp\n";
		$sum += $tmp;
	}
	# print STDERR "Sum1=$sum at n-1=$#s\n";
	# print STDERR "range_low=$range_low, x= $s[0]->[0], $s[1]->[0], $s[2]->[0]\n";
	$sum += expint::endint($range_low, $s[0]->[0], $s[0]->[1],
						$s[1]->[0], $s[1]->[1],
						$s[2]->[0], $s[2]->[1]);
	# print STDERR "Sum2=$sum at n-1=$#s\n";
	# print STDERR "range_high=$range_high, x= $s[$#s]->[0], $s[$#s-1]->[0], $s[$#s-2]->[0]\n";
	$sum -= expint::endint($range_high, $s[$#s]->[0], $s[$#s]->[1],
						$s[$#s-1]->[0], $s[$#s-1]->[1],
						$s[$#s-2]->[0], $s[$#s-2]->[1]);
	# print STDERR "Sum=$sum at n-1=$#s\n";

	return $sum;
}

1;
