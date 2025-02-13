# Whisper-fastapi
Whisper+fastapi testing website

## Overview
This project is a real-time, multi-language speech transcription web application using FastAPI, WebSockets, and OpenAI's Whisper model. It allows users to record speech from their browser and receive transcribed text.

## Features
- **Real-time transcription** via WebSockets
- **Multi-language support** with selectable options
- **GPU acceleration** (if available) for faster processing
- **Automatic audio processing** to match Whisper's requirements

## Installation
### Prerequisites
- Python 3.8+
- pip
- ffmpeg (required by pydub for audio processing)

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/jero98772/Whisper-fastapi
   cd Whisper-fastapi
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8002 --reload
   ```

## Usage
1. Open a web browser and navigate to:
   ```
   http://localhost:8002/
   ```
2. Select a language from the dropdown.
3. Click "Start Recording" and speak into your microphone.
4. The transcription will appear in real-time.

## WebSocket API
- **Endpoint:** `/ws`
- **Request:** Sends base64-encoded audio data.
- **Response:** Returns transcribed text.

## Screenshots
![](https://github.com/jero98772/Whisper-fastapi/blob/main/docs/1.jpeg)

## License
This project is free to use without restrictions.

## Notes
- This application automatically selects GPU if available.
- The Whisper model used is "**medium**"(with base is more faster and it need time for download); modify `whisper.load_model("medium")` to change the model.

- Audio input must be in 16kHz, mono, 16-bit format (handled automatically by the backend).

## Contributing
Feel free to fork and modify as needed.

