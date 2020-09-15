from types import FunctionType
from typing import Dict, Tuple

# SPECIAL_CHARS
# closing ')', '}' and ']'
# '-' (a range in character set)
# '&', '~', (extended character set operations)
# '#' (comment) and WHITESPACE (ignored) in verbose mode
_special_chars_map = {i: "\\" + chr(i) for i in b"()[]{}?*+-|^$\\.&~# \t\n\r\v\f"}


def escape(pattern):
    """
    Escape special characters in a string.
    """
    if isinstance(pattern, str):
        return pattern.translate(_special_chars_map)
    else:
        pattern = str(pattern, "latin1")
        return pattern.translate(_special_chars_map).encode("latin1")


class UnsupportedError(ValueError):
    pass


def generate_strict_key(
    *, args: Tuple, kwargs: Dict, func: FunctionType, is_method: bool = False
) -> Tuple[dict, dict, str]:
    """Generate function's arguments hash key from optionally typed positional and keyword arguments"""

    #: The code object representing the compiled function body.
    func_code = getattr(func, "__wrapped__", func).__code__
    #: co_argcount is the number of positional arguments (including arguments with default values)
    #: etc: 2(a and b) in lambda a, b=1, *c, d, e=2, **kwd:...
    pos_count = func_code.co_argcount
    #: co_varnames is a tuple containing the names of the local variables (starting with the argument names)
    #: etc: ('a', 'b', 'd', 'e', 'c', 'kwd') in lambda a, b=1, *c, d, e=2, **kwd:...
    arg_names = func_code.co_varnames
    #: A tuple containing positional arguments names
    #: etc: ('a', 'b') in lambda a, b=1, *c, d, e=2, **kwd:...
    positional = tuple(arg_names[:pos_count])
    #: Number of keyword only arguments (not including ** arg)
    #: etc: 2 in lambda a, b=1, *c, d, e=2, **kwd:...
    keyword_only_count = func_code.co_kwonlyargcount
    #: A tuple containing keyword only arguments names
    #: etc: ('d', 'e') in lambda a, b=1, *c, d, e=2, **kwd:...
    keyword_only = arg_names[pos_count : (pos_count + keyword_only_count)]
    #: A tuple containing default argument values for those arguments that have defaults
    #: etc: (1,) in lambda a, b=1, *c, d, e=2, **kwd:...
    defaults = func.__defaults__ or tuple()
    pos_default_count = len(defaults)
    #: A dict containing defaults for keyword-only parameters.
    #: etc: {'e': 2} in lambda a, b=1, *c, d, e=2, **kwd:...
    kwdefaults = func.__kwdefaults__

    keyword_args = {}
    key = ""

    start = 1 if is_method else 0
    args = args[start:]
    positional = positional[start:]
    # Non-keyword-only parameters w/o defaults.
    non_default_count = pos_count - pos_default_count - start
    while args and non_default_count:
        key += positional[0] + repr(args[0])
        args = args[1:]
        non_default_count -= 1
        positional = positional[1:]

    while args and positional:
        key += positional[0] + repr(args[0])
        args = args[1:]
        defaults = defaults[1:]
        positional = positional[1:]

    while non_default_count:
        value = kwargs.pop(positional[0])
        key += positional[0] + repr(value)
        keyword_args[positional[0]] = value
        positional = positional[1:]
        non_default_count -= 1

    while defaults:
        value = kwargs.pop(positional[0], defaults[0])
        keyword_args[positional[0]] = value
        key += positional[0] + repr(value)
        defaults = defaults[1:]
        positional = positional[1:]

    # *args
    if func_code.co_flags & 4:
        arg_index = pos_count + keyword_only_count
        name = arg_names[arg_index]
        for sub_index, value in enumerate(args[arg_index:]):
            key += f"{name}{sub_index}" + repr(value)

    # Keyword-only parameters.
    for name in keyword_only:
        value = kwargs.pop(name, kwdefaults.get(name))
        keyword_args[name] = value
        key += name + repr(value)

    # **kwargs
    if func_code.co_flags & 8:
        for name, value in sorted(kwargs.items()):
            key += name + repr(value)
    return keyword_args, kwargs, key


def generate_strict_key_pattern(
    *,
    args: Tuple,
    kwargs: Dict,
    func: FunctionType,
    is_method: bool = False,
) -> str:
    func_code = getattr(func, "__wrapped__", func).__code__
    pos_count = func_code.co_argcount
    arg_names = func_code.co_varnames
    positional = tuple(arg_names[:pos_count])
    keyword_only_count = func_code.co_kwonlyargcount
    keyword_only = arg_names[pos_count : (pos_count + keyword_only_count)]
    fillvalue = r".*?"
    key = ""

    start = 1 if is_method else 0
    args = args[start:]
    positional = positional[start:]

    while positional:
        name = positional[0]
        if args:
            key += name + escape(repr(args[0]))
            args = args[1:]
        elif positional[0] in kwargs:
            key += name + escape(repr(kwargs.pop(name)))
        else:
            key += name + fillvalue
        positional = positional[1:]

    # *args
    if func_code.co_flags & 4:
        arg_index = pos_count + keyword_only_count
        name = arg_names[arg_index]
        for sub_index, value in enumerate(args[arg_index:]):
            key += f"{name}{sub_index}" + escape(repr(value))
        key += fillvalue

    # Keyword-only parameters.
    for name in keyword_only:
        if name in kwargs:
            key += name + escape(repr(kwargs.pop(name)))
        else:
            key += name + fillvalue

    # **kwargs
    if func_code.co_flags & 8:
        for name, value in sorted(kwargs.items()):
            key += name + escape(repr(value))
        key += fillvalue
    return f"{key}$"


def generate_fast_key(
    *, args: Tuple, kwargs: Dict, func: FunctionType, is_method: bool = False
) -> Tuple[dict, dict, str]:
    key = args
    if is_method:
        key = args[1:]
    if kwargs:
        for item in kwargs.items():
            key += item
    return kwargs, {}, repr(key)


def generate_fast_key_pattern(
    *,
    args: Tuple,
    kwargs: Dict,
    func: FunctionType,
    is_method: bool = False,
) -> str:
    raise UnsupportedError("fast hash not support pattern delete")
