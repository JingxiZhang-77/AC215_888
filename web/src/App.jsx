import React, { useState, useRef } from "react";

const API_BASE = "http://localhost:8000/api";

export default function App() {
  const [input, setInput] = useState("");
  const [translation, setTranslation] = useState(null);
  const [classification, setClassification] = useState(null);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  const handleTranslate = async () => {
    setTranslation(null);
    const r = await fetch(`${API_BASE}/translate`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ text: input })
    });
    setTranslation(await r.json());
  };

  const handleClassify = async () => {
    const textToUse = translation?.translated_text || input;
    const r = await fetch(`${API_BASE}/classify`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ text: textToUse, already_english: true })
    });
    setClassification(await r.json());
  };

  const startSpeech = () => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      alert("Browser speech recognition not supported.");
      return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new SR();
    rec.lang = "zh-CN"; // user can change
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    rec.onresult = e => {
      const t = e.results[0][0].transcript;
      setInput(t);
      setListening(false);
    };
    rec.onerror = () => setListening(false);
    rec.onend = () => setListening(false);
    rec.start();
    recognitionRef.current = rec;
    setListening(true);
  };

  const stopSpeech = () => {
    recognitionRef.current && recognitionRef.current.stop();
    setListening(false);
  };

  return (
    <div style={{ fontFamily: "sans-serif", padding: 24, maxWidth: 900 }}>
      <h2>Safety Event Classification</h2>
      <textarea
        rows={6}
        style={{ width:"100%" }}
        value={input}
        placeholder="输入事件描述，可用中文/西班牙语等..."
        onChange={e => setInput(e.target.value)}
      />
      <div style={{ marginTop:12, display:"flex", gap:8 }}>
        <button onClick={handleTranslate}>Translate</button>
        <button onClick={handleClassify}>Classify</button>
        {!listening && <button onClick={startSpeech}>🎤 Speech Input</button>}
        {listening && <button onClick={stopSpeech}>Stop</button>}
      </div>

      {translation && (
        <div style={{ marginTop:20 }}>
          <h3>Translation</h3>
          <pre>{JSON.stringify(translation, null, 2)}</pre>
        </div>
      )}

      {classification && (
        <div style={{ marginTop:20 }}>
          <h3>Classification</h3>
          <pre>{JSON.stringify(classification, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
