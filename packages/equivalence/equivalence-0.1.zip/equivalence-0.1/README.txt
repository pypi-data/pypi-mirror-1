The ``Equivalence`` class can be used to maintain a partition of objects
into equivalence sets, making sure that the equivalence properties (reflexivity,
symmetry, transitivity) are maintained. Two objects ``x`` and ``y`` are
considered equivalent either implicitly (through a key function) or explicitly by
calling ``merge(x,y)``.

To learn how to use this module, read the docs and see the test cases in
test_equivalence.py.
