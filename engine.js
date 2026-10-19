// Little Math engine: exact queue and throughput arithmetic on BigInt values scaled by 1000.
var NUM_ERR = "each entry must be a number from 0 to 1000000 with at most 3 decimals";
var BLANK_ERR = "leave exactly one of the three boxes blank and fill the other two";
var POS_ERR = "each filled box must be a number above 0, up to 1000000, with at most 3 decimals";
var SERVICE_ERR = "the service rate must be above 0";
var PER_ITEM_ERR = "the time per item must be above 0";
var BATCH_ERR = "the batch size must be a whole number from 1 to 100000";
var TARGET_ERR = "the target must be above 0";

// parse "12.5" into 12500n (value x 1000); null when not a number in range
function _scaled(t) {
  t = typeof t === "string" ? t.trim() : "";
  var m = /^([0-9]{1,7})(?:\.([0-9]{1,3}))?$/.exec(t);
  if (!m) return null;
  var v = BigInt(m[1]) * 1000n + BigInt(((m[2] || "") + "000").slice(0, 3));
  return v > 1000000000n ? null : v;
}
function _fmt(num, den, k) {
  var p = 10n ** BigInt(k);
  var s = ((2n * num * p + den) / (2n * den)).toString();
  while (s.length < k + 1) s = "0" + s;
  return s.slice(0, s.length - k) + "." + s.slice(s.length - k);
}
function _two(num, den) { return _fmt(num, den, 2); }
function _show(v) {
  var s = _fmt(v, 1000n, 3);
  return s.replace(/0+$/, "").replace(/\.$/, "");
}

// The law truth: L = rate x time, with exactly one box left blank.
function lawTruth(items, rate, time) {
  var raw = [items, rate, time].map(function (t) { return typeof t === "string" ? t.trim() : ""; });
  var blanks = raw.filter(function (t) { return t === ""; }).length;
  if (blanks !== 1) throw new Error(BLANK_ERR);
  var v = raw.map(function (t) {
    if (t === "") return null;
    var s = _scaled(t);
    if (s === null || s === 0n) throw new Error(POS_ERR);
    return s;
  });
  var tail = " This is Little's law, L = rate x time, applied to your two numbers.";
  if (v[0] === null) {
    return "Solving for the items in the system: arrival rate " + _show(v[1]) + " x time in the system " + _show(v[2]) + " = " + _two(v[1] * v[2], 1000000n) + "." + tail;
  }
  if (v[1] === null) {
    return "Solving for the arrival rate: items in the system " + _show(v[0]) + " / time in the system " + _show(v[2]) + " = " + _two(v[0], v[2]) + "." + tail;
  }
  return "Solving for the time in the system: items in the system " + _show(v[0]) + " / arrival rate " + _show(v[1]) + " = " + _two(v[0], v[1]) + "." + tail;
}

// The drain truth: a backlog with steady arrivals and steady service.
function drainTruth(arrive, serve, backlog, hours) {
  var a = _scaled(arrive), s = _scaled(serve), b = _scaled(backlog), t = _scaled(hours);
  if (a === null || s === null || b === null || t === null) throw new Error(NUM_ERR);
  if (s === 0n) throw new Error(SERVICE_ERR);
  var num = b * 1000n + (a - s) * t;
  var X = num < 0n ? "0.00" : _two(num, 1000000n);
  var head = "From a backlog of " + _show(b) + ", ";
  if (a > s) {
    return head + "arrivals (" + _show(a) + " per hour) beat service (" + _show(s) + " per hour), so the backlog grows by " + _two(a - s, 1000n) +
      " per hour and is " + X + " at hour " + _show(t) + ". It never clears.";
  }
  if (a === s) {
    return b > 0n
      ? head + "arrivals and service are both " + _show(a) + " per hour, so the backlog stays at " + _show(b) + " and never clears."
      : head + "arrivals and service are both " + _show(a) + " per hour, so nothing queues and the backlog stays at 0.";
  }
  if (b === 0n) {
    return head + "service (" + _show(s) + " per hour) beats arrivals (" + _show(a) + " per hour) and nothing is waiting, so the backlog stays at 0.";
  }
  return head + "service (" + _show(s) + " per hour) beats arrivals (" + _show(a) + " per hour), so the backlog shrinks by " + _two(s - a, 1000n) +
    " per hour and is " + X + " at hour " + _show(t) + ". It clears at hour " + _two(b, s - a) + ".";
}

// The batch truth: setup time per batch against time per item.
function batchTruth(setup, perItem, size, target) {
  var c = _scaled(setup);
  if (c === null) throw new Error(NUM_ERR);
  var p = _scaled(perItem);
  if (p === null) throw new Error(NUM_ERR);
  if (p === 0n) throw new Error(PER_ITEM_ERR);
  var sz = typeof size === "string" ? size.trim() : "";
  if (!/^[0-9]{1,6}$/.test(sz) || parseInt(sz, 10) < 1 || parseInt(sz, 10) > 100000) throw new Error(BATCH_ERR);
  var n = BigInt(sz);
  var r = _scaled(target);
  if (r === null) throw new Error(NUM_ERR);
  if (r === 0n) throw new Error(TARGET_ERR);
  var T = c + n * p;
  var out = "A batch of " + n + " takes " + _two(T, 1000n) + " min (" + _two(T, n * 1000n) + " min per item, " + _two(60000n * n, T) + " items per hour). " +
    "No batch size can beat " + _two(60000n, p) + " items per hour. ";
  var room = 60000000n - r * p;
  if (room <= 0n) return out + "A target of " + _show(r) + " items per hour cannot be reached at any batch size.";
  var need = (r * c + room - 1n) / room;
  if (need < 1n) need = 1n;
  return out + "The smallest batch that reaches " + _show(r) + " items per hour is " + need + ", which gives " + _two(60000n * need, c + need * p) + " items per hour.";
}
