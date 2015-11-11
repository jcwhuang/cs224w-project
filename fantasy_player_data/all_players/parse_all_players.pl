#!/usr/bin/perl -w
# Jade Huang
# jayebird@stanford.edu

# This program grabs fantasy football player stats from (a)
# saved html page(s) from the UEFA Champions League.
# The output is of the following format:
# player name, team, player position, player price
#
# Example usage:
# perl parse_players.pl goalkeepers.html midfielders.html

use strict;

use Carp;

$| = 1;
print "# Player_num,Player_name,Team\n";

for my $html_file (@ARGV) {
    open(my $fh, "<", $html_file) or die "cannot open < $html_file: $!";

    my $content = ();

    while (my $row = <$fh>) {
        $content .= $row
    }
    my ($team) = $html_file =~ /(.*)\.html$/;
    $team =~ s/_/ /g;
    &grab_players($content, $team);
}

sub grab_players {
    my $content = shift;
    my $team = shift;
    skip:
        while ($content =~ s/tr [^"]*="player [0-9]*"><td [^"]*="number">([0-9]*)<\/td><td [^"]*="playername[^>]*><a href[^>]*>([^<]*)//) {
            my $player_num = $1;
            my $player_name = $2;
            print "$player_num,$player_name,$team\n";
        }
}
