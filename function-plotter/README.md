
# FUNction Plotter

> One of Santa's elves found this weird service on the internet. He doesn't like
> maths, so he asked you to check if there's anything hidden behind it.

![Screenshot](screenshot.png)

| Asset      | Note                                                             |
|------------|------------------------------------------------------------------|
| Author     | yakuhito                                                         |
| Category   | Misc                                                             |
| Server     | `nc challs.xmas.htsp.ro 13005`                                   |
| Writeup by | Max                                                              |

---

Psyqo called me for help on this one. From the title alone it seemed clear to me what the challenge would be about and how it would be solveable, but I had put it off for other flags until that point. 

(Sadly I don't have footage for this one, even though I screenshared it for two team members - just forgot to start OBS.)

## Analysis

Upon connecting to the server, you are greeted with a prompt:

```
Welcome to my guessing service!
Can you guess all 961 values?

f(28, 11)=
```

Psyqo told me that each answer has to be either one or zero, and that the same question always has the same answer across different attempts. That saved me the exploratory work.

Let's recap:

- The challenge is called **Function Plotter**
- We are to guess the function values of some 2 argument function somehow.
- `961 = 31 * 31`, and the queried function arguments appear to both always be within `[0, 31)`.
- For every answer we give, we are told whether it is right or wrong.
- The only valid values are 1 and 0.

Clearly, the solution will involve plotting the value of this binary function over a 31x31 grid.

My first thought was that you only get told certain values, and the remaining ones become obvious when you plot the function. But I quickly realized that we get all the information you need from a single run through all 961 questions.

So, let's do just that: `yes 0 | nc challs.xmas.htsp.ro 13005`.  
We answer `0` to every question, and the answer is either `Good!` (`0` is correct) or `Pretty close, but wrong!` (i.e. the correct answer is `1`).

For some reason it takes quite a few tries for that to actually run to completion. I don't know if it's a problem with the tools I'm using (`nc`) or their server. Doesn't matter for obtaining the flag though, eventually you get a full set of 961 answers. See [`out.txt`][1] for such an output.

### Let's plot that.

## Using regex.

That's right. I'm not in the mood for writing a program to place bits into a 31 by 31 grid. I know my trusty Notepad++ regexes can do it. So here we go:

 1. Paste the console log into a new Notepad++ file and remove the preamble and outro (by hand).
 2. Remove double newlines: `\r\n\r\n` -> `\r\n`
 2. Turn `Good!` into `0` and `Pretty close, but wrong!` into `1`. File now looks like this:
  ```
  f(20, 24)=1
  f(25, 4)=1
  f(11, 2)=1
  f(3, 30)=0
  ...
  ```
 4. We want to sort these lines by the coordinates (Edit -> Line Operations -> Sort Lines Lexicographically Ascending), but right now that will result in the order `0, 1, 10, 11, 12...`. We need to add a space before all single digit numbers:
    For the first arguments: `\((\d),` -> `\( \1,`
    Translation: "Find a literal `(` followed by a digit (which we capture), followed by a comma. Replace that with a literal `(`, a space, the captured digit and a comma."
    For the second arguments: ` (\d)\)` -> `  \1\)`
    Translation: "Find a space followed by a digit (which we capture) followed by a literal `)`. Replace that with two spaces, the digit and a `)`.
  The file now looks like this:
  ```
  f(20, 24)=1
  f(25,  4)=1
  f(11,  2)=1
  f( 3, 30)=0
  ...
  ```
 5. Sort the lines.
  ```
  f( 0,  0)=0
  f( 0,  1)=0
  f( 0,  2)=0
  f( 0,  3)=0
  ...
  ```
 6. Remove everything that is not an answer bit. `.*=` -> _nothing_
 7. Remove all newlines. `\r\n` -> _nothing_

We now have a flattened blob of all the answers (see [`blob.txt`][2]). You can use a regex with quantifiers to bring this into lines again, but it's time for my favorite cryptogram solving technique: **Change the width of the Notepad++ window until the data aligns** (i.e. until each line is 31 characters in this case).

![The data in lines of 31 columns][3]

To make things legible, use the Mark functionality to highlight all `1` values. We want to appreciate what we just plotted, right?  

![A wild QR code appears][4]

Surprise, it's a QR code! One of my teammates thankfully found a binary string QR decoding site (because of course that exists?) while I was still scrambling to find my phone. I would've doubled each character (to get roughly square "pixels" in the plot) before capturing the QR code with the phone, but that wasn't needed. Neither was it necessary to actually give 961 correct answers to the server - the QR code itself decodes to the flag:

`X-MAS{Th@t's_4_w31rD_fUnCt10n!!!_8082838205}`

[1]: out.txt
[2]: blob.txt
[3]: blob31.PNG
[4]: qr.PNG
