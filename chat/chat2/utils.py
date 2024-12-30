from diffusers import DiffusionPipeline,DDPMScheduler
import torch
import faiss
import base64
import pandas as pd
from transformers import AutoProcessor, AutoModelForVision2Seq, CLIPProcessor, CLIPModel
from functools import partial
from torchmetrics.functional.multimodal import clip_score
from PIL import Image
import os
from huggingface_hub import login
import io
import requests
import numpy as np
from huggingface_hub import InferenceClient


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Initialize the client
client = InferenceClient(api_key="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")
def client():
    return client

# Load Stable Diffusion model with LoRA weights
pipe = DiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float32,
    safety_checker = None,
).to(device)
# Load LoRA weights
lora_weights_path = r"C:\Users\betta\OneDrive\Bureau\projet_4ia\static\pytorch_lora_weights (1).safetensors"
pipe.load_lora_weights(lora_weights_path)
# Define number of inference steps and seed
num_inference_steps = 35
seed = 3

def pipe_numsteps_seed():
    return pipe,num_inference_steps,seed

# Load CSV file
csv_file = r"C:\Users\betta\OneDrive\Bureau\chatbot\chatbot\chat\static\exercices_rehab (1).xlsx"  
data = pd.read_excel(csv_file)
data['Category'] = data['Category'].str.replace('+', ' ', regex=False)
data['prompt'] = (
    'The ' + data['Exercice Title'] + ' is an exercice used in case you have in ' + data['Category'] + ' . '
    'It targets ' + data['Muscles Involved'] + ' . '
)
# Keep only the necessary columns
data = data[['Image URL', 'prompt']]
def preprocess_document(row):
    return {
        "image_url": row['Image URL'],
        "prompt": row['prompt']
    }
documents = data.apply(preprocess_document, axis=1).tolist()

def documents():
    return documents



def generate(pipeline, prompt, seed,num_inference_steps):
    generator = torch.Generator(device=device).manual_seed(seed)
    return pipeline(prompt, num_inference_steps=num_inference_steps, generator=generator).images[0]

def get_embeddings1(doc):
    # Process text and image together
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    if doc['image_url']:
        image=doc['image_url']
        # inputs = clip_processor(text=doc['exercise_title'], images=image, return_tensors="pt", padding=True)
        text_inputs = clip_processor(text=doc['prompt'], return_tensors="pt", padding=True)
        image_inputs = clip_processor(images=image, return_tensors="pt", padding=True)
    else:
        text_inputs = clip_processor(text=doc['prompt'], return_tensors="pt", padding=True)


    text_embeddings = clip_model.get_text_features(**text_inputs).detach().numpy()

    if image:
        image_embeddings = clip_model.get_image_features(**image_inputs).detach().numpy()
        embeddings = np.concatenate([text_embeddings, image_embeddings], axis=1)
        print(embeddings)
    else:
        embeddings = text_embeddings  # Only use text embeddings if there's no image
        print("text only embeddings")
        print(embeddings)

    return embeddings


faiss_index_path = r"C:\Users\betta\OneDrive\Bureau\chatbot\chatbot\chat\static\faiss_index.bin"
def faiss_index():
    if os.path.exists(faiss_index_path):
        # Load existing FAISS index
        index = faiss.read_index(faiss_index_path)
        print("FAISS index loaded from disk.")
        return index
    else: 
        return None
