"""Model backends. Real backends never receive the gold answer."""
import hashlib, os, time

class Backend:
    needs_item = False
    def generate(self, prompt, item=None):
        raise NotImplementedError

class OpenAICompatBackend(Backend):
    """Any OpenAI-compatible /chat/completions server (OpenAI, vLLM, Ollama at http://localhost:11434/v1)."""
    def __init__(self, model, base_url, api_key_env=None, max_tokens=32, temperature=0.0, retries=3):
        self.model, self.base_url = model, base_url.rstrip("/")
        self.key = os.environ.get(api_key_env, "") if api_key_env else ""
        self.max_tokens, self.temperature, self.retries = max_tokens, temperature, retries
    def generate(self, prompt, item=None):
        import requests
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        body = {"model": self.model, "temperature": self.temperature, "max_tokens": self.max_tokens,
                "messages": [{"role": "user", "content": prompt}]}
        for k in range(self.retries):
            try:
                r = requests.post(f"{self.base_url}/chat/completions", json=body, headers=headers, timeout=120)
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"]
            except Exception:
                if k == self.retries - 1:
                    raise
                time.sleep(2 ** k)

class HFBackend(Backend):
    """Local Hugging Face model (greedy decoding). Requires torch + transformers."""
    def __init__(self, model, max_tokens=32):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        self.tok = AutoTokenizer.from_pretrained(model)
        self.lm = AutoModelForCausalLM.from_pretrained(model, torch_dtype="auto", device_map="auto")
        self.max_tokens, self.torch = max_tokens, torch
    def generate(self, prompt, item=None):
        msgs = [{"role": "user", "content": prompt}]
        ids = self.tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt").to(self.lm.device)
        with self.torch.no_grad():
            out = self.lm.generate(ids, max_new_tokens=self.max_tokens, do_sample=False)
        return self.tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)

class DummyBackend(Backend):
    """PLUMBING TESTS ONLY. Deterministic fake model that sees the gold answer; never use for results."""
    needs_item = True
    def __init__(self, name, skill=0.7, abstain=0.0):
        self.name, self.skill, self.abstain = name, skill, abstain
    def _u(self, item, salt):
        h = hashlib.sha256(f"{self.name}|{item['id']}|{salt}".encode()).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF
    def generate(self, prompt, item=None):
        from .data import LETTERS
        n = len(item["options"])
        if self._u(item, "a") < self.abstain:
            return "ANSWER: NS\nCONFIDENCE: 0"
        if self._u(item, "c") < self.skill:
            ans = item["answer"]
        else:
            wrong = [L for L in LETTERS[:n] if L != item["answer"]]
            ans = wrong[int(self._u(item, "w") * len(wrong)) % len(wrong)]
        return f"ANSWER: {ans}\nCONFIDENCE: {int(self.skill*100)}"

def make_backend(spec):
    t = spec["type"]
    if t == "openai_compat":
        return OpenAICompatBackend(spec["model"], spec["base_url"], spec.get("api_key_env"),
                                   spec.get("max_tokens", 32))
    if t == "hf":
        return HFBackend(spec["model"], spec.get("max_tokens", 32))
    if t == "dummy":
        return DummyBackend(spec["name"], spec.get("skill", 0.7), spec.get("abstain", 0.0))
    raise ValueError(f"unknown backend type {t}")
