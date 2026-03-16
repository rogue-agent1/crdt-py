#!/usr/bin/env python3
"""CRDTs: G-Counter, PN-Counter, G-Set, OR-Set, LWW-Register."""
import sys

class GCounter:
    def __init__(self,node_id,n=3):self.id=node_id;self.counts=[0]*n
    def increment(self):self.counts[self.id]+=1
    def value(self):return sum(self.counts)
    def merge(self,other):self.counts=[max(a,b)for a,b in zip(self.counts,other.counts)]

class PNCounter:
    def __init__(self,nid,n=3):self.p=GCounter(nid,n);self.n=GCounter(nid,n)
    def increment(self):self.p.increment()
    def decrement(self):self.n.increment()
    def value(self):return self.p.value()-self.n.value()
    def merge(self,other):self.p.merge(other.p);self.n.merge(other.n)

class GSet:
    def __init__(self):self.s=set()
    def add(self,elem):self.s.add(elem)
    def lookup(self,elem):return elem in self.s
    def merge(self,other):self.s|=other.s

class ORSet:
    def __init__(self):self.elements={};self._tag=0
    def add(self,elem):self._tag+=1;self.elements.setdefault(elem,set()).add(self._tag)
    def remove(self,elem):self.elements.pop(elem,None)
    def lookup(self,elem):return elem in self.elements and bool(self.elements[elem])
    def value(self):return{e for e,tags in self.elements.items() if tags}
    def merge(self,other):
        for e,tags in other.elements.items():
            self.elements.setdefault(e,set()).update(tags)

class LWWRegister:
    def __init__(self):self.value=None;self.ts=0
    def set(self,value,ts):
        if ts>self.ts:self.value=value;self.ts=ts
    def get(self):return self.value
    def merge(self,other):
        if other.ts>self.ts:self.value=other.value;self.ts=other.ts

def main():
    if len(sys.argv)>1 and sys.argv[1]=="--test":
        # G-Counter
        a,b=GCounter(0,2),GCounter(1,2)
        a.increment();a.increment();b.increment()
        a.merge(b)
        assert a.value()==3
        # PN-Counter
        p=PNCounter(0,2);q=PNCounter(1,2)
        p.increment();p.increment();q.decrement()
        p.merge(q)
        assert p.value()==1
        # G-Set
        s1,s2=GSet(),GSet();s1.add("a");s2.add("b");s1.merge(s2)
        assert s1.lookup("a") and s1.lookup("b")
        # OR-Set
        o=ORSet();o.add("x");o.add("y");o.remove("x")
        assert not o.lookup("x") and o.lookup("y")
        # LWW-Register
        r1,r2=LWWRegister(),LWWRegister()
        r1.set("old",1);r2.set("new",2);r1.merge(r2)
        assert r1.get()=="new"
        print("All tests passed!")
    else:
        c=GCounter(0,3);c.increment();c.increment()
        print(f"G-Counter: {c.value()}")
if __name__=="__main__":main()
