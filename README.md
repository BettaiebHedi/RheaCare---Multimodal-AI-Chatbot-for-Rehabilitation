# RhéaCare — Multimodal AI Chatbot for Rehabilitation  

**RhéaCare** is an AI-powered assistant designed for physiotherapists and rehabilitation patients. It provides personalized exercise recommendations and real-time corrective feedback using multimodal AI techniques.  

This project leverages **text, image, and video inputs** to deliver adaptive guidance for patients’ rehabilitation exercises, integrating advanced AI models and real-time posture analysis.  

---  

## 🚀 Features  

### 🧑‍⚕️ Personalized Exercise Recommendations  
- Suggests exercises based on patient condition, movement anomalies, and recovery stage.  
- Provides step-by-step instructions and visual demonstration.  

### 🏃 Real-Time Movement Correction  
- Integrates **OpenPose** and **MediaPipe** to track patient posture and movement.  
- Detects errors and provides instant corrective feedback.  

### 🧠 Multimodal RAG System  
- Built using **LLaVA 3.2 11B Vision-Instruct**.  
- Processes text, image, and video data.  
- Trained on **5,000+ rehabilitation exercises** including images, videos, and descriptions.  

### 🎨 Fine-Tuned Image Generation  
- Fine-tuned **Stable Diffusion** models for custom exercise illustrations.  
- Uses **PEFT techniques**: **LoRA** and **QLoRA** for efficient fine-tuning.  

---

## 🛠 Tech Stack  

| Category | Tools |
|----------|-------|
| Language | Python |
| Models | LLaVA 3.2 11B Vision, Stable Diffusion |
| AI Techniques | RAG, Multimodal AI, PEFT (LoRA, QLoRA) |
| Movement Analysis | OpenPose, MediaPipe |
| Data | CSV datasets, Exercise Images & Videos |

---

## 🛠 Installation  

### 1. Clone the repository  
git clone https://github.com/YOUR_USERNAME/rheacare.git  
cd rheacare  
### 2. Create a virtual environment  
python3 -m venv venv  
source venv/bin/activate  # Linux/macOS  
venv\Scripts\activate     # Windows  
### 3. Install dependencies  
pip install -r requirements.txt  

### ▶️ Running the Project  
Note: You need GPU access for LLaVA and Stable Diffusion inference/fine-tuning.  
For integration with GUI or web interface, you can extend this with Streamlit / Gradio.  

---

# 📜 License  
This project is licensed under the MIT License — see LICENSE file for details.  

# 👤 Authors
Mohamed el hedi Bettaieb - AI Engineer • Multimodal & Agentic AI • RAG Systems  
Siwar Jlassi - AI Engineer • Multimodal & Agentic AI • RAG Systems  
Sirine Nmiri - AI Engineer • Multimodal & Agentic AI • RAG Systems  
Sarra ben Ouihiba - AI Engineer • Multimodal & Agentic AI • RAG Systems  
Latifa Zouaoui - AI Engineer • Multimodal & Agentic AI • RAG Systems  
Mehdi Fgaier - AI Engineer • Multimodal & Agentic AI • RAG Systems  
