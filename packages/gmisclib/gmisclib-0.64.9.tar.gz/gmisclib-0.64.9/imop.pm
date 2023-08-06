#!/usr/local/bin/perl -w --

package imop;

use FileHandle;
use IPC::Open2;

my $running = 0;
my $pid = '';
my $debug = 0;

sub flags(@)
{
	$pid = open2(\*Reader, \*Writer, "imop", "-stdin", @_, "--");
	Writer->autoflush();
	$running = 1;
}


sub send_stuff(@)		# Internal use only.
{
	flags() if(!$running);
	my $c;
	while(defined($c=shift(@_)))	{
		print Writer "$c\n";
		if($debug)	{
			print STDERR "INFO: imop.pm::get: writing {$c}\n";
		}
	}
}



sub get(@)
{
	send_stuff(@_);
	my $rv = <Reader>;
	if(!defined($rv))	{
		warn "WARN: imop::get: EOF from imop";
		print STDERR "WARN: EOF on {" . join(' ', @_) . "}\n";
	}
	chomp($rv) if(defined($rv));
	print STDERR "INFO: imop.pm::get: read {$rv}\n" if($debug);
	return $rv;
}


my $counter = 1;


sub sync()
{
	my $tmp = get($counter, "=");
	die if($tmp != $counter);
}




sub exec(@)
{
	if($debug)	{		# Make sure we're synchronized with imop.
		send_stuff(@_, $counter, '=');
		my $x = <Reader>;
		if(!defined($x))	{
			print STDERR "WARN: error on {" . join(' ', @_) . "}\n";
			die "ERR: imop::exec: EOF on synchronization $counter";
			}
		elsif($x != $counter)	{
			chomp($x);
			print STDERR "WARN: error on {" . join(' ', @_) . "}\n";
			die "ERR: imop::exec: Synchronization error: {$x}, vs. $counter\n";
		}
 	$counter++;
	}
	else	{
		send_stuff(@_);
	}
}


sub close()
{
	my $x = get($counter, '=');
	my $ok3 = 1;
	if($x != $counter)	{
		chomp($x);
		print STDERR "ERR: imop::close: Error or unexpected result: {$x}, vs. $counter\n";
		$ok3 = 0;
	}

	print STDERR "INFO: imop.pm: waiting for close on $pid\n" if($debug);
	my $ok = close(Writer);
	print STDERR "INFO: imop.pm: waiting for $pid\n" if($debug);
	waitpid($pid, 0);
	print STDERR "INFO: imop.pm: got $pid\n" if($debug);
	my $stat = $?;
	$running = 0;
	my $ok2 = close(Reader);
	print STDERR "INFO: imop.pm: closed reader for $pid\n" if($debug);
	return $ok2 && $stat==0 && $ok && $ok3;
}



sub debug()
{
	$debug = 1;
}



END	{
	if($running)	{
		imop::close();
		}
	}

1;
