# Sleepy

A lexer and parser for the [Sleep scripting language](http://sleep.dashnine.org/).
All versions of Sleep 2.1 and below are supported.

All Sleep extensions are supported as defined in the Sleep manual.
The only deviation from the language specification are "operator bridges" which _must_ be a valid identifier for sleepy to parse them (e.g., `r'[a-zA-Z_][a-zA-Z_0-9]*'`).
This change was made to allow sleepy to define operator precedence rules.
This change should not cause any issues.

Sleepy will not tokenize Java object expressions (a.k.a, "Haphazard Object Extensions for Sleep") into their individual components because doing so would create ambiguous grammar rules.
A seperate lexer may be added in the future to handle these expressions.
All other Sleep statements are fully tokenized.

One issue that was encountered when developing Sleepy is that the parser in the official Sleep distribution does not conform to its corresponding documentation.
Namely, it allows for missing semicolons after statements and missing commas between list items.
Sleepy's parser will warn the user of these syntax errors, recover, and then continue parsing.

This project is released under an MIT license.
The unit tests are included from the [official Sleep distribution](http://sleep.dashnine.org/download.html) which is released under a [BSD-3 license](https://github.com/rsmudge/sleep/blob/master/license.txt) and copyrighted to [Raphael Mudge](https://github.com/rsmudge/sleep/tree/master).

The unit tests have been modified to remove profanity using the profanity checker included with the example scripts.
Please excuse anything that may have been missed.