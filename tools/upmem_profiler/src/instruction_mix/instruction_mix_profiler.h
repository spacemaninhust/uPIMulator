#ifndef UPMEM_PROFILER_INSTRUCTION_MIX_INSTRUCTION_MIX_PROFILER_H_
#define UPMEM_PROFILER_INSTRUCTION_MIX_INSTRUCTION_MIX_PROFILER_H_

#include <map>
#include <set>
#include <string>
#include <tuple>
#include <vector>

#include "abi/instruction/op_code.h"
#include "abi/instruction/suffix.h"
#include "main.h"
#include "util/argument_parser.h"

namespace upmem_profiler::instruciton_mix {

class InstructionMixProfiler {
public:
  explicit InstructionMixProfiler(util::ArgumentParser *argument_parser);
  ~InstructionMixProfiler() = default;

  void register_mix(std::string mix, abi::instruction::OpCode op_code, abi::instruction::Suffix suffix);

  void profile();

private:
  std::map<std::string, std::set<std::tuple<abi::instruction::OpCode, abi::instruction::Suffix>>> mixes_;
  std::vector<std::vector<std::tuple<abi::instruction::OpCode, abi::instruction::Suffix>>> instructions_;
  std::vector<std::string> inst_type_{"arithmetic", "arithmetic_and_cond_branch", "heavy_arithmetic", "heavy_arithmetic_and_cond_branch",
    "system", "system_and_cond_branch", "call", "reg_move_and_cond_branch", "scratchpad_access", "mainmemory_access", "synchronization"};
  
  uint64_t total_inst_cnt_;
  double logic_frequency_ = 350.0;
  uint64_t total_cycles_ = 0;
  uint64_t io_cycles_ = 0;
  uint64_t read_bytes_ = 0;
  uint64_t write_bytes_ = 0;
  double read_bw_ = 0.063;
  double write_bw_ = 0.296;
  int ndpu_ = 1;
};

} // namespace upmem_profiler::instruciton_mix

#endif
