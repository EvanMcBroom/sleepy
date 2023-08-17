sub my_compare
{
   if ($1 eq $2)
   {
      return 0;
   }

   if ($1 lt $2)
   {
      return 1;
   }

   return -1;
}

push(@data, "stuff");
push(@data, "this");
push(@data, "is");
push(@data, "a");
push(@data, "test");

sorta(@data);

foreach $var (@data)
{
   printf($var);
}

if ('*!*@*.aol.com' iswm "`butane!lamer@irc.aol.com")
{
   printf("lamah");
}
