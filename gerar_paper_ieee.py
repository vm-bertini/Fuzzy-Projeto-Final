"""
Gerador de paper no estilo IEEE — Projeto ANFIS / Heart Failure
Usa reportlab (platypus + frames) para layout de 2 colunas.
"""
import os
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, KeepTogether,
    NextPageTemplate, PageBreak,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfgen.canvas import Canvas

# ---------------------------------------------------------------------------
# Medidas
# ---------------------------------------------------------------------------
PW, PH     = LETTER                        # 612 x 792 pt
ML         = 0.70 * inch                  # margem esquerda
MR         = 0.70 * inch                  # margem direita
MT         = 0.75 * inch                  # margem topo
MB         = 1.00 * inch                  # margem base
GUTTER     = 0.20 * inch                  # espaço entre colunas
BODY_W     = PW - ML - MR                 # largura total do corpo
COL_W      = (BODY_W - GUTTER) / 2       # largura de cada coluna
BODY_H     = PH - MT - MB
HEADER_H   = 2.85 * inch                  # altura do bloco título/abstract (pag 1)

RES = os.path.join('src', 'results', '2026_06_23_03_55')

# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------
def make_styles():
    base = dict(fontName='Times-Roman', leading=12)
    bold = dict(fontName='Times-Bold',  leading=12)
    S    = {}

    S['title'] = ParagraphStyle('title',
        fontName='Times-Bold', fontSize=16, leading=20,
        alignment=TA_CENTER, spaceAfter=4)

    S['authors'] = ParagraphStyle('authors',
        fontName='Times-Bold', fontSize=10, leading=13,
        alignment=TA_CENTER, spaceAfter=2)

    S['affil'] = ParagraphStyle('affil',
        fontName='Times-Italic', fontSize=9, leading=11,
        alignment=TA_CENTER, spaceAfter=6)

    S['abstract_label'] = ParagraphStyle('abstract_label',
        fontName='Times-Bold', fontSize=9, leading=11,
        alignment=TA_JUSTIFY)

    S['abstract'] = ParagraphStyle('abstract',
        fontName='Times-Roman', fontSize=9, leading=11,
        alignment=TA_JUSTIFY, spaceAfter=4)

    S['keywords'] = ParagraphStyle('keywords',
        fontName='Times-Roman', fontSize=9, leading=11,
        alignment=TA_JUSTIFY, spaceAfter=6)

    S['body'] = ParagraphStyle('body',
        fontName='Times-Roman', fontSize=10, leading=13,
        alignment=TA_JUSTIFY, spaceAfter=4)

    S['section'] = ParagraphStyle('section',
        fontName='Times-Bold', fontSize=10, leading=13,
        alignment=TA_CENTER, spaceBefore=8, spaceAfter=4)

    S['subsection'] = ParagraphStyle('subsection',
        fontName='Times-Italic', fontSize=10, leading=13,
        alignment=TA_LEFT, spaceBefore=5, spaceAfter=3)

    S['caption'] = ParagraphStyle('caption',
        fontName='Times-Roman', fontSize=8, leading=10,
        alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)

    S['caption_bold'] = ParagraphStyle('caption_bold',
        fontName='Times-Bold', fontSize=8, leading=10,
        alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)

    S['table_header'] = ParagraphStyle('table_header',
        fontName='Times-Bold', fontSize=9, leading=11,
        alignment=TA_CENTER)

    S['table_body'] = ParagraphStyle('table_body',
        fontName='Times-Roman', fontSize=9, leading=11,
        alignment=TA_CENTER)

    S['math'] = ParagraphStyle('math',
        fontName='Times-Italic', fontSize=10, leading=14,
        alignment=TA_CENTER, spaceBefore=4, spaceAfter=4)

    return S

S = make_styles()

def p(text, style='body'):
    return Paragraph(text, S[style])

def sp(h=4):
    return Spacer(1, h)

def hr():
    return HRFlowable(width='100%', thickness=0.5,
                      color=colors.black, spaceAfter=4, spaceBefore=4)

def section(num, title):
    return p(f'{num}. {title.upper()}', 'section')

def subsec(letter, title):
    return p(f'<i>{letter}. {title}</i>', 'subsection')

def fig(path, width, caption, label):
    if not os.path.exists(path):
        return [p(f'[Figura: {caption}]', 'caption')]
    ar   = __import__('PIL.Image', fromlist=['Image']).open(path)
    h    = width * ar.size[1] / ar.size[0]
    elem = Image(path, width=width, height=h)
    cap  = p(f'<b>Fig. {label}.</b> {caption}', 'caption')
    return [elem, cap]

# ---------------------------------------------------------------------------
# Número de página
# ---------------------------------------------------------------------------
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 8)
    canvas.drawCentredString(PW / 2, 0.5 * inch,
                             str(doc.page))
    canvas.restoreState()

# ---------------------------------------------------------------------------
# Document / Frames
# ---------------------------------------------------------------------------
doc = BaseDocTemplate(
    'paper_ieee.pdf',
    pagesize=LETTER,
    leftMargin=ML, rightMargin=MR,
    topMargin=MT, bottomMargin=MB,
    showBoundary=False,
)

# Página 1: frame de cabeçalho (título + abstract) + 2 colunas abaixo
header_frame = Frame(ML, PH - MT - HEADER_H,
                     BODY_W, HEADER_H,
                     id='header', showBoundary=False, topPadding=0)

col1_p1 = Frame(ML,                    MB,
                COL_W, BODY_H - HEADER_H,
                id='col1', showBoundary=False, topPadding=0)
col2_p1 = Frame(ML + COL_W + GUTTER,   MB,
                COL_W, BODY_H - HEADER_H,
                id='col2', showBoundary=False, topPadding=0)

# Páginas seguintes: 2 colunas plenas
col1_pn = Frame(ML,                   MB, COL_W, BODY_H,
                id='col1', showBoundary=False, topPadding=0)
col2_pn = Frame(ML + COL_W + GUTTER, MB, COL_W, BODY_H,
                id='col2', showBoundary=False, topPadding=0)

tpl_p1 = PageTemplate('first',  [header_frame, col1_p1, col2_p1], onPage=on_page)
tpl_pn = PageTemplate('later',  [col1_pn, col2_pn],               onPage=on_page)
doc.addPageTemplates([tpl_p1, tpl_pn])

# ---------------------------------------------------------------------------
# Conteúdo
# ---------------------------------------------------------------------------
story = []

# ---- Título / Autores / Abstract ------------------------------------------
story += [
    p('Sistemas Neuro-Fuzzy para Classificação de Risco Cardíaco: '
      'Comparação entre ANFIS e MLP com Foco em Interpretabilidade', 'title'),
    sp(2),
    p('Victor M. Bertini', 'authors'),
    p('Faculdade de Engenharia Elétrica e de Computação (FEEC) — Universidade Estadual de Campinas (Unicamp)<br/>'
      'Campinas, SP, Brasil — RA: 194761 — victor.m.bertini@gmail.com', 'affil'),
    sp(4),
    hr(),
]

abstract_text = (
    '<b>Abstract</b>—Este trabalho investiga o tradeoff entre acurácia preditiva e '
    'interpretabilidade em modelos de aprendizado de máquina aplicados a classificação '
    'de risco de doença cardíaca. Propomos e avaliamos um sistema ANFIS (Adaptive '
    'Neuro-Fuzzy Inference System) de Takagi-Sugeno com fuzzificação mista—funções '
    'Gaussianas para variáveis numéricas e codificação one-hot suavizada para '
    'variáveis categóricas—cujo pool de regras é gerado por agrupamento K-Means. '
    'Os experimentos no Heart Failure Prediction Dataset (918 pacientes, 11 features) '
    'mostram que o ANFIS atinge AUC-ROC de 0,912, acurácia de 84,2% e F1-Score de 85,9%, '
    'superando o MLP baseline (AUC 0,901; acurácia 81,5%; F1 82,5%) com apenas 228 '
    'parâmetros treináveis frente a 2.881 do MLP. Além do desempenho superior, '
    'o ANFIS produz 10 regras linguísticas SE-ENTÃO auditáveis, revelando padrões '
    'clínicos alinhados à literatura médica sobre isquemia cardíaca.'
)
story += [
    p(abstract_text, 'abstract'),
    sp(3),
    p('<b>Keywords</b>—ANFIS; Lógica Fuzzy; Redes Neurais; Doença Cardíaca; '
      'Interpretabilidade; Takagi-Sugeno; K-Means', 'keywords'),
    hr(),
    sp(4),
]

# Transição para 2 colunas (já na p1 após o header_frame)
story.append(NextPageTemplate('later'))

# ---- I. INTRODUÇÃO ---------------------------------------------------------
story += [
    section('I', 'Introdução'),
    p('Sistemas de apoio a decisão clínica baseados em aprendizado de máquina atingem '
      'alta acurácia em tarefas de diagnóstico, porém frequentemente operam como '
      'caixas-pretas, fornecendo predições sem justificativa inteligível [1]. No '
      'contexto médico, a rastreabilidade das decisões é tanto um requisito ético '
      'quanto regulatório: um especialista precisa entender <i>por que</i> um paciente '
      'foi classificado como alto risco para validar ou contestar a recomendação.'),
    p('Sistemas Neuro-Fuzzy—em particular o ANFIS—combinam a capacidade de '
      'aprendizado de redes neurais com a interpretabilidade de sistemas de inferência '
      'fuzzy [2]. Regras linguísticas do tipo SE <i>antecedente</i> ENTÃO '
      '<i>consequente</i> permitem que clínicos e auditores inspecionem os critérios '
      'decisórios sem exigir expertise em aprendizado de máquina.'),
    p('Este trabalho apresenta: (i) uma arquitetura ANFIS com fuzzificação mista '
      'para lidar com features numéricas e categóricas no mesmo pipeline; '
      '(ii) um método de geração de pool de regras por K-Means que escala para '
      'datasets com múltiplas variáveis categóricas; e (iii) uma comparação '
      'quantitativa com MLP no Heart Failure Prediction Dataset [3], demonstrando '
      'que o ANFIS supera o MLP em todas as métricas com 13× menos parâmetros.'),
    sp(2),
]

# ---- II. DATASET -----------------------------------------------------------
story += [
    section('II', 'Dataset e Pré-Processamento'),
    subsec('A', 'Heart Failure Prediction Dataset'),
    p('O dataset combina registros de cinco fontes clínicas distintas, totalizando '
      '918 pacientes adultos. A variável alvo, <b>HeartDisease</b>, é binária '
      '(0 = saudável, 1 = doença cardiovascular), com prevalência de '
      'aproximadamente 55% de positivos. A divisão treino/teste segue a proporção '
      '80/20 com estratificação por classe.'),
    p('As 11 features compreendem 5 variáveis numéricas e 6 categóricas:'),
]

# Tabela de features
feat_data = [
    [p('Feature', 'table_header'),     p('Tipo', 'table_header'),      p('Descrição', 'table_header')],
    [p('Age', 'table_body'),           p('Numérica', 'table_body'),    p('Idade (anos)', 'table_body')],
    [p('RestingBP', 'table_body'),     p('Numérica', 'table_body'),    p('Pressão arterial em repouso (mmHg)', 'table_body')],
    [p('Cholesterol', 'table_body'),   p('Numérica', 'table_body'),    p('Colesterol sérico (mg/dL)', 'table_body')],
    [p('MaxHR', 'table_body'),         p('Numérica', 'table_body'),    p('Frequência cardíaca máxima (bpm)', 'table_body')],
    [p('Oldpeak', 'table_body'),       p('Numérica', 'table_body'),    p('Depressão do segmento ST (mm)', 'table_body')],
    [p('Sex', 'table_body'),           p('Categórica', 'table_body'),  p('M / F', 'table_body')],
    [p('ChestPainType', 'table_body'), p('Categórica', 'table_body'),  p('ATA / NAP / ASY / TA', 'table_body')],
    [p('FastingBS', 'table_body'),     p('Categórica', 'table_body'),  p('Glicemia em jejum > 120 mg/dL (0/1)', 'table_body')],
    [p('RestingECG', 'table_body'),    p('Categórica', 'table_body'),  p('Normal / ST / LVH', 'table_body')],
    [p('ExerciseAngina', 'table_body'),p('Categórica', 'table_body'),  p('Y / N', 'table_body')],
    [p('ST_Slope', 'table_body'),      p('Categórica', 'table_body'),  p('Up / Flat / Down', 'table_body')],
]

feat_table = Table(feat_data, colWidths=[COL_W*0.30, COL_W*0.25, COL_W*0.45])
feat_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E7D32')),
    ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F5F5F5'), colors.white]),
    ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#BBBBBB')),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ('LEFTPADDING', (0,0), (-1,-1), 3),
]))

story += [
    KeepTogether([feat_table, p('<b>TABELA I.</b> Features do dataset.', 'caption')]),
    sp(2),
]

story += [
    subsec('B', 'Pré-Processamento'),
    p('Valores zerados em <b>RestingBP</b> e <b>Cholesterol</b> (clinicamente impossíveis) '
      'são substituídos pela mediana das entradas não-nulas. Features categóricas '
      'são codificadas como inteiros via <i>pd.Categorical.codes</i>. A normalização '
      'é realizada pelo <b>PartialScaler</b>: z-score exclusivamente nas 5 features '
      'numéricas, preservando os códigos inteiros das categóricas. '
      'Esta distinção é fundamental para a <i>MixedFuzzyLayer</i>, que trata os '
      'dois grupos com mecanismos de fuzzificação distintos.'),
    sp(2),
]

# ---- III. ARQUITETURA ANFIS ------------------------------------------------
story += [
    section('III', 'Arquitetura ANFIS'),
    p('O modelo ANFIS proposto segue o paradigma Takagi-Sugeno de ordem zero e '
      'é composto por três camadas treináveis encadeadas. O fluxo de dados '
      'segue a sequência:'),
    p('<i>X</i> [B,11] → MixedFuzzyLayer → [B,11,M] → ClusterRuleLayer '
      '→ [B,R] → DefuzzyLayer → [B,1] → sigmoid → P(doença)', 'math'),
    p('onde B é o tamanho do batch, M o número de funções de pertinência por '
      'feature numérica, e R o número de regras no pool.'),
    sp(2),
    subsec('A', 'MixedFuzzyLayer'),
    p('Esta camada fuzzifica cada feature de acordo com seu tipo:'),
    p('<u>Features numéricas</u>: Funções de Pertinência (MFs) Gaussianas treináveis '
      'com parâmetros de centro c e variância σ:'),
    p('μ(x) = exp(−½ · ((x − c) / σ)²)', 'math'),
    p('Os parâmetros c e σ são otimizados por retropropagação. As variâncias são '
      'clampeadas em σ ≥ 10⁻⁶ para evitar instabilidade numérica e inicializadas '
      'com σ = |N(0,1)| + 0,1 para garantir positividade.'),
    p('<u>Features categóricas</u>: Codificação one-hot suavizada sem parâmetros '
      'treináveis:'),
    p('μ<sub>j</sub>(cat) = 0,95 se j=cat, senão 0,05/(n<sub>cats</sub>−1)', 'math'),
    p('Este esquema preserva a estrutura discreta da variável enquanto fornece '
      'um sinal de gradiente não-nulo para as demais posições, evitando o '
      'colapso de regras durante o treinamento.'),
    sp(2),
    subsec('B', 'ClusterRuleLayer'),
    p('Calcula a força de disparo de cada regra k por T-norma produto:'),
    p('w<sub>k</sub> = ∏<sub>i</sub> μ<sub>i, combo[k,i]</sub>(x<sub>i</sub>)', 'math'),
    p('onde <i>combo[k,i]</i> é o índice da MF da regra k na feature i. '
      'A tabela de combinações <i>rule_idx</i> é armazenada como <i>register_buffer</i>, '
      'garantindo migração automática para GPU. A camada não possui parâmetros '
      'treináveis: seu único papel é estrutural.'),
    sp(2),
    subsec('C', 'DefuzzyLayer'),
    p('Implementa defuzzificação Takagi-Sugeno normalizada:'),
    p('w̃<sub>k</sub> = w<sub>k</sub> / (Σ<sub>j</sub> w<sub>j</sub> + ε)', 'math'),
    p('ŷ = Σ<sub>k</sub> w̃<sub>k</sub> · c<sub>k</sub>', 'math'),
    p('Os consequentes c<sub>k</sub> são os pesos de uma <i>nn.Linear(R→1)</i> '
      'otimizada por retropropagação. A normalização garante que a saída permaneça '
      'na escala correta independentemente do número de regras que disparam '
      'simultaneamente, preservando a interpretação TS dos consequentes.'),
    sp(2),
    subsec('D', 'Função de Perda'),
    p('A função de perda combina entropia cruzada binária com uma penalidade de '
      'separação de centros de MFs:'),
    p('L = BCE(σ(ŷ), y) + λ · Σ<sub>i&lt;j</sub> relu(σ<sub>i</sub> + σ<sub>j</sub> − |c<sub>i</sub> − c<sub>j</sub>|)', 'math'),
    p('O termo de penalidade (λ=0,1) é zero quando os centros de MFs adjacentes '
      'estão afastados por pelo menos σ<sub>i</sub>+σ<sub>j</sub>, e cresce '
      'linearmente caso contrário. Isso evita que uma MF estreita fique '
      'inteiramente contida dentro de uma MF larga, o que tornaria a partição '
      'linguística incoerente.'),
    sp(2),
]

# ---- IV. GERAÇÃO DE REGRAS -------------------------------------------------
story += [
    section('IV', 'Geração do Pool de Regras via K-Means'),
    p('O número de combinações possíveis de antecedentes cresce exponencialmente '
      'com o número de features: n<sub>rules</sub> = M<sup>n<sub>inputs</sub></sup>. '
      'Para 11 features com M=3, isso resultaria em 177.147 regras—inviável. '
      'Para mitigar esta explosão combinatória, adotamos o seguinte pipeline '
      'de geração de regras antes do treinamento:'),
    p('<b>Passo 1 — Picos percentílicos</b> (artifício de mapeamento): Para cada '
      'feature numérica, calculamos n<sub>mfs</sub> percentis uniformemente '
      'espaçados da distribuição de treino (P25, P50, P75 para n<sub>mfs</sub>=3). '
      'Estes percentis servem como "picos" de MFs triangulares auxiliares para '
      'o mapeamento—não são as MFs Gaussianas do ANFIS.'),
    p('<b>Passo 2 — K-Means clustering</b>: Aplicamos K-Means com 200 clusters '
      'no espaço de features de treino, identificando as regiões de maior densidade.'),
    p('<b>Passo 3 — Mapeamento dominante</b>: Para cada centro de cluster, '
      'determinamos a MF dominante em cada feature: '
      'numérica → argmax da MF triangular nos picos; '
      'categórica → round(centro) → código inteiro.'),
    p('<b>Passo 4 — Deduplicação</b>: Clusters com o mesmo vetor de MFs '
      'dominantes são colapsados em uma única regra. Dos 200 clusters, '
      'resultaram 197 combinações únicas nesta execução.'),
    p('<b>Passo 5 — Inicialização</b>: Os centros Gaussianos do ANFIS são '
      'inicializados nos percentis dos centros K-Means por feature, '
      'fornecendo um ponto de partida informado para o treinamento end-to-end.'),
    sp(2),
]

# ---- V. SETUP EXPERIMENTAL -------------------------------------------------
story += [
    section('V', 'Configuração Experimental'),
    p('Os hiperparâmetros foram fixados conforme a Tabela II. Ambos os modelos '
      'são treinados com otimizador Adam, scheduler de learning rate por plateau '
      'e early stopping com paciência de 20 épocas.'),
]

hp_data = [
    [p('Parâmetro', 'table_header'), p('ANFIS', 'table_header'), p('MLP', 'table_header')],
    [p('Épocas', 'table_body'),      p('200', 'table_body'),     p('200', 'table_body')],
    [p('Batch size', 'table_body'),  p('32', 'table_body'),      p('32', 'table_body')],
    [p('Learning rate', 'table_body'), p('1×10⁻³', 'table_body'), p('1×10⁻³', 'table_body')],
    [p('Arquitetura', 'table_body'), p('3 MFs, 197 regras', 'table_body'), p('[64, 32]', 'table_body')],
    [p('Parâmetros', 'table_body'),  p('228', 'table_body'),     p('2.881', 'table_body')],
    [p('Regularização', 'table_body'), p('Sep. penalty λ=0,1', 'table_body'), p('—', 'table_body')],
    [p('Semente', 'table_body'),     p('42', 'table_body'),      p('42', 'table_body')],
]

hp_table = Table(hp_data, colWidths=[COL_W*0.40, COL_W*0.30, COL_W*0.30])
hp_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E7D32')),
    ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F5F5F5'), colors.white]),
    ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#BBBBBB')),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ('LEFTPADDING', (0,0), (-1,-1), 3),
]))
story += [
    KeepTogether([hp_table, p('<b>TABELA II.</b> Hiperparâmetros experimentais.', 'caption')]),
    sp(2),
]

story += [
    p('As métricas de avaliação são calculadas no conjunto de teste (20% dos dados): '
      'AUC-ROC (insensível ao limiar), acurácia (limiar 0,5) e F1-Score '
      '(média harmônica de precisão e revocação, preferível para classes '
      'desbalanceadas). A aleatoriedade é controlada pela semente 42 em numpy, '
      'torch e sklearn.'),
    sp(2),
]

# ---- VI. RESULTADOS --------------------------------------------------------
story += [
    section('VI', 'Resultados e Discussão'),
    subsec('A', 'Métricas de Desempenho'),
    p('A Tabela III apresenta os resultados quantitativos. O ANFIS supera o '
      'MLP em todas as três métricas, com destaque para a AUC-ROC (Δ=+0,011) '
      'e o F1-Score (Δ=+3,4 p.p.), indicando melhor capacidade de separação '
      'entre classes positiva e negativa.'),
]

res_data = [
    [p('Modelo',    'table_header'), p('Parâm.', 'table_header'),
     p('Treino (s)', 'table_header'), p('Acurácia', 'table_header'),
     p('F1-Score',  'table_header'), p('AUC-ROC', 'table_header')],
    [p('ANFIS',   'table_body'), p('228',   'table_body'),
     p('14,9',    'table_body'), p('84,2%', 'table_body'),
     p('85,9%',   'table_body'), p('<b>0,912</b>', 'table_body')],
    [p('MLP',     'table_body'), p('2.881', 'table_body'),
     p('4,8',     'table_body'), p('81,5%', 'table_body'),
     p('82,5%',   'table_body'), p('0,901', 'table_body')],
]

res_table = Table(res_data,
    colWidths=[COL_W*0.17, COL_W*0.14, COL_W*0.17, COL_W*0.17, COL_W*0.17, COL_W*0.18])
res_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E7D32')),
    ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
    ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#C8E6C9')),
    ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white]),
    ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#BBBBBB')),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ('LEFTPADDING', (0,0), (-1,-1), 2),
]))
story += [
    KeepTogether([res_table, p('<b>TABELA III.</b> Resultados comparativos (Heart Failure, split 80/20).', 'caption')]),
    sp(2),
]

story += [
    p('A eficiência paramétrica é notável: o ANFIS usa 13× menos parâmetros que o MLP '
      '(228 vs. 2.881), o que reduz o risco de overfitting e facilita inspeção e '
      'auditoria do modelo. O custo é um treinamento aproximadamente 3× mais lento '
      '(14,9 s vs. 4,8 s), aceitável em aplicações de diagnóstico offline.'),
    sp(2),
    subsec('B', 'Funções de Pertinência Aprendidas'),
    p('A Fig. 1 mostra as MFs Gaussianas após o treinamento para as 5 features '
      'numéricas, além das MFs triangulares de saída (fixas). Os centros '
      'aprendidos revelam limiares clinicamente coerentes: em <b>Age</b>, '
      'as três MFs separam jovens (~40 anos), meia-idade (~55 anos) e idosos (~65 anos); '
      'em <b>MaxHR</b>, a MF "baixa" concentra-se em ~120 bpm, abaixo da '
      'frequência esperada de resposta ao esforço. Em <b>Oldpeak</b>, '
      'a MF "elevado" captura depressões do segmento ST acima de ~1,5 mm, '
      'alinhado ao critério diagnóstico de isquemia.'),
]

story += fig(os.path.join(RES, 'mfs_anfis.png'), COL_W * 0.98,
             'Funções de Pertinência Gaussianas aprendidas pelo ANFIS após 200 épocas '
             '(features numéricas) e MFs triangulares de saída (hardcoded).', '1')

story += [
    sp(2),
    subsec('C', 'Matrizes de Confusão'),
]

story += fig(os.path.join(RES, 'confusion_matrix.png'), COL_W * 0.98,
             'Matrizes de confusão no conjunto de teste: ANFIS (esq.) e MLP (dir.).', '2')

story += [
    sp(2),
    p('O ANFIS apresenta 18 falsos negativos (FN) a menos que o MLP no conjunto '
      'de teste, o que em contexto clínico (risco de doença não detectada) '
      'representa uma vantagem diagnóstica significativa. A redução em FN '
      'contribui para o maior F1-Score observado.'),
    sp(2),
    subsec('D', 'Regras Linguísticas Extraídas'),
    p('As 10 regras com maior força de disparo média sobre o conjunto de treino '
      'são apresentadas na Tabela IV. Dois padrões emergem consistentemente:'),
    p('• <b>Alto risco</b>: ChestPainType=ASY (assintomático), MaxHR baixa, '
      'ExerciseAngina=Y, Oldpeak elevado, ST_Slope=Flat. '
      'Estes são marcadores estabelecidos de isquemia coronariana [4].'),
    p('• <b>Baixo risco</b>: ChestPainType=ATA (atípica), MaxHR alta, '
      'ExerciseAngina=N, Oldpeak normal, ST_Slope=Up. '
      'Compatível com resposta fisiológica normal ao esforço.'),
]

rules_data = [
    [p('#', 'table_header'), p('Antecedente (abrev.)', 'table_header'), p('Risco', 'table_header')],
    [p('1',  'table_body'), p('Age=jovem, CPT=ATA, MaxHR=alta, Ang=N, OP=normal, ST=Up', 'table_body'),   p('BAIXO', 'table_body')],
    [p('2',  'table_body'), p('Age=jovem, CPT=ASY, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat', 'table_body'), p('ALTO', 'table_body')],
    [p('3',  'table_body'), p('Age=idoso, CPT=ASY, ECG=ST, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat', 'table_body'), p('ALTO', 'table_body')],
    [p('4',  'table_body'), p('Age=jovem, CPT=ATA, RBP=elevado, MaxHR=baixa, Ang=N, OP=normal, ST=Up', 'table_body'), p('BAIXO', 'table_body')],
    [p('5',  'table_body'), p('Age=jovem, CPT=ATA, RBP=otimo, MaxHR=baixa, Ang=N, OP=normal, ST=Up', 'table_body'), p('BAIXO', 'table_body')],
    [p('6',  'table_body'), p('Age=jovem, Sex=F, CPT=ATA, MaxHR=baixa, Ang=N, OP=normal, ST=Up', 'table_body'), p('BAIXO', 'table_body')],
    [p('7',  'table_body'), p('Age=idoso, CPT=ASY, ECG=LVH, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat', 'table_body'), p('ALTO', 'table_body')],
    [p('8',  'table_body'), p('Age=jovem, CPT=NAP, MaxHR=alta, Ang=N, OP=normal, ST=Up', 'table_body'), p('BAIXO', 'table_body')],
    [p('9',  'table_body'), p('Age=jovem, CPT=ASY, FBS=1, MaxHR=baixa, Ang=N, OP=normal, ST=Flat', 'table_body'), p('ALTO', 'table_body')],
    [p('10', 'table_body'), p('Age=jovem, CPT=ASY, RBP=elevado, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat', 'table_body'), p('ALTO', 'table_body')],
]

rules_table = Table(rules_data, colWidths=[COL_W*0.07, COL_W*0.77, COL_W*0.16])
rules_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E7D32')),
    ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F5F5F5'), colors.white]),
    ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#BBBBBB')),
    ('TOPPADDING', (0,0), (-1,-1), 1),
    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ('LEFTPADDING', (0,0), (-1,-1), 3),
    # Highlight ALTO rows: R2=idx2, R3=idx3, R7=idx7, R9=idx9, R10=idx10
    ('BACKGROUND', (2,2),  (2,2),  colors.HexColor('#FFCDD2')),
    ('BACKGROUND', (2,3),  (2,3),  colors.HexColor('#FFCDD2')),
    ('BACKGROUND', (2,7),  (2,7),  colors.HexColor('#FFCDD2')),
    ('BACKGROUND', (2,9),  (2,9),  colors.HexColor('#FFCDD2')),
    ('BACKGROUND', (2,10), (2,10), colors.HexColor('#FFCDD2')),
]))
story += [
    KeepTogether([
        rules_table,
        p('<b>TABELA IV.</b> Top-10 regras ANFIS por força de disparo média. '
          'CPT=ChestPainType, RBP=RestingBP, Ang=ExerciseAngina, OP=Oldpeak, '
          'FBS=FastingBS.', 'caption'),
    ]),
    sp(2),
]

# ---- VII. CONCLUSÃO --------------------------------------------------------
story += [
    section('VII', 'Conclusão'),
    p('Este trabalho demonstrou que o ANFIS com fuzzificação mista e pool de '
      'regras gerado por K-Means é uma alternativa viável e superior ao MLP '
      'para classificação de risco cardíaco, atingindo AUC-ROC de 0,912 com '
      'apenas 228 parâmetros treináveis—13× menos que o MLP—e produzindo '
      '10 regras linguísticas auditáveis alinhadas à literatura clínica.'),
    p('A interpretabilidade genuína obtida—centros Gaussianos com significado '
      'físico, consequentes TS por regra, e regras SE-ENTÃO inteligíveis—'
      'diferencia o ANFIS de métodos post-hoc como SHAP, onde a explicação '
      'é gerada após o fato e não faz parte do processo decisório.'),
    p('<b>Limitações e trabalho futuro</b>: O modelo foi testado em um único '
      'dataset (n=918). Trabalhos futuros devem: (i) validar em datasets maiores '
      'e multi-classe; (ii) incorporar conhecimento de especialistas na '
      'inicialização das MFs; (iii) comparar com ANFIS clássico (Jang, 1993) '
      'e sistemas fuzzy Mamdani; e (iv) investigar métodos formais de '
      'definição de MFs para variáveis categóricas.'),
    sp(4),
]

# ---- REFERÊNCIAS -----------------------------------------------------------
story += [
    section('', 'Referências'),
    p('[1] A. Holzinger, G. Langs, H. Denk, K. Zatloukal, and H. Müller, '
      '"Causability and explainability of artificial intelligence in medicine," '
      '<i>WIREs Data Mining Knowl. Discov.</i>, vol. 9, no. 4, 2019.'),
    sp(2),
    p('[2] J.-S. R. Jang, "ANFIS: Adaptive-network-based fuzzy inference system," '
      '<i>IEEE Trans. Syst. Man Cybern.</i>, vol. 23, no. 3, pp. 665–685, 1993.'),
    sp(2),
    p('[3] F. Fedesoriano, "Heart Failure Prediction Dataset," Kaggle, 2021. '
      '[Online]. Available: https://www.kaggle.com/fedesoriano/heart-failure-prediction'),
    sp(2),
    p('[4] R. A. Gibbons et al., "ACC/AHA 2002 Guideline Update for Exercise '
      'Testing," <i>J. Am. Coll. Cardiol.</i>, vol. 40, no. 8, pp. 1531–1540, 2002.'),
    sp(2),
    p('[5] J. C. Bezdek, R. Ehrlich, and W. Full, "FCM: The fuzzy c-means '
      'clustering algorithm," <i>Comput. Geosci.</i>, vol. 10, no. 2–3, '
      'pp. 191–203, 1984.'),
    sp(2),
    p('[6] L. A. Zadeh, "Fuzzy sets," <i>Inf. Control</i>, '
      'vol. 8, no. 3, pp. 338–353, 1965.'),
]

# ---------------------------------------------------------------------------
doc.build(story)
print(f'Paper gerado: paper_ieee.pdf')
