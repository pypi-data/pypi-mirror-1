#!/usr/bin/perl

use WWW::Mechanize;

my $mech = WWW::Mechanize->new();

my $url = 'http://cadensa.bl.uk/cgi-bin/webcat';
$mech->agent('FireFox');    # to be a little less obvious
$mech->get( $url );

$mech->follow_link( text_regex => qr/Advanced search/);

#print $mech->content;

# form begins on line 735 of the html
$mech->submit_form(
        form_name => 'searchform',
        fields => { pubyear => 1900 },
        # enters the year 1900 and submits the form
);

foreach my $base (1,21,41,61,81,101,121) {

        if( $base > 1 ) {
                $mech->submit_form(
                        form_name => 'hitlist',
                        fields => { form_type => "JUMP^$base" },
                );
        }
        foreach my $i (0..19) {
                $i += $base;
                $mech->submit_form(
                        form_name => 'hitlist',
                        button => "VIEW^$i",
                );

                if( open( my $fh, "> perl/page$i.html" ) ) {
                        print $fh $mech->content;
                        close $fh;
                } else {
                        print $mech->content; next
                }
                sleep 1         if( $i % 2);    # give the server a rest
                $mech->back();
        }
}

