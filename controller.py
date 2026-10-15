from model import PDFMergerModel

class PDFMergerController:
    def __init__(self, view):
        self.view = view

    def select_files(self):
        files = self.view.ask_open_files()
        if files:
            self.add_files(files)

    def add_files(self, files):
        valid = [path for path in files if PDFMergerModel.is_valid_pdf(path)]
        if valid:
            self.view.add_files(valid)
        rejected = len(files) - len(valid)
        if rejected:
            self.view.status.set(
                f'{rejected} arquivo(s) ignorado(s). Apenas PDFs válidos, com páginas e sem senha são aceitos.'
            )
        return bool(valid)

    def remove_selected(self):
        self.view.remove_selected_files()

    def move_selected(self, direction):
        self.view.move_selected_files(direction)

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
            self.view.clear_files()

        except Exception as e:
            self.view.show_error("Erro", str(e))
