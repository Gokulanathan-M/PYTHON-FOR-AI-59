import tkinter as tk
from tkinter import messagebox, filedialog
import string
import os
from deep_translator import GoogleTranslator
from fpdf import FPDF
import pygame
from nltk.tokenize import word_tokenize
import nltk
from gtts import gTTS

nltk.download('punkt')

# Supported languages: display name -> ISO code
lang_display_names = {
    "Tamil": "ta",
    "Hindi": "hi",
    "English": "en",
    "Japanese": "ja",
    "Bengali": "bn"
}

def explain_words_word_by_word(text, src_lang_code, target_lang_code):
    """
    Tokenizes input text, translates each word individually from src_lang_code
    to target_lang_code, and returns a formatted explanation string.
    """
    words = word_tokenize(text)
    explanation_lines = []

    for word in words:
        word_clean = word.strip(string.punctuation)
        if not word_clean:
            continue
        try:
            translated_word = GoogleTranslator(source=src_lang_code, target=target_lang_code).translate(word_clean)
        except Exception:
            translated_word = "[Translation error]"
        explanation_lines.append(f"{word_clean} : {translated_word}")

    return "\n".join(explanation_lines)

def translate_full_sentence(text, src_lang_code, target_lang_code):
    """
    Translate the full sentence from src_lang_code to target_lang_code.
    """
    return GoogleTranslator(source=src_lang_code, target=target_lang_code).translate(text)

def translate_and_explain():
    text = input_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Input Required", "Please enter a sentence.")
        return
    
    src_lang_code = lang_display_names[selected_src_lang.get()]
    target_lang_code = lang_display_names[selected_target_lang.get()]
    
    try:
        # Full sentence translation
        translated = translate_full_sentence(text, src_lang_code, target_lang_code)
        translated_text.delete("1.0", tk.END)
        translated_text.insert(tk.END, translated)

        # Word-by-word explanation (each source word translated individually)
        explanation = explain_words_word_by_word(text, src_lang_code, target_lang_code)
        explanation_text.delete("1.0", tk.END)
        explanation_text.insert(tk.END, explanation)
    except Exception as e:
        messagebox.showerror("Translation Error", str(e))

def play_audio(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        filename = "temp_audio.mp3"
        tts.save(filename)

        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.stop()
        pygame.mixer.quit()
        os.remove(filename)
    except Exception as e:
        messagebox.showerror("TTS Error", str(e))

def save_output():
    content = f"Original ({selected_src_lang.get()}): {input_text.get('1.0', tk.END)}\n"
    content += f"Translated ({selected_target_lang.get()}): {translated_text.get('1.0', tk.END)}\n"
    content += f"Word-by-word Explanation (to {selected_target_lang.get()}):\n{explanation_text.get('1.0', tk.END)}"

    file_type = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text File", "*.txt"), ("PDF File", "*.pdf")])
    if not file_type:
        return
    if file_type.endswith('.txt'):
        with open(file_type, "w", encoding='utf-8') as file:
            file.write(content)
    elif file_type.endswith('.pdf'):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for line in content.split('\n'):
            pdf.cell(0, 10, txt=line, ln=True)
        pdf.output(file_type)

# GUI setup
root = tk.Tk()
root.title("Multilingual Translator with Word-by-Word Explanation")
root.geometry("750x700")

tk.Label(root, text="Enter sentence:").pack()
input_text = tk.Text(root, height=4)
input_text.pack()

tk.Label(root, text="Select source language:").pack()
selected_src_lang = tk.StringVar(value="Tamil")
tk.OptionMenu(root, selected_src_lang, *lang_display_names.keys()).pack()

tk.Label(root, text="Select target language:").pack()
selected_target_lang = tk.StringVar(value="Japanese")
tk.OptionMenu(root, selected_target_lang, *lang_display_names.keys()).pack()

tk.Button(root, text="Translate & Explain", command=translate_and_explain).pack(pady=5)

tk.Label(root, text="🌍 Translated Sentence:").pack()
translated_text = tk.Text(root, height=3)
translated_text.pack()

tk.Label(root, text="📖 Word-by-word Explanation:").pack()
explanation_text = tk.Text(root, height=15)
explanation_text.pack()

tk.Button(root, text="🔊 Hear Translation", command=lambda: play_audio(translated_text.get("1.0", tk.END).strip(), lang_display_names[selected_target_lang.get()])).pack(pady=5)

tk.Button(root, text="💾 Save to File", command=save_output).pack(pady=5)

root.mainloop()
