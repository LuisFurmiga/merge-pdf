import tempfile
import unittest
from pathlib import Path
import tkinter as tk
from types import SimpleNamespace
from tkinterdnd2 import COPY, REFUSE_DROP
from PyPDF2 import PdfReader, PdfWriter
from model import PDFMergerModel
from view import PDFMergerView
from controller import PDFMergerController


class OrderingTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.view = PDFMergerView(self.root)
        self.view.set_controller(PDFMergerController(self.view))
        self.view.add_files(['a.pdf', 'b.pdf', 'c.pdf', 'd.pdf', 'e.pdf'])

    def tearDown(self):
        self.root.destroy()

    def test_move_multiple_and_boundaries(self):
        self.view.listbox.selection_set(['1', '2'])
        self.view.controller.move_selected(-1)
        self.assertEqual(self.view.files, ['b.pdf', 'c.pdf', 'a.pdf', 'd.pdf', 'e.pdf'])
        self.assertEqual(self.view._selected_indices(), [0, 1])
        self.view.controller.move_selected(-1)
        self.assertEqual(self.view.files[:2], ['b.pdf', 'c.pdf'])
        self.view.controller.move_selected(1)
        self.assertEqual(self.view.files, ['a.pdf', 'b.pdf', 'c.pdf', 'd.pdf', 'e.pdf'])

    def test_nonadjacent_and_removal(self):
        self.view.listbox.selection_set(['1', '3'])
        self.view.controller.move_selected(1)
        self.assertEqual(self.view.files, ['a.pdf', 'c.pdf', 'b.pdf', 'e.pdf', 'd.pdf'])
        self.view.controller.remove_selected()
        self.assertEqual(self.view.files, ['a.pdf', 'c.pdf', 'e.pdf'])
        self.view.add_files(['a.pdf'])
        self.assertEqual(len(self.view.files), 3)
        self.view.clear_files()
        self.assertEqual(self.view.get_selected_files(), [])
        self.assertEqual(str(self.view.merge_button['state']), 'disabled')

    def _drag_rows(self, source, target, after=False, cancel=False):
        self.root.deiconify()
        self.root.update()
        tree = self.view.listbox
        tree.see(str(source))
        self.root.update()
        _, y, _, height = tree.bbox(str(source))
        tree.event_generate('<ButtonPress-1>', x=90, y=y + height // 2)
        tree.see(str(target))
        self.root.update()
        _, y, _, height = tree.bbox(str(target))
        destination = y + height - 2 if after else y + 2
        tree.event_generate('<B1-Motion>', x=90, y=destination)
        self.root.update()
        if cancel:
            tree.event_generate('<Escape>')
        tree.event_generate('<ButtonRelease-1>', x=90, y=destination)
        self.root.update()

    def test_drag_down_and_up(self):
        self.view.listbox.selection_set('0')
        self._drag_rows(0, 3, after=True)
        self.assertEqual(self.view.get_selected_files(), ['b.pdf', 'c.pdf', 'd.pdf', 'a.pdf', 'e.pdf'])
        self.assertEqual(self.view._selected_indices(), [3])
        self._drag_rows(3, 0)
        self.assertEqual(self.view.files, ['a.pdf', 'b.pdf', 'c.pdf', 'd.pdf', 'e.pdf'])
        self.assertIsNone(self.view._drag_scroll_job)

    def test_drag_group_and_cancel(self):
        self.view.listbox.selection_set(['1', '3'])
        self._drag_rows(1, 4, after=True)
        self.assertEqual(self.view.files, ['a.pdf', 'c.pdf', 'e.pdf', 'b.pdf', 'd.pdf'])
        self.assertEqual(self.view._selected_indices(), [3, 4])
        self._drag_rows(3, 0, cancel=True)
        self.assertEqual(self.view.files, ['a.pdf', 'c.pdf', 'e.pdf', 'b.pdf', 'd.pdf'])
        self.assertIsNone(self.view._drag)

    def test_drop_outside_keeps_order(self):
        self.root.deiconify()
        self.root.update()
        tree = self.view.listbox
        _, y, _, height = tree.bbox('0')
        tree.event_generate('<ButtonPress-1>', x=90, y=y + height // 2)
        tree.event_generate('<B1-Motion>', x=-10, y=100)
        tree.event_generate('<ButtonRelease-1>', x=-10, y=100)
        self.assertEqual(self.view.files, ['a.pdf', 'b.pdf', 'c.pdf', 'd.pdf', 'e.pdf'])
        self.assertIsNone(self.view._drag_scroll_job)

    def test_external_drop_appends_only_valid_pdfs_and_restores_internal_drag(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            pdf = folder / 'documento com espaços e acentos.PDF'
            second = folder / 'segundo.pdf'
            fake = folder / 'falso.pdf'
            other = folder / 'texto.txt'
            pdf_directory = folder / 'pasta.pdf'
            pdf_directory.mkdir()
            fake.write_text('Isto não é um PDF', encoding='utf-8')
            other.write_text('Texto', encoding='utf-8')
            for path in (pdf, second):
                writer = PdfWriter()
                writer.add_blank_page(width=100, height=200)
                with path.open('wb') as stream:
                    writer.write(stream)
            paths = [str(path) for path in (pdf, other, fake, pdf_directory, second)]
            data = self.root.tk.call('list', *paths)
            event = SimpleNamespace(data=data)
            self.view._drag = dict(active=True)
            self.view._drag_scroll_job = self.root.after(1000, lambda: None)
            self.assertEqual(self.view._external_drag_enter(event), COPY)
            self.assertIsNone(self.view._drag)
            self.assertIsNone(self.view._drag_scroll_job)
            mouse = SimpleNamespace(x=90, y=50, state=0)
            self.assertEqual(self.view._drag_start(mouse), 'break')
            self.assertEqual(self.view._drag_motion(mouse), 'break')
            self.assertEqual(self.view._drag_release(mouse), 'break')
            self.assertEqual(self.view._external_drop(event), COPY)
            self.assertEqual(self.view.files, ['a.pdf', 'b.pdf', 'c.pdf', 'd.pdf', 'e.pdf', str(pdf), str(second)])
            self.assertFalse(self.view._external_drag)
            self.assertIn('3 arquivo(s) ignorado(s)', self.view.status.get())
            self.view._external_drop(event)
            self.assertEqual(len(self.view.files), 7)
            # Internal reordering works again after the external drop.
            self.view.listbox.selection_set('0')
            self._drag_rows(0, 1, after=True)
            self.assertEqual(self.view.files[:2], ['b.pdf', 'a.pdf'])

    def test_rejected_external_drop_and_leave_do_not_change_list(self):
        before = self.view.get_selected_files()
        event = SimpleNamespace(data=self.root.tk.call('list', 'inexistente.pdf', 'foto.png'))
        self.view._external_drag_enter(event)
        self.assertEqual(self.view._external_drop(event), REFUSE_DROP)
        self.assertEqual(self.view.files, before)
        self.assertFalse(self.view._external_drag)
        self.view._external_drag_enter(event)
        self.view._external_drag_leave(event)
        self.assertFalse(self.view._external_drag)

    def test_external_hover_animation_and_cleanup(self):
        self.root.deiconify()
        self.root.update()
        event = SimpleNamespace(data='')
        self.view._external_drag_enter(event)
        self.root.update()
        canvas = self.view._drop_overlay
        self.assertTrue(canvas.winfo_ismapped())
        self.assertEqual(canvas.winfo_width(), self.view.listbox.winfo_width())
        self.assertTrue(canvas.find_all())
        phase = self.view._drop_phase
        animation = self.view._drop_animation_job
        self.view._external_drag_enter(event)
        self.assertEqual(self.view._drop_animation_job, animation)
        self.view._schedule_external_leave(event)
        self.view._external_drag_enter(event)
        self.assertIsNone(self.view._drop_leave_job)
        self.root.after(160, self.root.quit)
        self.root.mainloop()
        self.assertGreater(self.view._drop_phase, phase)
        self.view._external_drag_leave()
        self.root.update()
        self.assertFalse(canvas.winfo_ismapped())
        self.assertIsNone(self.view._drop_animation_job)
        self.assertFalse(self.view._external_drag)


class LayoutTests(unittest.TestCase):
    def test_controls_fit_at_different_sizes_and_display_scales(self):
        for scaling in (1.0, 1.25, 1.67, 2.0):
            root = tk.Tk()
            root.withdraw()
            try:
                root.tk.call('tk', 'scaling', scaling)
                view = PDFMergerView(root)
                root.deiconify()
                root.update()
                minimum_width, minimum_height = root.minsize()
                for width, height in ((minimum_width, minimum_height), (860, 560), (1072, 700)):
                    with self.subTest(scaling=scaling, size=(width, height)):
                        root.geometry(f'{width}x{height}')
                        root.update()
                        for widget in (view.select_button, view.up_button, view.down_button,
                                       view.remove_button, view.merge_button, view.help_label):
                            self.assertTrue(widget.winfo_ismapped())
                            right = widget.winfo_rootx() - root.winfo_rootx() + widget.winfo_width()
                            bottom = widget.winfo_rooty() - root.winfo_rooty() + widget.winfo_height()
                            self.assertLessEqual(right, root.winfo_width())
                            self.assertLessEqual(bottom, root.winfo_height())
                            self.assertGreaterEqual(widget.winfo_height(), widget.winfo_reqheight())
            finally:
                root.destroy()


class MergeTests(unittest.TestCase):
    def test_output_order_and_safe_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for width in (100, 200, 300):
                path = Path(directory) / f'{width}.pdf'
                writer = PdfWriter()
                writer.add_blank_page(width=width, height=400)
                with path.open('wb') as stream:
                    writer.write(stream)
                paths.append(str(path))
            output = Path(directory) / 'merged.pdf'
            PDFMergerModel.merge_pdfs(paths[::-1], str(output))
            self.assertEqual([int(page.mediabox.width) for page in PdfReader(output).pages], [300, 200, 100])
            original = output.read_bytes()
            with self.assertRaises(Exception):
                PDFMergerModel.merge_pdfs([str(Path(directory) / 'missing.pdf')], str(output))
            self.assertEqual(output.read_bytes(), original)
            with self.assertRaises(ValueError):
                PDFMergerModel.merge_pdfs(paths, paths[0])
            with self.assertRaises(ValueError):
                PDFMergerModel.merge_pdfs([], str(output))


if __name__ == '__main__':
    unittest.main()
