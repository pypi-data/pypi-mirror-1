#!/usr/local/bin/perl -w -I/home/gpk/bin --

package wnpp;
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

my $ew = escape($w);
my ($pos, $nsenses, $sense, $cluster) = ('', '', '', '');
my $x;
if(print_rules($w, $ew))	{
	return @o;
	}

print_local($w);
open(W, "wn \"$wq\" -synsr -synsa -hypen -hypev |") or die "ERR: no open wn";
while(defined($x=<W>))	{
	chomp($x);
	if($x =~ m'^[a-zA-Z/]+ (.Ordered by Frequency. )?of (noun|verb|adj|adv) \w+$')	{
		my $tmppos = $2;
		start($ew, $tmppos);
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
		start($ew, $pos);
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
return @o;
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


my $expanded_w;
my @qlist = ();
my $stored_pos;


sub start($$)
{
 my ($ew, $pos) = @_;
 if($#qlist >= 0)	{
	printout($pos, $ew, @qlist);
	}
 $expanded_w = $ew;
 $stored_pos = $pos;
 @qlist = ();
}


sub end()
{
 if($#qlist >= 0)	{
	printout($stored_pos, $expanded_w, @qlist);
	}
 $expanded_w = undef();
 $stored_pos = undef();
 @qlist = ();
}


sub add($$)
{
 my ($indent, $q) = @_;
 if($indent <= $#qlist)	{
	printout($stored_pos, $expanded_w, @qlist);
	splice(@qlist, $indent);
	}
 $qlist[$indent] = $q;
}


sub printout($$$)
{
 my ($spos, $ew, @qlist) = @_;

 push @o,  "$pos:" . join(':', @qlist, $ew);
}


sub print_local($)
{
 my $w = shift;
 my $t;
 my @s = split(' ', wnpp_local::lookup($w));
 foreach $t (@s)	{
	start('noun');
	add($t);
	end();
	}
}


sub print_rules($)
{
 my $w = shift;
 my $ew = escape($w);
 my $t;
 my @s = split(' ', wnpp_rules::lookup($w));
 foreach $t (@s)	{
	start('rule');
	add($t);
	end();
	}
 return scalar(@s);
}


sub escape($)
{
 my $s = shift;
 $s =~ s'([^\w\d])'"%".ord($1)'eg;
 return $s;
}


1;
