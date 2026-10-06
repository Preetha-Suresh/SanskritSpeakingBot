import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import re
import threading
import tempfile
import time

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

# Whisper
from faster_whisper import WhisperModel

# Optional Text-to-Speech
import pyttsx3


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_NAME = "संस्कृतवाणी - Sanskrit Speaking Tutor"

DATA_DIR = "data"
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")

SAMPLE_RATE = 16000
RECORD_SECONDS = 7


# ============================================================
# VOCABULARY DATABASE
# ============================================================

VOCABULARY = [

    ("नमस्ते", "Hello / Greetings", "Greeting"),
    ("सुप्रभातम्", "Good morning", "Greeting"),
    ("शुभसन्ध्या", "Good evening", "Greeting"),
    ("शुभरात्रिः", "Good night", "Greeting"),
    ("धन्यवादः", "Thank you", "Greeting"),
    ("स्वागतम्", "Welcome", "Greeting"),

    ("अहम्", "I", "Pronoun"),
    ("अहं", "I", "Pronoun"),
    ("भवान्", "You (male)", "Pronoun"),
    ("भवती", "You (female)", "Pronoun"),
    ("सः", "He", "Pronoun"),
    ("सा", "She", "Pronoun"),
    ("मित्रम्", "Friend", "Noun"),

    ("शिक्षकः", "Teacher", "Noun"),
    ("छात्रः", "Male student", "Noun"),
    ("छात्रा", "Female student", "Noun"),

    ("गृहम्", "House / Home", "Noun"),
    ("विद्यालयः", "School", "Noun"),
    ("महाविद्यालयः", "College", "Noun"),
    ("बाजारः", "Market", "Noun"),

    ("जलम्", "Water", "Noun"),
    ("भोजनम्", "Food", "Noun"),
    ("पुस्तकम्", "Book", "Noun"),
    ("लेखनी", "Pen", "Noun"),
    ("दूरवाणी", "Telephone", "Noun"),

    ("माता", "Mother", "Noun"),
    ("पिता", "Father", "Noun"),
    ("भ्राता", "Brother", "Noun"),
    ("भगिनी", "Sister", "Noun"),

    ("गच्छामि", "I go", "Verb"),
    ("गच्छति", "He/She goes", "Verb"),

    ("पठामि", "I study/read", "Verb"),
    ("पठति", "He/She studies/reads", "Verb"),

    ("पिबामि", "I drink", "Verb"),
    ("पिबति", "He/She drinks", "Verb"),

    ("खादामि", "I eat", "Verb"),
    ("खादति", "He/She eats", "Verb"),

    ("करोमि", "I do", "Verb"),
    ("करोति", "He/She does", "Verb"),

    ("अस्मि", "I am", "Verb"),
    ("अस्ति", "He/She/It is", "Verb"),

    ("कुशली", "Fine / Well", "Adjective"),
    ("सुन्दरम्", "Beautiful", "Adjective"),
    ("उत्तमम्", "Excellent / Good", "Adjective"),

    ("अद्य", "Today", "Adverb"),
    ("श्वः", "Tomorrow", "Adverb"),
    ("अधुना", "Now", "Adverb"),

    ("संस्कृतम्", "Sanskrit", "Noun"),

    ("प्रश्नः", "Question", "Noun"),
    ("उत्तरम्", "Answer", "Noun"),
    ("समयः", "Time", "Noun"),
    ("दिनम्", "Day", "Noun"),
    ("रात्रिः", "Night", "Noun"),
]


# ============================================================
# TRANSLATION DATABASE
# ============================================================

TRANSLATIONS = {

    "hello": "नमस्ते।",
    "hi": "नमस्ते।",
    "good morning": "सुप्रभातम्।",
    "good evening": "शुभसन्ध्या।",
    "good night": "शुभरात्रिः।",

    "thank you": "धन्यवादः।",
    "welcome": "स्वागतम्।",

    "how are you": "भवान् कथम् अस्ति?",
    "i am fine": "अहं कुशली अस्मि।",
    "i am good": "अहं कुशली अस्मि।",

    "i am a student": "अहं छात्रः अस्मि।",
    "i am a female student": "अहं छात्रा अस्मि।",

    "i am learning sanskrit": "अहं संस्कृतं पठामि।",
    "i study sanskrit": "अहं संस्कृतं पठामि।",

    "i drink water": "अहं जलं पिबामि।",
    "i eat food": "अहं भोजनं खादामि।",

    "i go to school": "अहं विद्यालयं गच्छामि।",
    "i go to college": "अहं महाविद्यालयं गच्छामि।",

    "i read a book": "अहं पुस्तकं पठामि।",
    "i do my work": "अहं मम कार्यं करोमि।",

    "what is your name": "भवतः नाम किम्?",
    "my name is": "मम नाम प्रीथा अस्ति।",

    "where are you going": "भवान् कुत्र गच्छति?",
    "what are you doing": "भवान् किं करोति?",

    "i like sanskrit": "मम संस्कृतं रोचते।",
}


# ============================================================
# CONVERSATION SCENARIOS
# ============================================================

SCENARIOS = {

    "Greetings": [

        {
            "bot": "नमस्ते! भवान् कथम् अस्ति?",
            "expected": [
                "अहं कुशली अस्मि",
                "कुशली अस्मि"
            ],
            "hint": "Say: अहं कुशली अस्मि।"
        },

        {
            "bot": "भवतः नाम किम्?",
            "expected": [
                "मम नाम"
            ],
            "hint": "Say: मम नाम ... अस्ति।"
        },

        {
            "bot": "भवान् संस्कृतं पठति वा?",
            "expected": [
                "पठामि",
                "आम्"
            ],
            "hint": "Say: आम्, अहं संस्कृतं पठामि।"
        }
    ],

    "College": [

        {
            "bot": "भवान् कुत्र पठति?",
            "expected": [
                "महाविद्यालय",
                "विद्यालय"
            ],
            "hint": "Say: अहं महाविद्यालये पठामि।"
        },

        {
            "bot": "भवान् किं पठति?",
            "expected": [
                "संस्कृत",
                "पुस्तक"
            ],
            "hint": "Say: अहं संस्कृतं पठामि।"
        }
    ],

    "Daily Life": [

        {
            "bot": "भवान् प्रातः किं करोति?",
            "expected": [
                "गच्छामि",
                "पठामि",
                "करोमि"
            ],
            "hint": "Use a sentence with करोमि / पठामि / गच्छामि."
        },

        {
            "bot": "भवान् जलं पिबति वा?",
            "expected": [
                "पिबामि",
                "आम्"
            ],
            "hint": "Say: आम्, अहं जलं पिबामि।"
        }
    ],

    "Food": [

        {
            "bot": "भवान् किं खादति?",
            "expected": [
                "खादामि"
            ],
            "hint": "Say: अहं भोजनं खादामि।"
        }
    ]
}


# ============================================================
# GRAMMAR RULES
# ============================================================

GRAMMAR_RULES = [

    (
        "अहं विद्यालयं गच्छति",
        "अहं विद्यालयं गच्छामि",
        "With अहं, use the first-person verb गच्छामि."
    ),

    (
        "अहं जलं पिबति",
        "अहं जलं पिबामि",
        "With अहं, use पिबामि instead of पिबति."
    ),

    (
        "अहं भोजनं खादति",
        "अहं भोजनं खादामि",
        "With अहं, use खादामि instead of खादति."
    ),

    (
        "अहं संस्कृतं पठति",
        "अहं संस्कृतं पठामि",
        "With अहं, use पठामि instead of पठति."
    ),

    (
        "अहं पुस्तकं पठति",
        "अहं पुस्तकं पठामि",
        "The first-person verb should be पठामि."
    ),

    (
        "अहं गच्छति",
        "अहं गच्छामि",
        "The first-person form is गच्छामि."
    ),

    (
        "अहं पिबति",
        "अहं पिबामि",
        "The first-person form is पिबामि."
    ),

    (
        "अहं खादति",
        "अहं खादामि",
        "The first-person form is खादामि."
    ),

    (
        "अहं करोति",
        "अहं करोमि",
        "The first-person form is करोमि."
    ),

    (
        "सः गच्छामि",
        "सः गच्छति",
        "सः requires the third-person singular form गच्छति."
    ),

    (
        "सः पिबामि",
        "सः पिबति",
        "सः requires पिबति."
    ),

    (
        "सः पठामि",
        "सः पठति",
        "सः requires पठति."
    ),

    (
        "सः करोमि",
        "सः करोति",
        "सः requires करोति."
    ),
]


# ============================================================
# QUIZ
# ============================================================

QUIZ = [

    {
        "question": "What does नमस्ते mean?",
        "options": [
            "Hello / Greetings",
            "Water",
            "Book",
            "Food"
        ],
        "answer": 0
    },

    {
        "question": "What is the Sanskrit word for water?",
        "options": [
            "भोजनम्",
            "जलम्",
            "पुस्तकम्",
            "गृहम्"
        ],
        "answer": 1
    },

    {
        "question": "Which is the first-person form?",
        "options": [
            "गच्छति",
            "पठति",
            "गच्छामि",
            "करोति"
        ],
        "answer": 2
    },

    {
        "question": "What does अहं mean?",
        "options": [
            "He",
            "She",
            "I",
            "You"
        ],
        "answer": 2
    },

    {
        "question": "Complete: अहं जलं ______।",
        "options": [
            "पिबति",
            "पिबामि",
            "गच्छति",
            "करोति"
        ],
        "answer": 1
    },

    {
        "question": "Complete: अहं संस्कृतं ______।",
        "options": [
            "पठामि",
            "पठति",
            "गच्छति",
            "खादति"
        ],
        "answer": 0
    }
]


# ============================================================
# PROGRESS MANAGEMENT
# ============================================================

def create_default_progress():

    return {
        "messages": 0,
        "voice_messages": 0,
        "grammar_checks": 0,
        "grammar_errors": 0,
        "quiz_attempts": 0,
        "quiz_correct": 0,
        "words_learned": 0,
        "practice_sessions": 0,
        "last_active": ""
    }


def load_progress():

    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(PROGRESS_FILE):

        progress = create_default_progress()

        with open(
            PROGRESS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                progress,
                file,
                ensure_ascii=False,
                indent=4
            )

        return progress

    try:

        with open(
            PROGRESS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return create_default_progress()


def save_progress(progress):

    os.makedirs(DATA_DIR, exist_ok=True)

    with open(
        PROGRESS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            progress,
            file,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# COMPUTATIONAL LINGUISTIC ENGINE
# ============================================================

class SanskritLinguisticEngine:

    def __init__(self):

        self.vocabulary = {
            word.lower(): {
                "meaning": meaning,
                "category": category
            }
            for word, meaning, category in VOCABULARY
        }


    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    def normalize(self, text):

        text = text.strip()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text


    # --------------------------------------------------------
    # TOKENIZATION
    # --------------------------------------------------------

    def tokenize(self, text):

        text = self.normalize(text)

        tokens = re.findall(
            r"[\u0900-\u097F]+|[A-Za-z]+|\d+|[^\w\s]",
            text,
            flags=re.UNICODE
        )

        return tokens


    # --------------------------------------------------------
    # MORPHOLOGICAL ANALYSIS
    # --------------------------------------------------------

    def analyze_morphology(self, text):

        tokens = self.tokenize(text)

        analysis = []

        for token in tokens:

            clean_token = token.strip("।,.!?")

            lower = clean_token.lower()

            if lower in self.vocabulary:

                entry = self.vocabulary[lower]

                analysis.append({
                    "token": clean_token,
                    "meaning": entry["meaning"],
                    "category": entry["category"]
                })

            else:

                analysis.append({
                    "token": clean_token,
                    "meaning": "Unknown",
                    "category": "Unknown"
                })

        return analysis


    # --------------------------------------------------------
    # GRAMMAR CHECK
    # --------------------------------------------------------

    def grammar_check(self, text):

        normalized = self.normalize(text)

        issues = []

        corrected = normalized

        for wrong, right, explanation in GRAMMAR_RULES:

            if wrong in normalized:

                issues.append({
                    "wrong": wrong,
                    "correct": right,
                    "explanation": explanation
                })

                corrected = corrected.replace(
                    wrong,
                    right
                )

        return {
            "correct": len(issues) == 0,
            "issues": issues,
            "corrected": corrected
        }


    # --------------------------------------------------------
    # TRANSLATION
    # --------------------------------------------------------

    def translate(self, text):

        normalized = self.normalize(text)

        key = normalized.lower()

        if key in TRANSLATIONS:

            return TRANSLATIONS[key]

        key_without_punctuation = re.sub(
            r"[.!?]+$",
            "",
            key
        )

        if key_without_punctuation in TRANSLATIONS:

            return TRANSLATIONS[
                key_without_punctuation
            ]

        return (
            "I do not have a predefined translation for this "
            "sentence yet. Try a simpler sentence."
        )


# ============================================================
# WHISPER SPEECH RECOGNITION
# ============================================================

class WhisperSpeechRecognizer:

    def __init__(self):

        self.model = None

        self.model_name = "small"

        self.loading = False


    def load_model(self):

        if self.model is not None:

            return True

        if self.loading:

            return False

        self.loading = True

        try:

            print()
            print("=" * 60)
            print("Loading Whisper model...")
            print("=" * 60)

            self.model = WhisperModel(
                self.model_name,
                device="cpu",
                compute_type="int8"
            )

            print("Whisper model loaded successfully.")

            return True

        except Exception as error:

            print("Whisper loading error:", error)

            return False

        finally:

            self.loading = False


    # --------------------------------------------------------
    # RECORD AUDIO
    # --------------------------------------------------------

    def record_audio(
        self,
        seconds=RECORD_SECONDS
    ):

        print(
            f"Recording for {seconds} seconds..."
        )

        audio = sd.rec(
            int(seconds * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32"
        )

        sd.wait()

        audio = np.squeeze(audio)

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        )

        temp_file.close()

        write(
            temp_file.name,
            SAMPLE_RATE,
            audio
        )

        return temp_file.name


    # --------------------------------------------------------
    # WHISPER TRANSCRIPTION
    # --------------------------------------------------------

    def transcribe(
        self,
        audio_file
    ):

        if not self.load_model():

            return (
                "",
                "Whisper model could not be loaded."
            )

        try:

            segments, info = self.model.transcribe(
                audio_file,
                language="sa",
                beam_size=5,
                vad_filter=True
            )

            text_parts = []

            for segment in segments:

                text_parts.append(
                    segment.text.strip()
                )

            text = " ".join(
                text_parts
            ).strip()

            detected_language = getattr(
                info,
                "language",
                "sa"
            )

            return (
                text,
                detected_language
            )

        except Exception as error:

            return (
                "",
                str(error)
            )


# ============================================================
# TEXT TO SPEECH
# ============================================================

class SanskritSpeaker:

    def __init__(self):

        try:

            self.engine = pyttsx3.init()

            self.available = True

        except Exception:

            self.engine = None

            self.available = False


    def speak(self, text):

        if not self.available:

            return

        try:

            self.engine.say(text)

            self.engine.runAndWait()

        except Exception as error:

            print(
                "TTS error:",
                error
            )


# ============================================================
# MAIN GUI APPLICATION
# ============================================================

class SanskritSpeakingBot:

    def __init__(self, root):

        self.root = root

        self.root.title(
            APP_NAME
        )

        self.root.geometry(
            "1200x800"
        )

        self.root.minsize(
            1000,
            700
        )

        self.engine = SanskritLinguisticEngine()

        self.whisper = WhisperSpeechRecognizer()

        self.speaker = SanskritSpeaker()

        self.progress = load_progress()

        self.current_scenario = "Greetings"

        self.scenario_index = 0

        self.current_quiz = 0

        self.create_style()

        self.create_header()

        self.create_notebook()

        self.create_conversation_tab()

        self.create_speaking_tab()

        self.create_grammar_tab()

        self.create_translation_tab()

        self.create_vocabulary_tab()

        self.create_quiz_tab()

        self.create_progress_tab()

        self.refresh_progress()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )


    # ========================================================
    # STYLE
    # ========================================================

    def create_style(self):

        style = ttk.Style()

        try:

            style.theme_use(
                "clam"
            )

        except Exception:

            pass

        style.configure(
            "Title.TLabel",
            font=(
                "Arial",
                22,
                "bold"
            )
        )

        style.configure(
            "Heading.TLabel",
            font=(
                "Arial",
                15,
                "bold"
            )
        )

        style.configure(
            "Large.TButton",
            font=(
                "Arial",
                12,
                "bold"
            ),
            padding=10
        )


    # ========================================================
    # HEADER
    # ========================================================

    def create_header(self):

        frame = ttk.Frame(
            self.root,
            padding=15
        )

        frame.pack(
            fill="x"
        )

        title = ttk.Label(
            frame,
            text=(
                "संस्कृतवाणी\n"
                "Computational Sanskrit Speaking Tutor"
            ),
            style="Title.TLabel",
            justify="center"
        )

        title.pack()

        subtitle = ttk.Label(
            frame,
            text=(
                "Whisper Speech Recognition + "
                "Sanskrit NLP + Grammar Feedback"
            )
        )

        subtitle.pack(
            pady=(5, 0)
        )


    # ========================================================
    # NOTEBOOK
    # ========================================================

    def create_notebook(self):

        self.notebook = ttk.Notebook(
            self.root
        )

        self.notebook.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )


    # ========================================================
    # CONVERSATION TAB
    # ========================================================

    def create_conversation_tab(self):

        self.conversation_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.conversation_tab,
            text="💬 Conversation"
        )

        top = ttk.Frame(
            self.conversation_tab,
            padding=10
        )

        top.pack(
            fill="x"
        )

        ttk.Label(
            top,
            text="Choose scenario:"
        ).pack(
            side="left"
        )

        self.scenario_var = tk.StringVar(
            value="Greetings"
        )

        scenario_box = ttk.Combobox(
            top,
            textvariable=self.scenario_var,
            values=list(
                SCENARIOS.keys()
            ),
            state="readonly",
            width=20
        )

        scenario_box.pack(
            side="left",
            padx=10
        )

        scenario_box.bind(
            "<<ComboboxSelected>>",
            self.change_scenario
        )

        self.conversation_area = scrolledtext.ScrolledText(
            self.conversation_tab,
            wrap="word",
            font=(
                "Arial",
                14
            )
        )

        self.conversation_area.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        input_frame = ttk.Frame(
            self.conversation_tab,
            padding=10
        )

        input_frame.pack(
            fill="x"
        )

        self.conversation_input = ttk.Entry(
            input_frame,
            font=(
                "Arial",
                14
            )
        )

        self.conversation_input.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.conversation_input.bind(
            "<Return>",
            lambda event: self.send_text_message()
        )

        ttk.Button(
            input_frame,
            text="Send",
            style="Large.TButton",
            command=self.send_text_message
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            input_frame,
            text="🎤 Speak",
            style="Large.TButton",
            command=self.start_voice_conversation
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            input_frame,
            text="🔊 Bot Voice",
            command=self.speak_last_bot_message
        ).pack(
            side="left",
            padx=5
        )

        self.add_bot_message(
            "नमस्ते! संस्कृतवाणी मध्ये स्वागतम्।\n"
            "You can type or speak in Sanskrit."
        )

        self.show_current_scenario()


    def change_scenario(self, event=None):

        self.current_scenario = (
            self.scenario_var.get()
        )

        self.scenario_index = 0

        self.conversation_area.delete(
            "1.0",
            tk.END
        )

        self.show_current_scenario()


    def show_current_scenario(self):

        scenario = SCENARIOS[
            self.current_scenario
        ]

        if self.scenario_index >= len(scenario):

            self.scenario_index = 0

        prompt = scenario[
            self.scenario_index
        ]["bot"]

        self.add_bot_message(
            prompt
        )

        self.last_bot_message = prompt


    def add_bot_message(self, text):

        self.conversation_area.insert(
            tk.END,
            f"\n🤖 Bot: {text}\n"
        )

        self.conversation_area.see(
            tk.END
        )


    def add_user_message(
        self,
        text,
        voice=False
    ):

        icon = "🎤" if voice else "👤"

        self.conversation_area.insert(
            tk.END,
            f"\n{icon} You: {text}\n"
        )

        self.conversation_area.see(
            tk.END
        )


    def send_text_message(self):

        text = self.conversation_input.get().strip()

        if not text:

            return

        self.conversation_input.delete(
            0,
            tk.END
        )

        self.process_conversation_input(
            text,
            voice=False
        )


    def process_conversation_input(
        self,
        text,
        voice=False
    ):

        self.add_user_message(
            text,
            voice=voice
        )

        self.progress["messages"] += 1

        if voice:

            self.progress[
                "voice_messages"
            ] += 1

        self.progress["last_active"] = (
            time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        grammar = self.engine.grammar_check(
            text
        )

        if not grammar["correct"]:

            self.progress[
                "grammar_errors"
            ] += len(
                grammar["issues"]
            )

            self.add_bot_message(
                "व्याकरण सुधार:\n"
                + grammar["corrected"]
            )

        response = self.generate_response(
            text
        )

        self.add_bot_message(
            response
        )

        self.last_bot_message = response

        save_progress(
            self.progress
        )

        self.refresh_progress()


    def generate_response(self, text):

        normalized = text.lower()

        scenario = SCENARIOS[
            self.current_scenario
        ]

        current = scenario[
            self.scenario_index
        ]

        expected = current[
            "expected"
        ]

        matched = False

        for keyword in expected:

            if keyword.lower() in normalized:

                matched = True

                break

        if matched:

            self.scenario_index += 1

            if self.scenario_index >= len(scenario):

                self.scenario_index = 0

                return (
                    "उत्तमम्! 🎉 "
                    "भवान् संवादं सफलतया पूर्णवान्। "
                    "पुनः आरभामः।"
                )

            next_prompt = scenario[
                self.scenario_index
            ]["bot"]

            return (
                "उत्तमम्! ✓\n"
                + next_prompt
            )

        grammar = self.engine.grammar_check(
            text
        )

        if not grammar["correct"]:

            return (
                "प्रयत्नः उत्तमः। "
                "कृपया पुनः वदतु।\n"
                "Correct form: "
                + grammar["corrected"]
            )

        return (
            "अच्छा प्रयत्नः! "
            "कृपया संस्कृतेन अधिकं वदतु।"
        )


    # ========================================================
    # VOICE CONVERSATION
    # ========================================================

    def start_voice_conversation(self):

        self.add_bot_message(
            "🎤 कृपया संस्कृतेन वदतु... "
            "Recording started."
        )

        thread = threading.Thread(
            target=self.voice_worker,
            daemon=True
        )

        thread.start()


    def voice_worker(self):

        try:

            audio_file = self.whisper.record_audio(
                RECORD_SECONDS
            )

            text, info = (
                self.whisper.transcribe(
                    audio_file
                )
            )

            try:

                os.remove(
                    audio_file
                )

            except Exception:

                pass

            self.root.after(
                0,
                lambda: self.handle_voice_result(
                    text,
                    info
                )
            )

        except Exception as error:

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Voice Error",
                    str(error)
                )
            )


    def handle_voice_result(
        self,
        text,
        info
    ):

        if not text:

            self.add_bot_message(
                "मम श्रवणे त्रुटिः अभवत्। "
                "कृपया पुनः स्पष्टं वदतु।"
            )

            return

        self.process_conversation_input(
            text,
            voice=True
        )


    def speak_last_bot_message(self):

        if not hasattr(
            self,
            "last_bot_message"
        ):

            return

        text = self.last_bot_message

        thread = threading.Thread(
            target=self.speaker.speak,
            args=(text,),
            daemon=True
        )

        thread.start()


    # ========================================================
    # SPEAKING PRACTICE TAB
    # ========================================================

    def create_speaking_tab(self):

        self.speaking_tab = ttk.Frame(
            self.notebook,
            padding=20
        )

        self.notebook.add(
            self.speaking_tab,
            text="🎤 Speaking Practice"
        )

        ttk.Label(
            self.speaking_tab,
            text="Sanskrit Speaking Practice",
            style="Heading.TLabel"
        ).pack(
            pady=10
        )

        self.practice_prompt = tk.StringVar(
            value=(
                "Say: अहं संस्कृतं पठामि।"
            )
        )

        ttk.Label(
            self.speaking_tab,
            textvariable=self.practice_prompt,
            font=(
                "Arial",
                18
            ),
            wraplength=800,
            justify="center"
        ).pack(
            pady=30
        )

        ttk.Button(
            self.speaking_tab,
            text="🎤 Record and Check",
            style="Large.TButton",
            command=self.practice_voice
        ).pack(
            pady=10
        )

        self.practice_result = scrolledtext.ScrolledText(
            self.speaking_tab,
            height=15,
            font=(
                "Arial",
                13
            )
        )

        self.practice_result.pack(
            fill="both",
            expand=True,
            pady=20
        )


    def practice_voice(self):

        self.practice_result.delete(
            "1.0",
            tk.END
        )

        self.practice_result.insert(
            tk.END,
            "🎤 Recording...\n"
        )

        thread = threading.Thread(
            target=self.practice_voice_worker,
            daemon=True
        )

        thread.start()


    def practice_voice_worker(self):

        try:

            audio_file = self.whisper.record_audio(
                RECORD_SECONDS
            )

            text, info = (
                self.whisper.transcribe(
                    audio_file
                )
            )

            try:

                os.remove(
                    audio_file
                )

            except Exception:

                pass

            self.root.after(
                0,
                lambda: self.display_practice_result(
                    text
                )
            )

        except Exception as error:

            self.root.after(
                0,
                lambda: self.practice_result.insert(
                    tk.END,
                    f"\nError: {error}"
                )
            )


    def display_practice_result(
        self,
        text
    ):

        self.progress[
            "practice_sessions"
        ] += 1

        self.progress[
            "last_active"
        ] = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.practice_result.insert(
            tk.END,
            "\nRecognized Sanskrit:\n"
        )

        self.practice_result.insert(
            tk.END,
            text + "\n\n"
        )

        grammar = self.engine.grammar_check(
            text
        )

        if grammar["correct"]:

            self.practice_result.insert(
                tk.END,
                "✓ Grammar: Correct\n"
            )

            self.practice_result.insert(
                tk.END,
                "Excellent pronunciation attempt!\n"
            )

        else:

            self.progress[
                "grammar_errors"
            ] += len(
                grammar["issues"]
            )

            self.practice_result.insert(
                tk.END,
                "⚠ Grammar issues found:\n\n"
            )

            for issue in grammar["issues"]:

                self.practice_result.insert(
                    tk.END,
                    f"Incorrect: {issue['wrong']}\n"
                )

                self.practice_result.insert(
                    tk.END,
                    f"Correct: {issue['correct']}\n"
                )

                self.practice_result.insert(
                    tk.END,
                    f"Explanation: "
                    f"{issue['explanation']}\n\n"
                )

        save_progress(
            self.progress
        )

        self.refresh_progress()


    # ========================================================
    # GRAMMAR TAB
    # ========================================================

    def create_grammar_tab(self):

        self.grammar_tab = ttk.Frame(
            self.notebook,
            padding=15
        )

        self.notebook.add(
            self.grammar_tab,
            text="🧠 Grammar"
        )

        ttk.Label(
            self.grammar_tab,
            text="Sanskrit Grammar Analyzer",
            style="Heading.TLabel"
        ).pack(
            pady=10
        )

        self.grammar_input = ttk.Entry(
            self.grammar_tab,
            font=(
                "Arial",
                15
            )
        )

        self.grammar_input.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ttk.Button(
            self.grammar_tab,
            text="Check Grammar",
            command=self.check_grammar
        ).pack(
            pady=10
        )

        self.grammar_output = scrolledtext.ScrolledText(
            self.grammar_tab,
            font=(
                "Arial",
                13
            )
        )

        self.grammar_output.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )


    def check_grammar(self):

        text = self.grammar_input.get().strip()

        if not text:

            return

        result = self.engine.grammar_check(
            text
        )

        morphology = (
            self.engine.analyze_morphology(
                text
            )
        )

        self.grammar_output.delete(
            "1.0",
            tk.END
        )

        self.grammar_output.insert(
            tk.END,
            "INPUT:\n"
        )

        self.grammar_output.insert(
            tk.END,
            text + "\n\n"
        )

        if result["correct"]:

            self.grammar_output.insert(
                tk.END,
                "✓ Grammar appears correct.\n\n"
            )

        else:

            self.grammar_output.insert(
                tk.END,
                "⚠ Grammar Issues:\n\n"
            )

            for issue in result["issues"]:

                self.grammar_output.insert(
                    tk.END,
                    f"Incorrect: "
                    f"{issue['wrong']}\n"
                )

                self.grammar_output.insert(
                    tk.END,
                    f"Correct: "
                    f"{issue['correct']}\n"
                )

                self.grammar_output.insert(
                    tk.END,
                    f"Reason: "
                    f"{issue['explanation']}\n\n"
                )

        self.grammar_output.insert(
            tk.END,
            "\nCORRECTED SENTENCE:\n"
        )

        self.grammar_output.insert(
            tk.END,
            result["corrected"]
            + "\n\n"
        )

        self.grammar_output.insert(
            tk.END,
            "MORPHOLOGICAL ANALYSIS:\n\n"
        )

        for item in morphology:

            self.grammar_output.insert(
                tk.END,
                f"Word: {item['token']}\n"
                f"Meaning: {item['meaning']}\n"
                f"Category: {item['category']}\n\n"
            )

        self.progress[
            "grammar_checks"
        ] += 1

        if not result["correct"]:

            self.progress[
                "grammar_errors"
            ] += len(
                result["issues"]
            )

        save_progress(
            self.progress
        )

        self.refresh_progress()


    # ========================================================
    # TRANSLATION TAB
    # ========================================================

    def create_translation_tab(self):

        self.translation_tab = ttk.Frame(
            self.notebook,
            padding=20
        )

        self.notebook.add(
            self.translation_tab,
            text="🌐 Translation"
        )

        ttk.Label(
            self.translation_tab,
            text="English → Sanskrit",
            style="Heading.TLabel"
        ).pack(
            pady=10
        )

        self.translation_input = ttk.Entry(
            self.translation_tab,
            font=(
                "Arial",
                15
            )
        )

        self.translation_input.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ttk.Button(
            self.translation_tab,
            text="Translate",
            command=self.translate_text
        ).pack(
            pady=10
        )

        self.translation_output = tk.Text(
            self.translation_tab,
            height=10,
            font=(
                "Arial",
                18
            )
        )

        self.translation_output.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )


    def translate_text(self):

        text = self.translation_input.get().strip()

        if not text:

            return

        result = self.engine.translate(
            text
        )

        self.translation_output.delete(
            "1.0",
            tk.END
        )

        self.translation_output.insert(
            tk.END,
            result
        )


    # ========================================================
    # VOCABULARY TAB
    # ========================================================

    def create_vocabulary_tab(self):

        self.vocabulary_tab = ttk.Frame(
            self.notebook,
            padding=10
        )

        self.notebook.add(
            self.vocabulary_tab,
            text="📚 Vocabulary"
        )

        columns = (
            "Sanskrit",
            "Meaning",
            "Category"
        )

        self.vocabulary_tree = ttk.Treeview(
            self.vocabulary_tab,
            columns=columns,
            show="headings"
        )

        for column in columns:

            self.vocabulary_tree.heading(
                column,
                text=column
            )

            self.vocabulary_tree.column(
                column,
                width=250
            )

        self.vocabulary_tree.pack(
            fill="both",
            expand=True
        )

        for word, meaning, category in VOCABULARY:

            self.vocabulary_tree.insert(
                "",
                tk.END,
                values=(
                    word,
                    meaning,
                    category
                )
            )

        ttk.Button(
            self.vocabulary_tab,
            text="✓ Mark Selected Word as Learned",
            command=self.mark_word_learned
        ).pack(
            pady=10
        )


    def mark_word_learned(self):

        selection = (
            self.vocabulary_tree.selection()
        )

        if not selection:

            messagebox.showinfo(
                "Vocabulary",
                "Select a word first."
            )

            return

        self.progress[
            "words_learned"
        ] += 1

        save_progress(
            self.progress
        )

        self.refresh_progress()

        messagebox.showinfo(
            "Vocabulary",
            "Word marked as learned!"
        )


    # ========================================================
    # QUIZ TAB
    # ========================================================

    def create_quiz_tab(self):

        self.quiz_tab = ttk.Frame(
            self.notebook,
            padding=20
        )

        self.notebook.add(
            self.quiz_tab,
            text="🧪 Quiz"
        )

        ttk.Label(
            self.quiz_tab,
            text="Sanskrit Knowledge Quiz",
            style="Heading.TLabel"
        ).pack(
            pady=10
        )

        self.quiz_question = ttk.Label(
            self.quiz_tab,
            text="",
            font=(
                "Arial",
                16
            ),
            wraplength=900
        )

        self.quiz_question.pack(
            pady=20
        )

        self.quiz_answer = tk.IntVar(
            value=-1
        )

        self.quiz_radio_frame = ttk.Frame(
            self.quiz_tab
        )

        self.quiz_radio_frame.pack(
            pady=10
        )

        self.quiz_radios = []

        for i in range(4):

            radio = ttk.Radiobutton(
                self.quiz_radio_frame,
                text="",
                variable=self.quiz_answer,
                value=i
            )

            radio.pack(
                anchor="w",
                pady=5
            )

            self.quiz_radios.append(
                radio
            )

        ttk.Button(
            self.quiz_tab,
            text="Submit Answer",
            command=self.submit_quiz
        ).pack(
            pady=20
        )

        self.quiz_result = ttk.Label(
            self.quiz_tab,
            text=""
        )

        self.quiz_result.pack(
            pady=10
        )

        self.load_quiz_question()


    def load_quiz_question(self):

        if self.current_quiz >= len(QUIZ):

            self.current_quiz = 0

        question = QUIZ[
            self.current_quiz
        ]

        self.quiz_question.config(
            text=question["question"]
        )

        self.quiz_answer.set(
            -1
        )

        for i, option in enumerate(
            question["options"]
        ):

            self.quiz_radios[i].config(
                text=option
            )

        self.quiz_result.config(
            text=""
        )


    def submit_quiz(self):

        selected = self.quiz_answer.get()

        if selected == -1:

            messagebox.showwarning(
                "Quiz",
                "Select an answer."
            )

            return

        question = QUIZ[
            self.current_quiz
        ]

        self.progress[
            "quiz_attempts"
        ] += 1

        if selected == question["answer"]:

            self.progress[
                "quiz_correct"
            ] += 1

            self.quiz_result.config(
                text="✓ Correct! उत्तमम्!"
            )

        else:

            correct_answer = question[
                "options"
            ][
                question["answer"]
            ]

            self.quiz_result.config(
                text=(
                    "✗ Incorrect.\n"
                    f"Correct answer: "
                    f"{correct_answer}"
                )
            )

        save_progress(
            self.progress
        )

        self.current_quiz += 1

        self.root.after(
            1500,
            self.load_quiz_question
        )

        self.refresh_progress()


    # ========================================================
    # PROGRESS TAB
    # ========================================================

    def create_progress_tab(self):

        self.progress_tab = ttk.Frame(
            self.notebook,
            padding=30
        )

        self.notebook.add(
            self.progress_tab,
            text="📊 Progress"
        )

        ttk.Label(
            self.progress_tab,
            text="Learning Progress",
            style="Heading.TLabel"
        ).pack(
            pady=20
        )

        self.progress_text = tk.Text(
            self.progress_tab,
            font=(
                "Arial",
                15
            ),
            height=15
        )

        self.progress_text.pack(
            fill="both",
            expand=True
        )


    def refresh_progress(self):

        if not hasattr(
            self,
            "progress_text"
        ):

            return

        attempts = self.progress[
            "quiz_attempts"
        ]

        correct = self.progress[
            "quiz_correct"
        ]

        if attempts > 0:

            accuracy = (
                correct / attempts
            ) * 100

        else:

            accuracy = 0

        text = (
            "संस्कृतवाणी - Progress\n"
            "\n"
            "--------------------------------\n"
            f"Text/Conversation Messages : "
            f"{self.progress['messages']}\n"
            "\n"
            f"Voice Messages             : "
            f"{self.progress['voice_messages']}\n"
            "\n"
            f"Grammar Checks             : "
            f"{self.progress['grammar_checks']}\n"
            "\n"
            f"Grammar Errors Detected    : "
            f"{self.progress['grammar_errors']}\n"
            "\n"
            f"Words Learned              : "
            f"{self.progress['words_learned']}\n"
            "\n"
            f"Speaking Practice Sessions : "
            f"{self.progress['practice_sessions']}\n"
            "\n"
            f"Quiz Attempts              : "
            f"{attempts}\n"
            "\n"
            f"Quiz Correct               : "
            f"{correct}\n"
            "\n"
            f"Quiz Accuracy              : "
            f"{accuracy:.1f}%\n"
            "\n"
            f"Last Active                : "
            f"{self.progress['last_active']}\n"
            "\n"
            "--------------------------------\n"
            "\n"
            "Learning Pipeline:\n"
            "\n"
            "🎤 Speech\n"
            "   ↓\n"
            "Whisper Speech Recognition\n"
            "   ↓\n"
            "Sanskrit Text\n"
            "   ↓\n"
            "Tokenization\n"
            "   ↓\n"
            "Morphological Analysis\n"
            "   ↓\n"
            "Grammar Checking\n"
            "   ↓\n"
            "Conversation Engine\n"
            "   ↓\n"
            "Feedback / Response\n"
            "   ↓\n"
            "🔊 Text-to-Speech"
        )

        self.progress_text.delete(
            "1.0",
            tk.END
        )

        self.progress_text.insert(
            tk.END,
            text
        )


    # ========================================================
    # CLOSE
    # ========================================================

    def on_close(self):

        save_progress(
            self.progress
        )

        self.root.destroy()


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("संस्कृतवाणी - Sanskrit Speaking Tutor")
    print("=" * 70)
    print()
    print("Starting application...")
    print()
    print(
        "Whisper model will be downloaded the first time "
        "voice recognition is used."
    )
    print()

    root = tk.Tk()

    app = SanskritSpeakingBot(
        root
    )

    root.mainloop()


if __name__ == "__main__":

    main()