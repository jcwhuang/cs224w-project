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


#
# wanted_content
#
#
#  this function should check to see if the current URL content
#  is something which is either
#
#    a) something we are looking for (e.g. postscript, pdf,
#       plain text, or html). In this case we should save the URL in the
#       @wanted_urls array.
#
#    b) something we can traverse and search for links
#       (this can be just text/html).
#

# sub wanted_content {
#     my $content = shift;

#     # right now we only accept text/html
#     #  and this requires only a *very* simple set of additions
#     #
#     if ( $content =~ m@application/postscript@ ) {
#         push @wanted_urls, $content;
#     }

#     return ($content =~ m@text/html@ || $content =~ m@application/postcript@);
# }

#
# extract_content
#
#
#  this function should read through the context of all the text/html
#  documents retrieved by the web robot and extract three types of
#  contact information described in the assignment

# sub extract_content {
#     my $content = shift;
#     my $url = shift;

#     my $phone = "\([0-9]{3}\)( )*[0-9]{3}-[0-9]{$}";;
#     my $phone2 = "[0-9]{3}-[0-9]{3}-[0-9]{3}";
#     my $email = "[a-zA-Z]+@[a-zA-Z]+\.[a-zA-Z]{3}";

#     while ($content =~ s/<\s*([^>]*)>\s*([^>]*)<\/\s*([^>]*)>//) {
#         my $tag_text = $1;
# 	    my $reg_text = $2;
#         my $link = "";
#         # print LOG "tag: $1\n";
#         # print LOG "reg: $2\n";
# 	    if (defined $reg_text) {
#             if ( $reg_text =~ /[A-Z][a-z ]+,\s*[A-Z]+[a-z]*\s*[0-9-]+/) {
#                 print CONTENT "($url; CITY/STATE/ZIP; $reg_text)\n";
#                 print LOG "($url; CITY/STATE/ZIP; $reg_text)\n";
#             }
#             if ( $reg_text =~ /$email/) {
#                 print CONTENT "($url; EMAIL; $reg_text)\n";
#                 print LOG "($url; EMAIL; $reg_text)\n";
#             }
#             if ( $reg_text =~ /$phone/ || $reg_text =~ /$phone2/) {
#                 print CONTENT "($url; PHONE; $reg_text)\n";
#                 print LOG "($url; PHONE; $reg_text)\n";
#             }
#             $| = 1;
#         }
#     }

#     return;
# }
