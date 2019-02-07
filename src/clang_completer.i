%module clang_completer

%include "std_string.i"
%include "std_vector.i"
%include "std_pair.i"

%{
#include "clang_completer.h"
#include "argument_manager.h"
#include "c_argument_manager.h"
#include "cpp_argument_manager.h"
#include "objc_argument_manager.h"
#include "objcpp_argument_manager.h"
%}

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
                                   int column, const ArgumentManager& arg_manager);

  int file_count() const;
};

%template(ResultKind) std::pair<std::string, std::string>;
%template(Result) std::vector<std::pair<std::string, std::string>>;
%template(Results) std::vector<std::vector<std::pair<std::string, std::string>>>;

class ArgumentManager {
 public:
  ArgumentManager();

  bool AddArg(const std::string& arg);
  void AddArgs(const std::vector<std::string>& args);
  bool AddIncludePath(const std::string& include_path);
  void AddIncludePaths(const std::vector<std::string>& include_paths);
  bool AddDefinition(const std::string& def);
  void AddDefinitions(const std::vector<std::string>& defs);
  void PrepareArgs(std::vector<char*>& args) const;

  std::vector<std::string> args() const { return args_; }
};

class CArgumentManager : public ArgumentManager {
 public:
  CArgumentManager();

  void SetCStandard(int standard);
};

class CPPArgumentManager : public ArgumentManager {
 public:
  CPPArgumentManager();

  void SetCPPStandard(int standard);
};

class OBJCArgumentManager : public ArgumentManager {
 public:
  OBJCArgumentManager();
};

class OBJCPPArgumentManager : public ArgumentManager {
 public:
  OBJCPPArgumentManager();
};
