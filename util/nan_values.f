      real plus_inf, minus_inf, plus_nanq, minus_nanq, nans
      real large
 
      data plus_inf /z'7f800000'/
      data minus_inf /z'ff800000'/
      data plus_nanq /z'7fc00000'/
      data minus_nanq /z'ffc00000'/
      data nans /z'7f800001'/
 
      print*, 'Test of local zero, this should be zero -->',itest
      print*, 'Special values:', plus_inf, minus_inf, plus_nanq, minus_nanq, nans
 
* They can also occur as the result of operations.

      large = 10.0 ** 200
      print*, 'Number too big for a REAL:', large * large
      print*, 'Number divided by zero:', (-large) / 0.0
      print*, 'Nonsensical results:', plus_inf - plus_inf, sqrt(-large)
 
* To find if something is a NaN, compare it to itself.

      print*, 'Does a NaNQ equal itself:', plus_nanq .eq. plus_nanq
      print*, 'Does a NaNS equal itself:', nans .eq. nans
      print*, 'Does a sqrt(-large) equal itself:', sqrt(-large) .eq. sqrt(-large)
      print*, 'Does sqrt(-1.) equal a NaN:', sqrt(-1.)

* Only for a NaN is this comparison false.

      end
