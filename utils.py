from typing import Iterable
from collections import namedtuple

def pad_list(ls, count, item):
    ret = list(ls)
    pad_len = count - len(ret)
    if pad_len > 0:
        ret.extend([item]*pad_len)
    return ret

def get_between(string: str, start_str: str, end_str: str, matching: bool = False) -> str:
    if start_str == "":
        start = 0
    else:
        start = string.find(start_str)
        if start < 0:
            return None
        start += 1

    if end_str == "":
        end = len(string)

    # Include up to matching occurance of end_str
    elif matching:
        count = 1
        current_span = start - 1
        while count > 0:
            current_span += 1
            next_start = string[current_span:].find(start_str)
            next_end = string[current_span:].find(end_str)
            
            if next_end == -1:
                return None # no matching ends left, so no match

            # No starts left, next end is before next start, or start_str == end_str
            if (
                next_start == -1
                or next_end < next_start
                or next_start == next_end
            ):
                # Run to next end
                current_span += next_end
                count -= 1

            # Next start is before next end
            else:
                # Run to next start
                current_span += next_start
                count += 1

        end = current_span

    # Include up to first occurance of end_str
    else:
        end = string[start:].find(end_str)
        if end < 0:
            return None
        end += start

    return string[start:end]

Bounds = namedtuple("Bounds", ["start", "end"])

def split_top_level(string: str, delim: str, subexpr_list: list):
    ls = []
    
    rest = string
    batch = ""
    while True:
        next_delim = rest.find(delim)
        
        if next_delim < 0:
            ls.append(batch + rest)
            break

        # subexpr_list = eg. [("<", ">"), ("|", "|")] or []
        subexpr_ranges = []
        for o, c in subexpr_list: # open/close delimiters
            subexpr_str = get_between(rest, o, c, True)
            if subexpr_str is not None:
                subexpr_str_wrapped = o + subexpr_str + c
                subexpr_start = rest.find(subexpr_str_wrapped)
                subexpr_end = subexpr_start + len(subexpr_str_wrapped)
                subexpr_ranges.append(Bounds(subexpr_start, subexpr_end))

        # Ensure that earliest_subexpr[0] cannot be < next_delim
        # WARNING: -1 is NOT a valid index of next_subexprs_str
        earliest_subexpr = Bounds(next_delim, next_delim)
        if len(subexpr_ranges) != 0:
            earliest_subexpr = min(
                subexpr_ranges,
                key=lambda ser: ser.start
            )

        # Add the whole sub-expression to the batch and keep going
        if earliest_subexpr.start < next_delim:
            batch += rest[:earliest_subexpr.end]
            rest = rest[earliest_subexpr.end:]

        # Or add the rest of the batch and finalise it, then move
        # on to the next batch.
        else:
            batch += rest[:next_delim]
            rest = rest[next_delim+1:]

            ls.append(batch)
            batch = ""

    return ls

# Based on: https://stackoverflow.com/a/44328500, plus Charlie's comment
def is_iterable(obj):
    return (
        isinstance(obj, Iterable) 
        and not isinstance(obj, str)
    )
