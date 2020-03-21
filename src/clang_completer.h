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
#include "file_content.h"
#include "token.h"

class ClangCompleter {
 public:
  typedef std::pair<std::string, std::string> ResultKind;
  typedef std::vector<ResultKind> Result;

  ClangCompleter();
  ~ClangCompleter();

  void Parse(const std::string& file, const std::string& content,
             const ArgumentManager& arg_manager);
  void Update();
  std::vector<Result> ObtainCodeCompleteResult(
      const std::string& file, const std::string& content, int line, int column,
      const ArgumentManager& arg_manager);
  std::vector<Result> CodeComplete(const std::string& file,
                                   const std::string& content, int line,
                                   int column,
                                   const ArgumentManager& arg_manager);

  int file_count() const { return content_.file_count(); }

 private:
  Result GetResult(CXCompletionString cs);

  CXIndex index_;
  int parse_option_;
  int complete_option_;

  std::map<std::string, CXTranslationUnit> trans_units_;
  FileContent content_;

  struct CompletionLocation {
    std::string file;
    std::string snap_shot;
    int line;
    int column;
  };
  typedef std::pair<CompletionLocation, std::vector<Result>> CacheData;
  std::map<std::string, CacheData> cache_;
};
