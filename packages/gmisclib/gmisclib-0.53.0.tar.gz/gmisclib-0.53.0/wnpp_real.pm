#!/usr/local/bin/perl -w -I/home/gpk/bin --

package wnpp_real;
require 5.002;

use wnpp_local;
use wnpp_rules;

$nospace = 1;

sub expand_word($)
{
my $w = shift;
local @o;

my $wq = $w;
$wq =~ s'"'\\"';
$wq =~ s'\\$'\\$';
# print STDERR "wq={$wq}\n";

my ($pos, $nsenses, $sense, $cluster) = ('', '', '', '');
my $x;
if(print_rules($w))	{
	return @o;
	}

print_local($w);

{ my $tmp = $wq; $tmp =~ m/([a-zA-Z']+)/o;  $wq = $1; } # Untaint for demon.

open(W, "wn '$wq' -synsr -synsa -hypen -hypev |") or die "ERR: no open wn";
while(defined($x=<W>))	{
	chomp($x);
	if($x =~ m'^[a-zA-Z/]+ (.Ordered by Frequency. )?of (noun|verb|adj|adv) \w+$')	{
		my $tmppos = $2;
		start($w, $tmppos, 0);
		$pos = $tmppos;
		$sense = '';
		$nsenses = '';
		}
	elsif($x =~ m'^(\d+) sense(s?) of')	{
		$nsenses = $1;
		$sense='';
		}
	elsif($x =~ m'^Sense (\d+)')	{
		my $tmpsense = $1;
		start($w, $pos, $tmpsense);
		$sense = $tmpsense;
		$cluster = '';
		}
	elsif($sense ne '' && !$cluster)	{
		$cluster = $x;
		add(0, prep($cluster));
		}
	elsif($x =~ m'^( +)=>\s*')	{
		my $w = $';
		my $il = length($1);
		add($il, prep($w));
		}
	elsif($x =~ m'^\s*$')	{
		}
	else	{
		# print STDERR "U:" . $x . "\n";
		}
	}
close(W);	# We ignore errors here.
end();
return normalize_probabilities(@o);
}


sub prep($)
{
 my $s = shift;
 if($nospace)	{
	$s =~ s' '~'g;
	}
 $s =~ s'[/:,]~*'^'g;
 return $s;
}


my $expanded_w = '';
my @qlist = ();
my $stored_pos;
my $stored_sense = '';


sub start($$$)
{
 my ($w, $pos, $sense) = @_;
 # print STDERR "start($w, $pos)\n";
 if($#qlist >= 0)	{
	printout($pos, $w, $stored_sense, @qlist);
	}
 $expanded_w = $w;
 $stored_pos = $pos;
 $stored_sense = $sense;
 @qlist = ();
}


sub end()
{
 # print STDERR "end(..., $expanded_w, $stored_pos)\n";
 if($#qlist >= 0)	{
	printout($stored_pos, $expanded_w, $stored_sense, @qlist);
	}
 $expanded_w = undef();
 $stored_pos = undef();
 $stored_sense = undef();
 @qlist = ();
}


sub add($$)
{
 my ($indent, $q) = @_;
 # print STDERR "add($indent, $q, ..., $expanded_w, $stored_pos)\n";
 if($indent <= $#qlist)	{
	printout($stored_pos, $expanded_w, $stored_sense, @qlist);
	splice(@qlist, $indent);
	}
 $qlist[$indent] = $q;
}


sub printout($$$@)
{
 my ($spos, $w, $ssense, @qlist) = @_;
 # print STDERR "printout($spos, $w, $ssense, ...)\n";

 push @o,  {pos => $spos,
		hype => join('/', reverse( map { defined($_) ? ($_) : ();} @qlist)),
		word => $w,
		sense => $ssense,
		p => exp(-$ssense)
		};
}


sub print_local($$)
{
 my ($w, $w) = @_;
 my $t;
 my @s = split(' ', wnpp_local::lookup($w));
 foreach $t (@s)	{
	start($w, 'noun', '');
	add(0, $t);
	end();
	}
}


sub print_rules($$)
{
 my ($w) = @_;
 my $t;
 my @s = split(' ', wnpp_rules::lookup($w));
 foreach $t (@s)	{
	start($w, 'rule', '0');
	add(0, $t);
	end();
	}
 return scalar(@s);
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
