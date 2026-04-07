import json
import argparse
import sys
try:
    from evtx import PyEvtxParser
except ImportError:
    PyEvtxParser = None
    print("[-] Warning: python-evtx not installed. Please run 'pip install evtx'")

def convert_evtx_to_jsonl(evtx_path, output_path):
    if not PyEvtxParser:
        sys.exit(1)
        
    print(f"[*] Parsing {evtx_path}...")
    parser = PyEvtxParser(evtx_path)
    
    count = 0
    extracted = 0
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in parser.records():
            count += 1
            try:
                # The python-evtx Rust wrapper provides JSON directly
                record_json = json.loads(record['data'])
                event = record_json.get('Event', {})
                sys_data = event.get('System', {})
                event_id = sys_data.get('EventID')
                
                # We only care about Event ID 1 (Process Create) and 4104 (PS Script Block)
                if event_id not in [1, 4104]:
                    continue
                    
                event_data = event.get('EventData', {})
                
                out_record = {
                    "event_id": event_id,
                    "timestamp": sys_data.get('TimeCreated', {}).get('#attributes', {}).get('SystemTime'),
                    "computer": sys_data.get('Computer')
                }

                if event_id == 1:
                    out_record["command_line"] = event_data.get('CommandLine')
                elif event_id == 4104:
                    out_record["command_line"] = event_data.get('ScriptBlockText')
                
                # Only write if there's actual text to analyze
                if out_record.get("command_line"):
                    f.write(json.dumps(out_record) + "\n")
                    extracted += 1
                    
            except Exception as e:
                # Skip malformed records silently
                continue

    print(f"[+] Complete. Scanned {count} records, extracted {extracted} NLP artifacts to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Sysmon EVTX to Morpheus JSONLines")
    parser.add_argument("evtx_file", help="Path to input .evtx file")
    parser.add_argument("output_file", help="Path to output .jsonlines file")
    args = parser.parse_args()
    
    convert_evtx_to_jsonl(args.evtx_file, args.output_file)
