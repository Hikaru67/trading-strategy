#!/usr/bin/env python3
"""
Fix indicators errors in backtest.py
"""

def fix_indicators_errors():
    """Fix all indicators errors in backtest.py"""
    
    with open('backtest.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all lines with signal['indicators']['signal_reversed'] = True
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if "signal['indicators']['signal_reversed'] = True" in line:
            # Find the line before this one
            if len(fixed_lines) > 0:
                prev_line = fixed_lines[-1]
                if "signal['indicators']" in prev_line and "signal_reversed" not in prev_line:
                    # Already has the fix, just add this line
                    fixed_lines.append(line)
                else:
                    # Need to add the fix
                    fixed_lines.append("                # Update indicators (ensure indicators dict exists)")
                    fixed_lines.append("                if 'indicators' not in signal:")
                    fixed_lines.append("                    signal['indicators'] = {}")
                    fixed_lines.append(line)
            else:
                # First line, add the fix
                fixed_lines.append("                # Update indicators (ensure indicators dict exists)")
                fixed_lines.append("                if 'indicators' not in signal:")
                fixed_lines.append("                    signal['indicators'] = {}")
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write back to file
    with open('backtest.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Fixed indicators errors in backtest.py")

if __name__ == "__main__":
    fix_indicators_errors()
