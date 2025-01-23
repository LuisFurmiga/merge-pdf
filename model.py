from PyPDF2 import PdfMerger # type: ignore

class PDFMergerModel:
    @staticmethod
    def merge_pdfs(pdf_list, output_path):
        """
        Mescla os PDFs fornecidos e salva no caminho especificado.
        
        Args:
            pdf_list (list): Lista com os caminhos dos PDFs.
            output_path (str): Caminho do arquivo final mesclado.
        
        Raises:
            Exception: Caso ocorra algum erro durante o processo.
        """
        if not pdf_list:
            raise ValueError("Nenhum arquivo PDF fornecido para mesclar.")

        try:
            merger = PdfMerger()
            for pdf in pdf_list:
                merger.append(pdf)
            merger.write(output_path)
            merger.close()
        except Exception as e:
            raise Exception(f"Erro ao mesclar PDFs: {e}")
