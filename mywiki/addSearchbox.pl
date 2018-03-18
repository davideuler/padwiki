#!/usr/bin/perl -w
use strict;

my $foundLine = $ARGV[0];
my $result;
    open OUT, '>', \$result;
    while(<STDIN>) {
	if (/<body/) {
	    print OUT;
	    print OUT <<OEF;
<script type="text/javascript">
function DoSearch(form)
{
top.location='/searchbar/?data='+form.data.value;
}
</script>
<form name="SearchForm" onSubmit="DoSearch(this.form)" method="get" action="/searchbar">
Search for
<input type="text" name="data" size="50">
<input type="button" value="Submit" onclick="DoSearch(this.form)">
<br>
<hr>
</form>
OEF
	    print OUT "<H3>".$foundLine."</H3>";
	} else {
	    print OUT;
	}
    }
    close OUT;

    print $result;
