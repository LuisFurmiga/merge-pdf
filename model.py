import os
import tempfile
from PyPDF2 import PdfMerger, PdfReader

class PDFMergerModel:
    @staticmethod
    def is_valid_pdf(path):
        if os.path.splitext(path)[1].lower() != '.pdf' or not os.path.isfile(path):
            return False
        try:
            with open(path, 'rb') as stream:
                reader = PdfReader(stream)
                return not reader.is_encrypted and len(reader.pages) > 0
        except Exception:
            return False

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

        output_path = os.path.abspath(output_path)
        if any(os.path.normcase(os.path.realpath(pdf)) == os.path.normcase(os.path.realpath(output_path)) for pdf in pdf_list):
            raise ValueError("Escolha um arquivo de saída diferente dos PDFs de origem.")
        merger = PdfMerger()
        temporary_path = None
        try:
            for pdf in pdf_list:
                merger.append(pdf)
            with tempfile.NamedTemporaryFile(dir=os.path.dirname(output_path), suffix=".pdf", delete=False) as temporary:
                temporary_path = temporary.name
                merger.write(temporary)
            merger.close()
            os.replace(temporary_path, output_path)
        except Exception as e:
            raise Exception(f"Erro ao mesclar PDFs: {e}") from e
        finally:
            merger.close()
            if temporary_path and os.path.exists(temporary_path):
                os.remove(temporary_path)
