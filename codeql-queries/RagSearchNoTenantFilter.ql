/**
 * @name RAG search without tenant filter
 * @description A retrieval call with only a query argument can return
 *              another tenant's documents to the prompt.
 * @kind problem
 * @problem.severity error
 * @id sid/rag-search-no-tenant-filter
 */

import python

from Call call, Attribute func
where
  call.getFunc() = func and
  func.getName() = "search" and
  count(call.getAnArg()) = 1 and
  not exists(call.getAKeyword())
select call, "Retrieval call has no tenant filter."
