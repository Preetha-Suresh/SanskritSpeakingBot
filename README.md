# Sanskrit Speaking Bot

## Overview

Sanskrit Speaking Bot is a Python-based desktop application designed to help users learn and practice Sanskrit through voice interaction.

The application uses speech recognition to capture the user's voice and provides Sanskrit-related responses. It is developed as a learning tool for improving basic Sanskrit vocabulary and speaking practice.

## Features

* Voice input using a microphone
* Speech recognition using Faster-Whisper
* Sanskrit vocabulary and phrase support
* Text-to-speech output
* Simple desktop graphical user interface
* Python-based implementation
* Docker support for application packaging
* Jenkins support for Continuous Integration

## Technologies Used

* Python 3.11
* Tkinter
* Faster-Whisper
* SoundDevice
* SciPy
* NumPy
* Pyttsx3
* Docker
* Jenkins
* Git and GitHub

## Project Structure

```text
SanskritSpeakingBot/
│
├── main.py
├── requirements.txt
├── Dockerfile
├── Jenkinsfile
└── data/
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Preetha-Suresh/SanskritSpeakingBot.git
```

Move into the project directory:

```bash
cd SanskritSpeakingBot
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Running the Application

Run the following command:

```bash
python main.py
```

The application will open the desktop graphical interface.

## Docker

The application can be packaged using Docker.

Build the Docker image:

```bash
docker build -t sanskrit-speaking-bot:1.0 .
```

Check the created image:

```bash
docker images
```

## Continuous Integration

Jenkins is used to implement Continuous Integration for the project.

The Jenkins pipeline performs the following stages:

1. Checkout the source code from GitHub
2. Install project dependencies
3. Validate the Python application
4. Build the Docker image
5. Display the build result

The pipeline configuration is stored in the `Jenkinsfile`.

## Git Workflow

The project uses Git and GitHub for source code management.

After making changes:

```bash
git add .
git commit -m "Describe the changes"
git push
```

Jenkins can then retrieve the updated source code and execute the CI pipeline.

## Purpose

The main purpose of this project is to provide a simple platform for Sanskrit speaking and vocabulary practice while demonstrating software development practices such as version control, Docker containerization, and Continuous Integration using Jenkins.
