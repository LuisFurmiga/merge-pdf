from model import PDFMergerModel
from tkinter import filedialog

class PDFMergerController:
    def __init__(self, view):
        self.view = view

    def select_files(self):
        files = self.view.ask_open_files()
        if files:
            self.view.add_files(files)

    def remove_selected(self):
        self.view.remove_selected_files()

    def merge_pdfs(self):
        pdf_list = self.view.get_selected_files()
        if not pdf_list:
            self.view.show_error("Erro", "Nenhum arquivo PDF selecionado para mesclar!")
            return

        output_file = self.view.ask_save_file()
        if not output_file:
            return

        try:
            PDFMergerModel.merge_pdfs(pdf_list, output_file)
            self.view.show_info("Sucesso", f"PDFs mesclados com sucesso!\nArquivo salvo em: {output_file}")
            
            # Limpar a lista de arquivos após o merge
            self.view.listbox.delete(0, 'end')

        except Exception as e:
            self.view.show_error("Erro", str(e))
