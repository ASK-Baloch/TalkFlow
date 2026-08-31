from omegaconf import OmegaConf
import nemo.collections.asr as asr
import torch

model_path = '/app/models/parakeet-unified-en-0.6b/parakeet-unified-en-0.6b.nemo'
model = asr.models.EncDecRNNTBPEModel.restore_from(model_path).cuda()

# Try to setup biasing
from nemo.collections.asr.parts.context_biasing.boosting_graph_batched import BoostingTreeModelConfig

print(model.cfg.decoding.strategy)
if hasattr(model.cfg.decoding, 'beam'):
    print('Has beam config')
    model.cfg.decoding.beam.boosting_tree = BoostingTreeModelConfig()
    model.cfg.decoding.beam.boosting_tree_alpha = 1.0
    
    # How to set the list of words?
    for f in model.cfg.decoding.beam.boosting_tree.keys():
        print(f)
