from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import whisper
import torch
import io
import base64
from pydub import AudioSegment
import tempfile
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Select device automatically (GPU if available, otherwise CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
#['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large']
#https://github.com/openai/whisper/discussions/63
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
print(torch.cuda.memory_allocated(0) / 1e9, "GB allocated")
print(torch.cuda.memory_reserved(0) / 1e9, "GB reserved")


# Load the best Whisper model (large) on the selected device
model = whisper.load_model("medium", device=device)
model.to(device)  # Move model to the correct device
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
print(torch.cuda.memory_allocated(0) / 1e9, "GB allocated")
print(torch.cuda.memory_reserved(0) / 1e9, "GB reserved")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


async def process_audio(audio_data: str) -> Optional[str]:
    """
    Process audio data and return transcription.
    Returns None if processing fails.
    """
    try:
        # Remove the data URL prefix if present
        if "," in audio_data:
            audio_data = audio_data.split(",")[1]
        
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data)
        
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            try:
                # Convert audio bytes to WAV using pydub
                audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
                
                # Ensure audio is in the correct format for Whisper
                audio = audio.set_frame_rate(16000)  # Whisper expects 16kHz
                audio = audio.set_channels(1)        # Convert to mono
                audio = audio.set_sample_width(2)    # 16-bit depth
                
                # Export to WAV
                audio.export(temp_wav.name, format='wav')
                
                # Transcribe using Whisper
                with torch.no_grad():
                    result = model.transcribe(temp_wav.name)
                
                return result["text"].strip()
                
            except Exception as e:
                logger.error(f"Error processing audio file: {e}")
                raise
            
    except Exception as e:
        logger.error(f"Error in process_audio: {e}")
        raise

@app.get("/")
async def get():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())




@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio transcription.
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            try:
                # Receive audio data
                audio_data = await websocket.receive_text()
                logger.debug("Received audio data")
                
                # Process the audio
                transcription = await process_audio(audio_data)
                
                if transcription:
                    await websocket.send_text(transcription)
                    logger.debug(f"Sent transcription: {transcription}")
                else:
                    await websocket.send_text("No speech detected")
                    
            except Exception as e:
                error_message = f"Error processing audio: {str(e)}"
                logger.error(error_message)
                await websocket.send_text(error_message)
                continue
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()
        logger.info("WebSocket connection closed")

