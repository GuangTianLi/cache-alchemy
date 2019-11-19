from types import FunctionType
from typing import Dict, Tuple


def strict_generate_key(
    args: Tuple, kwargs: Dict, func: FunctionType, is_method: bool = False
) -> Tuple[dict, dict, str]:
    """Generate function's arguments hash key from optionally typed positional and keyword arguments
    """

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

    # Non-keyword-only parameters w/o defaults.
    non_default_count = pos_count - pos_default_count
    for value, name in zip(args[start:], positional[start:non_default_count]):
        key += name + str(value)
    for name in positional[len(args) : non_default_count]:
        value = kwargs.pop(name)
        keyword_args[name] = value
        key += name + str(value)
    # ... w/ defaults.
    for offset, name in enumerate(positional[non_default_count:]):
        value = kwargs.pop(name, defaults[offset])
        keyword_args[name] = value
        key += name + str(value)

    # *args
    if func_code.co_flags & 4:
        arg_index = pos_count + keyword_only_count
        name = arg_names[arg_index]
        for sub_index, value in enumerate(args[arg_index:]):
            key += f"{name}{sub_index}" + str(value)

    # Keyword-only parameters.
    for name in keyword_only:
        value = kwargs.pop(name, kwdefaults.get(name))
        keyword_args[name] = value
        key += name + str(value)

    # **kwargs
    if func_code.co_flags & 8:
        for name, value in sorted(kwargs.items()):
            key += name + str(value)
    return keyword_args, kwargs, key


def fast_generate_key(
    args: Tuple, kwargs: Dict, func: FunctionType, is_method: bool = False
) -> Tuple[dict, dict, str]:
    key = args
    if is_method:
        key = args[1:]
    if kwargs:
        for item in kwargs.items():
            key += item
    return kwargs, {}, str(key)
