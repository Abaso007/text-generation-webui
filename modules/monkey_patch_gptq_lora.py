# Copied from https://github.com/johnsmith0031/alpaca_lora_4bit

import sys
from pathlib import Path

sys.path.insert(0, str(Path("repositories/alpaca_lora_4bit")))

import autograd_4bit
from autograd_4bit import (Autograd4bitQuantLinear,
                           load_llama_model_4bit_low_ram)
from monkeypatch.peft_tuners_lora_monkey_patch import (
    Linear4bitLt, replace_peft_model_with_gptq_lora_model)

from modules import shared
from modules.GPTQ_loader import find_quantized_model_file

replace_peft_model_with_gptq_lora_model()

def load_model_llama(model_name):

    config_path = str(Path(f'{shared.args.model_dir}/{model_name}'))
    model_path = str(find_quantized_model_file(model_name))
    model, tokenizer = load_llama_model_4bit_low_ram(config_path, model_path, groupsize=shared.args.groupsize, is_v1_model=False)

    for n, m in model.named_modules():
        if isinstance(m, (Autograd4bitQuantLinear, Linear4bitLt)):
            if m.is_v1_model:
                m.zeros = m.zeros.half()
            m.scales = m.scales.half()
            m.bias = m.bias.half()
    autograd_4bit.use_new = True
    autograd_4bit.auto_switch = True

    try:
        tokenizer.eos_token_id = 2
        tokenizer.bos_token_id = 1
        tokenizer.pad_token_id = 0
    except:
        pass

    return model, tokenizer