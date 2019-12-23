# Reverthable X-Math

> Thought you might like reversing a more functional programming language ;)

![Screenshot](screenshot.png)

| Asset        | Note                                                          |
|--------------|---------------------------------------------------------------|
| Author       | PinkiePie1189                                                 |
| Category     | Reverse Engineering                                           |
| Attachment   | 💾 [Cached][1] 💾 [Original Link][2]                          |
| Writeup by   | Max                                                           |

## Analysis

We have a LISP program that obfuscates a flag, as well as what it outputs. Never written any LISP, but this looks easy enough to work with. I know it's in Polish Notation (and I can't help but link [this xkcd][3] here) and that I can look stuff up as needed.

Since I can't really read Polish Notation, I decided to transpile it (by hand) into something more readable and go from there. (**Warning:** I transpiled it into some abominable child of Python and C with no consistent syntax.)

We have three functions: The recursive `frobnicate`, an obscure `cheekybreeky`, and `hello` which encrypts the flag using the first two functions and prints the result.

After looking up `setq` (I admit to still not fully understanding its "scope") and working through `cheekybreeky`, it becomes clear that we are looking at a convoluted "divide by two" function:

```
int cheekybreeky(num):
  int n = 0
  while (true)
    if (2 * n) >= num:
       break;
    n = n + 1

  if (num == 2 * n):
    return n;
  else
    return n-1;
```

_Side note: Why the heck do half the LISP references on the internet have no HTTPS? I get it, [LISP is timeless][4], but the world around it is not..._

Transpiling the rest and replacing every call to `cheekybreeky` with a division by two, we get ([`task.wtf`][5]):

```
void frobnicate(str, xor, offset, lvl)
	mead = (xor + offset) / 2

	if (xor + 1 < offset)
		print((str[mead] - '0') ^ 42)
		print("/")
		if (lvl == 3)
			mead = 8
		
		frobnicate(str, xor, mead, lvl+1)
		frobnicate(str, mead+1, offset, lvl+1)


int main()
	frobnicate(flagString, 0, length(flagString), 0.0)
	print(0)
```

A few observations:

- The string is never modified.
- We essentially print the string's character values, if a bit obfuscated (the xor with 42 doesn't really complicate things).
- The content of the flag does not affect the control flow - only its length does.

This still looks too complicated for my tastes (the switching around of arguments in the recursive calls is annoying). However, we gathered the information that each printed character maps to some flag characters in a trivially invertible way (xor with 42 and add '0'). If we can find out the order in which the flag characters are printed, we're done.

To my surprise, turning this into proper python code and running it with a known flag didn't work out. I didn't know for sure whether `mead` would have to be a global or a local, but either way I couldn't produce output of the correct length. See [`lisp_pythonized.py`][6] (and let me know if you can spot what I messed up).

But I didn't need a working python implementation, I can just run the original LISP code (with some modifications) on https://tio.run to figure out the pieces I need (namely the order in which the encoded flag characters are printed). So let's go there, pick one of the LISP flavors (I guess Common Lisp does it?), modify the code to `(princ (char str mead))` instead of the encoded one (while failing to guess how to comment in LISP - my screen recording captured an audible sigh googling that one after trying `#` and `//` without approval by the Notepad++ syntax highlighting). Keep the default flag string `"your flag is in another castle"` for now and see what it outputs:

```
 /a/r/o/u/f/ /l/s/ /g/i/i/ /n/r/o/a/n/h/t/e/s/c/ /a/l/t/e/0
```

That in itself won't help me, but I can use a better flag. With `"0123456789abcdefghijkl"` as flag string [I get][7]:

```
b/5/2/1/3/4/8/6/7/9/a/g/d/c/e/f/j/h/i/k/l/0
```

That's still too short, but the solution is clear from here: Add unique characters to the input flag until the output has the same length as the provided one, then use the output to un-permute the provided one (and undo the xor). A [python script][8] later we get the flag:

```
 -MAS{= l0v3 (+ 5t4llm4n 54n74)}
```

I don't know where the X went (and I needed at least a double-take to confirm this is the flag due to the unconventional character set) but that's clearly the flag. Or, for people like me who can't read Polish Notation:

```
love = stallman + santa
```

(PS: I enjoyed the lithp punth in the title - very clever!)


[1]: ./files/
[2]: https://drive.google.com/drive/folders/1CwU_R5PbK-YdSOK40sXlzvY4jPW-dAm2
[3]: https://xkcd.com/645/
[4]: ./lisp_pythonized.py
[5]: ./task.wtf
[6]: https://xkcd.com/297/
[7]: https://tio.run/##hVLbUsMgEH3PV@zUl8VONWlr1fHyJb6kKblYCikhjn593ABpSJypPDDAnj275yyZqJq66/DA81ZCrtVeVllqODZGw7fSoPK84QbEl2ARANL5DCeeHgCzkvPjz173O@AyQDPGoh6cKUk4fLUhXA1cCeup3HrBWlcyAxSq8CgiTvWqksadoO@kr8hYELr5iOm@XQdUA9MsaR5f3C@CtyoH5Oc2Fb1C2IyRK1qTXcAacI3uweCey15a8lD2HEsQC03YYNIsye3oCQzEl1cWkdl@ftORyPY0zkxCbC9CqTq6SH9/A7yl2JqBR7v2NDetlpPSnoX6SkAyVzmaOPiHydOsSOxp2pv8D0D/QHrxocCSC6FwVJWLtIBFnKw324fd49Nzus8IWJTV51HYMYdGW3BMFnBZmNJeGcR3zpfL5wmaoC9ma9uqLOq6Xw
[8]: ./lispMead.py
