# ruff: noqa
import warnings

import nemo.collections.asr as nemo_asr
import numpy as np

warnings.filterwarnings("ignore")

def main():
    print("Loading Parakeet...")
    model = nemo_asr.models.EncDecRNNTBPEModel.restore_from("/app/models/parakeet-unified-en-0.6b/parakeet-unified-en-0.6b.nemo")
    
    # Enable partial hypotheses by turning on return_hypotheses
    model.change_decoding_strategy(model.cfg.decoding)
    
    # Generate 4 seconds of random audio
    audio = np.random.randn(16000 * 4).astype(np.float32)
    
    print("Testing chunk 1 (0 to 1s)...")
    chunk1 = audio[:16000]
    res1 = model.transcribe(audio=chunk1, return_hypotheses=True)
    print("Chunk 1 type:", type(res1))
    
    hyp = res1[0] if isinstance(res1, tuple) else res1
    print("Chunk 1 hyp:", type(hyp), hyp)
    
    print("Testing chunk 2 (1s to 2s) with partial_hypothesis...")
    chunk2 = audio[16000:32000]
    res2 = model.transcribe(audio=chunk2, return_hypotheses=True, partial_hypothesis=hyp)
    hyp2 = res2[0] if isinstance(res2, tuple) else res2
    print("Chunk 2 text:", hyp2[0].text)

if __name__ == "__main__":
    main()

