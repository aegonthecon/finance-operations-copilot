#!/usr/bin/env python3
"""Standalone script that directly tries three known multimodal models.
It prints the repr() of every model name, then attempts OCR with the models
in this exact order:
    1. models/gemini-2.5-flash
    2. models/gemini-2.5-pro
    3. models/gemini-pro-latest
For each model it:
  - uploads the test invoice image
  - calls generate_content (high‑level API if available)
  - logs any exception and moves to the next model
The first successful response is printed with:
  * selected model name
  * uploaded file identifier
  * raw Gemini response object
  * extracted text / JSON
"""
import os, sys, json
from pathlib import Path

def header(title: str):
    print(f"\n{'=' * 10} {title} {'=' * 10}\n")

# ----------------------------------------------------------------------
# Load environment variables (requires python-dotenv).
# ----------------------------------------------------------------------
try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError("python-dotenv is required to load .env")

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

# ----------------------------------------------------------------------
# Import SDK and instantiate client.
# ----------------------------------------------------------------------
import importlib
genai = importlib.import_module("google.genai")
print("google.genai version:", getattr(genai, "__version__", "unknown"))

ClientCls = getattr(genai, "Client", None)
if not ClientCls:
    raise RuntimeError("google.genai does not expose a Client class")
client = ClientCls(api_key=api_key)
header("Client instantiated")
print(client)

# ----------------------------------------------------------------------
# List all models and print their repr() values.
# ----------------------------------------------------------------------
models_mod = getattr(client, "models", None)
if not models_mod:
    raise RuntimeError("client has no 'models' attribute")
list_fn = getattr(models_mod, "list", None)
if not callable(list_fn):
    raise RuntimeError("models module does not have a callable 'list' method")
all_models = list_fn()
header("All model names (repr)")
for m in all_models:
    print(repr(getattr(m, "name", None)))

# ----------------------------------------------------------------------
# Prepare upload function.
# ----------------------------------------------------------------------
files_mod = getattr(client, "files", None)
if not files_mod:
    raise RuntimeError("client has no 'files' attribute")
upload_fn = getattr(files_mod, "upload", None)
if not callable(upload_fn):
    raise RuntimeError("files module does not have a callable 'upload' method")

image_path = Path(__file__).parent / "uploads" / "sample_invoice_a.png"
if not image_path.is_file():
    raise FileNotFoundError(f"Test image not found at {image_path}")

prompt = (
    "Read the attached invoice image. Do not generate example values. Extract only values visible in the image and return valid JSON with the following fields: invoice_number, vendor_name, invoice_date, due_date, amount, currency."
)
# Debug: show the exact prompt being sent
print("--- Prompt sent to Gemini ---")
print(prompt)

# ----------------------------------------------------------------------
# Ordered list of known multimodal models.
# ----------------------------------------------------------------------
ordered_models = [
    "models/gemini-2.5-flash",
    "models/gemini-2.5-pro",
    "models/gemini-pro-latest",
    "models/gemini-3.5-flash",
    "models/gemini-3-pro-image",
]

# Use the high‑level generate_content if present.
generate_top = getattr(models_mod, "generate_content", None)
if not callable(generate_top):
    print("models.generate_content not available – will fall back to per‑model method.")

for img_path in [
    Path(__file__).parent / "uploads" / "sample_invoice_a.png",
    Path(__file__).parent / "uploads" / "invoice_template_1_w450px.jpg",
]:
    if not img_path.is_file():
        raise FileNotFoundError(f"Test image not found at {img_path}")
    print(f"\n========== Processing image: {img_path.name} ==========")
    success = False
    for model_name in ordered_models:
        print(f"\n--- Trying model: {model_name} ---")
        try:
            # Upload fresh for each attempt (as required by the request).
            uploaded_file = upload_fn(file=str(img_path))
            # Debug: show the uploaded file object
            print("--- Uploaded file object ---")
            print(repr(uploaded_file))
            # Prepare contents list and debug (prompt first)
            contents = [prompt, uploaded_file]
            print("--- Contents list to be sent (prompt first) ---")
            print(contents)
            if callable(generate_top):
                print("--- Calling generate_top ---")
                response = generate_top(model=model_name, contents=contents)
            else:
                # Per‑model path: get the model object then call generate_content.
                get_fn = getattr(models_mod, "get", None)
                if not callable(get_fn):
                    raise RuntimeError("models module lacks 'get' method for per‑model access")
                model_obj = get_fn(model_name)
                gen_fn = getattr(model_obj, "generate_content", None)
                if not callable(gen_fn):
                    raise RuntimeError(f"Model object for {model_name} lacks 'generate_content'")
                print("--- Calling per‑model generate_content ---")
                response = gen_fn(contents=contents)
            # If we reach here the request succeeded.
            success = True
            header("Selected model")
            print(model_name)
            header("Raw Gemini response")
            print(response)
            # Extract raw response text
            resp_text = getattr(response, "text", None)
            if resp_text is None:
                parts = getattr(response, "parts", [])
                if parts:
                    resp_text = getattr(parts[0], "text", str(response))
                else:
                    resp_text = str(response)
            # Validate that response contains non-empty text
            if not resp_text or not resp_text.strip():
                raise ValueError("Empty model output")
            header("Extracted text / JSON (raw response)")
            print(resp_text)
            break
        except Exception as exc:
            print(f"Error with model {model_name}: {exc.__class__.__name__}: {exc}")
            continue
    if not success:
        raise RuntimeError(f"All candidate models failed for image {img_path.name}")

header("Done")
