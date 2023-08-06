#!/usr/local/bin/perl

package parsedata;
require 5.002;
use escape;

# Parses a line in a=v; a=v form into an array that can form a hash table.
# Takes one required arg: the string to be parsed.  Returns an associative array.
# Doesn't take the fully escaped a=v syntax.  Oh, well.
sub ::parse($)
{
 my $s = shift;
 chomp($s);
 $s =~ s'^\s+'';
 $s =~ s'\s+$'';
 my ($ss, $sc) = split('\s*#\s*', $s, 2);
 if(defined($sc) && $sc ne '') {
	push @rv, '_COMMENT', $sc;
	}
 my @s = split('\s*;\s*', $ss);
 my $q;
 my @rv;
 while(defined($q=shift(@s)))	{

	next if($q eq '');

	my ($a, $v) = split('\s*=\s*', $q, 2);

	if($a eq '' || !defined($v))	{
		print STDERR "ERR: bad attribute-value pair {$q}. No equals sign?\n";
		return ();
		}

#	$v =~ s/^"(\w+)"$/$1/;   # AWG 

	push @rv, $a, escape::back($v);
	}
 (@rv);
}


# Parses a line from a multicolumn file (just columns of numbers).
# Second arg is a reference to an array of names.
sub ::mcparse($$)
{
 my ($rnames, $s) = @_;
 die "ERR: parsedata.pm: mcparse: need ref to array of names" if(ref($rnames) ne 'ARRAY');
 my @s = split(' ', $s);
 my $i;
 my @rv;
 my $n = $#s + 1;
 if($n > $#{$rnames}+1)	{ $n = $#{$rnames} + 1;}
 for($i=0; $i<$n; $i++)	{
	my $a = ($rnames->[$i] || '');
	if($a)	{
		push(@rv, ( $a, $s[$i] ));
		}
	}
 (@rv);
}


# Checks that the specified attributes are all present.
# First arg is a reference to a hash table.
sub present($@)
{
 my $r = shift;
 my $x;
 foreach $x (@_)	{
	if(!defined($r->{$x}))	{
		return 0;
		}
	}

 return 1;
}


sub ::filterparse($)
{
	my $arg = shift;
	# print STDERR "filterparse($arg)\n";
	my ($a0, $a1, $a2);
	if($arg =~ m'\s*(<|>|==|!=|>=|<=)\s*' )	{
		($a0, $a1, $a2) = ($`, $1, $');
		}
	elsif($arg =~ m'\s*[\s.](eq|ne|!?matches)[\s.]\s*')	{
		($a0, $a1, $a2) = ($`, $1, $');
		}
	elsif($arg =~ m'\s*[\s.](!?exists)([\s.]|$)')	{
		($a0, $a1, $a2) = ($`, $1, '');
		}
	else	{
		return undef();
		}
	if(!defined($a0) || !defined(filterop($a1)))	{
		die "ERR: Bad select: {" . join(' ', @a) . "}\n";
		}
	# print STDERR "filter {$a0} {$a1} {$a2}\n";
	[$a0, filterop($a1), $a2];
}


sub filterop($)
{
 my $op = shift;
 if($op eq '==')	{ return \&numeq; }
 elsif($op eq '!=')	{ return \&numne; }
 elsif($op eq 'eq')	{ return \&xeq; }
 elsif($op eq 'ne')	{ return \&xne; }
 elsif($op eq '>')	{ return \&numgt; }
 elsif($op eq '<')	{ return \&numlt; }
 elsif($op eq '<=')	{ return \&numle; }
 elsif($op eq '>=')	{ return \&numge; }
 elsif($op =~ '!matches')	{ return \&xnmatches; }
 elsif($op =~ 'matches')	{ return \&xmatches; }
 elsif($op =~ '!exists')	{ return \&xnexists; }
 elsif($op =~ 'exists')	{ return \&xexists; }

 warn "No such filterop: {$op}\n";
 return undef();
}


sub numeq	{ defined($_[0]) and $_[0] == $_[1]; }
sub numne	{ defined($_[0]) and $_[0] != $_[1]; }
sub numgt	{ defined($_[0]) and $_[0] > $_[1]; }
sub numlt	{ defined($_[0]) and $_[0] < $_[1]; }
sub numge	{ defined($_[0]) and $_[0] >= $_[1]; }
sub numle	{ defined($_[0]) and $_[0] <= $_[1]; }
sub xeq	{ defined($_[0]) and $_[0] eq $_[1]; }
sub xne	{ defined($_[0]) and $_[0] ne $_[1]; }
sub xmatches	{ defined($_[0]) and $_[0] =~ m"$_[1]"; }
sub xnmatches	{ defined($_[0]) and $_[0] !~ m"$_[1]"; }
sub xexists	{ defined($_[0]); }
sub xnexists	{ !defined($_[0]); }

sub ::filter($@)
{
 my $r = shift;
 my $x;
 foreach $x (@_)	{
	# ${$x}[1] is a ref to a function
	# ${$x}[0] is an attribute name
	# ${$x}[2] is a value it should be compared to.
	my ($a, $f, $v) = @$x;
	if(!defined($f))	{ die "ERR: Filter parsing error\n"; }
	if(! $f->($r->{$a}, $v))	{
		return 0;
		}
	}

 return 1;
}


sub rename($@)
{
 my $r = shift;
 my $x;
 foreach $x (@_)	{
	my ($from, $to) = @$x;
	if(defined($r->{$from}))	{
		$r->{$to} = $r->{$from};
		delete $r->{$from};
		}
	}
}


sub add($@)
{
 my $r = shift;
 my $x;
 foreach $x (@_)	{
	my ($a, $v) = @$x;
	$r->{$a} = $v;
	}
}



sub project_all($@)
{
 my $r = shift;
 my $x;
 my %tmp;
 foreach $x (@_)	{
	return undef() unless(exists($r->{$x}));
	$tmp{$x} = $r->{$x};
	}

 \%tmp;
}


sub project_any($@)
{
 my $r = shift;
 my $x;
 my %tmp;
 my $n;
 foreach $x (@_)	{
	$tmp{$x} = $r->{$x} if(exists($r->{$x}));
	$n++;
	}

 $n>=0 ? \%tmp : undef();
}


sub exclude($@)
{
 my $r = shift;
 my $x;
 my %tmp = %$r;
 foreach $x (@_)	{
	delete($tmp{$x});
	}

 scalar(%tmp) ? \%tmp : undef();
}



sub ::showAV(@)
{
 my $r;
 while($r = shift)	{
 	print concoct($r) . "\n";
	}
}


sub concoct_many(@)
{
 my @o;
 my $r;
 while($r = shift)	{
 	push @o, concoct($r);
	}
 join("\n", @o) . "\n";
}


sub concoct($)
{
	my $r = shift(@_);
	die "ERR: parsedata.pm: showAV: need ref to HASH" if(ref($r) ne 'HASH');
	my $c = delete($r->{_COMMENT});
	my ($k, $v);
	my @out;
	while(($k, $v)=each(%$r))	{
		$v = escape::fwd($v);
		push(@out, "$k=$v;");
		}
	return join(' ', sort @out) . (defined($c) ? " # $c" : '');
}






sub ::showAVf($@)
{
 my $arg = shift;
 my @arg = split('\$([a-zA-Z][a-zA-Z0-9_.]*)', $arg);
 my $ps = "'" . shift(@arg) . "'";
 my @tmp = @_;
 my ($varbl, $quot);
 while(defined($varbl=shift(@arg)))	{
	my $xx = '$r->{' . "'$varbl'" . '}';
	$ps .= " . (defined($xx) ? $xx : '')";
	if(defined($quot=shift(@arg)))	{
		$ps .= ". '" . $quot . "'";
		}
	}
 $ps .= ' . "\n"';
 # print STDERR "ps=$ps\n";
 # print STDERR "Nitems=" + scalar(@_) + "\n";
 eval("my \$r; while(\$r = shift(\@tmp)) { print $ps; }");
}





1;
