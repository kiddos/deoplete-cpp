#include "argument_manager.h"
#include <iostream>

#ifndef CLANG_INCLUDE_DIR
#define CLANG_INCLUDE_DIR "."
#endif

ArgumentManager::ArgumentManager() {
  AddArg("-fsyntax-only");
  AddIncludePath(CLANG_INCLUDE_DIR);
}

bool ArgumentManager::AddArg(const std::string& arg) {
  if (std::find(args_.begin(), args_.end(), arg) == args_.end()) {
    args_.push_back(arg);
    return true;
  }
  return false;
}

void ArgumentManager::AddArgs(const std::vector<std::string>& args) {
  for (int i = 0; i < args.size(); ++i) {
    AddArg(args[i]);
  }
}

bool ArgumentManager::AddIncludePath(const std::string& include_path) {
  std::string arg = "-I" + include_path;
  return AddArg(arg);
}

void ArgumentManager::AddIncludePaths(
    const std::vector<std::string>& include_paths) {
  for (int i = 0; i < include_paths.size(); ++i) {
    AddIncludePath(include_paths[i]);
  }
}

bool ArgumentManager::AddDefinition(const std::string& def) {
  std::string arg = "-D" + def;
  return AddArg(arg);
}

void ArgumentManager::AddDefinitions(const std::vector<std::string>& defs) {
  for (int i = 0; i < defs.size(); ++i) {
    AddDefinition(defs[i]);
  }
}

void ArgumentManager::PrepareArgs(std::vector<char*>& args) const {
  for (int i = 0; i < args_.size(); ++i) {
    args.push_back(const_cast<char*>(args_[i].c_str()));
  }
}
