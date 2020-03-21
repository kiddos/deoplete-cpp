#ifndef COMPLETION_CACHE_H
#define COMPLETION_CACHE_H

#include <map>
#include <utility>
#include <vector>

#include "completion_result.h"

typedef std::vector<CompletionResult> CompletionResults;

class CompletionCache : public std::map<std::string, CompletionResults> {
 public:
  CompletionCache() = default;

  bool has_cache(const std::string& token) {
    return this->find(token) != this->end();
  }
  void insert(const std::string& token, const CompletionResults& results) {
    (*this)[token] = results;
  }
};

#endif /* end of include guard: COMPLETION_CACHE_H */
