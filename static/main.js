const form = document.getElementById('convertForm');
const result = document.getElementById('result');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(form);

  result.innerHTML = "⏳ Convirtiendo...";
  const res = await fetch('/convert', { method: 'POST', body: formData });
  if (!res.ok) return result.textContent = "❌ Error en la conversión.";

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = res.headers.get('Content-Disposition').split('filename=')[1];
  a.textContent = "⬇️ Descargar archivo convertido";
  result.innerHTML = "";
  result.appendChild(a);
});

// --- Texto a voz (navegador) ---
document.getElementById('speakBtn').addEventListener('click', () => {
  const text = document.getElementById('textInput').value;
  if (!window.speechSynthesis) return alert("Tu navegador no soporta voz.");
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = "es-ES";
  window.speechSynthesis.speak(utter);
});
