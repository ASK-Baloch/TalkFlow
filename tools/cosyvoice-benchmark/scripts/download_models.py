import os

from modelscope import snapshot_download


def download_models():
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
    os.makedirs(models_dir, exist_ok=True)
    
    print("Downloading Fun-CosyVoice3-0.5B-2512 from ModelScope...")
    snapshot_download(
        'FunAudioLLM/Fun-CosyVoice3-0.5B-2512',
        local_dir=os.path.join(models_dir, 'Fun-CosyVoice3-0.5B-2512')
    )
    print("Successfully downloaded Fun-CosyVoice3-0.5B-2512.")
    
    print("Downloading CosyVoice2-0.5B from ModelScope...")
    snapshot_download(
        'iic/CosyVoice2-0.5B',
        local_dir=os.path.join(models_dir, 'CosyVoice2-0.5B')
    )
    print("Successfully downloaded CosyVoice2-0.5B.")

if __name__ == '__main__':
    download_models()
