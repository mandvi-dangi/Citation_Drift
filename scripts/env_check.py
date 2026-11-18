#!/usr/bin/env python
"""Environment diagnostics (prompt 08). Paste the full console output into docs/env_log.txt."""
import sys, platform, importlib
print("python", sys.version.split()[0], platform.platform())
for m in ["numpy", "requests", "torch", "transformers"]:
    try:
        mod = importlib.import_module(m); print(m, getattr(mod, "__version__", "?"))
    except Exception as e:
        print(m, "NOT INSTALLED" if m in ("torch", "transformers") else f"MISSING ({e})")
try:
    import torch; print("cuda available:", torch.cuda.is_available(),
                        torch.cuda.get_device_name(0) if torch.cuda.is_available() else "")
except Exception:
    pass
from factsens.scoring import f_score
assert abs(f_score(list("CCCIIN")) - 2*0.6*0.5/1.1) < 1e-12
print("factsens import + metric sanity: OK")
