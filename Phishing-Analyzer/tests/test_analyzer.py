import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer import analyze_email, print_report

def run_test():
    """Runs the analyzer against the sample .eml file."""
    sample_path = os.path.join(os.path.dirname(__file__), "sample.eml")
    
    print(f"--- Running Test Simulation on {sample_path} ---")
    report = analyze_email(sample_path)
    print_report(report)

if __name__ == "__main__":
    run_test()
