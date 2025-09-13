"""
   _____ _______ ____  _   _ _  __ _____ 
  / ____|__   __/ __ \| \ | | |/ // ____|
 | (___    | | | |  | |  \| | ' /| (___  
  \___ \   | | | |  | | . ` |  <  \___ \ 
  ____) |  | | | |__| | |\  | . \ ____) |
 |_____/   |_|  \____/|_| \_|_|\_\_____/ 

Test Runner - Make sure everything works! 🧪

Simple test runner to validate all components before deploying so you don't embarass yourself at this step.. there's time for that later.
"""

import sys
import importlib
from pathlib import Path

# Add project root to path so imports work
sys.path.insert(0, str(Path(__file__).parent))

def run_all_tests():
    """Run all test modules."""
    print("🧪 STONKS Test Suite 🚀\n")
    
    test_modules = [
        "test.test_data_fetcher",
        # Add more test modules here as we create them
        # "test.test_strategies",
        # "test.test_dashboard",
    ]
    
    total_passed = 0
    total_tests = 0
    
    for module_name in test_modules:
        print(f"📋 Running {module_name}...")
        try:
            module = importlib.import_module(module_name)
            # Assume each test module has a main function that returns (passed, total)
            if hasattr(module, 'main'):
                passed, total = module.main()
            else:
                print(f"⚠️  Module {module_name} has no main() function")
                continue
                
            total_passed += passed
            total_tests += total
            
        except Exception as e:
            print(f"❌ Failed to run {module_name}: {e}")
        
        print()  # Empty line between modules
    
    # Summary
    print("=" * 50)
    print(f"📊 Final Results: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Good boy! 🚀")
        return True
    else:
        print("🔧 Some tests failed. Fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)