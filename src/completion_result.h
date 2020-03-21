#ifndef COMPLETION_RESULTS_H
#define COMPLETION_RESULTS_H

#include <string>
#include <utility>
#include <vector>

#include <clang-c/Index.h>

typedef std::pair<std::string, std::string> CompletionResultData;
typedef std::vector<CompletionResultData> CompletionResult;

CompletionResult ParseResult(CXCompletionString cs);

#endif /* end of include guard: COMPLETION_RESULTS_H */
