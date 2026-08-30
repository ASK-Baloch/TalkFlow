import torch
import numpy as np
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import get_settings
import nemo.collections.asr as asr

def run():
    print("Loading model...")
    model = asr.models.EncDecRNNTBPEModel.restore_from(get_settings().asr_model)
    model.eval()
    if torch.cuda.is_available():
        model = model.cuda()
        
    # Generate some fake audio (1 second of silence/noise)
    sample_rate = 16000
    audio1 = np.random.randn(sample_rate).astype(np.float32) * 0.01
    audio2 = np.random.randn(sample_rate).astype(np.float32) * 0.01
    
    device = model.device
    print(f"Device: {device}")
    
    cache_last_channel = None
    cache_last_time = None
    cache_last_channel_len = None
    previous_hypotheses = None
    previous_pred_out = None
    
    for audio in [audio1, audio2]:
        audio_tensor = torch.from_numpy(audio).float().unsqueeze(0).to(device)
        audio_len = torch.tensor([audio_tensor.shape[1]], dtype=torch.long, device=device)
        
        with torch.no_grad():
            feat_signal, feat_signal_len = model.preprocessor(
                input_signal=audio_tensor,
                length=audio_len
            )
            
            print(f"Calling conformer_stream_step on feat {feat_signal.shape}...")
            out = model.conformer_stream_step(
                processed_signal=feat_signal,
                processed_signal_length=feat_signal_len,
                cache_last_channel=cache_last_channel,
                cache_last_time=cache_last_time,
                cache_last_channel_len=cache_last_channel_len,
                previous_hypotheses=previous_hypotheses,
                previous_pred_out=previous_pred_out,
                return_transcription=True
            )
            
            print(f"Output tuple length: {len(out)}")
            preds, text_list, cache_last_channel, cache_last_time, cache_last_channel_len, previous_hypotheses = out[:6]
            
            print(f"Text list: {text_list}")

if __name__ == "__main__":
    run()
