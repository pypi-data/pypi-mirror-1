import copy
import re
import simplejson

__all__ = ["jsondiff", "jsonapply"]

def jsondiff(left, right, stream=None):
    if stream is None:
        stream = sys.stdout
    flushed = 0
    path = []
    for command in iter_diff(left, right):
        if command["op"] not in ["descend", "ascend"]:
            for i in range(flushed, len(path)):
                stream.write("%s\n" % simplejson.dumps(path[i]))
            flushed = len(path)
            stream.write("%s\n" % simplejson.dumps(command))
        elif command["op"] == "descend":
            path.append(command)
        else:
            if flushed == len(path):
                stream.write("%s\n" % simplejson.dumps(command))
            path.pop()
            flushed = min(flushed, len(path))

def jsonapply(stream, curr, in_place=False):
    if not in_place:
        ref = copy.deepcopy(curr)
    if isinstance(curr, dict):
        return apply_object(stream, curr, root=True)
    elif isinstance(curr, list):
        return apply_array(stream, curr, root=True)
    else:
        return apply_value(stream, curr, root=True)

def iter_diff(left, right):
    if isinstance(left, dict) and isinstance(right, dict):
        for key in left:
            if key in right:
                yield {"op": "descend", "key": key}
                for comm in iter_diff(left[key], right[key]):
                    yield comm
                yield {"op": "ascend"}
            else:
                yield {"op": "rem", "key": key}
        for key in right:
            if key not in left:
                yield {"op": "add", "key": key, "value": right[key]}
    elif isinstance(left, list) and isinstance(right, list):
        idx = 0
        while idx < len(left) and idx < len(right):
            yield {"op": "descend", "index": idx}
            for comm in iter_diff(left[idx], right[idx]):
                yield comm
            yield {"op": "ascend"}
            idx += 1
        assert idx == len(left) or idx == len(right)
        for l in range(idx, len(left)):
            yield {"op": "rem", "index": l}
        for r in range(idx, len(right)):
            yield {"op": "add", "index": r, "value": right[r]}
    elif left != right:
        yield {"op": "swap", "value": right}

def apply_object(stream, curr, root=False):
    try:
        command = simplejson.loads(stream.next())
        if command["op"] == "swap":
            curr = command["value"]
            command = simplejson.loads(stream.next())
            if command["op"] != "ascend":
                raise RuntimeError("Invalid operation on value: '%s'" % command)
            return curr
        while command:
            if command["op"] == "ascend":
                return curr
            elif command["op"] == "descend":
                curr[command["key"]] = jsonapply(stream, curr[command["key"]])
            elif command["op"] == "add":
                curr[command["key"]] = command["value"]
            elif command["op"] == "rem":
                del curr[command["key"]]
            else:
                raise RuntimeError("Unknown command: '%s'" % command)
            command = simplejson.loads(stream.next())
    except StopIteration:
        if not root:
            raise RuntimeError("Early termination of edit stream.")
    return curr

def apply_array(stream, curr, root=False):
    try:
        removed = 0
        command = simplejson.loads(stream.next())
        if command["op"] == "swap":
            curr = command["value"]
            command = simplejson.loads(stream.next())
            if command["op"] != "ascend":
                raise RuntimeError("Invalid operation on value: '%s'" % command)
            return curr
        while command:
            if command["op"] == "ascend":
                return curr
            elif command["op"] == "descend":
                curr[command["index"]] = jsonapply(stream, curr[command["index"]])
            elif command["op"] == "rem":
                curr.pop(command["index"]-removed)
                removed += 1
            elif command["op"] == "add":
                if len(curr) != command["index"]:
                    raise RuntimeError("Adding element beyond end of an array.")
                curr.append(command["value"])
            else:
                raise RuntimeError("Unknown command: '%s'" % command)
            command = simplejson.loads(stream.next())
    except StopIteration:
        if not root:
            raise RuntimeError("Early termination of edit stream.")
    return curr

def apply_value(stream, curr, root=False):
    try:
        command = simplejson.loads(stream.next())
        if command["op"] != "swap":
            raise RuntimeError("Invalid command on value: '%s'" % command)
        curr = command["value"]
        command = simplejson.loads(stream.next())
        if command["op"] != "ascend":
            raise RuntimeError("Invalid operation on value: '%s'" % command)
    except StopIteration:
        if not root:
            raise
    return curr
