#ifndef CPP_ARGUMENT_MANAGER_H
#define CPP_ARGUMENT_MANAGER_H

#include "argument_manager.h"

class CPPArgumentManager : public ArgumentManager {
 public:
  CPPArgumentManager();

  void SetCPPStandard(int standard);
};

#endif /* end of include guard: CPP_ARGUMENT_MANAGER_H */
