#ifndef C_ARGUMENT_MANAGER_H
#define C_ARGUMENT_MANAGER_H

#include "argument_manager.h"

class CArgumentManager : public ArgumentManager {
 public:
  CArgumentManager();

  void SetCStandard(int standard);
};

#endif /* end of include guard: C_ARGUMENT_MANAGER_H */
