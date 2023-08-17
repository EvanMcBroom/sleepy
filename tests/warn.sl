#
# Test the built in warning(s) mechanism...
#

sub test1
{
   printf("I like ice cream");
   printz("Testing...");
}

suy test2
{
   printf("Skanalicious");
}

for ($x = 0; $x < 3; $x++)
{
   test1();
}

test2();

$z = $z *8 30; # 00pZ I made a typo...  *8 will be interpreted as an operator, doh!@

printf("Value of z is: $z");
