*Note: This is a reference copy. The canonical source file lives at `data/annotations/annotation_guidelines.md`.*

# BALLRIQ Annotation Guidelines

## Overview
This document defines the event labels used for annotating cricket commentary text in the BALLRIQ dataset.

## Event Labels

### FOUR
A boundary scored by the ball reaching the rope after being hit by the bat. Keywords: four, boundary, four runs, चौका, चार रन, चौका.
Example: "Smashed through the covers for four"

### SIX
A shot where the ball clears the boundary rope without bouncing. Keywords: six, over the ropes, maximum, छक्का, छह रन, षटकार.
Example: "Huge six over long-on"

### WICKET
A batsman getting out in any form (caught, bowled, lbw, run out, stumped, hit wicket). Keywords: wicket, out, bowled, caught, lbw, विकेट, आउट.
Example: "Bumrah strikes! Bowled him through the gate"

### DOT
A delivery where no runs are scored off the bat and the batsman is not out. Keywords: dot, no run, defended, beaten.
Example: "Solid defensive shot, no run"

### SINGLE
Exactly one run taken off the bat. Keywords: single, one run, quick single.
Example: "Nudged into the leg side for one"

### DOUBLE
Exactly two runs taken off the bat. Keywords: couple, two runs, double.
Example: "Swept nicely for a couple"

### WIDE
An illegal delivery called by the umpire that is too wide for the batsman. Keywords: wide, wide ball, extra, वाइड.
Example: "Wide down the leg side, one extra"

### NO_BALL
An illegal delivery, typically overstepping the crease. Keywords: no ball, no-ball, free hit, नो बॉल.
Example: "No ball called, free hit coming up"

### FIFTY
A batsman reaching 50 runs in their innings. Keywords: fifty, half-century, 50, अर्धशतक.
Example: "Kohli brings up his fifty with a single"

### CENTURY
A batsman reaching 100 runs in their innings. Keywords: century, hundred, 100, शतक.
Example: "Brilliant century from Rohit Sharma"

### OTHER
Any event that does not fit the above categories. Use sparingly. Examples: overthrows, penalties, byes, leg byes, reviews, weather delays.

## Annotation Rules
1. Read the full commentary text before assigning a label.
2. Assign exactly one label per commentary text.
3. If multiple events are described, label the PRIMARY event.
4. When uncertain, prefer DOT over OTHER.
5. For code-mixed text, label based on the cricket event described, regardless of language.
6. Record your annotator ID and date with each annotation.