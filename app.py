import streamlit as st
import chromadb
import os
import google.generativeai as genai
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

st.set_page_config(page_title="Microprocessor AI")
with st.sidebar:
    gemini_api_key=st.text_input("Enter Gemini Api Key",type="password")
    
CHROMA_PATH = "Microprocessor_ChromaDB_Database"

def retrieval(user_query,CHROMA_PATH):
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = chroma_client.get_or_create_collection(name="microprocessor_data")
        user_query_en=GoogleTranslator(source="auto",target="en").translate(user_query)
        results = collection.query(query_texts=[user_query_en], n_results=3)
        if results["documents"]:
            context = results['documents'][0] if results["documents"] else ""
        else:
            context=""
        return context
    
def augumented_generation(api_key,user_query,context):
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
        if response:
            return response.text
        else:
            return ""
        
st.title("Microprocessor AI")
st.write("Bu asistan, mikroişlemcilerle ilgili sorularınıza yanıt vermek için tasarlanmıştır. Sorularınızı aşağıdaki kutuya yazabilirsiniz.")


if "messages" not in st.session_state:
    st.session_state["messages"] = []


for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_query := st.chat_input("Soru yazın ve Enter'a basın..."):
    
    with st.chat_message("user"):
        st.write(user_query)

    
    st.session_state["messages"].append({"role": "user", "content": user_query})

    try:
        context=retrieval(user_query,CHROMA_PATH)
        response=augumented_generation(gemini_api_key,user_query,context)
        with st.chat_message("assistant"):
            st.write("**Yanıt:**")
            st.write(response)

        
        st.session_state["messages"].append({"role": "assistant", "content": response})
    except Exception as e:
        st.write(f"Error found {e}")
