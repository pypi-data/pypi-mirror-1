"""This file lets the py_interface files function as a package."""
__version__ = "0.93"
__author__ = "Tomas Abrahamsson"
__license__ = "GNU Library General Public License"
__all__ = [
    "erl_async_conn",
    "erl_common",
    "erl_epmd",
    "erl_eventhandler",
    "erl_node",
    "erl_node_conn",
    "erl_opts",
    "erl_term"
    ]

__import__('py_interface',globals(),locals(),__all__,-1)
