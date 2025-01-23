
# PDF Merge

## Descrição
Este projeto é uma aplicação Python com interface gráfica para mesclar arquivos PDF. A interface permite que os usuários:
- Selecionem arquivos PDF.
- Organizem a ordem dos arquivos para o merge.
- Salvem o PDF mesclado no local desejado.
- Limpem a lista automaticamente após o merge.

O código segue o padrão MVC (Model-View-Controller) para garantir uma estrutura organizada e escalável.

---

## Funcionalidades
- Seleção de múltiplos arquivos PDF.
- Reorganização e remoção de arquivos selecionados.
- Salvamento do PDF final em um local definido pelo usuário.
- Interface gráfica intuitiva com `tkinter`.

---

## Estrutura de Arquivos
O projeto está dividido em quatro arquivos principais:

```
merge-pdf/
├── controller.py  # Gerencia as interações entre View e Model
├── model.py       # Contém a lógica de merge de PDFs
├── view.py        # Define a interface gráfica
└── main.py        # Ponto de entrada do aplicativo
```

---

## Requisitos

Antes de executar o projeto, certifique-se de ter o Python instalado e instale a biblioteca necessária:

```sh
pip install PyPDF2
```

---

## Como Executar

1. Clone ou faça o download deste repositório.
2. Navegue até o diretório do projeto:
   ```sh
   cd merge-pdf
   ```
3. Execute o arquivo principal:
   ```sh
   python main.py
   ```

---

## Uso

1. Clique em **Selecionar PDFs** e escolha os arquivos que deseja mesclar.
2. Organize a ordem dos arquivos ou remova aqueles que não deseja incluir.
3. Clique em **Mesclar PDFs** e salve o arquivo mesclado no local desejado.
4. A lista de arquivos será limpa automaticamente após o merge.

---

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests para melhorias.
