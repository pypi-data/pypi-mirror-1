package arith;


sub arith::getprm($)
{
 my $p = shift;
 if(!defined($::ARGV[$p]))	{
	die "ERR: parameter $p is not defined.\n";
	}
 if($paramlist)	{
	push(@$paramlist, $p);
	}
 return $argv->[$p];
}


sub arith::negexp($)
{
 my $p = shift;
 return exp(-1 * $p);
}



sub arith::sqrt($)
{
 my $x = shift;
 return sqrt($x);
}


sub arith::pow($$)
{
 my $x = shift;
 my $y = shift;
 return ($x)**($y);
}



sub arith($;$$$)
{
 my $s = shift;
 local $argv = shift;
 local $paramlist = shift;
 my $trace = shift;

 if($trace)	{ print STDERR "arith($s)\n"; }

 if(!defined($s) || $s eq "")	{
	warn "WARN: undefined/empty value in arith, line $.\n";
	return undef();
	}

 if($s =~ m'\b(NaN|xxx)\b')	{
	warn "WARN: NaN/xxx in arith, line $.: {%s}\n";
	return undef();
	}

 $s =~ s'\bph\b'$::seed'gi;
 $s =~ s"\bp([0-9]+)\b"getprm($1)"gi;
 $s = "package arith;" . $s . ";";

 # print STDERR "Arith($s)\n";

 my $rv = eval($s);
 if($@)	{
	die "ERR: expand_lensfile.sh: Arithmetic error line $. : {$s}\n";
	}
 $rv;
}


1;
