These tests are replacements for the tests from the Archetypes 1.5 branch.
traversal.txt and editing.txt doctests are still broken but this seems
unrelated to archetypes.schematuning.

All changes relate to calling invalidateSchema whenever a schema is
manipulated in a test.
