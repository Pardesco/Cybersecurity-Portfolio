import os
import argparse
import logging

from morpheus.config import Config
from morpheus.config import PipelineModes
from morpheus.pipeline import LinearPipeline
from morpheus.stages.input.file_source_stage import FileSourceStage
from morpheus.stages.preprocess.preprocess_nlp_stage import PreprocessNLPStage
from morpheus.stages.inference.triton_inference_stage import TritonInferenceStage
from morpheus.stages.postprocess.add_classifications_stage import AddClassificationsStage
from morpheus.stages.postprocess.filter_detections_stage import FilterDetectionsStage
from morpheus.stages.output.write_to_file_stage import WriteToFileStage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_pipeline(input_file, output_file, model_name, triton_url, vocab_file):
    # Setup configuration optimized for RTX 5070 Ti (16GB VRAM)
    config = Config()
    config.mode = PipelineModes.NLP
    config.class_labels = ["benign", "malicious_obfuscated"]
    
    # 5070 Ti is fast but 16GB VRAM means we need to manage batch sizes
    config.model_max_batch_size = 32
    config.pipeline_batch_size = 256
    config.feature_length = 256
    config.edge_buffer_size = 128
    
    # Create the linear pipeline
    pipeline = LinearPipeline(config)
    
    # Stage 1: Read JSONL Sysmon Data
    logger.info(f"Adding FileSourceStage for {input_file}")
    pipeline.set_source(FileSourceStage(config, filename=input_file, iterative=False))
    
    # Stage 2: Tokenize the text on the GPU using cuDF
    # We parse the 'command_line' field extracted from EVTX EventID 1 & 4104
    logger.info(f"Adding PreprocessNLPStage")
    pipeline.add_stage(PreprocessNLPStage(config, 
                                          vocab_hash_file=vocab_file,
                                          do_lower_case=True, 
                                          truncation=True,
                                          add_special_tokens=True,
                                          column='command_line'))
    
    # Stage 3: Send to Triton Inference Server for NLP Scoring
    logger.info(f"Adding TritonInferenceStage (Model: {model_name})")
    pipeline.add_stage(TritonInferenceStage(config, 
                                            model_name=model_name, 
                                            server_url=triton_url, 
                                            force_convert_inputs=True))
    
    # Stage 4: Add classification scores to the data frame
    logger.info("Adding AddClassificationsStage")
    pipeline.add_stage(AddClassificationsStage(config, labels=["malicious_obfuscated"], prefix="score_"))
    
    # Stage 5: Filter out benign events. Only keep detections >= 0.70 anomaly score.
    logger.info("Adding FilterDetectionsStage")
    pipeline.add_stage(FilterDetectionsStage(config, threshold=0.7, filter_source=True, field_name='score_malicious_obfuscated'))
    
    # Stage 6: Write alerts to output JSONL
    logger.info(f"Adding WriteToFileStage to {output_file}")
    pipeline.add_stage(WriteToFileStage(config, filename=output_file, overwrite=True))
    
    # Run the pipeline
    logger.info("Executing Pipeline...")
    pipeline.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Morpheus GPU-Accelerated Sysmon Threat Hunter")
    parser.add_argument("--input", default="data/sysmon_logs.jsonlines", help="Input JSONL file from EVTX parser")
    parser.add_argument("--output", default="data/alerts.jsonlines", help="Output JSONL file for malicious alerts")
    parser.add_argument("--model", default="sysmon-nlp-detector", help="Triton Model Name")
    parser.add_argument("--server", default="localhost:8001", help="Triton Server gRPC URL")
    parser.add_argument("--vocab", default="data/vocab.txt", help="Path to model vocabulary hash file")
    
    args = parser.parse_args()
    
    print("[*] Initializing NVIDIA Morpheus Pipeline on RTX 5070 Ti (FP4 Acceleration Supported)")
    build_pipeline(args.input, args.output, args.model, args.server, args.vocab)
    print(f"[+] Pipeline complete. Suspicious logs exported to {args.output}")
