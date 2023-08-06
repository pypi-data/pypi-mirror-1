import math
import types

__all__ = ["jsoncmp"]

def jsoncmp(left, right, tolerance=1E-6):
    if isinstance(left, dict) and isinstance(right, dict):
        return compare_object(left, right)
    elif isinstance(left, list) and isinstance(right, list):
        return compare_array(left, right)
    elif type(left) == types.FloatType and type(right) == types.FloatType:
        return math.fabs(left - right) < tolerance
    else:
        return left == right
    
def compare_object(left, right):
    lset = set(left.keys())
    rset = set(right.keys())
    if lset != rset:
        return False
    for k in lset:
        if not jsoncmp(left[k], right[k]):
            return False
    return True

def compare_array(left, right):
    if len(left) != len(right):
        return False
    for idx, val in enumerate(left):
        if not jsoncmp(val, right[idx]):
            return False
    return True