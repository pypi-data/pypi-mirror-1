Overview
--------

Provides tools for guerilla (monkey)-patching.

The package provides two methods, ``patch`` and ``wrap``, that are
used to decorate the patch method.

Patching is only allowed if a signature on the original method is
provided. Multiple signatures can be provided corresponding to various
bona fide versions of the method.

Usage
-----

  >>> from monkey import patch, wrap

A patch completely replaces the original method.
  
  >>> @patch(Module.existing_method, *method_signatures)
  ... def some_patch(*args):
  ...     pass

  >>> Module.existing_method = some_patch

A wrap gets the original method passed as the first argument.

  >>> @wrap(Module.existing_method, *method_signatures)
  ... def some_wrap(func, *args):
  ...     pass

  >>> Module.existing_method = some_wrap

See the inline doctests for more information.
