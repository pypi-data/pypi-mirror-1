#!/usr/local/bin/perl -I/home/httpd/bin -w --

package wnpp_local;
require 5.002;
use parsedata;

my $rawdir = "/home/gpk/lib/wnpp_local/data";
my $datadir = "/home/gpk/lib/wnpp_local";
my $dbf = 'db.gdbm';


BEGIN {
	require Config; import Config;
	if ($Config{'extensions'} !~ /\bGDBM_File\b/) {
		print "1..0\n";
		exit 0;
		}
	}

use GDBM_File;

my %h;
my $tied = 0;

sub init()
{
 if($tied)	{ return; }

 my $bored = 0;
 do  {
	$tied = tie(%h, GDBM_File, "$datadir/$dbf", &GDBM_WRCREAT, 0664);
	sleep(1) if(!$tied);
	} until($tied or $bored++>15);
 if(!$tied)  {die "can't open preferences database $pref\n";}
}


sub expand_word($)
{
 init();
 my $w = lc(shift);
 # print STDERR "INFO: wnpp_local: $w -> $h{$w}\n";
 # return map {my $tmp = ::parse($_); \$tmp;} split("\n", $h{$w} || '');
 return map { { hype=>$_ }; } split(' ', $h{$w} || '');
}


sub  set_one($$)
{
 my ($category, $word) = @_;
 $category =~ s/[ ,;]/~/g;
 $word = lc($word);
 
 init();
 my @tmp = split("\n", $h{$word} || '');
 my $t;
 foreach $t (@tmp)	{
	my %a = ::parse($t);
	if($t->{hype} eq $category)	{
		return;
		}
	}
 print STDERR "Adding $category to $word\n";
 push(@tmp, {hype=>$category});
 $h{$word} = parsedata::concoct_many(@tmp);
}


sub set_from_file($$)
{
 my ($category, $file) = @_;
 print STDERR "set_from_file $category $file\n";
 open(F, "<$file") or die;
 my $l;
 while(defined($l=<F>))	{
	my @x = split(' ', $l);
	my $t;
	foreach $t (@x)	{
		set_one($category, $t);
		}
	}
 close(F);
}


sub set_from_dir()
{
 my $dir = $rawdir;
 my $t;
 unlink("$datadir/$dbf");
 foreach $t (split(' ', qx{find $dir -type f -print}))	{
	my $category = $t;
	$category =~ s"(./)?$dir/"";
	$category =~ s"/[^/]*$"";
	print STDERR "Setting category $category from $t\n";
	set_from_file($category, $t);
	}
}

1;
