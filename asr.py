import torch
import asyncio
import torchaudio
import torchaudio.functional as AF
from transformers import Wav2Vec2ForCTC, AutoProcessor

import numpy as np


class Transcribe:
    def __init__(
        self, sfreq: float = 16_000.0, lang: str = "en", device="cuda"
    ) -> None:
        model_id = "facebook/mms-1b-fl102"

        self.sfreq = sfreq  # sampling frequency
        self.device = device
        self.processor = AutoProcessor.from_pretrained(model_id)

        print(f"Initializing model for `{lang}` ... ")
        print(f"Loading Tokenizer ... ")

        self.processor.tokenizer.set_target_lang(lang)
        print(f"Loading Model ... ")
        self.model = Wav2Vec2ForCTC.from_pretrained(model_id).to(device)
        self.model.load_adapter(lang)

    @torch.inference_mode()
    def __call__(self, audio_array: np.array, src_sfreq):

        audio_tensor = torch.tensor(audio_array).to(self.device)
        audio_tensor = audio_tensor / audio_tensor.max()

        # resample audio to 16khz
        audio_tensor = AF.resample(audio_tensor, src_sfreq, self.sfreq)
        audio_tensor = audio_tensor.view(1, -1)

        outputs = self.model(audio_tensor)
        logits = outputs.logits

        tokens = torch.argmax(logits, dim=-1)[0]

        return self.processor.decode(tokens)
