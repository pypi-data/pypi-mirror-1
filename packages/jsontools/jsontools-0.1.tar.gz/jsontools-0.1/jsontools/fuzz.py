
import copy
import random

__all__ = ["FuzzyJson"]

class FuzzyJson(object):
    def __init__(self):
        self.probs = {
            "types": {
                "object": 0.5,
                "array": 0.2,
                "string": 0.1,
                "number": 0.1,
                "special": 0.1,
            },
            "object": {
                "descend": 0.9,
                "rem": 0.1
            },
            "array": {
                "descend": 0.9,
                "rem": 0.1,
            },
            "extension": {
                "object": 0.85,
                "array": 0.85,
                "string": 0.9
            }
        }
    
    def __iter__(self):
        return self
    
    def next(self):
        vtype = self.choose(self.probs["types"])
        return getattr(self, vtype)(None, True, 1)

    def generate(self, num=100):
        for i in range(num):
            yield self.next()

    def modify(self, val, in_place=False):
        if in_place:
            return self.mutate(val, False, 1)
        else:
            return self.mutate(copy.deepcopy(val), False, 1)

    def add_initial(self, val):
        self.initial.append(val)
    
    def choose(self, probs):
        val = random.random()
        curr = 0.0
        for k, v in probs.iteritems():
            curr += v
            if val < curr:
                return k
        assert True == False, "Failed to pick a random value."
    
    def randomchar(self):
        return random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 \t")
    
    def mutate(self, val, create, depth):
        if isinstance(val, dict):
            return self.object(val, create, depth)
        elif isinstance(val, list):
            return self.array(val, create, depth)
        else:
            return random.choice([self.string, self.number, self.special])(None, False, depth)
    
    def object(self, curr, create, depth):
        if curr is None:
            curr = {}
        extension = self.probs["extension"]["object"] / float(depth)
        if not create:
            extension /= 2
        while random.random() < extension:
            key = self.string(None, True, depth)
            vtype = self.choose(self.probs["types"])
            ret = getattr(self, vtype)(None, True, depth+1)
            if ret in [{}, []]:
                ret = random.choice([self.string, self.number, self.special])(None, True, depth+1)
            curr[key] = ret
        for key in list(curr.keys()):
            action = self.choose(self.probs["object"])
            if action == "descend":
                curr[key] = self.mutate(curr[key], False, depth+1)
            elif action == "rem":
                del curr[key]
            else:
                raise RuntimeError("Unknown action type: '%s'" % action)
        return curr

    def array(self, curr, create, depth):
        if curr is None:
            curr = []
        extension = self.probs["extension"]["object"] / depth
        if not create:
            extension /= 2
        while random.random() < extension:
            vtype = self.choose(self.probs["types"])
            ret = getattr(self, vtype)(None, True, depth+1)
            if ret in [{}, []]:
                ret = random.choice([self.string, self.number, self.special])(None, True, depth+1)
            curr.append(ret)  
        idx = 0
        while idx < len(curr):
            action = self.choose(self.probs["array"])
            if action == "descend":
                curr[idx] = self.mutate(curr[idx], False, depth+1)
            elif action == "rem":
                curr.pop(idx)
            else:
                raise RuntimeError("Unknown action type: '%s'" % action)
            idx += 1
        return curr
        
    def string(self, curr, create, depth):
        curr = [self.randomchar()]
        while random.random() < self.probs["extension"]["string"]:
            curr.append(self.randomchar())
        return ''.join(curr)        
    
    def number(self, curr, create, depth):
        return random.choice([lambda: random.randint(0, 10000), random.random])()
    
    def special(self, curr, create, depth):
        return random.choice([True, False, None])
