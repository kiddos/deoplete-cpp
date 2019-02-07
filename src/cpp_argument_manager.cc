#include "cpp_argument_manager.h"

CPPArgumentManager::CPPArgumentManager() {
  AddArg("-xc++");
}

void CPPArgumentManager::SetCPPStandard(int standard) {
  std::stringstream ss;
  ss << "-std=c++" << standard;
  std::string arg = ss.str();
  AddArg(arg);
}
