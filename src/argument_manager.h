#ifndef ARGUMENT_MANAGER_H
#define ARGUMENT_MANAGER_H

#include <string>
#include <vector>
#include <algorithm>
#include <sstream>

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

 protected:
  std::vector<std::string> args_;
};

#endif /* end of include guard: ARGUMENT_MANAGER_H */
