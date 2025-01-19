.. _ref_schemeeval_guide:

.. vale Google.Spacing = NO

Scheme code evaluation
======================

Each session provides an instance of :obj:`~ansys.fluent.core.services.scheme_eval.SchemeEval` on which Fluent's
scheme code can be executed.

Examples
--------

.. code-block:: python

   >>> from ansys.fluent.core.services.scheme_eval import Symbol as S
   >>> session.scheme_eval.eval([S('+'), 2, 3])
   5
   >>> session.scheme_eval.eval([S('rpgetvar'), [S('string->symbol'), "mom/relax"]])
   0.7
   >>> session.scheme_eval.exec(('(ti-menu-load-string "/report/system/proc-stats")',))
   >>> # Returns TUI output string
   >>> session.scheme_eval.string_eval("(+ 2 3)")
   '5'
   >>> session.scheme_eval.string_eval("(rpgetvar 'mom/relax)")
   '0.7'
   >>> session.scheme_eval.scheme_eval("(+ 2 3)")
   5
   >>> session.scheme_eval.scheme_eval("(rpgetvar 'mom/relax)")
   0.7
