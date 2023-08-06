#!/usr/local/bin/perl -w -I/home/gpk/bin --

package wnpp_rules;
require 5.002;

sub expand_word($)
{
 my $w = shift;
 my @o;

 # print STDERR "INFO: Wnpp_rules: $w\n";

 if($w =~ m'\$([0-9,]+)(.[0-9][0-9])?')	{
	push @o, {hype=>"AMOUNT/DOLLAR/" . length($1), pos=>'noun'};
	}

 if($w =~ m'^\d+$')	{
	push @o, {hype=>"NUMBER/INTEGER/" . int(length($w)/3)};
	}
 elsif($w =~ m'^-*[0-9.]+$')	{
	push @o, {hype=>"NUMBER/FLOAT" . int(length($w)/3)};
	}
 elsif($w =~ m'^-*[0-9.eE+-]+$')	{
	push @o, {hype=>"NUMBER/SCI" . int(length($w)/3)};
	}

 if($w =~ m'^(19|20)\d\d$')	{
	push @o, {hype=>"GTIME/DATE/YEAR", pos=>'noun'};
	}
 elsif($w =~ m'^\d\d/\d\d$')	{
	push @o, {hype=>"GTIME/DATE/DATE", pos=>'noun'};
	}
 elsif($w =~ m'^\d\d[-/]\d\d[-/]\d\d$')	{
	push @o, {hype=>"GTIME/DATE/DATE", pos=>'noun'};
	}
 elsif($w =~ m'^\d\d-(Jan|Feb|Mar|Apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*-\d\d$'i)	{
	push @o, {hype=>"GTIME/DATE/DATE", pos=>'noun'};
	}
 elsif($w =~ m'^\d\d:\d\d:\d\d$')	{
	push @o, {hype=>"GTIME/TIME", pos=>'noun'};
	}
 elsif($w =~ m'^\d\d:\d\d$')	{
	push @o, {hype=>"GTIME/TIME", pos=>'noun'};
	}

 if($w =~ m"[()<>=+*^/-]+")	{
	push @o, {hype=>"CHARS/MATH"};
	}
 if($w =~ m'[&<>"]+')	{
	push @o, {hype=>"CHARS/HTML"};
	}
 if($w =~ m@[|&"{}()+=*/<>-]+@)	{
	push @o, {hype=>"CHARS/C"};
	}
 if($w =~ m'[:->.]+')	{
	push @o, {hype=>"CHARS/CPP"};
	}
 if($w =~ m'[%@{}\$]+')	{
	push @o, {hype=>"CHARS/SHELL"};
	}
 if($w =~ m@['"=()`\$]+@)	{
	push @o, {hype=>"CHARS/PERL"};
	}

 if(scalar(@o)==0 && $w =~ m"[^'\s\w\d-]")	{
	push @o, {hype=>"CHARS/MISC"};
	}

 return map { $_->{p}=1; return $_;} @o;
}

1;
