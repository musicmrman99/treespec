import collections.abc

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
            return ""
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
                return "" # no matching ends left, so no match

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
            return ""
        end += start

    return string[start:end]

# Based on: https://stackoverflow.com/a/44328500, plus Charlie's comment
def is_iterable(obj):
    return (
        isinstance(obj, collections.abc.Iterable) 
        and not isinstance(obj, str)
    )
