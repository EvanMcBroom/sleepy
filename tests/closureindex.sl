#
# test out indexing in some other cases.
#

sub phoenetic
{
   this('$bad');

   $this["a"] = "alpha";
   $this["b"] = "bravo";
   $this["c"] = "charlie";
   $this["d"] = "delta";   

   $bad = "bad test!!!";

   println("bad test --- $bad");

   yield; 

   println("yeap, bad is now $bad");
}

phoenetic(); # set everything up please..

println("a    is: " . &phoenetic["a"]);
println("bad is: " . &phoenetic['$bad']);

&phoenetic['$bad'] = "oooh, changes... eee";
phoenetic();
