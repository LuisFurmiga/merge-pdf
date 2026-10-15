import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class PDFMergerView:
    def __init__(self, root=None):
        self.controller = None
        self.files = []
        self.root = root if root else tk.Tk()
        self.root.title('Organizar e mesclar PDFs')
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TButton', padding=(12, 8))
        style.configure('Treeview', rowheight=32)
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'))
        style.configure('Accent.TButton', foreground='white', background='#2457c5')
        style.map('Accent.TButton',
                  background=[('disabled', '#d9d9d9'),
                              ('pressed', '#173b87'),
                              ('active', '#1d46a0')],
                  foreground=[('disabled', '#666666'), ('!disabled', 'white')])
        main = ttk.Frame(self.root, padding=24)
        self.main = main
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(3, weight=1, minsize=64)
        self.title_label = ttk.Label(main, text='Seus PDFs, na ordem certa', style='Title.TLabel', wraplength=500)
        self.title_label.grid(row=0, column=0, sticky='w')
        self.description_label = ttk.Label(main, text='Adicione arquivos, ajuste a ordem e salve tudo em um único PDF.', wraplength=500)
        self.description_label.grid(row=1, column=0, sticky='w', pady=(6, 18))
        toolbar = ttk.Frame(main)
        toolbar.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        self.select_button = ttk.Button(toolbar, text='+ Adicionar PDFs', command=lambda: self.controller.select_files())
        self.select_button.pack(side=tk.LEFT)
        self.count = tk.StringVar(value='Nenhum PDF adicionado')
        ttk.Label(toolbar, textvariable=self.count).pack(side=tk.RIGHT)
        table = ttk.Frame(main)
        table.grid(row=3, column=0, sticky='nsew')
        self.listbox = ttk.Treeview(table, height=3, columns=('position', 'name', 'folder'), show='headings', selectmode='extended')
        for column, title, width in (('position', 'Ordem', 60), ('name', 'Arquivo PDF', 260), ('folder', 'Pasta', 300)):
            self.listbox.heading(column, text=title)
            self.listbox.column(column, width=width, minwidth=50, stretch=column != 'position')
        scrollbar = ttk.Scrollbar(table, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind('<<TreeviewSelect>>', lambda event: self._update_controls())
        self.listbox.bind('<Alt-Up>', lambda event: self._move_shortcut(-1))
        self.listbox.bind('<Alt-Down>', lambda event: self._move_shortcut(1))
        self.listbox.bind('<Delete>', lambda event: self.controller.remove_selected())
        actions = ttk.Frame(main)
        self.actions = actions
        actions.grid(row=4, column=0, sticky='ew', pady=12)
        actions.columnconfigure(3, weight=1)
        self.up_button = ttk.Button(actions, text='↑ Subir', command=lambda: self.controller.move_selected(-1))
        self.down_button = ttk.Button(actions, text='↓ Descer', command=lambda: self.controller.move_selected(1))
        self.remove_button = ttk.Button(actions, text='Remover', command=lambda: self.controller.remove_selected())
        for column, button in enumerate((self.up_button, self.down_button, self.remove_button)):
            button.grid(row=0, column=column, padx=(0, 8))
        self.merge_button = ttk.Button(actions, text='Mesclar e salvar…', style='Accent.TButton', command=lambda: self.controller.merge_pdfs())
        self.merge_button.grid(row=0, column=3, sticky='e')
        self.status = tk.StringVar(value='Comece adicionando os PDFs que deseja juntar.')
        self.status_label = ttk.Label(main, textvariable=self.status, wraplength=500)
        self.status_label.grid(row=5, column=0, sticky='w')
        self.help_label = ttk.Label(main, text='A mesclagem segue a ordem acima. Ctrl seleciona vários; Alt + ↑/↓ move a seleção.', wraplength=500)
        self.help_label.grid(row=6, column=0, sticky='w', pady=(8, 0))
        self._compact_actions = None
        main.bind('<Configure>', self._resize_layout)
        self._update_controls()
        self.root.update_idletasks()
        minimum_width = max(420, toolbar.winfo_reqwidth() + 48,
                            sum(button.winfo_reqwidth() + 8 for button in
                                (self.up_button, self.down_button, self.remove_button)) + 48)
        # Measure wrapped text and the compact button row at the narrowest width.
        self.root.geometry(f'{minimum_width}x{self.root.winfo_screenheight()}')
        self.root.update_idletasks()
        self._resize_layout_width(minimum_width - 48)
        self.root.update_idletasks()
        minimum_height = (48 + self.title_label.winfo_reqheight()
                          + self.description_label.winfo_reqheight() + 24
                          + toolbar.winfo_reqheight() + 10 + table.winfo_reqheight()
                          + actions.winfo_reqheight() + 24
                          + self.status_label.winfo_reqheight()
                          + self.help_label.winfo_reqheight() + 8)
        self.root.minsize(minimum_width, minimum_height)
        width = max(minimum_width, min(860, self.root.winfo_screenwidth() - 80))
        height = max(minimum_height, min(600, self.root.winfo_screenheight() - 100))
        self.root.geometry(f'{width}x{height}')

    def _resize_layout(self, event):
        self._resize_layout_width(max(1, event.width - 48))
        self.root.after_idle(self._update_minimum_height)

    def _update_minimum_height(self):
        # Font metrics can change when Windows first maps a high-DPI window.
        minimum_width, _ = self.root.minsize()
        self.root.minsize(minimum_width, self.main.winfo_reqheight())

    def _resize_layout_width(self, width):
        for label in (self.title_label, self.description_label, self.status_label, self.help_label):
            label.configure(wraplength=width)
        required = sum(button.winfo_reqwidth() + 8 for button in
                       (self.up_button, self.down_button, self.remove_button, self.merge_button))
        compact = width < required
        if compact != self._compact_actions:
            self._compact_actions = compact
            self.merge_button.grid_configure(row=1 if compact else 0,
                                             column=0 if compact else 3,
                                             columnspan=4 if compact else 1,
                                             sticky='ew' if compact else 'e',
                                             pady=(8, 0) if compact else 0)

    def set_controller(self, controller):
        self.controller = controller

    def run(self):
        self.root.mainloop()

    def get_selected_files(self):
        return list(self.files)

    def _selected_indices(self):
        return sorted(int(item) for item in self.listbox.selection())

    def _refresh(self, selected=()):
        children = self.listbox.get_children()
        if children:
            self.listbox.delete(*children)
        for index, path in enumerate(self.files):
            self.listbox.insert('', tk.END, iid=str(index), values=(index + 1, os.path.basename(path), os.path.dirname(path)))
        self.listbox.selection_set([str(index) for index in selected])
        if selected:
            self.listbox.focus(str(selected[0]))
            self.listbox.see(str(selected[0]))
        self.count.set(f'{len(self.files)} PDF(s) na lista' if self.files else 'Nenhum PDF adicionado')
        self._update_controls()

    def _update_controls(self):
        selected = self._selected_indices()
        self.up_button.configure(state='normal' if selected and selected[0] > 0 else 'disabled')
        self.down_button.configure(state='normal' if selected and selected[-1] < len(self.files) - 1 else 'disabled')
        self.remove_button.configure(state='normal' if selected else 'disabled')
        self.merge_button.configure(state='normal' if self.files else 'disabled')

    def add_files(self, files):
        known = {os.path.normcase(os.path.abspath(path)) for path in self.files}
        added = []
        for path in files:
            key = os.path.normcase(os.path.abspath(path))
            if key not in known:
                known.add(key)
                added.append(len(self.files))
                self.files.append(path)
        self._refresh(added)
        self.status.set(f'{len(added)} PDF(s) adicionado(s). Arquivos repetidos são ignorados.')

    def move_selected_files(self, direction):
        selected = self._selected_indices()
        if not selected or direction not in (-1, 1):
            return
        if selected[0] + direction < 0 or selected[-1] + direction >= len(self.files):
            return
        for index in selected if direction == -1 else reversed(selected):
            target = index + direction
            self.files[index], self.files[target] = self.files[target], self.files[index]
        self._refresh([index + direction for index in selected])
        self.status.set('Ordem atualizada. O PDF final seguirá esta sequência.')

    def _move_shortcut(self, direction):
        self.controller.move_selected(direction)
        return 'break'

    def remove_selected_files(self):
        selected = self._selected_indices()
        for index in reversed(selected):
            del self.files[index]
        self._refresh([min(selected[0], len(self.files) - 1)] if selected and self.files else [])
        self.status.set('Seleção removida da lista.' if self.files else 'Comece adicionando os PDFs que deseja juntar.')

    def clear_files(self):
        self.files.clear()
        self._refresh()
        self.status.set('PDF salvo com sucesso. Você já pode iniciar outra mesclagem.')

    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self.root)

    def show_info(self, title, message):
        messagebox.showinfo(title, message, parent=self.root)

    def ask_save_file(self):
        return filedialog.asksaveasfilename(parent=self.root, title='Salvar PDF mesclado', initialfile='PDF mesclado.pdf', defaultextension='.pdf', filetypes=[('Arquivos PDF', '*.pdf')])

    def ask_open_files(self):
        return filedialog.askopenfilenames(parent=self.root, title='Adicionar arquivos PDF', filetypes=[('Arquivos PDF', '*.pdf')])
