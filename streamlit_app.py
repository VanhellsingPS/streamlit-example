from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Research Bot")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "NoOfFollowups" not in st.session_state:
    st.session_state["NoOfFollowups"] = 2

system_prompt = """
You are a market researcher [indicated as Research Bot] and the respondent is a Health Care Professional. Ask a single follow-up question based on the prior question and answer flow provided below until there is sufficient clarity, detail, and correlation to the first question.

Please generate the questions using the following guidelines:
1. Your question should be an open-ended question to understand greater detail for the response to the original question.
2. Do not ask questions that could throw potential Adverse Events.
3. If HCP has mentioned that they couldn't recall anything in the original response, ask a follow-up question that will make them think harder and respond.
4. The question is about understanding what was discussed during an interaction between the HCP and a sales rep.
5. If the answer is already in detail, thank the HCP and do not generate the next question.
"""

initial_question = "What are the primary messages you recall hearing during your discussion about Kyprolis for Multiple Myeloma?"
Thankyou_message = "Thank you for answering the follow-up Questions"


if "concatenated_prompt" not in st.session_state:
    st.session_state["concatenated_prompt"] = f"Research Bot: {initial_question}"


if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": initial_question})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.NoOfFollowups > -1:
    if prompt := st.chat_input("Enter Response"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.concatenated_prompt += f"User: {prompt}"

        if st.session_state.NoOfFollowups == 0:
            with st.chat_message("assistant"):
                st.markdown(Thankyou_message)
                st.session_state.messages.append({"role": "assistant", "content": Thankyou_message})
                st.session_state.NoOfFollowups -= 1
                   
        if st.session_state.NoOfFollowups > 0:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for response in client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": st.session_state.concatenated_prompt}
                    ],
                    stream=True,
                ):
                    full_response += (response.choices[0].delta.content or "")
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)
                st.session_state.concatenated_prompt += f"Research Bot: {full_response}"
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.NoOfFollowups -= 1  