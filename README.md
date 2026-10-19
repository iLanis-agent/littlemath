# Little Math

Little's law and queue backlog arithmetic. A backlog of 50 with 8 arriving and 10 served per hour takes 25 hours to clear, not the 5 you get by ignoring arrivals.

## What it computes

- **The law truth** - items in the system = arrival rate x time in the system. Leave one of the three boxes blank and it solves for it.
- **The drain truth** - a backlog with steady arrivals and steady service: how it moves, the backlog at the hour you pick, and when it clears (or that it never does).
- **The batch truth** - setup time per batch against time per item: batch time, minutes per item, items per hour, the ceiling no batch size can beat, and the smallest batch that reaches a target rate.

Entries are numbers from 0 to 1000000 with up to 3 decimals (batch size is a whole number from 1 to 100000). Results are rounded half up to 2 decimals.

## Boundary

Arithmetic only, on steady rates. It does not know how any real queue, line, team or machine behaves, and gives no verdict on staffing, capacity or whether a plan will work. Every figure is the owner's own entry.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic (BigInt values scaled by 1000, closed-form smallest batch).
- `oracle.py` - the Python mirror (Fractions and Decimals, smallest batch by search) that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (74 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/littlemath/
Repo: https://github.com/iLanis-agent/littlemath
