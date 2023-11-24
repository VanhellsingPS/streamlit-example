from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Research Bot")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

initial_question = "What are the primary messages you recall hearing during your discussion about Kyprolis for Multiple Myeloma?"

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": initial_question})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

concatenated_prompt = f"Research Bot: {initial_question}"

if prompt := st.chat_input("Enter Response"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    concatenated_prompt += f"User: {prompt}"
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": "system", "content": "You are a market researcher [indicated as Research Bot] and the respondent is a Health Care Professional. Generate a followup question to the conversation provided.Provide only the question text and not Researcher : Question text"},
                {"role": "user", "content": concatenated_prompt}
            ],
            stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        concatenated_prompt += f"Research Bot: {full_response}"

    st.session_state.messages.append({"role": "assistant", "content": full_response})
   
