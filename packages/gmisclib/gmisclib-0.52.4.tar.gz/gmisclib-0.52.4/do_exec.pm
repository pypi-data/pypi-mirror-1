package do_exec;
require 5.002;

sub main::do_exec	# deprecated
{
 return go($_[0], $_[1]);
}


sub go($$)
{
 my $s = shift;
 my $lbl = shift;
 my @errs;

 print STDERR "#$lbl: $s\n";

 if(!open(Z, "$s |"))	{
	print STDERR "WARN: do_exec.pm: do_exec: can't open (err $!): $lbl\n";
	return undef();
	}
 while(<Z>)	{
	push(@errs, $_);
	}
 if(!close(Z))	{
	print STDERR "ERR: $lbl returns $? $!:\n";
	foreach $ln (@errs)	{
		print STDERR $ln;
		}
	}
 $?;
}


sub main::do_exec_rep	# deprecated
{
 return go_rep($_[0], $_[1]);
}


sub go_rep($$)
{
 my $s = shift;
 my $lbl = shift;
 my $rv = go($s, $lbl);
 if($rv != 0)	{
	sleep(10);
	print STDERR "#INFO: do_exec.pm: do_exec_rep: $? $!: re-execcing $lbl\n";
	$rv = go($s, $lbl);
	}
 $rv;
}


sub main::do_exec_getnum	# deprecated
{
 return getline($_[0]);
}


sub getline($)
{
 my $x = shift;
 my @l = getall($x);
 if(scalar(@l) < 1) {
	warn "#WARN: getline: no useful return from '$x'\n";
	return undef();
 }
 return $l[0];
}


sub main::do_exec_getnum_rep	# deprecated
{
 return getline_rep($_[0]);
}


sub getline_rep($)
{
 my $l = shift;
 my $rv = getline($l);
 if(!defined($rv))	{
	sleep(10);
	print STDERR "#INFO: do_exec.pm: do_exec_getnum_rep: $? $!: re-execcing $l\n";
	$rv = getline($l);
	}
 $rv;
}



sub main::do_exec_getall	# deprecated
{
 return getall($_[0]);
}


sub getall($)
{
 my $l = shift;
 print STDERR "# $l\n";
 open(CMP, "$l |") || die "slowly: $l";
 my @uc;
 my @out;
 while(defined($l=<CMP>))	{
	chomp($l);
	push(@uc, $l);
	next if($l =~ m'^#');
	die $l if($l =~ m'^ERR:');
	$l =~ s'\s*#.*$'';
	$l =~ s'^\s+'';
	$l =~ s'\s+$'';
	push(@out, $l);
	}
 if(!close(CMP) or $? != 0)	{
	my $lll;
	print STDERR "ERR: do_exec.pm: program fails with $?";
	foreach $lll (@uc)	{ print STDERR $lll; }
	return undef();
	}

 return wantarray() ? @out : join("\n", @out);
}


1;
