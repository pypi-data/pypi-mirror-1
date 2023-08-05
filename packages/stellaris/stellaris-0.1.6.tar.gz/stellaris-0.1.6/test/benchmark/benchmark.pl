#!/usr/bin/perl -w

use Time::HiRes qw ( time );

# number of contexts to upload
my $num_contexts = 10;
my $queryfile = 'benchmark.rq';
my $internal_query_result = 'internal.xml';
my $external_query_result = 'external.xml';

my $help = 0;
my $rdfserver      = shift or $help = 1;
my $sparqlerserver = shift or $help = 1;

die "Usage: $0 <rdfserver:port> <sparqlerserver:port>\n\n" .
    "       eg. $0 mintaka.aip.de:24001 mintaka.aip.de:24100\n\n" if ($help);

# upload the data
for (my $i = 0; $i < $num_contexts; $i++) {
  system ("curl --silent --upload-file benchmark.rdf http://$rdfserver/context/benchmark/$i");
}

# read the benchmark SPARQL query
my $query = `cat $queryfile`;
die "Couldn't read SPARQL query file '$queryfile'" if ($?);

# benchmark external query engine
my $external_query_url = "http://$sparqlerserver/sparql?query=" .
                         HTMLise ($query) .
                         '\&default-graph-uri=' .
                         HTMLise ("http://$rdfserver/context");
$elapsed_time = Time::HiRes::time;
system ("curl --silent $external_query_result $external_query_url");
$elapsed_time = Time::HiRes::time - $elapsed_time;
print "SPARQLer: $elapsed_time seconds\n";

# benchmark internal query engine
my $internal_query_url = "http://$rdfserver/query/query?query=" . HTMLise ($query);
my $elapsed_time = Time::HiRes::time;
system ("wget -q -O $internal_query_result $internal_query_url");
$elapsed_time = Time::HiRes::time - $elapsed_time;
print "Icecore:  $elapsed_time seconds\n";

print "\n";
print "Query results are stored in '$internal_query_result' and '$external_query_result',\nthey should have the same contents.\n";
###############################################################################

# this subroutine returns the given input string in HTML-encoded format
sub HTMLise
{
  my ($in) = @_;
  my @out = ();

  foreach (split (//, $in)) {
    if (/[\w\-\.\*]/) {
      # a normal character, no encoding needed
      push (@out, $_);
    } elsif ($_ eq ' ') {
      # a space turns into '+' character
      push (@out, '+');
    } else {
      # everything else is ascii-hex-encoded
      push (@out, sprintf ("%%%02X", ord ($_)));
    }
  }

  return join ('', @out);
}

