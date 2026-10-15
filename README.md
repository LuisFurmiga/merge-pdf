
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

## Como Executar

1. Clone ou faça o download deste repositório.
2. Navegue até o diretório do projeto:
   ```sh
   cd merge-pdf
   ```
3. Antes de executar, certifique-se de ter o Python instalado e instale as bibliotecas necessárias:
   ```sh
   python requirements.py
   ```
4. Execute o arquivo principal:
   ```sh
   python main.py
   ```

---

## Uso

1. Clique em **Adicionar PDFs** ou arraste arquivos do Explorador para a lista. Apenas PDFs válidos são aceitos; outros formatos, pastas e PDFs ilegíveis ou protegidos por senha são ignorados. Os arquivos recebidos por arraste são sempre adicionados ao final, sem alterar a ordem dos anteriores. Durante esse arraste externo, a reorganização interna fica suspensa e volta a funcionar ao soltar ou sair da lista.
2. Arraste um PDF para a posição desejada: a linha azul indica onde ele será inserido. Para mover vários juntos, selecione-os com Ctrl ou Shift, solte a tecla e arraste um dos selecionados. A lista rola automaticamente ao arrastar próximo às bordas; Esc cancela o arraste. Você também pode usar **Subir** e **Descer**, ou **Alt + ↑/↓**. A coluna **Ordem** mostra a sequência do PDF final. Use **Remover** ou **Delete** para retirar arquivos da lista.
3. Clique em **Mesclar PDFs** e salve o arquivo mesclado no local desejado.
4. A lista de arquivos será limpa automaticamente após o merge.

Arquivos repetidos são ignorados. O aplicativo impede salvar sobre um dos PDFs de origem e mantém a lista se você cancelar o salvamento ou ocorrer um erro. O Tkinter acompanha as instalações padrão do Python para Windows; FFmpeg não é necessário.

---

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests para melhorias.
