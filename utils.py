import collections.abc

def pad_list(ls, count, item):
    ret = list(ls)
    pad_len = count - len(ret)
    if pad_len > 0:
        ret.extend([item]*pad_len)
    return ret

def get_between(string: str, start_str: str, end_str: str) -> str:
    if start_str == "":
        start = 0
    else:
        start = string.find(start_str)
        if start < 0:
            return ""
        start += 1

    if end_str == "":
        end = len(string)
    else:
        end = string[start:].find(end_str)
        if end < 0:
            return ""
        end += start

    return string[start:end]

# Based on: https://stackoverflow.com/a/44328500, plus Charlie's comment
def is_iterable(obj):
    return (
        isinstance(obj, collections.abc.Iterable) 
        and not isinstance(obj, str)
    )
