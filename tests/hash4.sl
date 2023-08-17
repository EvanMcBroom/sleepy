#
# Test of clearing hashes and arrays and removing elements from hashes/arrays
#

println("Pre Removal:");

try
{
   %hash = hash(@array);
}
catch $ex
{

}

%hash = hash("key=hello world!@", "blah=bleh", "user=password", "stuff", "testing", "", "zing=1+2=3 or 4");

remove(%hash, "user");

foreach $var (keys(%hash))
{
   println("   $[10]var = ".%hash[$var]);
}

println("Post Removal:");
clear(%hash);

foreach $var (keys(%hash))
{
   println("   $[10]var = ".%hash[$var]);
}

