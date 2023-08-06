DIA Wrapper
===========

DIA is Microsoft's Debug Interface Acccess API, for inspection
of PDB files. It's exposed as a COM object, with no automation, hence
access through Python COM is not possible.

pydia is a wrapper that exposes much of the DIA API as-is to Python.
For detailed information of the API, see the Microsoft documentation at

http://msdn.microsoft.com/en-us/library/x93ctkx8.aspx

This module assumes the VS 2005 version of the DIA API; some of the
attributes it exposes weren't defined in VS 2003. To use the binary
modules, VS 2005 or newer needs to be installed on the system.

See the included diademo.py for an example.
