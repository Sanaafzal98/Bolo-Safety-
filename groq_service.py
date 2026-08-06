"""
Groq service:
1. transcribe_urdu()      -> original Urdu script (whisper-large-v3)
2. translate_to_english() -> English translation (whisper-large-v3, translation endpoint)
3. categorize()           -> structured JSON via llama-3.3-70b-versatile
   { category, severity, location, reporter_name }

All calls use the free Groq API. Set GROQ_API_KEY in your .env file.
"""

import os
import json
from groq import Groq
from aksharamukha import transliterate

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env file.")
        _client = Groq(api_key=api_key)
    return _client


def transcribe_original(audio_path: str) -> str:
    """Returns the Urdu-script transcript."""
    client = get_client()
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), f.read()),
            model="whisper-large-v3",
            language="ur",
            response_format="text",
        )
    return str(result).strip()


# kept for backwards compatibility with any existing callers
transcribe_urdu = transcribe_original


def _to_urdu_script(text: str) -> str:
    """Whisper sometimes writes Urdu speech in Devanagari or Gurmukhi script
    instead of Urdu script, even when language='ur' is forced. Detect that
    and auto-convert to proper Urdu script."""
    if not text:
        return text

    devanagari = sum(1 for ch in text if '\u0900' <= ch <= '\u097F')
    gurmukhi = sum(1 for ch in text if '\u0A00' <= ch <= '\u0A7F')
    total_letters = sum(1 for ch in text if ch.isalpha())

    if total_letters == 0:
        return text

    if devanagari / total_letters > 0.3:
        try:
            return transliterate.process('Devanagari', 'Urdu', text)
        except Exception:
            return text

    if gurmukhi / total_letters > 0.3:
        try:
            return transliterate.process('Gurmukhi', 'Urdu', text)
        except Exception:
            return text

    return text


def translate_to_english(audio_path: str) -> str:
    """Returns an English translation of the audio (Groq's translation endpoint)."""
    client = get_client()
    with open(audio_path, "rb") as f:
        result = client.audio.translations.create(
            file=(os.path.basename(audio_path), f.read()),
            model="whisper-large-v3",
            response_format="text",
        )
    return str(result).strip()


def categorize(english_text: str, fallback_reporter_name: str = "") -> dict:
    """
    Uses llama-3.3-70b-versatile to parse the English translation into
    structured fields matching the observation log format.
    """
    client = get_client()

    system_prompt = (
        "You are a Health, Safety & Environment (HSE) assistant for an industrial site "
        "(oil/gas terminal type facility with jetties, tank farms, loading bays, trestles etc). "
        "You will be given an English translation of a worker's verbal safety observation report. "
        "Extract structured data and respond with ONLY valid JSON, no markdown, no commentary, "
        "in exactly this shape:\n"
        '{"category": "Unsafe Act" | "Unsafe Condition" | "Near Miss" | "LTI", '
        '"severity": "High" | "Medium" | "Low", '
        '"location": "<short location name, e.g. Loading Bay, Tank Farm, Jetty, Jetty Trestle, or Not specified>", '
        '"reporter_name": "<name if mentioned in the text, otherwise empty string>", '
        '"summary": "<a clean one-sentence English summary of the incident, similar in style to '
        '\'A reversing truck nearly struck a worker who was in the blind spot at the loading bay entrance\'>"}\n'
        "Category definitions: Near Miss = hazard occurred but no injury/damage; "
        "Unsafe Act = risky behaviour by a person; Unsafe Condition = hazardous environment/equipment state; "
        "LTI = Lost Time Injury, someone was actually injured and could not continue work. "
        "Severity: High = could cause death/serious injury, Medium = moderate injury/damage possible, "
        "Low = minor/negligible risk."
    )

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": english_text},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    raw = completion.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}

    category = data.get("category") if data.get("category") in (
        "Unsafe Act", "Unsafe Condition", "Near Miss", "LTI"
    ) else "Not specified"

    severity = data.get("severity") if data.get("severity") in ("High", "Medium", "Low") else "Not specified"

    return {
        "category": category,
        "severity": severity,
        "location": data.get("location") or "Not specified",
        "reporter_name": data.get("reporter_name") or fallback_reporter_name or "Anonymous",
        "summary": data.get("summary") or english_text,
    }


def process_audio_report(audio_path: str, fallback_reporter_name: str = "") -> dict:
    """
    Full pipeline: audio -> Urdu script + English translation -> categorized fields.
    Returns a dict ready to be saved into the Observation model.
    """
    urdu_text = _to_urdu_script(transcribe_original(audio_path))
    english_text = translate_to_english(audio_path)
    fields = categorize(english_text, fallback_reporter_name=fallback_reporter_name)

    return {
        "urdu_script": urdu_text,
        "english_translation": fields["summary"] or english_text,
        "category": fields["category"],
        "severity": fields["severity"],
        "location": fields["location"],
        "reporter_name": fields["reporter_name"],
    }
