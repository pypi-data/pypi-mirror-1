#!/usr/local/bin/perl

package ran;

my $nstore = undef();
my $M_PI = 3.1415926535;

sub ::Nnoise
{
 if(defined($nstore))	{
	my $x = $nstore;
	undef($nstore);
	return $x;
	}

 my ($x1, $x2);
 do	{
	$x1 = ran1();
	} while ($x1 == 0);
 do	{
	$x2 = ran1();
	} while ($x2 == 0);
 $nstore = sqrt(-2.0*log($x1)) * cos(2*$M_PI*$x2);
 sqrt(-2.0*log($x2)) * cos(2*$M_PI*$x1);
}


my @rstore;
my $N = 100;

sub ran1
{
 if($#rstore < $N-1)	{
	srand(time());
	my $i;
	for($i=0; $i<$N; $i++)	{
		$rstore[$i] = rand(1);
		}
	}
 my $n = int(rand($N));
 my $z = $rstore[$n] + 7*rand(1);
 $rstore[$n] = rand(1)/3;

 $z-int($z);
}


my $b16 = 65536;

sub ran2
{
 my $i = shift();
 my $j = unpack("%32b*", $i);

 my $t1 = (($i>>9)%$b16 ^ 11111) * ($i%$b16 ^ $j ^ 10001);
 my $t2 = ($i%$b16 ^ 17131) * (($i/$b16)%$b16 ^ 30020);

 my $q1 = (($t1>>14)%$b16 ^ 12111) * ($t2%$b16 ^ 20071);
 my $q2 = ($t1%$b16 ^ 17001) * (($t2/$b16)%$b16 ^ 10220);

 my $x1 = ( 197 ^ $j ^ (($t1>>11)%$b16)) * ($q2%$b16 ^ 1076) ^ ($t2>>3);
 my $x2 = (13 ^ ($i%97) ^ ($t2%$b16)) * (($q1>>3)%$b16 ^ 1117) ^ ($t1>>2);

 return (($x1%$b16)/$b16 + $x2%$b16)/$b16;
}

