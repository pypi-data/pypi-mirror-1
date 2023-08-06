#!/usr/local/bin/perl -w -I/home/gpk/bin --

package cosmology;
use parsedata;

# /* Reference: Schneider, Ahlers and Falco */
# /* From equations 4.57b and 4.52.5 . Angular diameter distance in */
# /* a uniform dust universe.   No cosmological constant. */
sub D_angular	# (double z1, double z2, C char *cosmology)
{
 my ($z1, $z2, $cosmology) = @_;

 die unless($z1>=0 && $z2>$z1);
 die unless($cosmology);

 my %c = ::parse($cosmology);

 die unless($c{omega});
 die if($c{lambda});

 my $omega_m = $c{omega};
 my $omega_l = $c{lambda};
 my $H0 = 1;
 my $cspeed = 1;

 my $Da12 = (1/(1+$z2)) * ( Dm($z2, $omega_m, $omega_l)*

 return ($cspeed/$H0)*$Da12;
}

sub Dm
{
 my ($z, $omega_m, $omega_lambda) = @_;
 my $omega_r = 1 - $omega_lambda - $omega_m;
}


1;
