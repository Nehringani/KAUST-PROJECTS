# Como Executar o Projecto JailbreakMap (Passo a Passo)

Este guia é para quem **nunca programou antes**. Siga na ordem.
Todo o resto do projecto (código, comentários, dados) está em inglês, como pedido.

---

## 1. O que você vai instalar (tudo gratuito)

| Ferramenta | Para quê | Link oficial |
|---|---|---|
| **Python 3.10 ou superior** | Linguagem de programação | https://www.python.org/downloads/ |
| **Visual Studio Code (VS Code)** | Editor de código (IDE) | https://code.visualstudio.com/ |
| **Extensão Python para VS Code** | Faz o VS Code entender Python | Dentro do VS Code, aba *Extensions* → procure "Python" (Microsoft) |
| **Git** (opcional) | Baixar código de repositórios | https://git-scm.com/downloads |

> **Windows**: ao instalar o Python, marque a caixinha **“Add Python to PATH”**. Isto é obrigatório.
> **macOS / Linux**: Python já costuma vir instalado; confirme com `python3 --version`.

---

## 2. Baixar e abrir o projecto

1. Descompacte o ficheiro `JailbreakMap.zip` numa pasta à sua escolha (ex.: `Documentos/JailbreakMap`).
2. Abra o **VS Code**.
3. Vá em **File → Open Folder…** e selecione a pasta `JailbreakMap`.
4. No VS Code, abra o terminal integrado: menu **Terminal → New Terminal**.

Todos os comandos seguintes são executados nesse terminal.

---

## 3. Criar o ambiente virtual (isola as dependências)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Se aparecer `(.venv)` no início da linha do terminal, deu certo.

---

## 4. Instalar as bibliotecas Python

Ainda com o ambiente activo:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Isto pode demorar alguns minutos na primeira vez (baixa `sentence-transformers`, `scikit-learn`, etc.).

---

## 5. Executar o pipeline (modo demonstração)

O projecto já vem com um **gerador de dados sintético** para você conseguir executar tudo mesmo sem baixar os datasets reais.

```bash
python -m src.run_pipeline --synthetic
```

Você verá logs para cada etapa (Step 1 a Step 8). No final:

- Figuras: `outputs/figures/`
- Tabelas: `outputs/tables/`
- Dataset limpo: `data/processed/jailbreakmap_dataset.csv`
- Relatório de conclusões: `outputs/tables/summary_findings.md`

Abra qualquer imagem `.png` no VS Code (basta um duplo-clique) para visualizar.

---

## 6. Usar dados reais (opcional, recomendado)

1. Baixe o CSV do **JailbreakHub**: https://github.com/verazuo/jailbreak_llms
   Procure por um ficheiro do tipo `jailbreak_prompts_*.csv`.
2. Coloque-o em `data/raw/jailbreakhub.csv`.
3. Opcional: coloque também `data/raw/wildjailbreak.csv` e `data/raw/harmbench.csv`.
4. Execute:
```bash
python -m src.run_pipeline
```

O pipeline detecta automaticamente quais ficheiros existem e junta o que encontrar. Se nada for encontrado, ele cai no modo sintético.

---

## 7. Rodar os testes (verificação)

```bash
pytest -q
```

Se todos os testes passarem, o ambiente está funcional.

---

## 8. Problemas comuns

| Problema | Solução |
|---|---|
| `python não é reconhecido` (Windows) | Reinstale Python marcando **Add to PATH**. |
| `ModuleNotFoundError: sentence_transformers` | Você esqueceu `pip install -r requirements.txt` **com o venv activo**. |
| Download do modelo `all-MiniLM-L6-v2` muito lento | Normal na 1ª vez (~90 MB). Depois fica em cache. |
| Figuras não aparecem | Elas são salvas em disco, não em janela. Abra `outputs/figures/`. |

---

## 9. Estrutura para entrega

Zipar novamente a pasta (com `outputs/` preenchido) já dá um pacote pronto para submissão académica. O ficheiro `outputs/tables/summary_findings.md` contém as conclusões que alimentam directamente os *resume bullets* do projecto.

Bom trabalho! 🚀
