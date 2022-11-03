# Countdown: Tutorial + Tips

To ensure you can enjoy this game maximally, here is a detailed
tutorial on it, from the basic idea to more complex mechanics.
Tips are included to help you.

## Getting started

### Aim of the game

In this game, 7 random numbers are generated and using these numbers, along with
basic mathematical operators and parentheses, you must form a mathematical expression
equal to a larger target number.

However, you only have **30 seconds**, meaning you must be quick in finding
a solution. Therefore, strong mental maths skills are highly beneficial.

### Selecting numbers

From the main menu, click on the large orange 'Play' button.

Now, you need to select 7 numbers to be used as the numbers you can use for
the expression to create.

There are two categories of number:
* Small numbers (2-9) - each can be generated only once
* Big numbers (25, 50, 75, 100) - each can be generated up to twice

Click on any orange rectangle to select a number. A small number can be selected
from the top row, and the bottom row selects a big number.

The maximum number of both small and big numbers is 5, meaning there must be
at least 2 small and big numbers.

After selecting 7 numbers, click on the 'Start' button to begin the round.

### Forming an expression equal to the target

Upon starting, a preliminary countdown begins (3, 2, 1, GO!). After this, the target
number is generated using a fairly complex algorithm to ensure it is possible to get
with 4 numbers, but not less (not too easy, not too hard). The target number is
between 201 and 999 (inclusive).

Once displayed, the countdown begins and the timer at the bottom visibly starts
progressing. This is the 30 second timer. You must use this time to try and find a
solution (expression).

Criteria for a valid solution:
* It is equal to the target number
* It only uses the 7 numbers provided (not all numbers need to be used)
* It only uses addition (+), subtraction (-), multiplication (x), division (÷),
and parentheses (which can be nested). So, exponentiation is disallowed.

Don't forget the order of operations:
* Parentheses first
* Multiplication/division (left to right)
* Addition/subtraction (left to right)

Here is an example of a possible round:

    You have the following numbers: 2, 4, 5, 9, 25, 75, 100
    The target is: 515

    Three valid solutions would be:
    - 100x5+4+9+2
    - (100-2)x5+25
    - ((2x100+75)x9+25x4)÷5

    An example of an invalid solution would be: 2^9+75÷25, because
    despite evaluating correctly as 515, exponentiation is used which is disallowed.

It is often challenging to find a solution in just 30 seconds. Here are some tips nonetheless:
* Try to get as close to the target as possible using as few numbers as possible,
so that any remaining numbers can be used to make the expression fully correct.
* Consider making 2 factors of the target and multiplying them. This strategy is best
if the target is a nice number, such as 240, and not 863.
* Don't be afraid to use parentheses. They can be extremely powerful.
* Do not waste time! Spend every second trying to reach a solution.
* Use pen and paper to help you, unless you have an excellent working memory.
* A calculator may seem beneficial, but this game is all about mental
maths and using a calculator may cause you to run out of time. So, train your brain
and don't rely on a calculator unless you're desperate.
* **Take breaks** whenever you just cannot concentrate! Remember, despite involving
maths, you are still meant to have fun playing this game, and doing something else
when you are just not playing well is encouraged.

### Entering your solution

Once the time runs out, you will be automatically directed to enter a solution.
If you could not find a solution in time, just click on the 'No solution' button.
Unfortunately, you lose.

However, if you have successfully found a solution, congrats!
Using the buttons, enter each part of the solution into the green box
(including parentheses, operators and numbers). Try to omit useless parentheses
which do not change order of evaluation to reduce clutter. To delete a part, just
click on the button '←'.

Once you enter your proposed solution, click on 'Submit'. The solution is checked,
and if indeed correct, you win! If it is wrong, you will stay where you are.
Perhaps you just made a minor mistake in the input, or your solution is outright wrong.

### End of the game

The round is complete! Either you win (found a solution), or lose (no solution).

Below, references to stats, achievements, solution generation and history are
involved. To find out more about each, go to the corresponding parts of the tutorial.

If you win, your solution is displayed and a congratulatory message is shown alongside.
Your win streak is incremented by 1, and you earn a good amount of XP just for your
solution, with extra based on factors such as:
* How many numbers used in the solution
* Operators used (using all operators grants a bonus 50XP)
* Current win streak

But if you lose, a reassuring message is displayed, and your win streak is reset to 0.
However, you still earn 25 XP just for playing.

For both outcomes, the game data is saved in history,
and any achievements earned at the end are displayed too.

You then have a few navigation options:
* Generate solutions - see what amazing expressions can be formed from the 7 numbers to
equate to the target
* Play again - begin a new round
* Home - return to the main menu

## Stats

Stats are data points which provide insights about your play, such as the number
of games you have played and won, and your level.

Many stats are also timed, meaning you can see them based on your play in the last
24 hours, last 7 days, last 30 days, and all time.

Here are the stats implemented:
* Games played - how many rounds you have completed, whether win or loss
* Games won - the number of wins you have achieved
* Operators used - how many times you have used each operator in solutions
* Small numbers used - how many small numbers (2-9) you have used in solutions
* Big numbers used - how many big numbers (25, 50, 75, 100) you have used in solutions
* XP earned - total XP earned from playing
* Level - based on XP - provides a rough indication of how much experience you have
in the game. The maximum level is 100. Each level requires 100 more XP
than the previous, starting at level 1, with 100 XP needed to reach level 2.
* Best win streak - the highest win streak you have ever achieved (not your current streak)

## Solution Generation

Humans can play this game and find nice solutions, but computer are insane,
and despite technically being super dumb, can follow a series of complex algorithms to
find godly solutions not even a genius would have a chance to see.

Indeed, functionality has been added for you to generate solutions from 7 numbers
for a given target, either at the end of a round, or from history.

Several options allow you to customise solution generation:
* Minimum number count - how many numbers a solution must have at least
* Maximum number count - how many numbers a solution can have at most
* Maximum solution count - how many solutions should be generated at most
* Parentheses - whether to allow nested parentheses or not, or disable them entirely
* Operators - which operators a solution can have in it
* Maximum seconds to generate for - this is often a somewhat slow, intensive process.
So a time limit is set to ensure the result is returned in a practical length of time,
even at the cost of possibly not generating the requested number of solutions, if at
all.

Once the generation completes, any solutions found are displayed in the box
on the right. If no solutions are found, the box remains empty.

## Game History

When you complete a game, it is automatically saved into history. Then, in the
history window, you can view the recent games you have played.
Click into any of them and you get data on the game such as the 7 numbers,
the target number, the start/stop times
(in the current system time zone) and the outcome (win/loss).

You can also generate solutions for any past game you select, just like at the
end of a round.

## Achievements

Achievements are a feature to increase motivation to play the game and provide
something in-game to work towards. They serve as evidence of your dedication,
skill and expertise in this game!

The four tiers of achievement are:
* Bronze (very easy)
* Silver (easy)
* Gold (hard)
* Platinum (very hard)

There are a total of **32** achievements of varying difficulty.

### Tiered achievements
4 achievements are grouped into one stat, but get progressively harder
(bronze, silver, gold, platinum). 24 achievements total.

* *Countdown Commitment* - games played
* *Getting good at maths!* - wins
* *Time flies when you're having fun* - time played
* *Expertise Development* - level
* *Winner Winner Chicken Dinner* - maximum win streak
* *Achievement for achievements* - achievements earned

### Special achievements
Achievements which are earned once with an appropriate tier
selected for their difficulty. 8 achievements total.

* *Obsession!* - games played in the last 24 hours
* *Addiction!* - games played in the last 7 days
* *OOPS!* - incorrect solution
* *Small numbers reign!* - small number use
* *Brutal big numbers!* - big number use
* *Full House!* - all numbers used
* *Together they are strong!* - all operators used
* *One Operator!* - one operator used only

## Options

Various settings are available to customise your in-game experience:
* Music - can either be ON/OFF, various countdown tracks available
to play during the 30 second timer
* Sound Effects - can either be ON/OFF
* Stats/Achievements/History - can either be ON/OFF. When ON, your
stats are updated, achievements are checked for, and completed games
are saved in history. None of this occurs when this setting is OFF,
and win streak is also unaffected when OFF. Also, turning this setting
OFF will not reset anything: you can turn it ON again and the previous
data will be intact.
* Auto generate numbers - can either be ON/OFF,
useful to automatically select 7 numbers rather than manually (great if you are lazy!)
* Time limit to enter solution - can either be ON/OFF, limits the length
of time you have to enter a solution before timing out and automatically losing.

Settings can be reset to default in case you mess them up!

Another option available is to completely reset your data. This means
your stats, achievements and history are wiped and basically, you
would be starting from scratch. However, please only do this if you are 100% certain,
as wiped data **CANNOT BE RESTORED**.

## Other Important Information

Before ending the tutorial, here are some other points to note to ensure
you gain the best experience:
* **No internet connection** is needed to play.
* It is recommended you play in **full-screen** to prevent window sizing issues.
* Only **one** instance of the game can be running at once.
* Game data is stored locally, meaning if you really wanted to, you could find it
in the AppData/Local folder and create manual backups.
* In theory, you could cheat in this game in various different ways,
but why would you? It ruins the fun!
* If you mess with any of the game-related files and the game itself breaks,
congratulations! What did you expect?
* If any unhandled errors occur, unfortunately, the game will crash and you will
receive an error message. Sorry for the inconvenience if this occurs and you did
not tamper with the game files.

## Conclusion

This is plenty of information for you to enjoy the game. There are a few
other tiny features which you may encounter as well, but the information
provided in this tutorial should be adequate and accurate.

Overall, hopefully all this detailed information helps you navigate through
the game and play it to the best of your ability whilst maximising fun.

*Good luck, and happy solving!*