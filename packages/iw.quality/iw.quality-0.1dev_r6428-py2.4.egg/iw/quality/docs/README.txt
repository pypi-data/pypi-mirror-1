==========
iw.quality
==========

Helpers for QA tests.

Levenshtein
===========

Calculates the Levenshtein distance in a base code.

    >>> from iw.quality import similarities
    >>> sim = similarities(data_dir, node_treshold=1)
    >>> sim.next()
    (0.88..., '/...source2.py logger:5', '/.../source1.py enable_log:17')


