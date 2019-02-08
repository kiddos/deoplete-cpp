#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include <clang-c/Index.h>

#include "argument_manager.h"
#include "cpp_argument_manager.h"

class ClangCompleter {
 public:
  typedef std::pair<std::string, std::string> ResultKind;
  typedef std::vector<ResultKind> Result;

  ClangCompleter();
  ~ClangCompleter();

  void Reparse(const std::string& file, const std::string& content);
  bool HasFile(const std::string& file);
  void AddFile(const std::string& file, const ArgumentManager& arg_manager);
  void AddFile(const std::string& file, const std::string& content,
               const ArgumentManager& arg_manager);
  std::string GetFileContent(const std::string& file);
  std::vector<Result> CodeComplete(const std::string& file,
                                   const std::string& content, int line,
                                   int column,
                                   const ArgumentManager& arg_manager);
  int GetCodeCompleteColumn(const std::string& content, int line, int column);

  int file_count() const { return files_.size(); }

 private:
  Result GetResult(CXCompletionString cs);

  CXIndex index_;
  int parse_option_;
  int complete_option_;

  struct {
    int line;
    int column;
    std::string file;
    std::vector<Result> result;
  } last_completion_;

  std::vector<std::string> files_;
  std::vector<CXTranslationUnit> tus_;
};
