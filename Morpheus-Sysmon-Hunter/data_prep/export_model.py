import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def download_and_export_model():
    model_name = "microsoft/codebert-base"
    output_dir = "models/sysmon-nlp-detector/1"
    onnx_file = os.path.join(output_dir, "model.onnx")

    print(f"[*] Downloading {model_name} from Hugging Face...")
    
    # Load tokenizer and model
    # We initialize with num_labels=2 for binary classification (Benign vs Malicious)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    
    # Set model to evaluation mode
    model.eval()

    # Create dummy input for tracing the ONNX graph
    # Max sequence length for BERT is typically 512
    dummy_text = "powershell.exe -e JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdAByAGUAYQBt"
    inputs = tokenizer(dummy_text, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
    
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]

    print(f"[*] Exporting model to ONNX format at {onnx_file}...")
    
    # Export to ONNX
    torch.onnx.export(
        model, 
        (input_ids, attention_mask), 
        onnx_file,
        export_params=True,
        opset_version=14,          # Opset 14 is widely supported by Triton
        do_constant_folding=True,
        input_names=["input_ids", "attention_mask"],
        output_names=["output"],
        dynamic_axes={
            "input_ids": {0: "batch_size"},
            "attention_mask": {0: "batch_size"},
            "output": {0: "batch_size"}
        }
    )
    
    print("[+] Successfully exported CodeBERT to ONNX format.")
    
    # Save the vocabulary file required by Morpheus PreprocessNLPStage
    vocab_file = "data/vocab.txt"
    print(f"[*] Saving vocabulary to {vocab_file}...")
    with open(vocab_file, "w", encoding="utf-8") as f:
        for vocab_term in tokenizer.get_vocab().keys():
            f.write(vocab_term + "\n")
            
    print("[+] Vocabulary exported successfully.")

if __name__ == "__main__":
    download_and_export_model()
