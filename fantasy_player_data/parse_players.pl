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
print "# Player name, team name, player position, player price\n";

for my $html_file (@ARGV) {
    open(my $fh, "<", $html_file) or die "cannot open < $html_file: $!";

    my $content = ();

    while (my $row = <$fh>) {
        $content .= $row
    }
    &grab_players($content);
}

sub grab_players {
    my $content = shift;

    skip:
        while ($content =~ s/(tr id=[^>]*>)//) {
            my $player_info = $1;
            my ($player_name) = $player_info =~ /data-name="([^"]*)"/;
            my ($team_name) = $player_info =~ /data-tnm="([^"]*)"/;
            my ($player_pos) = $player_info =~ /data-pos="([^"]*)"/;
            my ($player_price) = $player_info =~ /data-val="([^"]*)"/;
            print "$player_name, $team_name, $player_pos, $player_price\n";
        }
}
