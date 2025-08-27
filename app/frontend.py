import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.replier import agent

st.title('💬 Assistant')
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

prompt = st.chat_input('Just ask...')
if prompt and len(str(prompt).strip()) != 0:
    st.session_state.chat_history.append({'Role':'User','Message':prompt})
    reply = agent(prompt)
    answer = reply['answer']
    steps = reply['intermediate_steps']
    tools = []
    context = []
    for step in steps:
        action,output = step
        tools.append(action.tool)
        if action.tool == 'context_retriever':
            for doc in output:
                context.append(doc.page_content)
    tools_used = ', '.join(list(set(tools)))
    response = f"**Tools Used** : {tools_used}   \n\n"
    if context:
        context_retrieved = ' '.join(context)
        cleaned_context = context_retrieved.replace("\n", " ")
        response += f"**Context Retrieved** : {cleaned_context}   \n\n"
    answer = answer.replace("\n", " \n")
    response += f"**Answer** : {answer}   \n\n"
    st.session_state.chat_history.append({'Role':'Assistant','Message':response})

for chat in st.session_state.chat_history:
    if chat['Role'] == 'User':
        with st.chat_message(name = 'user',width = 'stretch'):
            st.markdown(chat['Message'], unsafe_allow_html=True)
    else:
        with st.chat_message(name = 'ai',width = 'stretch'):
            st.markdown(chat['Message'], unsafe_allow_html=True)
