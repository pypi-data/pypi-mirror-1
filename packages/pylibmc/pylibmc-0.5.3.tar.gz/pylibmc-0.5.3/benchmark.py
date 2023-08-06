"""Benchmarking LOL!"""

import sys
from time import time

implementations = ("memcache", "cmemcache", "pylibmc")
test_servers = ["127.0.0.1:11211"]

def median(L):
    """Calculate median of L.

    >>> median(range(3))
    1
    >>> median(range(4))
    1.5
    """
    L = L[:]
    L.sort()
    if len(L) & 1:
        return L[int(len(L) / 2 + 0.5)]
    else:
        return (L[len(L) / 2 - 1] + L[len(L) / 2]) / 2.0

def run_test(mc, testfunc, prefunc=str, n_calls=30000):
    times = [None] * n_calls
    for i in xrange(n_calls):
        prefunc(mc)
        start_t = time()
        testfunc(mc)
        end_t = time()
        times[i] = end_t - start_t
    fname = testfunc.__name__
    fname_spaces = len(fname) * " "
    # Average times.
    avg_call_time = sum(times) / float(n_calls)
    avg_calls_sec = 1 / avg_call_time
    avg_call_time_micro = avg_call_time * 1000000
    # Median times.
    med_call_time = median(times)
    med_calls_sec = 1 / med_call_time
    med_call_time_micro = med_call_time * 1000000
    print "%s: avg: %.2f calls/sec  (%.2f microsec/call)" % (
        fname, avg_calls_sec, avg_call_time_micro)
    print "%s  med: %.2f calls/sec  (%.2f microsec/call)" % (
        fname_spaces, med_calls_sec, med_call_time_micro)

def simple_set(mc):
    mc.set("foo", "bar")
    mc.set("bar", "foo")

def multi_set(mc):
    d1 = {"foo": "bar", "bar": "foo", "hey": "yo"}
    d2 = {"abc": "cba", "chewbacca": "plankton", "lala": "yo"}
    if hasattr(mc, "set_multi"):
        mc.set_multi(d1)
        mc.set_multi(d2)
    else:
        for (key, value) in d1.items() + d2.items():
            mc.set(key, value)

def simple_get(mc):
    mc.get("foo")
    mc.get("bar")

def multi_get(mc):
    mc.get_multi(["foo", "bar", "hey"])
    mc.get_multi(["abc", "chewbacca", "lala"])

def simple_delete(mc):
    simple_set(mc)
    mc.delete("foo")
    mc.delete("bar")

def multi_delete(mc):
    multi_set(mc)
    if hasattr(mc, "delete_multi"):
        mc.delete_multi(["foo", "bar", "hey"])
        mc.delete_multi(["abc", "chewbacca", "lala"])
    else:
        for k in ("foo", "bar", "hey", "abc", "chewbacca", "lala"):
            mc.delete(k)

tests = ((str, simple_set),
         (str, multi_set),
         (simple_set, simple_get),
         (multi_set, multi_get),
         (simple_set, simple_delete),
         (multi_set, multi_delete))

do_tests_impls = sys.argv[1:] or implementations

for impl in implementations:
    if impl not in do_tests_impls:
        continue
    print "Testing", impl
    print "=" * (len(impl) + 8)
    Client = __import__(impl, {}, {}, ["Client"]).Client
    mc = Client(test_servers)
    # Test 1: Setting keys
    map(lambda (p, f): run_test(mc, f, p), tests)
    print
