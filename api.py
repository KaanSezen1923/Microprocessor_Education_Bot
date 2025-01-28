from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deep_translator import GoogleTranslator
import chromadb
import google.generativeai as genai



app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    api_key:str


@app.post("/ask")
def generate_response(request: QuestionRequest):
    try:
        gemini_api_key=request.api_key
        user_query=request.question
        user_query_en=GoogleTranslator(source="auto",target="en").translate(user_query)
        CHROMA_PATH = "Microprocessor_ChromaDB_Database"
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = chroma_client.get_or_create_collection(name="microprocessor_data")
        results = collection.query(query_texts=[user_query_en], n_results=3)
        if results["documents"]:
            context = results['documents'][0] if results["documents"] else ""
        else:
            context= {"question": user_query, "chroma":""}
            
        genai.configure(api_key=gemini_api_key)
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }


        system_prompt = """
        Siz, mikroişlemciler konusunda uzmanlaşmış bir yapay zeka destekli eğitim asistanısınız. 

        Temel Rol ve Amaçlarınız:
        1. Mikroişlemci kavramları, mimarileri, talimatları ve uygulamaları hakkında net, doğru ve özlü açıklamalar sağlamak.
        2. Öğrenme seviyesine bağlı olarak içeriği uyarlayarak başlangıç seviyesinden ileri seviyeye kadar her düzeydeki öğreniciye hizmet etmek.

        Yanıtlama Stratejiniz:
        - Verilen bağlamı ve sağlanan dokuman bilgilerini mutlaka dikkate alın.
        - Her teknik terimi açık ve anlaşılır bir şekilde açıklayın.
        - Karmaşık konuları somut örneklerle destekleyin.
        - Kullanılan dokuman ve bağlam çerçevesinde en alakalı ve doğru bilgiyi sağlayın.

        Yanıt Verme İlkeleri:
        - Dostane ve profesyonel bir iletişim tarzı benimseyin.
        - Bilimsel doğruluğu her zaman ön planda tutun.
        - Öğrenicinin anlama seviyesine uygun bir dil kullanın.

        Önemli Not: 
        Eğer sağlanan dokuman veya bağlamda belirli bir bilgi yoksa, bu durumu açıkça belirtin ve genel bilgilerinize başvurun.
        """


        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=system_prompt
        ) 
        
        contextual_prompt = f"{system_prompt}\n--------------------\n Soru: {user_query} \n--------------------\n The Context:\n{context}"

       
        chat_session = model.start_chat(history=[])
        chat_session.system_instruction = contextual_prompt
        response = chat_session.send_message(user_query)
        return {"question": user_query,"context":context, "response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bir hata oluştu: {str(e)}")



