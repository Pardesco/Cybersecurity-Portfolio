import sys
import argparse
from phish_analyzer import analyze_email, print_report

def main():
    parser = argparse.ArgumentParser(description="Phishing Email Analysis Toolkit")
    parser.add_argument("eml_file", help="Path to the raw .eml file to analyze")
    args = parser.parse_args()

    try:
        report = analyze_email(args.eml_file)
        print_report(report)
    except FileNotFoundError:
        print(f"[-] Error: Could not find file {args.eml_file}")
    except Exception as e:
        print(f"[-] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
