import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk

# ====================
# Encoding Function
# ====================
def encode_message(img_path, message, output_path):
    image = Image.open(img_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    encoded = image.copy()
    width, height = image.size
    index = 0
    message += "###END###"

    binary_message = ''.join([format(ord(char), '08b') for char in message])
    msg_len = len(binary_message)

    for row in range(height):
        for col in range(width):
            if index < msg_len:
                r, g, b = image.getpixel((col, row))
                r = r & ~1 | int(binary_message[index])
                index += 1
                if index < msg_len:
                    g = g & ~1 | int(binary_message[index])
                    index += 1
                if index < msg_len:
                    b = b & ~1 | int(binary_message[index])
                    index += 1
                encoded.putpixel((col, row), (r, g, b))
            else:
                encoded.save(output_path)
                return True
    encoded.save(output_path)
    return True

# ====================
# Decoding Function
# ====================
def decode_message(img_path):
    image = Image.open(img_path)
    binary_message = ""
    for pixel in image.getdata():
        for color in pixel[:3]:
            binary_message += str(color & 1)

    chars = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
    decoded = ""

    for char in chars:
        try:
            decoded += chr(int(char, 2))
        except ValueError:
            break
        if decoded.endswith("###END###"):
            return decoded.split("###END###")[0]
    return "No hidden message found."

# ====================
# GUI Class
# ====================
class StegGUI:
    def __init__(self, master):
        self.master = master
        master.title("Steganography Tool")

        # === Window Sizing and Centering ===
        window_width = 800
        window_height = 600
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        master.resizable(False, False)  # Optional: disable resizing
        master.configure(bg="#f4f4f4")

        self.image_path = None

        # ==== Frames ====
        self.top_frame = tk.Frame(master, bg="#f4f4f4")
        self.top_frame.pack(pady=10)

        self.middle_frame = tk.Frame(master, bg="#f4f4f4")
        self.middle_frame.pack(pady=10)

        self.bottom_frame = tk.Frame(master, bg="#f4f4f4")
        self.bottom_frame.pack(pady=10)

        # ==== Top Frame ====
        self.choose_button = ttk.Button(self.top_frame, text="📁 Choose Image", command=self.choose_image)
        self.choose_button.grid(row=0, column=0, padx=10)

        self.image_label = tk.Label(self.top_frame, text="No image selected", bg="#f4f4f4")
        self.image_label.grid(row=0, column=1, sticky="w")

        self.preview = tk.Label(self.top_frame, bg="#ddd", width=300, height=200)
        self.preview.grid(row=1, column=0, columnspan=2, pady=10)

        # ==== Middle Frame ====
        ttk.Label(self.middle_frame, text="🔐 Message to Hide:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.message_entry = tk.Text(self.middle_frame, height=5, width=80)
        self.message_entry.grid(row=1, column=0, pady=5)

        self.encode_button = ttk.Button(self.middle_frame, text="🔒 Encode Message", command=self.encode)
        self.encode_button.grid(row=2, column=0, pady=10)

        # ==== Bottom Frame ====
        self.decode_button = ttk.Button(self.bottom_frame, text="🔓 Decode Message", command=self.decode)
        self.decode_button.grid(row=0, column=0, pady=5)

        ttk.Label(self.bottom_frame, text="📄 Decoded Message:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w")
        self.output_text = tk.Text(self.bottom_frame, height=10, width=80)
        self.output_text.grid(row=2, column=0, pady=5)

    def choose_image(self):
        path = filedialog.askopenfilename(filetypes=[("PNG Image", "*.png")])
        if path:
            self.image_path = path
            self.image_label.config(text=path.split("/")[-1])
            image = Image.open(path)
            image.thumbnail((300, 200))
            photo = ImageTk.PhotoImage(image)
            self.preview.config(image=photo)
            self.preview.image = photo

    def encode(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please choose an image.")
            return
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Please enter a message to hide.")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if output_path:
            try:
                success = encode_message(self.image_path, message, output_path)
                if success:
                    messagebox.showinfo("Success", f"Message successfully encoded in:\n{output_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Encoding failed:\n{str(e)}")

    def decode(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please choose an image.")
            return
        try:
            hidden_msg = decode_message(self.image_path)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, hidden_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Decoding failed:\n{str(e)}")

# ====================
# Run Application
# ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = StegGUI(root)
    root.mainloop()
