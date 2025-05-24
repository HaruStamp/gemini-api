from flask import Blueprint, request, send_file, jsonify
from google import genai
from google.genai import types
from utils.helpers import save_wave
import tempfile
import os

speech_bp = Blueprint("speech", __name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@speech_bp.route("/api/gen/speech", methods=["POST"])
def generate_speech():
   try:
      data = request.json
      model = data.get("model", "gemini-2.5-flash-preview-tts")
      contents = data.get("contents", "")
      config_data = data.get("config", {})

      if not contents:
         return jsonify({"error": "Missing content"}), 400

      # ดึงรายการ speaker voice configs
      speaker_configs_data = config_data.get("speech_config", {}) \
                                        .get("multi_speaker_voice_config", {}) \
                                        .get("speaker_voice_configs", [])

      # แปลง speaker configs จาก JSON ให้กลายเป็น Python object
      speaker_voice_configs = []
      for sc in speaker_configs_data:
          speaker = sc.get("speaker")
          voice_name = sc.get("voice_config", {}) \
                         .get("prebuilt_voice_config", {}) \
                         .get("voice_name")
          if speaker and voice_name:
              speaker_voice_configs.append(
                  types.SpeakerVoiceConfig(
                      speaker=speaker,
                      voice_config=types.VoiceConfig(
                          prebuilt_voice_config=types.PrebuiltVoiceConfig(
                              voice_name=voice_name
                          )
                      )
                  )
              )

      # สร้าง config object จากข้อมูลที่แปลง
      config = types.GenerateContentConfig(
          response_modalities=["AUDIO"],
          speech_config=types.SpeechConfig(
              multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=speaker_voice_configs
              )
          )
      )

      response = client.models.generate_content(
          model=model,
          contents=contents,
          config=config
      )

      audio_data = response.candidates[0].content.parts[0].inline_data.data

      with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
         save_wave(tmp.name, audio_data)
         return send_file(tmp.name, mimetype="audio/wav", as_attachment=True, download_name="output.wav")

   except Exception as e:
      return jsonify({"error": str(e)}), 500
