# DIY Doctor: A GenAI-Powered Personal Health Assistant

DIY Doctor is a GenAI-powered personal health assistant that enables users to securely query their own medical records and receive personalised, context-aware responses.  
The system uses a Retrieval-Augmented Generation (RAG) pipeline combined with dual-Large Language Models (LLMS) to generate and verify medical advice grounded in individual patient data.
  
## Getting Started
1. Clone the repository:
   ```bash
   git clone git@github.com:gohilriddhi21/diy-doctor.git
   ```

2. Go inside the src/ui directory. 
   ```
   cd src/ui/
   ```

3. Export the below variable in your system environment, or add it in .env file inside the `src/ui/` directory. 
   ```bash
      OPENROUTER_API_KEY=<YOUR_KEY_HERE>
   ```
   This requires setting up an OpenRouter key, which costs a small amount of money to use.
   If you want to use only free models, these GGUF models are free (steps to use listed below):
   - **aaditya/Llama3-OpenBioLLM-8B** (medically-focused model)
   - **Henrychur/MMed-Llama-3-8B** (medically-focused model)
   - **bigcode/starcoder2-7b** (programming-focused model)
   
   These other three models require OpenRouter, and are therefore not free:
   - **meta-llama/llama-3.2-3b-instruct** (generalist model)
   - **mistralai/mistral-7b-instruct** (generalist model)
   - **qwen/qwen-turbo** (generalist model)


3. Add GGUF (<file_name>.gguf) quantized versions of models to the diy-doctor/gguf_models directory. Paths below:
   - **aaditya/Llama3-OpenBioLLM-8B:** https://huggingface.co/aaditya/OpenBioLLM-Llama3-8B-GGUF?show_file_info=openbiollm-llama3-8b.Q8_0.gguf
   - **Henrychur/MMed-Llama-3-8B:** https://huggingface.co/wencan-lab/MMed-Llama-3-8B-Q4_K_M-GGUF?show_file_info=mmed-llama-3-8b-q4_k_m.gguf
   - **bigcode/starcoder2-7b:** https://huggingface.co/DevQuasar/bigcode.starcoder2-7b-GGUF?show_file_info=bigcode.starcoder2-7b.Q8_0.gguf


4. To run the program locally
   ```
   streamlit run DIYDoctorUI.py
   ```

5. **Quick Tip**:

   Testing credentials:

      `username`: bobby
      `password`: password


## ✨ Key Features
- **Secure User Authentication**: Private login using username/password and OCR-based ID verification.
- **Retrieval-Augmented Generation (RAG)**: Semantic search over patient-specific medical records.
- **Dual LLM Architecture**: 
  - **Query LLM** generates health advice.
  - **Judge LLM** independently verifies response faithfulness and relevance.
- **Veracity Scoring System**: Categorises responses as `GOOD`, `VERIFY`, or `BAD` for user guidance.
- **Interactive Streamlit Dashboard**: User-friendly web interface for querying and viewing judged responses.

## Technologies Used
- Python
- Streamlit
- OpenAI API
- Hugging Face
- LLama Index

## 🏗️ System Architecture

- **Backend Database**: MongoDB Atlas (stores patient records and user authentication)
- **Semantic Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Query Engine Models**: 
  - Domain-specific: OpenBioLLM-8B, MMed-Llama-3-8B
  - Generalist: Meta Llama-3.2-3B, Mistral-7B, Qwen-Turbo
  - Out-of-domain: StarCoder2-7B
- **Verification Models (Judge LLMs)**: Same model set used independently for evaluation
- **Frontend**: Built with Streamlit

## Important Links
- MongoDB: https://cloud.mongodb.com/v2/67d8b43aed149a23f0a54c5c#/metrics/replicaSet/67d8b569b6a2d65fd34b1ce6/explorer/sample_mflix/comments/find

## Notes
- If you want to run the model evaluation script "../src/model_evaluation/query_and_judge_evaluation.py", make sure your working directory is the "../diy-doctor" folder, or you may run into file path issues.
