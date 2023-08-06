Introduction
============

This is a specialized ZCatalog index type which does not actually store False
values in its forward index and thus reduces the persistent footprint of the
index.

Queries for True values are done with a normal intersection against the
forward index.

If experimental.catalogqueryplan is used queries for False values are done via
the difference of the passed in result set and the forward index. If no result
set is passed in, the difference of the forward index and the unindex is used.
