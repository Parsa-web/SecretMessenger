import customtkinter as ctk
import tkinter.filedialog as fd
from PIL import Image
import re

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SecretMessengerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SecretMessenger")
        self.geometry("500x400")
        self.tabview = ctk.CTkTabview(self, command=self._on_tab_changed)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)
        self.embed_tab = self.tabview.add("Embed Message")
        self.extract_tab = self.tabview.add("Extract Message")
        self.embed_image_path = ctk.StringVar()
        self.embed_message = ctk.StringVar()
        self.embed_status = ctk.StringVar()
        self.embed_file_btn = ctk.CTkButton(self.embed_tab, text="Select PNG Image", command=self._select_embed_image)
        self.embed_file_btn.pack(pady=(30,10))
        self.embed_file_label = ctk.CTkLabel(self.embed_tab, textvariable=self.embed_image_path)
        self.embed_file_label.pack()
        self.embed_message_entry = ctk.CTkEntry(self.embed_tab, textvariable=self.embed_message, width=350, placeholder_text="Enter your secret message")
        self.embed_message_entry.pack(pady=20)
        self.embed_message.trace_add("write", self._update_embed_entry_justify)
        self.embed_save_btn = ctk.CTkButton(self.embed_tab, text="Encode & Save Image", command=self._encode_and_save)
        self.embed_save_btn.pack(pady=10)
        self.embed_status_label = ctk.CTkLabel(self.embed_tab, textvariable=self.embed_status)
        self.embed_status_label.pack()
        self.extract_image_path = ctk.StringVar()
        self.extract_result = ctk.StringVar()
        self.extract_file_btn = ctk.CTkButton(self.extract_tab, text="Select PNG Image", command=self._select_extract_image)
        self.extract_file_btn.pack(pady=(30,10))
        self.extract_file_label = ctk.CTkLabel(self.extract_tab, textvariable=self.extract_image_path)
        self.extract_file_label.pack()
        self.extract_btn = ctk.CTkButton(self.extract_tab, text="Extract", command=self._extract_message)
        self.extract_btn.pack(pady=20)
        self.extract_result_label = ctk.CTkLabel(self.extract_tab, textvariable=self.extract_result, wraplength=400)
        self.extract_result_label.pack()
        self.extract_result.trace_add("write", self._update_extract_result_justify)

    def _select_embed_image(self):
        path = fd.askopenfilename(filetypes=[("PNG Images", "*.png")])
        if path:
            self.embed_image_path.set(path)

    def _encode_and_save(self):
        image_path = self.embed_image_path.get()
        message = self.embed_message.get()
        if not image_path or not message:
            self.embed_status.set("Select image and enter message.")
            return
        save_path = fd.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Images", "*.png")])
        if not save_path:
            return
        try:
            embed_message_in_image(image_path, message, save_path)
            self.embed_status.set("Image saved.")
        except Exception as e:
            self.embed_status.set(str(e))

    def _select_extract_image(self):
        path = fd.askopenfilename(filetypes=[("PNG Images", "*.png")])
        if path:
            self.extract_image_path.set(path)

    def _extract_message(self):
        image_path = self.extract_image_path.get()
        if not image_path:
            self.extract_result.set("Select image.")
            return
        try:
            message = extract_message_from_image(image_path)
            self.extract_result.set(message)
        except Exception as e:
            self.extract_result.set(str(e))

    def _on_tab_changed(self):
        self.embed_image_path.set("")
        self.embed_message.set("")
        self.embed_status.set("")
        self.extract_image_path.set("")
        self.extract_result.set("")

    def _update_embed_entry_justify(self, *args):
        text = self.embed_message.get()
        if re.search(r"[\u0600-\u06FF]", text):
            self.embed_message_entry.configure(justify="right")
        else:
            self.embed_message_entry.configure(justify="left")

    def _update_extract_result_justify(self, *args):
        text = self.extract_result.get()
        if re.search(r"[\u0600-\u06FF]", text):
            self.extract_result_label.configure(justify="right", anchor="e")
        else:
            self.extract_result_label.configure(justify="left", anchor="w")

def _message_to_bits(message):
    b = message.encode('utf-8')
    return ''.join(f'{byte:08b}' for byte in b)

def _bits_to_message(bits):
    bytes_list = [bits[i:i+8] for i in range(0, len(bits), 8)]
    byte_array = bytearray()
    for b in bytes_list:
        if len(b) == 8:
            byte_array.append(int(b, 2))
    try:
        return byte_array.decode('utf-8')
    except:
        return ''

def embed_message_in_image(image_path, message, output_path):
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    width, height = img.size
    max_bytes = width * height
    message += '\0'
    bits = _message_to_bits(message)
    if len(bits) > max_bytes:
        raise ValueError('Message too long for this image')
    pixels = list(img.getdata())
    new_pixels = []
    bit_idx = 0
    for pixel in pixels:
        r, g, b = pixel
        if bit_idx < len(bits):
            b = (b & ~1) | int(bits[bit_idx])
            bit_idx += 1
        new_pixels.append((r, g, b))
    img.putdata(new_pixels)
    img.save(output_path, 'PNG')

def extract_message_from_image(image_path):
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = list(img.getdata())
    bits = ''
    for pixel in pixels:
        b = pixel[2]
        bits += str(b & 1)
    bytes_list = [bits[i:i+8] for i in range(0, len(bits), 8)]
    byte_array = bytearray()
    for b in bytes_list:
        if len(b) == 8:
            val = int(b, 2)
            if val == 0:
                break
            byte_array.append(val)
    try:
        return byte_array.decode('utf-8')
    except:
        return ''

if __name__ == "__main__":
    app = SecretMessengerApp()
    app.mainloop() 