from view import PDFMergerView # type: ignore
from controller import PDFMergerController # type: ignore

def main():
    # Inicializa a View sem controller
    view = PDFMergerView()

    # Cria o Controller e o vincula à View
    controller = PDFMergerController(view)
    view.set_controller(controller)  # Configura o controller na View

    # Executa a interface gráfica
    view.run()

if __name__ == "__main__":
    main()
