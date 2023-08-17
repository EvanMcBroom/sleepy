#
# test of variable length arguments...
#

sub test
{
   println("Arg1: $1 \nArg2: $2 \nArg3: $3");
   println("Total Args: " . size(@_) . " and now...");
   println("Test: " . @_);

   foreach $var (@_)
   {
      println("Argument: $var");
   }
} 

sub test2
{
   println("Arg1: $1 \nArg2: $2 \nArg3: $3");
}

test("a", "b", "c", "d", "e", "f", "g", "h", "i", "j");
test(1, 2, 3, 4, 5);
test();

test2(1, 2, 3, 4, 5);
test2("a", "b", "c", "d");
test2();
