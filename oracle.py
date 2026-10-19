#!/usr/bin/env python3
# Little Math oracle - mirrors engine.js with Fractions and Decimals instead of scaled BigInts.
import json, re
from decimal import Decimal
from fractions import Fraction
from math import ceil, floor

NUM_ERR = "each entry must be a number from 0 to 1000000 with at most 3 decimals"
BLANK_ERR = "leave exactly one of the three boxes blank and fill the other two"
POS_ERR = "each filled box must be a number above 0, up to 1000000, with at most 3 decimals"
SERVICE_ERR = "the service rate must be above 0"
PER_ITEM_ERR = "the time per item must be above 0"
BATCH_ERR = "the batch size must be a whole number from 1 to 100000"
TARGET_ERR = "the target must be above 0"

def parse(t):
    t = t.strip() if isinstance(t, str) else ""
    if not re.fullmatch(r"[0-9]{1,7}(\.[0-9]{1,3})?", t): return None
    f = Fraction(t)
    return None if f > 1000000 else f

def two(f):
    sc = floor(Fraction(f) * 100 + Fraction(1, 2))
    s = str(sc).rjust(3, "0")
    return s[:-2] + "." + s[-2:]

def show(f):
    return format(Decimal(f.numerator) / Decimal(f.denominator), "f").rstrip("0").rstrip(".") if f.denominator != 1 else str(f.numerator)

def law(items, rate, time):
    raw = [x.strip() if isinstance(x, str) else "" for x in (items, rate, time)]
    if sum(1 for x in raw if x == "") != 1: raise ValueError(BLANK_ERR)
    v = []
    for x in raw:
        if x == "": v.append(None); continue
        f = parse(x)
        if f is None or f == 0: raise ValueError(POS_ERR)
        v.append(f)
    tail = " This is Little's law, L = rate x time, applied to your two numbers."
    if v[0] is None:
        return f"Solving for the items in the system: arrival rate {show(v[1])} x time in the system {show(v[2])} = {two(v[1] * v[2])}." + tail
    if v[1] is None:
        return f"Solving for the arrival rate: items in the system {show(v[0])} / time in the system {show(v[2])} = {two(v[0] / v[2])}." + tail
    return f"Solving for the time in the system: items in the system {show(v[0])} / arrival rate {show(v[1])} = {two(v[0] / v[1])}." + tail

def drain(arrive, serve, backlog, hours):
    a, s, b, t = parse(arrive), parse(serve), parse(backlog), parse(hours)
    if None in (a, s, b, t): raise ValueError(NUM_ERR)
    if s == 0: raise ValueError(SERVICE_ERR)
    at = b + (a - s) * t
    X = two(max(at, 0))
    head = f"From a backlog of {show(b)}, "
    if a > s:
        return head + f"arrivals ({show(a)} per hour) beat service ({show(s)} per hour), so the backlog grows by {two(a - s)} per hour and is {X} at hour {show(t)}. It never clears."
    if a == s:
        if b > 0: return head + f"arrivals and service are both {show(a)} per hour, so the backlog stays at {show(b)} and never clears."
        return head + f"arrivals and service are both {show(a)} per hour, so nothing queues and the backlog stays at 0."
    if b == 0:
        return head + f"service ({show(s)} per hour) beats arrivals ({show(a)} per hour) and nothing is waiting, so the backlog stays at 0."
    return head + f"service ({show(s)} per hour) beats arrivals ({show(a)} per hour), so the backlog shrinks by {two(s - a)} per hour and is {X} at hour {show(t)}. It clears at hour {two(b / (s - a))}."

def batch(setup, per_item, size, target):
    c = parse(setup)
    if c is None: raise ValueError(NUM_ERR)
    p = parse(per_item)
    if p is None: raise ValueError(NUM_ERR)
    if p == 0: raise ValueError(PER_ITEM_ERR)
    z = size.strip() if isinstance(size, str) else ""
    if not re.fullmatch(r"[0-9]{1,6}", z) or not (1 <= int(z) <= 100000): raise ValueError(BATCH_ERR)
    n = int(z)
    r = parse(target)
    if r is None: raise ValueError(NUM_ERR)
    if r == 0: raise ValueError(TARGET_ERR)
    T = c + n * p
    out = f"A batch of {n} takes {two(T)} min ({two(T / n)} min per item, {two(60 * n / T)} items per hour). No batch size can beat {two(60 / p)} items per hour. "
    if r * p >= 60:
        return out + f"A target of {show(r)} items per hour cannot be reached at any batch size."
    # smallest n with 60n/(c+np) >= r, found by search instead of the closed form
    need = 1
    while Fraction(60 * need) / (c + need * p) < r: need += 1
    return out + f"The smallest batch that reaches {show(r)} items per hour is {need}, which gives {two(60 * need / (c + need * p))} items per hour."

FNS = {"lawTruth": law, "drainTruth": drain, "batchTruth": batch}
CASES = [
    ("lawTruth", ["", "4", "3"]), ("lawTruth", ["12", "", "3"]), ("lawTruth", ["12", "4", ""]), ("lawTruth", ["", "2.5", "0.4"]), ("lawTruth", ["7", "", "3"]),
    ("lawTruth", ["10", "3", ""]), ("lawTruth", ["", "0.125", "8"]), ("lawTruth", ["1", "", "1"]), ("lawTruth", ["", "1000000", "1000000"]), ("lawTruth", ["0.001", "", "1000000"]),
    ("lawTruth", [" 6 ", " 2 ", " "]), ("lawTruth", ["", "007", "3.50"]), ("lawTruth", ["5", "", "0.3"]), ("lawTruth", ["100", "0.5", ""]), ("lawTruth", ["", "33.333", "3"]),
    ("lawTruth", ["", "", "3"]), ("lawTruth", ["1", "2", "3"]), ("lawTruth", ["", "", ""]), ("lawTruth", ["0", "4", ""]), ("lawTruth", ["", "-4", "3"]),
    ("lawTruth", ["x", "4", ""]), ("lawTruth", ["", "1.2345", "3"]), ("lawTruth", ["1000001", "", "3"]), ("lawTruth", ["", "4", "0"]), ("lawTruth", ["1e3", "4", ""]),
    ("drainTruth", ["8", "10", "50", "3"]), ("drainTruth", ["12", "10", "50", "3"]), ("drainTruth", ["10", "10", "50", "3"]), ("drainTruth", ["10", "10", "0", "3"]), ("drainTruth", ["5", "10", "0", "3"]),
    ("drainTruth", ["8", "10", "50", "100"]), ("drainTruth", ["8", "10", "50", "0"]), ("drainTruth", ["0", "10", "20", "1"]), ("drainTruth", ["0", "10", "0", "0"]), ("drainTruth", ["9.5", "10", "1", "0.5"]),
    ("drainTruth", ["2.5", "4", "7", "2"]), ("drainTruth", ["7", "9", "10", "5"]), ("drainTruth", ["7", "9", "10", "4"]), ("drainTruth", ["7", "9", "10", "6"]), ("drainTruth", ["10.001", "10", "0", "1000"]),
    ("drainTruth", ["1000000", "1", "1000000", "1000000"]), ("drainTruth", ["3", "7", "1", "1"]), ("drainTruth", [" 8 ", " 10 ", " 50 ", " 3 "]), ("drainTruth", ["8", "0", "50", "3"]), ("drainTruth", ["x", "10", "50", "3"]),
    ("drainTruth", ["8", "10", "", "3"]), ("drainTruth", ["8", "10", "50", "-1"]), ("drainTruth", ["8", "10", "50", "1.5555"]), ("drainTruth", ["1000001", "10", "50", "3"]),
    ("batchTruth", ["10", "2", "8", "20"]), ("batchTruth", ["10", "2", "1", "20"]), ("batchTruth", ["10", "2", "100", "20"]), ("batchTruth", ["0", "2", "5", "20"]), ("batchTruth", ["0", "2", "5", "30"]),
    ("batchTruth", ["0", "2", "5", "31"]), ("batchTruth", ["10", "2", "8", "30"]), ("batchTruth", ["10", "2", "8", "29.9"]), ("batchTruth", ["15", "0.5", "50", "100"]), ("batchTruth", ["15", "0.5", "50", "119"]),
    ("batchTruth", ["15", "0.5", "50", "120"]), ("batchTruth", ["5", "1", "1", "1"]), ("batchTruth", ["5", "1", "100000", "59"]), ("batchTruth", ["0.5", "0.25", "7", "200"]), ("batchTruth", ["60", "1", "10", "30"]),
    ("batchTruth", ["60", "1", "10", "0.5"]), ("batchTruth", [" 10 ", " 2 ", " 8 ", " 20 "]), ("batchTruth", ["x", "2", "8", "20"]), ("batchTruth", ["10", "0", "8", "20"]), ("batchTruth", ["10", "2", "0", "20"]),
    ("batchTruth", ["10", "2", "100001", "20"]), ("batchTruth", ["10", "2", "2.5", "20"]), ("batchTruth", ["10", "2", "8", "0"]), ("batchTruth", ["10", "2", "8", ""]), ("batchTruth", ["", "2", "8", "20"]),
]
out = []
for fn, args in CASES:
    try:
        exp = FNS[fn](*args)
    except ValueError as e:
        exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(len(out), "cases")
