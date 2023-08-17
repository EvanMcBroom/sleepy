# test some stuff with if statements...

sub test
{
   if ($1 eq "a" || $1 eq "d")
   {
      return "value1";
   }

   if ($1 eq "b")
   {
      return "value2";
   }

   if ($1 eq "c")
   {
      return "value3";
   }
 
   return "value4";
}

printf("a: " . test("a"));
printf("b: " . test("b")); # I'm another comment
printf("c: " . test("c"));
printf("d: " . test("d"));
printf("e: " . test("e"));

