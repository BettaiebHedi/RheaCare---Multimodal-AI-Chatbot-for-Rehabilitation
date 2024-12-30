from django.shortcuts import render
from django.http import JsonResponse
import json
# Create your views here.
from django.shortcuts import render
from . import utils
import json
import os
import faiss
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
import logging
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
from django.templatetags.static import static
logger = logging.getLogger(__name__)

# working with cuda
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# loading sd pipeline 
pipe,num_inference_steps,seed=utils.pipe_numsteps_seed()

# Vue pour starter-page.html
def starter_page(request):
    return render(request, 'starter-page.html')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
@login_required(login_url='/login/')  # Redirige l'utilisateur vers la page /login/ s'il n'est pas connecté
def chatbot(request):
    return render(request, 'index3.html')


def index_page(request):
    return render(request, 'index.html')


from django.shortcuts import redirect
from django.contrib.auth import logout

def user_logout(request):
    logout(request)  # Déconnecte l'utilisateur
    return redirect('login')  # Redirige vers la page de connexion après la déconnexion



def loader(request):
    return render(request, 'loader.html')
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login  # Import login as auth_login
from django.contrib import messages
from django.contrib.auth.models import User

# Renamed the view function to `login_view`
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Récupère le nom d'utilisateur depuis le formulaire
        password = request.POST.get('password')  # Récupère le mot de passe depuis le formulaire

        # Authentification de l'utilisateur
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Connexion de l'utilisateur (using `auth_login` to avoid conflict)
            messages.success(request, 'Connexion réussie !')
            return redirect('index_page')  # Redirige vers la page d'accueil après connexion
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'authentication-login.html')


def register(request):
    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already associated with an account.')
            return redirect('register')  # Redirect back to the registration page

        # Create a new user
        user = User.objects.create_user(username=name, email=email, password=password)
        user.save()

        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')  # Redirect to the login page after successful registration

    return render(request, 'authentication-register.html')


# function to generate list of documents to retrieve infos from it 
def preprocess_document(row):
    return {
        "image_url": row['Image URL'],
        "prompt": row['prompt']
    }


# function to retrieve relevent docs 
@csrf_exempt 
def query_documents(request):
    os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
    if request.method == 'POST':
        data = json.loads(request.body)
        query_text = data.get("prompt", "")
        query_image_url = data.get("image", None)
        csv_file = r"C:\Users\betta\OneDrive\Bureau\chatbot\chatbot\chat\static\exercices_rehab (1).xlsx"  
        data = pd.read_excel(csv_file)
        data['Category'] = data['Category'].str.replace('+', ' ', regex=False)
        data['prompt'] = ('The ' + data['Exercice Title'] + ' is an exercice used in case you have in ' + data['Category'] + ' . ''It targets ' + data['Muscles Involved'] + ' . ')
        # Keep only the necessary columns
        data = data[['Image URL', 'prompt']]

        documents = data.apply(preprocess_document, axis=1).tolist()
        faiss_index_path = r"C:\Users\betta\OneDrive\Bureau\projet_4ia\static\faiss_index.bin"
        if os.path.exists(faiss_index_path):
        # Load existing FAISS index
           index = faiss.read_index(faiss_index_path)
        print("FAISS index loaded from disk.")
        img = r"C:\Users\betta\OneDrive\Bureau\chatbot\chatbot\chat\static\generated_image.png"
        image = Image.open(img)
        
        # Generate query embeddings
        query_doc = {"prompt": query_text, "image_url": image}
        query_embedding = utils.get_embeddings1(query_doc)
        
        # Search FAISS index
        D, I = index.search(query_embedding, k=5)  # Retrieve top 5 documents
        print("Distances (D):", D)
        print("Indices (I):", I)
        retrieved_docs = [documents[i] for i in I[0]]
        
        if retrieved_docs:     
            print(retrieved_docs)
        else:
            print("No document retrieved")
        
        return JsonResponse(retrieved_docs, safe=False)
    


# function to generate response using llama 3.2 and the retrieved docs
@csrf_exempt
def generate_rag_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        query_text = data.get("prompt", "")
        # query_image_url = data.get("image_url", None)
        retrieved_docs = data.get("retrieved_docs", None)
        client = InferenceClient(api_key="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")
        # Combine context for LLaMA generation
        context = " ".join([doc["prompt"] for doc in retrieved_docs])

        # Upload the local image
        im = r"C:\Users\betta\OneDrive\Bureau\chatbot\chatbot\chat\static\generated_image.png"
        with open(im, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        
        image_url = f"data:image/png;base64,{base64_image}"    
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{query_text} while referring to the image and these retrieved documents: {context} give me an exercise that serves the issue with a detailed description and the steps to do it.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        }
                    }
                ]
            }
        ]
        
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct",
            messages=messages,
            max_tokens=500
        )

        response = completion.choices[0].message.content
        return JsonResponse({"response": response})
    

# function to generate image
@csrf_exempt
def generate_image(request):
    logger.info("generate_image view called.")
    if request.method == 'POST':
        data = json.loads(request.body)
        prompt = data.get('prompt')

        if not prompt:
            return JsonResponse({"error": "Prompt is required"}, status=400)

        try:
            # Generate the image
            image = utils.generate(pipe, prompt, seed,num_inference_steps) 
            
            # Save the generated image
            image_path = os.path.join(r"C:\Users\betta\OneDrive\Bureau\chatbot\chatbot\chat\static", "generated_image.png")
            image.save(image_path)

            relative_image_path = "generated_image.png"  
            image_url = static(relative_image_path)  


            print(image_path)
            return JsonResponse({"image_url": image_url })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)