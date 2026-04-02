import logging
import sys

from morpheus.config import Config
from morpheus.config import PipelineModes
from morpheus.pipeline.linear_pipeline import LinearPipeline
from morpheus.stages.input.file_source_stage import FileSourceStage
from morpheus.stages.preprocess.preprocess_nlp_stage import PreprocessNLPStage
from morpheus.stages.inference.triton_inference_stage import TritonInferenceStage
from morpheus.stages.postprocess.add_classifications_stage import AddClassificationsStage
from morpheus.stages.output.write_to_file_stage import WriteToFileStage
from morpheus.stages.general.monitor_stage import MonitorStage

def run_pipeline():
    """
    Constructs and runs the NVIDIA Morpheus pipeline for LLM Prompt Injection Detection.
    """
    # 1. Configure the pipeline for NLP text classification
    config = Config()
    config.mode = PipelineModes.NLP
    config.class_labels = ["legitimate", "prompt_injection"]
    config.model_max_batch_size = 32
    config.pipeline_batch_size = 256
    config.feature_length = 256  # Sequence length for the transformer model
    config.edge_buffer_size = 128
    
    # Use GPU acceleration for dataframe processing (cuDF)
    config.num_threads = 1 

    # Create a linear pipeline (data flows straight through)
    pipeline = LinearPipeline(config)
    
    # 2. INGESTION STAGE: Read intercepted HTTP traffic containing LLM prompts
    # In a production environment, this would be a KafkaSourceStage reading real-time network taps.
    pipeline.set_source(FileSourceStage(
        config, 
        filename="/workspace/data/sample_traffic.jsonlines", 
        iterative=False
    ))
    
    # 3. PRE-PROCESSING STAGE: Tokenize the text using the model's vocabulary
    # Converts raw strings like "Ignore previous instructions" into token tensors.
    pipeline.add_stage(PreprocessNLPStage(
        config, 
        vocab_hash_file="/workspace/models/vocab.txt",
        truncation=True, 
        do_lower_case=True, 
        add_special_tokens=False, 
        column="prompt"  # The JSON key containing the user's input
    ))
    
    # 4. INFERENCE STAGE: Send tensors to the Triton Inference Server
    # Triton runs the fine-tuned RoBERTa model on the GPU for sub-millisecond classification.
    pipeline.add_stage(TritonInferenceStage(
        config, 
        model_name="prompt-injection-detector", 
        server_url="triton:8001", 
        force_convert_inputs=True
    ))
    
    # 5. POST-PROCESSING STAGE: Convert output probabilities into actual labels
    pipeline.add_stage(AddClassificationsStage(config))
    
    # 6. OUTPUT STAGES: Monitor throughput and write alerts to a file (for Splunk ingestion)
    pipeline.add_stage(MonitorStage(config, description="Inference Rate", smoothing=0.001))
    pipeline.add_stage(WriteToFileStage(
        config, 
        filename="/workspace/data/alerts_output.jsonlines", 
        overwrite=True
    ))
    
    # Execute the GPU-accelerated pipeline
    print("[*] Starting Morpheus Pipeline for Prompt Injection Detection...")
    pipeline.run()
    print("[+] Pipeline complete. Alerts saved to /workspace/data/alerts_output.jsonlines")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()
