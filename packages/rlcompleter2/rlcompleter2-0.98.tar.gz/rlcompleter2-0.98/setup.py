from distutils.core import setup
import rlcompleter2

long_desc = """\
rlcompleter2 is an interactive readline completion handler, featuring:
 * completion on any python expression/statement
 * interactive introspection into function signatures and docstrings
 * convenient completions on module, instance and function objects
 * ultra simple user interface: <tab> (try hit it multiple times!)
"""

setup(
    name = "rlcompleter2",
    version = rlcompleter2.__version__, 
    author = "holger krekel", 
    author_email = "hpk@trillke.net",
    maintainer = "holger krekel", 
    maintainer_email = "hpk@trillke.net",
    url = rlcompleter2.__url__, 
    license = "MIT License", 
    description = "interactive tab-completion for python commandline", 
    platforms = ["unix", "linux", "cygwin"],
    py_modules = ["rlcompleter2"],
    long_description = long_desc,
    )
