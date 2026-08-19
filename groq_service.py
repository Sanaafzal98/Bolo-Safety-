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
    """Returns the original-language transcript. Language is auto-detected
    (Urdu, Punjabi, or Sindhi) rather than forced, so each is transcribed
    accurately in its own script."""
    client = get_client()
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), f.read()),
            model="whisper-large-v3",
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


def categorize(english_text: str, urdu_text: str = "", fallback_reporter_name: str = "") -> dict:
    """
    Uses llama-3.3-70b-versatile to parse the English translation (plus the
    original Urdu transcript as backup context) into structured fields
    matching the observation log format.
    """
    client = get_client()

    KNOWN_LOCATIONS = """Substation , Utility Pump Area, Utility Tank Area, VCM LCR, VCM Pump House, VCM Tank Farm, General Weighbridge, LPG Weighbridge, Cable Yard, Chemical Yard, E&I Yard, Hazardous Yard, Parking Area, Pipe Yard, Scrap Yard, Salvage Yard, Waste Water Handling Area, LPG Bullet Storage, Acetic Acid Pump House, Acetic Acid Tank Farm Area, Acetic Acid Truck Loading Area, Admin Building, Central Control Room, Canteen, First Aid Room, Fire Station, Generator Room, Hose Room, Maintenance BLD, Workshop, Main Gate, Record Room, Security Control Room, Admin Store, VCM Store, Training Room, Warehouse, Warehouse B (China Yard), EDC Pump House, EDC Tank Farm, EDC Truck Loading Area, Jetty, Jetty Head, Jetty Intersection, Jetty Equipment Room, Jetty Switch Room, Mooring Dolphin, Jetty Trestle, Jetty Walkway North Side, Jetty Walkway South Side, Main Control Room"""

    system_prompt = (
        "You are a Health, Safety & Environment (HSE) assistant for an industrial site "
        "(oil/gas/petrochemical terminal with jetties, tank farms, loading bays, substations, "
        "utility areas etc). "
        "You will be given an English translation of a worker's verbal safety observation report, "
        "originally spoken in Urdu/English mix. The worker often describes a location informally or "
        "vaguely (e.g. 'the grassy area', 'near the big tanks', 'by the main entrance') instead of "
        "using its official name.\n\n"
        "Here is the FIXED, OFFICIAL list of real locations at this site:\n"
        f"{KNOWN_LOCATIONS}\n\n"
        "Extract structured data and respond with ONLY valid JSON, no markdown, no commentary, "
        "in exactly this shape:\n"
        '{"category": "Unsafe Act" | "Unsafe Condition" | "Near Miss" | "LTI", '
        '"severity": "High" | "Medium" | "Low", '
        '"location": "<the single BEST-matching name from the official list above, chosen by meaning/'
        'context, not just keyword overlap — or exactly \\"Not specified\\" if nothing in the list '
        'plausibly matches or no location was mentioned at all>", '
        '"reporter_name": "<name if mentioned in the text, otherwise empty string>", '
        '"summary": "<a clean one-sentence English summary of the incident, similar in style to '
        '\'A reversing truck nearly struck a worker who was in the blind spot at the loading bay entrance\'>"}\n\n'
        "IMPORTANT location rules:\n"
        "- ALWAYS pick from the official list above. NEVER invent a new location name, and never output "
        "a generic guess like 'land' or 'area' that isn't literally in the list.\n"
        "- Match by real-world meaning: e.g. an open area with grass where vehicles park is almost "
        "certainly 'Parking Area'; a fire mentioned near LPG tanks likely means one of the "
        "'LPG Bullet Storage' locations; a report near the entrance/security likely means 'Main Gate'.\n"
        "- It's fine to make a reasonable best-guess pick even if the report is a bit vague — pick the "
        "closest sensible match from the list rather than defaulting to 'Not specified' too easily. "
        "Only use 'Not specified' when the report gives NO usable clue at all about where the worker is "
        "(e.g. they never mention any area, landmark, equipment type, or activity tied to a place).\n"
        "- When the report is vague about which numbered/lettered sub-unit of a place it means (e.g. "
        "'a tank farm' without saying which one, or 'a jetty' without a number), just pick the general "
        "location name from the list (e.g. 'VCM Tank Farm', 'Jetty') rather than refusing to answer.\n\n"
        "IMPORTANT reporter_name rule:\n"
        "- You will be given TWO versions of the report: an English translation, and (below it) the "
        "original Urdu-script transcript. The English translation is sometimes shortened and may DROP "
        "a self-introduction like 'my name is ...' even though the original Urdu clearly states it. "
        "Always check BOTH texts for a stated name — if the English translation has no name but the "
        "Urdu transcript does (e.g. 'mera naam X hai' / 'main X hoon'), use that name, transliterated "
        "into normal English spelling. Only leave reporter_name empty if NEITHER text states a name.\n\n"
        "Category definitions: Near Miss = hazard occurred but no injury/damage; "
        "Unsafe Act = risky behaviour by a person; Unsafe Condition = hazardous environment/equipment state; "
        "LTI = Lost Time Injury, someone was actually injured and could not continue work. "
        "Severity: High = could cause death/serious injury, Medium = moderate injury/damage possible, "
        "Low = minor/negligible risk."
    )

    user_content = f"English translation:\n{english_text}"
    if urdu_text:
        user_content += f"\n\nOriginal Urdu transcript (check this for names/details the translation may have dropped):\n{urdu_text}"

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
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
    fields = categorize(english_text, urdu_text=urdu_text, fallback_reporter_name=fallback_reporter_name)

    return {
        "urdu_script": urdu_text,
        "english_translation": fields["summary"] or english_text,
        "category": fields["category"],
        "severity": fields["severity"],
        "location": fields["location"],
        "reporter_name": fields["reporter_name"],
    }
