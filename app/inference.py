"""Inference engine using llama.cpp CLI via subprocess."""

import os, subprocess, time, logging

logger = logging.getLogger(__name__)


class HistoricalInference:
    def __init__(self, model_path: str, n_threads: int = 4):
        self.model_path = model_path
        self.n_threads = n_threads
        self.llama_cli = self._find_llama_cli()

    def _find_llama_cli(self) -> str:
        candidates = [
            "/usr/local/bin/llama-cli",
            os.path.expanduser("~/llama.cpp/build/bin/llama-cli"),
            "llama-cli",
        ]
        for c in candidates:
            try:
                result = subprocess.run([c, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    logger.info(f"Using llama-cli: {c}")
                    return c
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        logger.warning("llama-cli not found. Inference will fail.")
        return "llama-cli"

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 300) -> str:
        cmd = [
            self.llama_cli, "-m", self.model_path, "-n", str(max_tokens),
            "-ngl", "0", "--no-conversation", "--temp", str(temperature), "-p", prompt,
        ]
        env = os.environ.copy()
        env["LLAMA_ARG_THREADS"] = str(self.n_threads)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
            output = result.stdout
            lines = output.split("\n")
            response_lines = []
            capture = False
            for line in lines:
                if line.startswith("> ") and not capture:
                    capture = True
                    continue
                if capture:
                    if line.startswith("> ") or line.startswith("[") or line.strip() == "":
                        continue
                    if "Prompt:" in line or "Generation:" in line or "Exiting" in line:
                        continue
                    response_lines.append(line)
            response = "\n".join(response_lines).strip()
            if not response:
                last_prompt = output.rfind("> ")
                if last_prompt >= 0:
                    after = output[last_prompt + 2:]
                    for suffix in ["[Prompt:", "[Generation:", "Exiting..."]:
                        pos = after.find(suffix)
                        if pos >= 0:
                            after = after[:pos]
                    response = after.strip()
            return response or "(empty response)"
        except subprocess.TimeoutExpired:
            logger.error("Inference timed out")
            return "(inference timed out)"
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return f"(inference error: {e})"

    def benchmark(self) -> dict:
        test_prompts = [
            "Explain what electricity is.",
            "Describe the properties of steam engines.",
            "What is the capital of France?",
        ]
        results = {}
        for prompt in test_prompts:
            t0 = time.time()
            response = self.generate(prompt, temperature=0, max_tokens=50)
            elapsed = time.time() - t0
            word_count = len(response.split())
            results[prompt[:30]] = {
                "response_preview": response[:100],
                "time_s": round(elapsed, 2),
                "words": word_count,
                "tok_s": round(word_count / elapsed, 2) if elapsed > 0 else 0,
            }
        return results
