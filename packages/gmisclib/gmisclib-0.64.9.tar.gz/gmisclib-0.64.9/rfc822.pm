#!/usr/local/bin/perl -w -I/home/gpk/bin --

package rfc822;

my $open = 0;

sub open
{
 my $f = shift;
 $open = 1;
 $nxt = getline();
 return $open;
}


sub close
{
 $open = 0;
}


sub getline
{
 my $x = <STDIN>;
 if($x =~ m'^\s*$')	{
	return '';
	}
 print STDERR "GETLINE: {$x}\n";
 return $x;
}


$nxt = undef();

sub getbody
{
 my $x = <STDIN>;
 return $x;
}

sub get
{
 if(defined($nxt))	{
	my $rv = $nxt;
	while( ($nxt = getline()) =~ m'^\s+' )	{
		$nxt =~ s{^\s+}{};
		chomp($rv);
		$rv = "$rv $nxt";
		}
	chomp($rv);
	print STDERR "GET: {$rv}\n";
	my ($k, $v) =  split('\s*[:=]\s*', $rv, 2);
	if(defined($k) && defined($v))	{
		return ($k, $v);
		}
	return ();
	}
 return undef();
}

1;
