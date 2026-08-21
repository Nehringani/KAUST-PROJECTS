# Como Executar o PromptShield — Guia Completo (Português)

Este guia é para alguém que **nunca executou** um projeto Python. Lê do início ao fim, na ordem. Tudo o que precisas é **gratuito**.

---

## 1. Objetivo do projeto (em uma frase)

Construir um classificador (baseado em RoBERTa) que analisa um texto e diz **"isto é uma tentativa de injeção de prompt?"** antes desse texto ser enviado a um LLM usado num centro de operações de segurança (SOC).

## 2. Ferramentas que precisas instalar (todas gratuitas)

| Ferramenta | Para quê | Link | Custo |
|------------|----------|------|-------|
| **Python 3.10 ou superior** | Linguagem do projeto | https://www.python.org/downloads/ | Grátis |
| **Visual Studio Code** | Editor de código (IDE) | https://code.visualstudio.com/ | Grátis |
| **Extensão Python para VS Code** | Autocompletar, debug | Dentro do VS Code, aba Extensions → procurar "Python" (Microsoft) | Grátis |
| **Extensão Jupyter para VS Code** | Abrir os notebooks `.ipynb` | Dentro do VS Code, procurar "Jupyter" | Grátis |
| **Git** | Descarregar/enviar código | https://git-scm.com/downloads | Grátis |
| **Conta Google** | Usar o Google Colab (GPU grátis) | https://accounts.google.com/ | Grátis |
| **Google Colab** | Treinar o modelo com GPU T4 grátis | https://colab.research.google.com/ | Grátis |
| **Conta GitHub** (opcional) | Publicar o projeto | https://github.com/join | Grátis |
| **Conta OpenAI** (opcional) | Aumentar dataset com GPT-3.5 (~5 USD) | https://platform.openai.com/ | ~US$ 5–10 |

## 3. Instalação passo a passo

### 3.1. Instalar o Python
1. Vai a https://www.python.org/downloads/ e descarrega a versão **3.10 ou superior**.
2. No Windows, durante a instalação, **marca a caixa "Add Python to PATH"**.
3. Abre um terminal (Windows: `cmd` ou PowerShell; macOS/Linux: Terminal) e escreve:
   ```
   python --version
   ```
   Deves ver algo como `Python 3.11.x`.

### 3.2. Instalar o VS Code
1. Descarrega em https://code.visualstudio.com/ e instala.
2. Abre o VS Code → ícone de blocos à esquerda (Extensions) → instala:
   - **Python** (da Microsoft)
   - **Jupyter** (da Microsoft)

### 3.3. Descarregar o projeto
Duas opções:

**Opção A — Descompactar o ZIP:**
1. Descompacta `promptshield.zip` para uma pasta à tua escolha, por exemplo `C:\projetos\promptshield` (ou `~/projetos/promptshield`).

**Opção B — Git:**
```
git clone <url-do-teu-repo>.git promptshield
```

### 3.4. Abrir no VS Code
1. VS Code → **File → Open Folder…** → escolhe a pasta `promptshield`.
2. Abre o terminal integrado: **Terminal → New Terminal**.

### 3.5. Criar ambiente virtual e instalar dependências
No terminal integrado do VS Code, dentro da pasta do projeto:

**Windows:**
```
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

**macOS / Linux:**
```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Se o VS Code perguntar "We noticed a new virtual environment. Do you want to select it?" → clica **Yes**.

## 4. Ordem de execução do projeto

Segue esta ordem exata:

### Passo 1 — Gerar o dataset (rápido, roda no teu computador)
```
python -m src.data.preprocessor
```
Isto cria:
- `data/processed/cybersec_injections_v1.csv` (exemplos hand-crafted, semente)
- `data/processed/augmented_dataset.csv` (dataset final com paráfrases determinísticas)

Podes abrir os CSV no VS Code ou no Excel para inspeccionar.

### Passo 2 — Testar a camada de detecção (regras + heurísticas, sem GPU)
```
python -m src.detection.shield
```
Vê exemplos a serem classificados como injeção/limpo com o motor de regras. Isto **já funciona sem treinar o modelo**.

### Passo 3 — Treinar o classificador RoBERTa

**Opção A — No teu computador (só se tiveres GPU NVIDIA):** demora horas em CPU.
```
python -m src.models.trainer
```

**Opção B — Google Colab (RECOMENDADO, grátis, GPU T4):**
1. Vai a https://colab.research.google.com/
2. **File → Upload notebook** → seleciona `notebooks/03_classifier_training.ipynb`
3. **Runtime → Change runtime type → Hardware accelerator: T4 GPU → Save**
4. Faz upload da pasta `data/processed/` para o Colab (ícone de pasta à esquerda → botão upload) OU monta o Google Drive e coloca lá o CSV.
5. **Runtime → Run all**. O notebook instala tudo, treina e mostra as métricas.
6. Quando terminar, faz download da pasta `checkpoints/` e do `results/classification_report.json` de volta para o teu computador (mete-os em `results/`).

### Passo 4 — Avaliar
```
python -m src.evaluation.metrics
```
Isto lê o `results/classification_report.json` e imprime F1, FNR, FPR, latência p50/p95/p99 e a matriz de confusão. A imagem é guardada em `results/confusion_matrix.png`.

## 5. Estrutura recomendada de trabalho

1. Lê `data/taxonomy/injection_taxonomy_v1.md` antes de qualquer coisa — é a **contribuição intelectual central**.
2. Corre `preprocessor.py` para veres o dataset a existir.
3. Explora `notebooks/01_data_exploration.ipynb` no VS Code (basta abrir o ficheiro).
4. Vai para o Colab para o passo pesado de treino.
5. Volta ao VS Code para avaliação e para escrever o `RESEARCH_LOG.md` semanal.

## 6. Problemas comuns

| Problema | Solução |
|----------|---------|
| `python: command not found` | Usa `python3` (macOS/Linux) ou reinstala Python marcando "Add to PATH" (Windows). |
| `pip install` muito lento | Actualiza pip: `python -m pip install --upgrade pip`. |
| Falta de RAM ao treinar localmente | Usa Google Colab — é para isso que serve. |
| Colab desliga sozinho | Free tier: máximo ~12h. Guarda checkpoints no Google Drive. |
| Erro CUDA no Colab | Runtime → Change runtime type → confirma que está T4 GPU. |

## 7. Custos

- Tudo até aqui: **US$ 0**.
- Passo opcional de *augmentation* com API da OpenAI (GPT-3.5): **~US$ 5–10** para gerar 700+ paráfrases. O `preprocessor.py` deste repo faz augmentation **determinística offline** (grátis) por defeito; a variante com OpenAI é opcional e está marcada como `# OPTIONAL` no código.

## 8. Próximos passos depois de treinar

1. Preenche a secção "Results" no `README.md` com os teus números.
2. Actualiza o `RESEARCH_LOG.md` a cada semana.
3. Commit e push para o GitHub.
4. Usa os "Resume Bullets" no fundo do `README.md` para candidaturas.

Boa sorte com o VSRP.
