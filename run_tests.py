#!/usr/bin/env python3
"""
Test Runner Script
Run various tests for the BTC trading strategy system
"""

import sys
import os
import subprocess

def run_test(test_file):
    """Run a specific test file"""
    test_path = os.path.join('tests', test_file)
    if os.path.exists(test_path):
        print(f"🚀 Running {test_file}...")
        print("=" * 60)
        result = subprocess.run([sys.executable, test_path], capture_output=False)
        return result.returncode == 0
    else:
        print(f"❌ Test file {test_file} not found!")
        return False

def main():
    """Main function"""
    print("🎯 BTC TRADING STRATEGY TEST RUNNER")
    print("=" * 60)
    
    print("Available tests:")
    print("1. test_all_strategies.py - Test all strategies")
    print("2. test_new_requirements.py - Test against new requirements")
    print("3. test_wyckoff_vsa.py - Test Wyckoff VSA strategy")
    print("4. test_practical_wyckoff.py - Test Practical Wyckoff VSA")
    print("5. test_divergence_strategy.py - Test Divergence strategy")
    print("6. profile_divergence.py - Profile divergence performance")
    print("7. plot_wyckoff_chart.py - Plot Wyckoff charts with signals")
    print("8. Run all tests")
    print("9. Exit")
    
    while True:
        choice = input("\nChọn test (1-8): ").strip()
        
        if choice == '1':
            run_test('test_all_strategies.py')
        elif choice == '2':
            run_test('test_new_requirements.py')
        elif choice == '3':
            run_test('test_wyckoff_vsa.py')
        elif choice == '4':
            run_test('test_practical_wyckoff.py')
        elif choice == '5':
            run_test('test_divergence_strategy.py')
        elif choice == '6':
            run_test('profile_divergence.py')
        elif choice == '7':
            run_test('plot_wyckoff_chart.py')
        elif choice == '8':
            print("🚀 Running all tests...")
            tests = [
                'test_all_strategies.py',
                'test_new_requirements.py',
                'test_wyckoff_vsa.py',
                'test_practical_wyckoff.py',
                'test_divergence_strategy.py'
            ]
            for test in tests:
                print(f"\n{'='*60}")
                run_test(test)
        elif choice == '9':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice! Please select 1-9.")

if __name__ == "__main__":
    main()
