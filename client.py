import streamlit as st
import os
import asyncio 
import websockets
import json
import pyaudio
import base64
from pathlib import Path
import html
import uuid

from streamlit_tailwind import st_tw

def javascript(source: str) -> None:
    div_id = uuid.uuid4()

    st.markdown(f"""
    <div style="display:none" id="{div_id}">
        <iframe src="javascript: \
            var script = document.createElement('script'); \
            script.type = 'text/javascript'; \
            script.text = {html.escape(repr(source))}; \
            var div = window.parent.document.getElementById('{div_id}'); \
            div.appendChild(script); \
            div.parentElement.parentElement.parentElement.style.display = 'none'; \
        "/>
    </div>
    """, unsafe_allow_html=True)

# session state:
if 'text' not in st.session_state:
    st.session_state["text"] = "Listening..."
    st.session_state['run'] = False


st.sidebar.header('Websocket API')
ws_api=st.sidebar.text_input("Enter your API URL 👇", "ws://localhost:8980/streaming")
# ws_api="ws://localhost:8980/streaming"
# Audio params:

st.sidebar.header('Audio Params')

FRAMES_PER_BUFFER = int(st.sidebar.text_input('Frames per buffer', 512))
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = int(st.sidebar.text_input('Rate', 16000))

p = pyaudio.PyAudio()

# Audio streaming with above params
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER
)


def download_transcription():
	read_txt = open('transcription.txt', 'r')
	st.download_button(
		label="Download transcription",
		data=read_txt,
		file_name='transcription_output.txt',
		mime='text/plain')

# start & stop audio transcriptions
def start_listening():
    st.session_state['run'] = True

def stop_listening():
    st.session_state['run'] = False

# Web user interface
st.title('🎙️ Real-Time Transcription App Using LinSTT TN')

with st.expander('About this App'):
    st.markdown("""
        This Streamlit app uses LINAGORA Tunisian ASR system to performe real-time transcription.
        
        Tunisian ASR:      
            Libraries used:
                - `streamlit` - web framework
                - `pyaudio` - a Python library providing bindings to [PortAudio](http://www.portaudio.com/) (cross-platform audio processing library)
                - `websockets` - allows interaction with the API
                - `asyncio` - allows concurrent input/output processing

""")
Language = {
        "Arabic": "ar",
        "English": "en",
        "French": "fr",
    }

language = st.sidebar.selectbox("Select a language", list(Language.keys()), index=0)
language = Language[language]


col1, col2 = st.sidebar.columns(2)
col1.button('Start Streaming', on_click=start_listening)
col2.button('Stop Streaming', on_click=stop_listening)



# Send audio (Input) / Receive transcription (Output)
async def send_receive(ws_api):
    text = ""
    direction = 'rtl' if language == 'ar' else 'ltr'
    listening = "نسمع فيك...." if language == "ar" else "Listening...."
    html = f"""
    <style>
    .transcription-list {{
        border: 3px outset hsl(0, 0%, 73%);
        padding: 10px;
        border-radius: 5px;
        direction: {direction};
        text-align: {direction};
    }}
    .transcription-list .font-bold {{
        font-weight: bold;
    }}
    </style>

    <div class="transcription-list">
        <span class="font-bold" id="text-holder">
            {listening}
        </span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    try:   
        async with websockets.connect(ws_api) as websocket:
            await websocket.send(json.dumps({"config": {"sample_rate":16000}}))
            while st.session_state['run']:
                try:
                    data=stream.read(FRAMES_PER_BUFFER)
                    await websocket.send(data)
                    res = await websocket.recv()
                    message = json.loads(res)
                    if message is None:
                        continue
                    elif "text" in message.keys():
                        line = message['text']
                        if line or line != None:
                            if text:
                                text += "\n"
                            text += line
                            
                            js=f"""
                                window.parent.document.getElementById("text-holder").innerHTML = ` { text }`;
                            """
                            javascript(js)
                except KeyboardInterrupt:
                    stop_listening()    
                        
            await websocket.send(json.dumps({"eof" : 1}))
            res = await websocket.recv()
            message = json.loads(res)
            if isinstance(message, str):
                message = json.loads(message)
            if text:
                text += " "
            text += message["text"]
            try:
                res = await websocket.recv()
            except websockets.ConnectionClosedOK:
                print("Websocket Closed")
        
    except KeyboardInterrupt:
        print("\nKeyboard interrupt")     

    if st.session_state['run'] == False:
        st.session_state["text"] = text
        transcription_txt = open('transcription.txt', 'a')
        transcription_txt.write(st.session_state['text'])
        transcription_txt.write(' ')
        transcription_txt.close()
    

asyncio.run(send_receive(ws_api))

if Path('transcription.txt').is_file():
	st.markdown('### Download')
	download_transcription()
	os.remove('transcription.txt')
