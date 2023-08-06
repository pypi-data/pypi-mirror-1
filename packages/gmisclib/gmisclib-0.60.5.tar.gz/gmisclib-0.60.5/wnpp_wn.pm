#!/usr/local/bin/perl -w -I/home/gpk/bin --

package wnpp_wn;
require 5.002;

$nospace = 1;

sub expand_word($)
{
my $w = shift;
local @o;


my ($pos, $nsenses, $sense, $cluster) = ('', '', '', '');

my $wq = prep_arg($w);
# print STDERR "wq={$wq}\n";

open(W, "wn '$wq' -synsr -synsa -hypen -hypev |") or die "ERR: no open wn";
my $x;
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
		sense => $ssense,
		p => exp(-sqrt($ssense))
		};
}




sub prep_arg($)
{
 my $tmp = shift;
 $tmp =~ m/([a-zA-Z']+)/o;
 $wq = $1;
 $wq =~ s/'/\\'/g;
 $wq;
} # Untaint for demon.


1;
