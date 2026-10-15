import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import COPY, DND_FILES, REFUSE_DROP, TkinterDnD


class PDFMergerView:
    def __init__(self, root=None):
        self.controller = None
        self.files = []
        self.root = root if root else TkinterDnD.Tk()
        if root is not None:
            TkinterDnD._require(self.root)
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
        self._drag = None
        self._drag_scroll_job = None
        self._external_drag = False
        self._drop_animation_job = None
        self._drop_leave_job = None
        self._drop_phase = 0
        self._drop_indicator = tk.Frame(self.listbox, background='#2457c5', height=3)
        self._drop_overlay = tk.Canvas(self.listbox, background='#edf4ff',
                                       highlightthickness=0, borderwidth=0, cursor='plus')
        self._drop_overlay.bind('<Configure>', lambda event: self._draw_drop_overlay())
        self.listbox.bind('<Destroy>', self._drop_destroy, add='+')
        self.listbox.bind('<ButtonPress-1>', self._drag_start)
        self.listbox.bind('<B1-Motion>', self._drag_motion)
        self.listbox.bind('<ButtonRelease-1>', self._drag_release)
        self.listbox.bind('<Escape>', self._drag_cancel)
        for target in (self.listbox, self._drop_overlay):
            target.drop_target_register(DND_FILES)
            target.dnd_bind('<<DropEnter>>', self._external_drag_enter)
            target.dnd_bind('<<DropPosition>>', self._external_drag_enter)
            target.dnd_bind('<<DropLeave>>', self._schedule_external_leave)
            target.dnd_bind('<<Drop:DND_Files>>', self._external_drop)
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
        self.help_label = ttk.Label(main, text='Solte PDFs do Explorador nesta lista para adicioná-los ao final. Arraste itens da lista para reordenar; Ctrl seleciona vários.', wraplength=500)
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
        self._drag_cancel()
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

    def _drag_start(self, event):
        if self._external_drag:
            return 'break'
        self._drag_cancel()
        item = self.listbox.identify_row(event.y)
        # Preserve the Treeview's native Ctrl/Shift selection behavior.
        if not item or event.state & 0x0005:
            return
        if item not in self.listbox.selection():
            self.listbox.selection_set(item)
        self.listbox.focus(item)
        self.listbox.focus_set()
        self._drag = dict(item=item, selected=self._selected_indices(),
                          x=event.x, y=event.y, active=False, slot=None)
        return 'break'

    def _drag_motion(self, event):
        if self._external_drag:
            return 'break'
        if self._drag is None:
            return
        drag = self._drag
        if not drag['active'] and max(abs(event.x - drag['x']), abs(event.y - drag['y'])) < 5:
            return 'break'
        drag['active'] = True
        drag['pointer'] = (event.x, event.y)
        self.listbox.configure(cursor='fleur')
        self._drag_target(event.x, event.y)
        if self._drag_scroll_job is None:
            self._drag_scroll_job = self.root.after(100, self._drag_scroll)
        return 'break'

    def _drag_target(self, x, y):
        self._drag['slot'] = None
        self._drop_indicator.place_forget()
        if not (0 <= x < self.listbox.winfo_width() and 0 <= y < self.listbox.winfo_height()):
            return
        if self.listbox.identify_region(x, y) == 'heading':
            return
        item = self.listbox.identify_row(y)
        if item:
            _, top, _, height = self.listbox.bbox(item)
            after = y >= top + height / 2
            slot = int(item) + int(after)
            line_y = top + height if after else top
        else:
            # Empty space below the rows is a drop at the end.
            visible = [self.listbox.bbox(item) for item in self.listbox.get_children()]
            visible = [box for box in visible if box]
            if not visible or y < visible[-1][1] + visible[-1][3]:
                return
            slot = len(self.files)
            line_y = visible[-1][1] + visible[-1][3]
        self._drag['slot'] = slot
        self._drop_indicator.place(x=0, y=min(line_y, self.listbox.winfo_height() - 3), relwidth=1)
        self._drop_indicator.lift()

    def _drag_scroll(self):
        self._drag_scroll_job = None
        if self._drag is None or not self._drag['active']:
            return
        x, y = self._drag['pointer']
        if 0 <= x < self.listbox.winfo_width():
            if y < 45:
                self.listbox.yview_scroll(-1, 'units')
            elif y > self.listbox.winfo_height() - 28:
                self.listbox.yview_scroll(1, 'units')
        self._drag_target(x, y)
        self._drag_scroll_job = self.root.after(100, self._drag_scroll)

    def _drag_release(self, event):
        if self._external_drag:
            return 'break'
        if self._drag is None:
            return
        drag = self._drag
        if drag['active']:
            self._drag_target(event.x, event.y)
            slot = drag['slot']
            if slot is not None:
                selected = drag['selected']
                chosen = set(selected)
                moved = [self.files[index] for index in selected]
                remaining = [path for index, path in enumerate(self.files) if index not in chosen]
                target = slot - sum(index < slot for index in selected)
                reordered = remaining[:target] + moved + remaining[target:]
                if reordered != self.files:
                    self.files[:] = reordered
                    self._refresh(list(range(target, target + len(moved))))
                    self.status.set('Ordem atualizada. O PDF final seguirá esta sequência.')
        else:
            self.listbox.selection_set(drag['item'])
        self._drag_cancel()
        return 'break'

    def _drag_cancel(self, event=None):
        if self._drag_scroll_job is not None:
            self.root.after_cancel(self._drag_scroll_job)
            self._drag_scroll_job = None
        self._drag = None
        self._drop_indicator.place_forget()
        self.listbox.configure(cursor='')
        if event is not None:
            return 'break'

    def _external_drag_enter(self, event):
        if self._drop_leave_job is not None:
            self.root.after_cancel(self._drop_leave_job)
            self._drop_leave_job = None
        entering = not self._external_drag
        self._external_drag = True
        self._drag_cancel()
        self.listbox.configure(cursor='plus')
        if entering:
            self._drop_overlay.place(x=0, y=0, relwidth=1, relheight=1)
            self._drop_overlay.tk.call('raise', self._drop_overlay._w)
            self._animate_drop_overlay()
        return COPY

    def _draw_drop_overlay(self):
        canvas = self._drop_overlay
        width, height = canvas.winfo_width(), canvas.winfo_height()
        canvas.delete('all')
        if width < 24 or height < 24:
            return
        blue = '#2457c5'
        pulse = (math.sin(self._drop_phase / 5) + 1) / 2
        canvas.create_rectangle(8, 8, width - 9, height - 9,
                                outline=blue, width=2, dash=(8, 6),
                                dashoffset=self._drop_phase % 14)
        center_x, center_y = width / 2, height / 2
        if height >= 210:
            icon_y = center_y - 58
            canvas.create_rectangle(center_x - 20, icon_y - 24, center_x + 20,
                                    icon_y + 24, outline=blue, width=2)
            canvas.create_text(center_x, icon_y, text='PDF', fill=blue,
                               font=('Segoe UI', 10, 'bold'))
        title = canvas.create_text(center_x, center_y - 3, text='Solte os PDFs aqui', fill=blue,
                                   font=('Segoe UI', 12, 'bold'), width=max(40, width - 48), justify='center')
        title_box = canvas.bbox(title)
        arrow_gap = (title_box[2] - title_box[0]) / 2 + 20 + 10 * pulse
        if width / 2 > arrow_gap + 48 and height >= 110:
            for direction in (-1, 1):
                tip = center_x + direction * arrow_gap
                canvas.create_line(tip + direction * 28, center_y - 3, tip, center_y - 3,
                                   arrow=tk.LAST, arrowshape=(10, 12, 5), fill=blue, width=3)
        if height >= 110:
            canvas.create_text(center_x, center_y + 33, text='Apenas PDFs • Adicionados ao final da lista',
                               fill='#42618c', font=('Segoe UI', 10),
                               width=max(40, width - 48), justify='center')

    def _animate_drop_overlay(self):
        self._drop_animation_job = None
        if not self._external_drag:
            return
        self._drop_phase += 1
        self._draw_drop_overlay()
        self._drop_animation_job = self.root.after(50, self._animate_drop_overlay)

    def _schedule_external_leave(self, event):
        # Moving between the list and its overlay generates Leave/Enter events.
        if self._drop_leave_job is not None:
            self.root.after_cancel(self._drop_leave_job)
        self._drop_leave_job = self.root.after(60, self._external_drag_leave)

    def _external_drag_leave(self, event=None):
        for job in (self._drop_animation_job, self._drop_leave_job):
            if job is not None:
                self.root.after_cancel(job)
        self._drop_animation_job = None
        self._drop_leave_job = None
        self._external_drag = False
        self._drop_overlay.place_forget()
        self.listbox.configure(cursor='')

    def _drop_destroy(self, event):
        if event.widget is self.listbox:
            for job in (self._drop_animation_job, self._drop_leave_job, self._drag_scroll_job):
                if job is not None:
                    self.root.after_cancel(job)

    def _external_drop(self, event):
        self._external_drag = True
        self._drag_cancel()
        try:
            paths = self.root.tk.splitlist(event.data)
            if self.controller and paths and self.controller.add_files(paths):
                return COPY
            return REFUSE_DROP
        except tk.TclError:
            self.status.set('Não foi possível ler os arquivos arrastados. Tente novamente.')
            return REFUSE_DROP
        finally:
            self._external_drag_leave()

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
