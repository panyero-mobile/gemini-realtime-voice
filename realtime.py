
from google.genai.types import SpeechConfig, VoiceConfig, PrebuiltVoiceConfig
import pyaudio
import websockets
import asyncio
from google import genai

model_id = "gemini-2.0-flash-exp"
client = genai.Client(
    api_key="AIzaSyAnW8kehIVQyLYiNcPWphVEllOSkPZGfiY",
    http_options={"api_version": "v1alpha"},
)


config = {
    "response_modalities": ["AUDIO"],
    "speechConfig": SpeechConfig(
       voiceConfig=VoiceConfig(
           prebuiltVoiceConfig=PrebuiltVoiceConfig()
       )
    )
}

async def chat_with_gemini():
    while True:
        try:
            async with client.aio.live.connect(model=model_id, config=config) as session:
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=24000,
                                output=True,
                                )
                while True:
                    message = input("You: ")
                    await session.send(message, end_of_turn=True)
                    async for response in session.receive():
                        if response.server_content and response.server_content.model_turn:
                            for part in response.server_content.model_turn.parts:
                                if part.inline_data and part.inline_data.data:
                                    stream.write(part.inline_data.data)
                                if part.text:
                                    print(f"Response: {part.text}")       
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed with error: {e}. Reconnecting...")
            await asyncio.sleep(5)  # Wait before reconnecting

if __name__ == "__main__":
    asyncio.run(chat_with_gemini())
