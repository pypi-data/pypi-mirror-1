#!/usr/local/bin/perl -w --

package escape;

my %ue_map;
{
 my $i;
 for($i=0; $i<256; $i++)	{
	$ue_map{sprintf("%02x", $i)} = chr($i);
	}
}


sub back {
	my $todecode = shift;
	if($todecode ne '%mt') {
		$todecode =~ s/%([0-9a-fA-F][0-9a-fA-F])/$ue_map{$1}/go;
	} else {
		$todecode = '';
	}
	return $todecode;
}

my @esc_list = ('=', '%', ';', '#', " ", "\t", "\r", "\n");
{
 my $i;
 for($i=0; $i<32; $i++) {
	push @esc_list, chr($i);
	}
 for($i=127; $i<256; $i++) {
	push @esc_list, chr($i);
	}
}
my %esc_map = map {($_, '%'.sprintf("%02x", ord($_)));} @esc_list;
my $esc_re = "([" . quotemeta(join('', @esc_list)) . "])";


sub fwd {
	my $toencode = shift;

	if($toencode ne '') {
		$toencode =~ s/$esc_re/$esc_map{$1}/go;
	} else {
		$toencode = '%mt';
	}
	return $toencode;
}

=pod

print fwd("a;b\n")."\n";

my $test = "aaa;\003bbb\nccc++ddd=eee\r";
print fwd($test). "\n";
print "{" . back(fwd($test)). "}\n";
die if(back(fwd($test)) ne $test);
die if(fwd('') ne '%mt');
die if(back('%mt') ne '');

=end

1;
