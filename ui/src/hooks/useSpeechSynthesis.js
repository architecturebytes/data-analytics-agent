import { useState, useEffect } from "react";

export default function useSpeechSynthesis() {
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);

  // Default rate and pitch as per user's preference for a 'good' voice
  const preferredRate = 1.0; // Slightly higher than default 1.0
  const preferredPitch = 1.1; // Slightly higher than default 1.0

  useEffect(() => {
    const findAndSetVoice = () => {
      const allVoices = speechSynthesis.getVoices();
      setVoices(allVoices);

      console.log("Available en-US voices:");
      allVoices.filter(voice => voice.lang === "en-US").forEach((voice, index) => {
        console.log(`  ${index + 1}. Name: ${voice.name}, Lang: ${voice.lang}, Default: ${voice.default}`);
      });

      let chosenVoice = null;

      // User's preference: Google US English female, high rate/pitch.
      // We will try to find a voice that matches "Google US English" and sounds female.
      // Note: "Female" is often in the name, but not always.
      chosenVoice = allVoices.find(
        (voice) => voice.lang === "en-US" && voice.name.includes("Google") && (voice.name.includes("Female") || voice.name.includes("US English"))
      ) || allVoices.find(
        (voice) => voice.lang === "en-US" && voice.name.includes("Zira") // Common Windows female voice
      ) || allVoices.find(
        (voice) => voice.lang === "en-US" && voice.name.includes("Samantha") // Common Mac/iOS female voice
      ) || allVoices.find( // Fallback to any en-US voice that seems female-ish (heuristic)
        (voice) => voice.lang === "en-US" && (voice.name.toLowerCase().includes("female") || voice.name.toLowerCase().includes("google us"))
      );
      
      if (!chosenVoice) {
        // Fallback to any default en-US voice, or the first available voice
        chosenVoice = allVoices.find((voice) => voice.lang === "en-US" && voice.default) || 
                      allVoices.find((voice) => voice.lang === "en-US") || 
                      allVoices[0];
      }

      setSelectedVoice(chosenVoice);
    };

    speechSynthesis.addEventListener("voiceschanged", findAndSetVoice);
    findAndSetVoice(); // Call once in case voices are already loaded

    return () => {
      speechSynthesis.removeEventListener("voiceschanged", findAndSetVoice);
    };
  }, []);

  const speak = (text) => {
    if (!selectedVoice) {
      console.warn("No speech synthesis voice selected. Using default.");
    }
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = preferredRate; // Use preferred rate
    utter.pitch = preferredPitch; // Use preferred pitch
    utter.lang = selectedVoice?.lang || "en-US"; 
    if (selectedVoice) {
      utter.voice = selectedVoice;
    }
    speechSynthesis.speak(utter);
  };

  return { speak };
}