#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include <clang-c/Index.h>

#include "argument_manager.h"
#include "completion_cache.h"
#include "completion_result.h"
#include "file_content.h"
#include "token.h"

class ClangCompleter {
 public:
  ClangCompleter();
  ~ClangCompleter();

  void Parse(const std::string& file, const std::string& content,
             const ArgumentManager& arg_manager);
  void Update();
  CompletionResults ObtainCodeCompleteResult(
      const std::string& file, const std::string& content, int line, int column,
      const ArgumentManager& arg_manager);
  CompletionResults CodeComplete(const std::string& file,
                                 const std::string& content, int line,
                                 int column,
                                 const ArgumentManager& arg_manager);

  int file_count() const { return content_.file_count(); }

 private:
  CXIndex index_;
  int parse_option_;
  int complete_option_;

  std::map<std::string, CXTranslationUnit> trans_units_;
  FileContent content_;
  CompletionCache cache_;
};
