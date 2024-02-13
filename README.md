# Real-Time Transcription App using LinSTT TN

This Streamlit app utilizes the LINAGORA Tunisian ASR system to perform real-time transcription.

## Overview

The Real-Time Transcription App enables users to transcribe audio in real time using the LinTO-STT-Kaldi API. It offers a user-friendly interface for initiating and stopping transcription, as well as selecting the desired language.

## Features

- Real-time transcription of audio input.
- Support for multiple languages (Arabic, English, French).
- Start and stop buttons to control transcription.
- Downloadable transcription output.

## Prerequisites

- Python 3.x
- Streamlit
- PyAudio
- Websockets

## Setup

1. Clone this repository:

    ```bash
    git clone https://github.com/your_username/real-time-transcription.git
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Download and set up the [LinTO-STT-Kaldi](https://github.com/linto-ai/linto-stt/tree/master/kaldi).

4. Run the Streamlit app:

    ```bash
    streamlit run app.py
    ```

## Usage

1. Open the Streamlit app in your web browser.
2. Select the desired language from the sidebar.
3. Click the "Start Streaming" button to begin transcription.
4. Click the "Stop Streaming" button to end transcription.
5. Download the transcription output using the provided link.

## Credits

This project was developed by [Your Name](https://github.com/hedhoud).

