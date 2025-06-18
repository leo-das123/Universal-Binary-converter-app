import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import threading
import binascii

class BinaryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Binary Universe Converter")
        self.geometry("420x800")
        self.configure(bg='#1e1e2e')
        self.resizable(True, True)
        self.frames = {}
        self.dark_theme = True

        container = tk.Frame(self, bg='#1e1e2e')
        container.pack(side="top", fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)


        for F in (HomePage, TextToBinaryPage, ImageToBinaryPage, BinaryToTextPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()
        frame.fade_in()

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        for frame in self.frames.values():
            frame.apply_theme(self.dark_theme)

class StyledFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#1e1e2e')
        self.inner = tk.Frame(self, bg='#1e1e2e')
        self.inner.place(relx=0.5, rely=0.5, anchor='center')
        self.attributes = {'alpha': 0.0}

    def fade_in(self):
        def increment_alpha():
            current = float(self.attributes['alpha'])
            if current < 1.0:
                current += 0.1
                self.attributes['alpha'] = current
                self.after(20, increment_alpha)
        increment_alpha()

    def styled_label(self, text, size=14):
        label = tk.Label(
            self.inner,
            text=text,
            font=("Segoe UI", size, "bold"),
            fg="white",
            bg="#1e1e2e"
        )
        label.bind("<Enter>", lambda e: label.config(fg="#7aa2f7"))
        label.bind("<Leave>", lambda e: label.config(fg="white"))
        return label

    def styled_button(self, text, command):
        button = tk.Button(
            self.inner,
            text=text,
            command=command,
            font=("Segoe UI", 12),
            bg="#7aa2f7",
            fg="black",
            activebackground="#4c6ef5",
            relief="flat",
            padx=12,
            pady=6,
            bd=0,
            cursor="hand2",
            highlightthickness=0,
            borderwidth=0
        )
        button.bind("<Enter>", lambda e: button.config(bg="#a5bff9"))
        button.bind("<Leave>", lambda e: button.config(bg="#7aa2f7"))
        return button

    def styled_entry(self):
        return tk.Entry(
            self.inner,
            width=30,
            font=("Segoe UI", 12),
            bg="#2e3440",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#4c6ef5",
            highlightcolor="#7aa2f7"
        )

    def apply_theme(self, dark):
        bg_color = '#1e1e2e' if dark else '#ffffff'
        fg_color = 'white' if dark else 'black'
        self.configure(bg=bg_color)
        self.inner.configure(bg=bg_color)
        for widget in self.inner.winfo_children():
            if isinstance(widget, (tk.Label, tk.Button, tk.Entry, scrolledtext.ScrolledText)):
                widget.configure(bg=bg_color, fg=fg_color)
                if isinstance(widget, tk.Entry):
                    widget.configure(insertbackground=fg_color)

class HomePage(StyledFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.styled_label("🧠 Binary Universe Converter", 20).pack(pady=30)
        self.styled_button("Text / Decimal ↔ Binary", lambda: controller.show_frame(TextToBinaryPage)).pack(pady=12)
        self.styled_button("Image → Binary", lambda: controller.show_frame(ImageToBinaryPage)).pack(pady=12)
        self.styled_button("Binary ↔ Text / Decimal", lambda: controller.show_frame(BinaryToTextPage)).pack(pady=12)
        self.styled_button("Toggle Theme 🍗", controller.toggle_theme).pack(pady=12)

class TextToBinaryPage(StyledFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.styled_label("📝 Text / Decimal to Binary", 18).pack(pady=20)

        self.input_entry = self.styled_entry()
        self.input_entry.pack(pady=10)

        self.result_text = scrolledtext.ScrolledText(self.inner, height=12, width=45, font=("Courier", 10), bg="#2e3440", fg="white", insertbackground="white")
        self.result_text.pack(pady=15, padx=10)

        self.styled_button("Convert to Binary", self.convert).pack(pady=10)
        self.styled_button("Back to Home", lambda: controller.show_frame(HomePage)).pack(pady=5)

    def convert(self):
        text = self.input_entry.get()
        if text.isdigit():
            binary = bin(int(text))[2:]
        else:
            binary = ' '.join(format(ord(c), '08b') for c in text)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Binary: {binary}")

class ImageToBinaryPage(StyledFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.styled_label("🖼️ Image to Binary", 18).pack(pady=20)

        self.result_text = scrolledtext.ScrolledText(self.inner, height=25, width=45, font=("Courier", 9), bg="#2e3440", fg="white", insertbackground="white", wrap=tk.WORD)
        self.result_text.pack(pady=15, padx=10, fill=tk.BOTH, expand=True)

        self.styled_button("Upload Image", self.upload_image).pack(pady=10)
        self.styled_button("Refresh", self.clear_result).pack(pady=5)
        self.styled_button("Back to Home", lambda: controller.show_frame(HomePage)).pack(pady=5)

    def upload_image(self):
        threading.Thread(target=self.process_image).start()

    def process_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if filepath:
            try:
                with open(filepath, 'rb') as file:
                    binary_data = file.read()
                    binary = ''.join(format(byte, '08b') for byte in binary_data)
                    display_binary = binary[:5000]
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, f"Binary (first 5000 bits):\n{display_binary}\n\n...Output truncated.")
            except Exception as e:
                self.result_text.insert(tk.END, f"\nError: {str(e)}")

    def clear_result(self):
        self.result_text.delete(1.0, tk.END)

class BinaryToTextPage(StyledFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.styled_label("📎 Binary to Text / Decimal", 18).pack(pady=20)

        self.input_entry = self.styled_entry()
        self.input_entry.pack(pady=10)

        self.result_text = scrolledtext.ScrolledText(self.inner, height=12, width=45, font=("Courier", 10), bg="#2e3440", fg="white", insertbackground="white")
        self.result_text.pack(pady=15, padx=10)

        self.styled_button("Convert to Text & Decimal", self.convert).pack(pady=10)
        self.styled_button("Back to Home", lambda: controller.show_frame(HomePage)).pack(pady=5)

    def convert(self):
        binary = self.input_entry.get().replace(' ', '')
        try:
            text = ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
            decimal = int(binary, 2)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Text: {text}\nDecimal: {decimal}")
        except:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Invalid binary input.")

if __name__ == '__main__':
    app = BinaryApp()
    app.mainloop()
