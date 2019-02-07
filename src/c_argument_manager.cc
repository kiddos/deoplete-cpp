#include "c_argument_manager.h"

CArgumentManager::CArgumentManager() {
  AddArg("-xc");
}

void CArgumentManager::SetCStandard(int standard) {
  std::stringstream ss;
  ss << "-std=c" << standard;
  std::string arg = ss.str();
  AddArg(arg);
}
