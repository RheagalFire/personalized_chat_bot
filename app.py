import streamlit as st
from streamlit_chat import message
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.chains import ConversationChain
import openai
import db
from dotenv import load_dotenv
import os
from datetime import datetime

# Load .env files
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

st.title('Personalized Bot')


# choose the personality
current_person = st.radio(
    "ChatBot Beahave like",
    ('Aarish Alam', 'Prady Yadav'),
    horizontal=True,
    key="personality"
)

#make the context using openAI
embed_model = "text-embedding-ada-002"

#current config settings.
if 'config' not in st.session_state:
    st.session_state['config'] = ""

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []
    
if 'pre_query_context' not in st.session_state:
    st.session_state['pre_query_context'] = ""
    
if 'contexts' not in st.session_state:
    st.session_state['contexts'] = []

if 'actual_input' not in st.session_state:
    st.session_state.actual_input = ""
    
def submit():
    st.session_state.actual_input = st.session_state.clear_input_key
    st.session_state.clear_input_key = ''
    
input_query = st.text_input("Enter your query here 👇", key="clear_input_key", on_change=submit)



query = st.sidebar.radio(
	"Select your preference",
	('Food preferences', 'Game preferences', 'Travel preferences', 'Movie preferences'),
	key="preference"
)

if query:
    st.session_state.pre_query_context = query
    openai.api_key = OPENAI_API_KEY
    res = openai.Embedding.create(
        input=[query],
        engine=embed_model
    )
    xq = res['data'][0]['embedding']

    # get relevant contexts (including the questions)
    result = db.index.query(xq, top_k=10, include_metadata=True,namespace='text_field_9')

    contexts = [item['metadata']['text'] for item in result['matches']]


with open('prompt.txt','r') as file:
    string1 = file.read()

string2 = """.
{chat_history}
human:{human_input}
Chatbot:""
"""

## instructions given to gpt
primer = string1 + current_person + string2


llm = OpenAI(openai_api_key=OPENAI_API_KEY,temperature=0)

prompt = PromptTemplate(
	input_variables=["chat_history", "human_input"],
	template=primer
)

if 'entity_memory' not in st.session_state or st.session_state.config != (current_person+query):
    st.session_state.entity_memory = ConversationBufferMemory(memory_key="chat_history")
    st.session_state.config = current_person + query
    st.session_state['generated'] = []
    st.session_state['past'] = []

memory = st.session_state.entity_memory

llm_chain = LLMChain(
	llm=llm, 
	prompt=prompt, 
	verbose=True, 
	memory=memory,
)


if (st.session_state.actual_input):
	augmented_query = "\n\n---\n\n".join(contexts)+"\n\n-----\n\n"+ st.session_state.actual_input
	response = ""
		
	response = llm_chain.predict(human_input=augmented_query)
	
	## storing session states
	st.session_state.past.append(st.session_state.actual_input)
	st.session_state.generated.append(response)
	st.session_state.entity_memory = memory
	st.session_state.actual_input = ''


## rendering the messages
if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

message("Hello! I am a personalized bot trained to behave like " + current_person + ". Ask me any thing and I will reply in the way he does.") 


