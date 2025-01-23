import tkinter as tk
from tkinter import filedialog, messagebox

class PDFMergerView:
    def __init__(self, root=None):
        self.controller = None  # Inicialmente sem controller
        self.root = root if root else tk.Tk()
        self.root.title("Merge de PDFs")
        self.root.geometry("600x400")

        # Frame para a lista de arquivos
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(self.frame, selectmode=tk.MULTIPLE, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame dos botões (será configurado depois que o controller for definido)
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

    def set_controller(self, controller):
        """
        Define o controller e configura os botões que dependem dele.
        """
        self.controller = controller
        self.select_button = tk.Button(self.button_frame, text="Selecionar PDFs", command=self.controller.select_files)
        self.select_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = tk.Button(self.button_frame, text="Remover Selecionado", command=self.controller.remove_selected)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        self.merge_button = tk.Button(self.button_frame, text="Mesclar PDFs", command=self.controller.merge_pdfs)
        self.merge_button.pack(side=tk.LEFT, padx=5)

    def run(self):
        self.root.mainloop()

    def get_selected_files(self):
        return list(self.listbox.get(0, tk.END))

    def add_files(self, files):
        for file in files:
            self.listbox.insert(tk.END, file)

    def remove_selected_files(self):
        selected_items = self.listbox.curselection()
        for index in selected_items[::-1]:
            self.listbox.delete(index)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def ask_save_file(self):
        return filedialog.asksaveasfilename(
            title="Salvar como",
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")]
        )

    def ask_open_files(self):
        return filedialog.askopenfilenames(
            title="Selecione os arquivos PDF",
            filetypes=[("Arquivos PDF", "*.pdf")]
        )
