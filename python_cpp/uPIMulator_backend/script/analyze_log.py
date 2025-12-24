import sys
import re
from collections import defaultdict

def parse_log(filepath):
    data = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            
            # Split by the first colon
            parts = line.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip()
            
            # Try to convert value to number if possible
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass # Keep as string
            
            data[key] = value
    return data

def analyze_data(data):
    summary = {
        "Config": {},
        "Performance": {},
        "Instructions": {},
        "Latency": defaultdict(int),
        "Bandwidth": {}
    }

    # Config
    config_keys = ['benchmark', 'num_dpus', 'num_tasklets', 'logic_frequency', 'memory_frequency']
    for k in config_keys:
        if k in data:
            summary["Config"][k] = data[k]

    # Performance
    if '/Rank/rank_cycle' in data:
        summary["Performance"]["Total Cycles"] = data['/Rank/rank_cycle']
    
    # Instructions
    total_instr = 0
    tasklet_count = 0
    for key, value in data.items():
        # Matches ///Logic/{id}_num_instructions
        if 'Logic' in key and 'num_instructions' in key and 'active' not in key:
             # Filter out the total sum key if it exists (///Logic/num_instructions) to avoid double counting
             # The log has ///Logic/num_instructions which seems to be the total.
             # But let's sum individual ones to be safe or just use the total if available.
             if key == '///Logic/num_instructions':
                 continue
             total_instr += value
             tasklet_count += 1
    
    # If explicit total exists, use it for verification or primary value
    if '///Logic/num_instructions' in data:
        summary["Instructions"]["Total Instructions"] = data['///Logic/num_instructions']
    elif tasklet_count > 0:
        summary["Instructions"]["Total Instructions"] = total_instr
        
    if tasklet_count > 0:
        summary["Instructions"]["Avg Instructions per Tasklet"] = total_instr / tasklet_count

    # Latency Breakdown (Summing up for DPU#0 as an example)
    latency_categories = ['ARITHMETIC', 'SPM_ACCESS', 'WAIT_DATA', 'WAIT_SCHEDULE', 'WAIT_SYNC']
    for key, value in data.items():
        for cat in latency_categories:
            if cat in key:
                summary["Latency"][cat] += value

    # Bandwidth
    if '/Rank/read_bytes' in data:
        summary["Bandwidth"]["Read Bytes"] = data['/Rank/read_bytes']
    if '/Rank/write_bytes' in data:
        summary["Bandwidth"]["Write Bytes"] = data['/Rank/write_bytes']

    return summary

def print_summary(summary):
    print("="*50)
    print("uPIMulator Log Analysis Summary")
    print("="*50)
    
    print("\n[Configuration]")
    for k, v in summary["Config"].items():
        print(f"  {k:<25}: {v}")
        
    print("\n[Performance]")
    for k, v in summary["Performance"].items():
        print(f"  {k:<25}: {v}")

    print("\n[Instructions]")
    for k, v in summary["Instructions"].items():
        print(f"  {k:<25}: {v:.2f}" if isinstance(v, float) else f"  {k:<25}: {v}")

    print("\n[Latency Breakdown (Total Cycles across all Tasklets)]")
    total_latency = sum(summary["Latency"].values())
    for k, v in summary["Latency"].items():
        percentage = (v / total_latency * 100) if total_latency > 0 else 0
        print(f"  {k:<25}: {v:<15} ({percentage:.2f}%)")

    print("\n[Memory/Rank Stats]")
    for k, v in summary["Bandwidth"].items():
        print(f"  {k:<25}: {v}")
    print("="*50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_log.py <path_to_log_file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    data = parse_log(filepath)
    summary = analyze_data(data)
    print_summary(summary)
