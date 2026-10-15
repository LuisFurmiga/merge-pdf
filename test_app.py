import tempfile
import unittest
from pathlib import Path
import tkinter as tk
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
