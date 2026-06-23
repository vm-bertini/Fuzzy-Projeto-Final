"""
Geração da apresentação PPTX — Projeto ANFIS (FEEC/Unicamp)
Design: fundo branco, barra verde no topo com logo, texto limpo.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ---------------------------------------------------------------------------
# Cores
# ---------------------------------------------------------------------------
VERDE   = RGBColor(0x2E, 0x7D, 0x32)
VERDE_M = RGBColor(0x43, 0xA0, 0x47)
VERDE_C = RGBColor(0xC8, 0xE6, 0xC9)
NAVY    = RGBColor(0x1C, 0x3F, 0x6E)
CINZA   = RGBColor(0x55, 0x6B, 0x72)
BRANCO  = RGBColor(0xFF, 0xFF, 0xFF)
PRETO   = RGBColor(0x21, 0x21, 0x21)
TEAL    = RGBColor(0x00, 0x69, 0x5C)
AMARELO = RGBColor(0xE6, 0x5C, 0x00)

W = Inches(13.33)
H = Inches(7.5)

LOGO  = 'background.jpg'
RES   = os.path.join('src', 'results', '2026_06_23_03_55')

# Área de conteúdo
CX = Inches(0.45)         # content left margin
CW = W - Inches(0.9)      # content width
CY = Inches(1.25)         # content top (below header)
CH = Inches(5.85)         # content height (above footer)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H
BL = prs.slide_layouts[6]


# ---------------------------------------------------------------------------
# Primitivas
# ---------------------------------------------------------------------------

def rect(slide, x, y, w, h, fill):
    sh = slide.shapes.add_shape(1, x, y, w, h)
    sh.line.fill.background()
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    return sh


def tb(slide, text, x, y, w, h,
       size=14, bold=False, italic=False, color=PRETO, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf  = box.text_frame
    tf.word_wrap = True
    p   = tf.paragraphs[0]
    p.alignment = align
    r   = p.add_run()
    r.text            = text
    r.font.size       = Pt(size)
    r.font.bold       = bold
    r.font.italic     = italic
    r.font.color.rgb  = color
    return box


def bullets(slide, items, x, y, w, h, size=13, color=PRETO, gap=Pt(3)):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf  = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        p.space_before = gap
        p.alignment    = PP_ALIGN.LEFT
        r = p.add_run()
        r.text           = item
        r.font.size      = Pt(size)
        r.font.color.rgb = color
    return box


def img(slide, path, x, y, w, h=None):
    if os.path.exists(path):
        if h:
            slide.shapes.add_picture(path, x, y, w, h)
        else:
            slide.shapes.add_picture(path, x, y, w)


def header(slide, title):
    """Barra verde com logo à esquerda e título à direita."""
    rect(slide, 0, 0, W, Inches(1.1), VERDE)
    if os.path.exists(LOGO):
        slide.shapes.add_picture(LOGO, Inches(0.12), Inches(0.1),
                                 Inches(1.6), Inches(0.9))
    tb(slide, title,
       Inches(1.85), Inches(0.13), W - Inches(2.1), Inches(0.85),
       size=22, bold=True, color=BRANCO)


def footer(slide):
    rect(slide, 0, H - Inches(0.28), W, Inches(0.28), NAVY)
    tb(slide, 'Victor M. Bertini  |  FEEC / Unicamp  |  Junho 2026',
       Inches(0.3), H - Inches(0.27), W - Inches(0.6), Inches(0.25),
       size=8, color=BRANCO)


def slide_base(prs, title):
    s = prs.slides.add_slide(BL)
    header(s, title)
    footer(s)
    return s


def section_label(slide, text, y):
    """Rótulo verde pequeno antes de um bloco de conteúdo."""
    tb(slide, text, CX, y, CW, Inches(0.35), size=12, bold=True, color=VERDE)


# ===========================================================================
# Slide 1 — Título
# ===========================================================================
s = prs.slides.add_slide(BL)
rect(s, 0, 0, W, H, BRANCO)
rect(s, 0, 0, W, Inches(1.1), VERDE)

if os.path.exists(LOGO):
    s.shapes.add_picture(LOGO, Inches(0.12), Inches(0.1), Inches(1.6), Inches(0.9))

rect(s, 0, Inches(2.3), W, Inches(0.06), VERDE)
rect(s, 0, Inches(5.5), W, Inches(0.06), VERDE)

tb(s, 'Sistemas Neuro-Fuzzy para Classificação de Risco Cardíaco',
   CX, Inches(2.5), CW, Inches(1.4),
   size=30, bold=True, color=PRETO)
tb(s, 'Comparação entre ANFIS e MLP: Acurácia vs Interpretabilidade',
   CX, Inches(3.95), CW, Inches(0.65),
   size=18, italic=True, color=CINZA)
tb(s, 'Victor M. Bertini   |   FEEC / Unicamp   |   Junho 2026',
   CX, Inches(5.75), CW, Inches(0.5),
   size=14, color=CINZA)


# ===========================================================================
# Slide 2 — Motivação
# ===========================================================================
s = slide_base(prs, 'Motivação: O Custo da Caixa-Preta')

bullets(s, [
    '▸  Modelos de ML atingem alta acurácia em diagnóstico cardíaco',
    '▸  Médicos precisam ENTENDER a decisão — não apenas confiar nela',
    '▸  "Por que este paciente foi classificado como alto risco?"',
    '▸  Regulações clínicas exigem rastreabilidade das decisões',
    '▸  Redes neurais tradicionais (MLP) não fornecem nenhuma explicação',
    '',
    '→  Pergunta central:',
    '    É possível ter desempenho comparável ao MLP com interpretabilidade linguística?',
], CX, CY, CW, CH, size=16, color=PRETO)


# ===========================================================================
# Slide 3 — Lacuna
# ===========================================================================
s = slide_base(prs, 'A Lacuna: Acurácia vs Interpretabilidade')

# Caixa MLP
rect(s, CX, CY, Inches(5.9), Inches(5.5), VERDE_C)
tb(s, 'MLP  —  Caixa-Preta',
   CX + Inches(0.15), CY + Inches(0.1), Inches(5.6), Inches(0.45),
   size=15, bold=True, color=NAVY)
bullets(s, [
    '✓  Alta acurácia',
    '✓  Treinamento rápido',
    '✗  Zero interpretabilidade',
    '✗  Nenhuma regra auditável',
    '✗  Inaceitável em contextos regulados',
], CX + Inches(0.15), CY + Inches(0.6), Inches(5.6), Inches(4.6), size=14)

tb(s, 'vs', Inches(6.4), CY + Inches(2.4), Inches(0.5), Inches(0.6),
   size=20, bold=True, color=CINZA, align=PP_ALIGN.CENTER)

# Caixa ANFIS
rect(s, Inches(6.95), CY, Inches(5.9), Inches(5.5), VERDE_C)
tb(s, 'ANFIS  —  Neuro-Fuzzy',
   Inches(7.1), CY + Inches(0.1), Inches(5.6), Inches(0.45),
   size=15, bold=True, color=VERDE)
bullets(s, [
    '✓  Acurácia comparável',
    '✓  Regras linguísticas auditáveis',
    '✓  Parâmetros com significado físico',
    '✓  13× menos parâmetros que MLP',
    '~  Treinamento ligeiramente mais lento',
], Inches(7.1), CY + Inches(0.6), Inches(5.6), Inches(4.6), size=14)


# ===========================================================================
# Slide 4 — Roteiro
# ===========================================================================
s = slide_base(prs, 'Estrutura da Apresentação')

bullets(s, [
    '1.   Arquitetura ANFIS — camada a camada com equações',
    '2.   Dataset e Configuração Experimental',
    '3.   Pipeline K-Means — geração do pool de regras',
    '4.   Métricas de Avaliação',
    '5.   MFs de Saída — conversão TS → rótulo linguístico',
    '6.   Resultados: desempenho, MFs aprendidas e regras extraídas',
    '7.   Análise Comparativa ANFIS × MLP',
    '8.   Conclusões e Trabalho Futuro',
], CX, CY, CW, CH, size=17, color=PRETO, gap=Pt(7))


# ===========================================================================
# Slide 5 — Framework Teórico
# ===========================================================================
s = slide_base(prs, 'Arquitetura ANFIS — Camada a Camada')

# Pipeline no topo
py, ph, pw = CY, Inches(0.55), Inches(2.5)
boxes = [
    ('Entrada  [B, 11]',           Inches(0.2),  NAVY),
    ('MixedFuzzyLayer\n[B,11,M]',  Inches(2.82), VERDE),
    ('ClusterRuleLayer\n[B, R]',   Inches(5.44), TEAL),
    ('DefuzzyLayer\n[B, 1]',       Inches(8.06), VERDE),
    ('Sigmoid → P(d)',             Inches(10.68),NAVY),
]
for lbl, bx, col in boxes:
    b = rect(s, bx, py, pw, ph, col)
    bx2 = b.text_frame; bx2.word_wrap = True
    p2  = bx2.paragraphs[0]; p2.alignment = PP_ALIGN.CENTER
    r2  = p2.add_run(); r2.text = lbl
    r2.font.size = Pt(9); r2.font.bold = True; r2.font.color.rgb = BRANCO
    if bx < Inches(10.68):
        tb(s, '→', bx + pw, py + Inches(0.08), Inches(0.28), Inches(0.38),
           size=12, bold=True, color=CINZA, align=PP_ALIGN.CENTER)

# 3 colunas de descrição
y2 = CY + Inches(0.7)
ch2 = H - y2 - Inches(0.4)
cx1, cx2, cx3 = Inches(0.2), Inches(4.55), Inches(8.9)
cw3 = Inches(4.1)

# col 1
rect(s, cx1, y2, Inches(0.04), ch2, VERDE)
bullets(s, [
    'MixedFuzzyLayer',
    'Numéricas → MFs Gaussianas treináveis:',
    '  μ(x) = exp(−½·((x−c)/σ)²)',
    '  c, σ ajustados por backprop',
    '',
    'Categóricas → one-hot suavizado:',
    '  out[cat correta] = 0,95',
    '  out[demais] = 0,05/(n−1)',
    '',
    'Exemplos:',
    '  ChestPainType: ASY→3, ATA→0',
    '  ExerciseAngina: N→0, Y→1',
    '  ST_Slope: Down→0, Flat→1, Up→2',
], cx1 + Inches(0.15), y2, cw3, ch2, size=11)

# col 2
rect(s, cx2, y2, Inches(0.04), ch2, TEAL)
bullets(s, [
    'ClusterRuleLayer',
    'T-norma produto (diferenciável):',
    '',
    '  w_k = ∏ᵢ μᵢ,combo[k,i](xᵢ)',
    '',
    'combo[k,i] = índice da MF da',
    'regra k na feature i (K-Means)',
    '',
    'Normalização:',
    '  w̃_k = w_k / (Σⱼ wⱼ + ε)',
    '',
    'Sem parâmetros treináveis.',
    'rule_idx como register_buffer',
], cx2 + Inches(0.15), y2, cw3, ch2, size=11)

# col 3
rect(s, cx3, y2, Inches(0.04), ch2, VERDE)
bullets(s, [
    'DefuzzyLayer  +  Loss',
    'Takagi-Sugeno (ordem 0):',
    '  ŷ = Σ_k w̃_k · c_k',
    '  c_k ∈ nn.Linear(R→1)',
    '',
    'Loss = BCE + λ · penalidade',
    '',
    '  BCE(σ(ŷ), y)',
    '',
    '  λ·Σᵢ<ⱼ relu(σᵢ+σⱼ−|cᵢ−cⱼ|)',
    '  Penaliza MFs sobrepostas.',
    '  Se |cᵢ−cⱼ| < σᵢ+σⱼ:',
    '  MF j cabe dentro de MF i',
    '  → partição incoerente  (λ=0,1)',
], cx3 + Inches(0.15), y2, cw3, ch2, size=11)


# ===========================================================================
# Slide 6 — Dataset
# ===========================================================================
s = slide_base(prs, 'Dataset e Configuração Experimental')

# Coluna esquerda — info
bullets(s, [
    'Heart Failure Prediction Dataset',
    '',
    '▸  918 pacientes adultos',
    '▸  Variável alvo: HeartDisease (0/1)',
    '▸  Prevalência: ~55% positivos',
    '▸  Split: 80% treino / 20% teste',
    '',
    'Features numéricas (5):',
    '   Age, RestingBP, Cholesterol, MaxHR, Oldpeak',
    '',
    'Features categóricas (6):',
    '   Sex, ChestPainType, FastingBS,',
    '   RestingECG, ExerciseAngina, ST_Slope',
    '',
    'Pré-processamento:',
    '   PartialScaler: z-score só nas numéricas',
    '   Categóricas mantêm código inteiro',
], CX, CY, Inches(5.5), CH, size=13)

# Coluna direita — snippet
tb(s, 'Exemplo de registros no dataset:',
   Inches(6.1), CY, Inches(6.8), Inches(0.38),
   size=12, bold=True, color=NAVY)

headers = ['Age', 'Sex', 'ChestPain', 'MaxHR', 'ExAngina', 'Oldpeak', 'ST', 'HD']
rows_d  = [
    ['40', 'M', 'ATA', '172', 'N', '0.0', 'Up',   '0'],
    ['49', 'F', 'NAP', '156', 'N', '1.0', 'Flat', '1'],
    ['37', 'M', 'ATA', ' 98', 'N', '0.0', 'Up',   '0'],
    ['48', 'F', 'ASY', '108', 'Y', '1.5', 'Flat', '1'],
]
cw_cell = Inches(0.815)
ch_cell = Inches(0.43)
tx0 = Inches(6.1)
ty0 = CY + Inches(0.45)

for ci, h in enumerate(headers):
    b = rect(s, tx0 + ci*cw_cell, ty0, cw_cell - Inches(0.02), ch_cell, VERDE)
    tf2 = b.text_frame; tf2.paragraphs[0].alignment = PP_ALIGN.CENTER
    r2  = tf2.paragraphs[0].add_run()
    r2.text = h; r2.font.size = Pt(9); r2.font.bold = True; r2.font.color.rgb = BRANCO

for ri, row in enumerate(rows_d):
    bg = VERDE_C if ri % 2 == 0 else BRANCO
    for ci, val in enumerate(row):
        b = rect(s, tx0 + ci*cw_cell, ty0 + (ri+1)*ch_cell,
                 cw_cell - Inches(0.02), ch_cell - Inches(0.02), bg)
        tf2 = b.text_frame; tf2.paragraphs[0].alignment = PP_ALIGN.CENTER
        r2  = tf2.paragraphs[0].add_run()
        r2.text = val; r2.font.size = Pt(9); r2.font.color.rgb = PRETO

tb(s, 'HD = HeartDisease (variável alvo)',
   Inches(6.1), ty0 + Inches(2.2), Inches(6.8), Inches(0.3),
   size=9, italic=True, color=CINZA)

# Configuração
bullets(s, [
    'Configuração:',
    '   NUM_MFS=3  |  EPOCHS=200  |  lr=1e-3  |  batch=32',
    '   ANFIS: 200 clusters K-Means  |  MLP: [64, 32]',
], Inches(6.1), ty0 + Inches(2.65), Inches(6.8), Inches(1.5), size=12)


# ===========================================================================
# Slide 7 — K-Means pipeline
# ===========================================================================
s = slide_base(prs, 'Geração do Pool de Regras via K-Means')

# Caixa de aviso
b = rect(s, CX, CY, CW, Inches(0.72), VERDE_C)
tf2 = b.text_frame; tf2.word_wrap = True
tf2.paragraphs[0].alignment = PP_ALIGN.LEFT
r2 = tf2.paragraphs[0].add_run()
r2.text = ('⚠  A fuzzificação percentílica abaixo é um ARTIFÍCIO de mapeamento — '
           'não são as MFs do ANFIS. Servem exclusivamente para converter centros de '
           'clusters em índices discretos e selecionar quais combinações de antecedentes '
           'entram no pool de regras.')
r2.font.size = Pt(11); r2.font.color.rgb = PRETO

bullets(s, [
    '1.  Picos por percentil  (artifício de simplificação):',
    '      pcts = [25%, 50%, 75%]  →  peaks[fi] = percentis da distribuição de treino',
    '      Generalização que converte o espaço contínuo em labels baixo/médio/alto',
    '',
    '2.  K-Means (200 clusters) particiona o espaço de entrada:',
    '      Sem supervisão — agrupa por proximidade nas features',
    '',
    '3.  Mapeamento dominante por cluster:',
    '      Numérica:   argmax μ_triangular(centro_k, pico_j)  →  índice 0, 1, 2',
    '      Categórica: round(centro_k)                        →  código inteiro',
    '',
    '4.  Deduplicação: clusters com mesmo vetor de labels → uma regra',
    '      200 clusters → ~197 combos únicos nesta execução',
    '',
    '5.  Centros Gaussianos do ANFIS inicializados nos percentis dos centros K-Means',
    '      Treino end-to-end refina c, σ e c_k independentemente deste mapeamento',
], CX, CY + Inches(0.8), CW, CH - Inches(0.8), size=12)


# ===========================================================================
# Slide 8 — Métricas
# ===========================================================================
s = slide_base(prs, 'Métricas de Avaliação Utilizadas')

metrics = [
    ('AUC-ROC',
     ['Área sob a curva ROC.',
      'Mede separação das classes independentemente do limiar.',
      'AUC=1,0 → perfeito  |  AUC=0,5 → aleatório'],
     VERDE),
    ('Acurácia',
     ['Proporção de predições corretas.',
      '  Acurácia = (VP + VN) / N',
      'Sensível ao desbalanceamento de classes.'],
     TEAL),
    ('F1-Score',
     ['Média harmônica entre Precisão e Revocação.',
      '  F1 = 2·(P·R) / (P+R)',
      'Preferível quando as classes são desbalanceadas.'],
     NAVY),
]

bw = Inches(4.0)
for i, (name, lines, col) in enumerate(metrics):
    bx = CX + i * (bw + Inches(0.25))
    b  = rect(s, bx, CY, bw, Inches(0.52), col)
    tf2 = b.text_frame; tf2.paragraphs[0].alignment = PP_ALIGN.CENTER
    r2  = tf2.paragraphs[0].add_run()
    r2.text = name; r2.font.size = Pt(16); r2.font.bold = True; r2.font.color.rgb = BRANCO
    bullets(s, lines, bx, CY + Inches(0.58), bw, Inches(2.5), size=13)

tb(s, 'Limiar de decisão: 0,5  |  Testado no conjunto de teste (20% dos dados)',
   CX, CY + Inches(3.3), CW, Inches(0.4), size=12, italic=True, color=CINZA)


# ===========================================================================
# Slide 9 — MFs de saída hardcoded
# ===========================================================================
s = slide_base(prs, 'MFs de Saída — Conversão do Resultado TS em Rótulo Linguístico')

bullets(s, [
    'O problema:',
    '   DefuzzyLayer produz ŷ ∈ ℝ  →  sigmoid  →  P(doença) ∈ [0,1].',
    '   Regras Takagi-Sugeno não têm consequente linguístico, apenas um número c_k.',
    '   Para transcrever "SE ... ENTÃO risco = ALTO" precisamos mapear ŷ a um label.',
    '',
    'A solução (definição analítica manual):',
    '   5 MFs triangulares uniformemente espaçadas em [0, 1]:',
    '   centros  c = [1/6, 2/6, 3/6, 4/6, 5/6]',
    '   meia-largura  hw = 1/6  →  partição exata, sem sobreposição',
    '',
    '   μⱼ(ŷ) = max(0,  1 − |ŷ − cⱼ| / hw)',
    '   rótulo(ŷ) = argmaxⱼ μⱼ(ŷ)',
    '',
    '   Labels: baixo | baixo_médio | médio | médio_alto | alto',
    '',
    '   Ex.: ŷ = 0,78  →  μ₄(alto) = 0,68  →  risco = alto',
], CX, CY, Inches(7.0), CH, size=13)

img(s, os.path.join(RES, 'mfs_anfis.png'),
    Inches(7.2), CY, Inches(5.8), Inches(5.7))
tb(s, '↑ painel "Output — risco" (inferior direito)',
   Inches(7.2), CY + Inches(5.65), Inches(5.8), Inches(0.3),
   size=9, italic=True, color=CINZA)


# ===========================================================================
# Slide 10 — Resultados: métricas
# ===========================================================================
s = slide_base(prs, 'Resultados: Métricas de Desempenho')

rows = [
    ('Modelo',  'Parâmetros', 'Treino (s)', 'Acurácia', 'F1-Score', 'AUC-ROC'),
    ('ANFIS',   '228',        '14,9 s',     '84,2 %',   '85,9 %',  '0,912'),
    ('MLP',     '2.881',      '4,8 s',      '81,5 %',   '82,5 %',  '0,901'),
]
col_x = [Inches(0.45), Inches(2.7), Inches(4.65), Inches(6.6), Inches(8.7), Inches(10.8)]
col_w = [Inches(2.2),  Inches(1.9), Inches(1.9),  Inches(2.05), Inches(2.05), Inches(2.05)]
rh    = Inches(0.78)
ry    = [CY, CY + rh, CY + 2*rh]

for ri, row in enumerate(rows):
    bg = VERDE if ri == 0 else (VERDE_C if ri == 1 else RGBColor(0xF5,0xF5,0xF5))
    fg = BRANCO if ri == 0 else PRETO
    for ci, (cell, cx2, cw2) in enumerate(zip(row, col_x, col_w)):
        b = rect(s, cx2, ry[ri], cw2 - Inches(0.03), rh - Inches(0.03), bg)
        tf2 = b.text_frame; tf2.paragraphs[0].alignment = PP_ALIGN.CENTER
        r2  = tf2.paragraphs[0].add_run()
        r2.text = cell; r2.font.size = Pt(14)
        r2.font.bold = (ri == 0); r2.font.color.rgb = fg

bullets(s, [
    '▸  ANFIS supera o MLP em todas as métricas nesta execução',
    '▸  13× menos parâmetros (228 vs 2.881)',
    '▸  ANFIS ~3× mais lento para treinar — aceitável em produção offline',
    '▸  MLP não oferece nenhuma explicação sobre suas predições',
], CX, CY + Inches(2.55), CW, Inches(3.0), size=15, gap=Pt(6))


# ===========================================================================
# Slide 11 — MFs Aprendidas
# ===========================================================================
s = slide_base(prs, 'Funções de Pertinência Gaussianas Aprendidas (pós-treinamento)')
img(s, os.path.join(RES, 'mfs_anfis.png'), CX, CY, CW, CH)


# ===========================================================================
# Slide 12 — Regras (todas as 10)
# ===========================================================================
s = slide_base(prs, 'Regras Linguísticas Extraídas — Top-10 por Força de Disparo Média')

regras = [
    ('R1',  'BAIXO', 'Age=jovem, Sex=M, CPT=ATA, RBP=normal, Chol=alto,  FBS=0, ECG=Normal, MaxHR=alta,  Ang=N, OP=normal,  ST=Up'),
    ('R2',  'ALTO',  'Age=jovem, Sex=M, CPT=ASY, RBP=normal, Chol=desej, FBS=0, ECG=Normal, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat'),
    ('R3',  'ALTO',  'Age=idoso, Sex=M, CPT=ASY, RBP=normal, Chol=alto,  FBS=0, ECG=ST,     MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat'),
    ('R4',  'BAIXO', 'Age=jovem, Sex=M, CPT=ATA, RBP=elevado,Chol=desej, FBS=0, ECG=Normal, MaxHR=baixa, Ang=N, OP=normal,  ST=Up'),
    ('R5',  'BAIXO', 'Age=jovem, Sex=M, CPT=ATA, RBP=otimo,  Chol=desej, FBS=0, ECG=Normal, MaxHR=baixa, Ang=N, OP=normal,  ST=Up'),
    ('R6',  'BAIXO', 'Age=jovem, Sex=F, CPT=ATA, RBP=otimo,  Chol=alto,  FBS=0, ECG=Normal, MaxHR=baixa, Ang=N, OP=normal,  ST=Up'),
    ('R7',  'ALTO',  'Age=idoso, Sex=M, CPT=ASY, RBP=normal, Chol=desej, FBS=0, ECG=LVH,    MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat'),
    ('R8',  'BAIXO', 'Age=jovem, Sex=M, CPT=NAP, RBP=normal, Chol=desej, FBS=0, ECG=Normal, MaxHR=alta,  Ang=N, OP=normal,  ST=Up'),
    ('R9',  'ALTO',  'Age=jovem, Sex=M, CPT=ASY, RBP=otimo,  Chol=desej, FBS=1, ECG=Normal, MaxHR=baixa, Ang=N, OP=normal,  ST=Flat'),
    ('R10', 'ALTO',  'Age=jovem, Sex=M, CPT=ASY, RBP=elevado,Chol=desej, FBS=0, ECG=Normal, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat'),
]

rh2 = Inches(0.476)
lw  = Inches(1.1)
ty  = CY

for i, (num, risco, regra) in enumerate(regras):
    cor = VERDE if risco == 'ALTO' else (TEAL if 'MEDIO' in risco else NAVY)
    b = rect(s, CX, ty + i*rh2, lw, rh2 - Inches(0.03), cor)
    tf2 = b.text_frame; tf2.paragraphs[0].alignment = PP_ALIGN.CENTER
    r2 = tf2.paragraphs[0].add_run()
    r2.text = f'{num} {risco.upper()}'; r2.font.size = Pt(8)
    r2.font.bold = True; r2.font.color.rgb = BRANCO
    tb(s, regra,
       CX + lw + Inches(0.1), ty + i*rh2 + Inches(0.05),
       CW - lw - Inches(0.1), rh2,
       size=10, color=PRETO)


# ===========================================================================
# Slide 13 — Comparação de risco
# ===========================================================================
s = slide_base(prs, 'Comparação de Risco: ANFIS vs MLP (Conjunto de Teste)')
img(s, os.path.join(RES, 'risk_comparison.png'), CX, CY, CW, CH)


# ===========================================================================
# Slide 14 — Análise crítica
# ===========================================================================
s = slide_base(prs, 'Análise: ANFIS como Alternativa Interpretável ao MLP')

b = rect(s, CX, CY, CW, Inches(0.7), VERDE_C)
tf2 = b.text_frame; tf2.word_wrap = True
tf2.paragraphs[0].alignment = PP_ALIGN.LEFT
r2 = tf2.paragraphs[0].add_run()
r2.text = ('ANFIS supera o MLP em todas as métricas com 13× menos parâmetros '
           'e produz regras linguísticas auditáveis.')
r2.font.size = Pt(14); r2.font.bold = True; r2.font.color.rgb = VERDE

bullets(s, [
    'Eficiência paramétrica:',
    '   228 vs 2.881 parâmetros — centros e variâncias têm interpretação direta',
    '   Cada c_k aprendido representa a "opinião" daquela regra sobre o risco',
    '',
    'Interpretabilidade genuína:',
    '   ST_Slope=Flat + ExerciseAngina=Y + Oldpeak=elevado → padrão recorrente de alto risco',
    '   Compatível com literatura médica sobre isquemia cardíaca',
    '',
    'Tradeoff velocidade:',
    '   ANFIS: 14,9 s  vs  MLP: 4,8 s — diferença aceitável em produção offline',
], CX, CY + Inches(0.8), CW, CH - Inches(0.8), size=14)


# ===========================================================================
# Slide 15 — Pontos de atenção
# ===========================================================================
s = slide_base(prs, 'Pontos de Atenção e Limitações')

bullets(s, [
    '1.  Explosão de regras',
    '      n_regras ∝ num_mfs^n_inputs — inviável sem seleção/deduplicação',
    '      Solução: K-Means como filtro + deduplicação por combo de MFs dominantes',
    '',
    '2.  Features categóricas em sistemas fuzzy',
    '      Não existe grau de pertinência natural entre categorias discretas',
    '      MixedFuzzyLayer usa one-hot suavizado:  μ=0,95 (certa) / 0,05/(n−1) (demais)',
    '',
    '3.  Sensibilidade à inicialização',
    '      K-Means determinístico (semente fixa) — pool de regras pode variar',
    '      Penalidade de separação mitiga colapso de MFs durante treinamento',
    '',
    '4.  Testado em um único dataset (n=918)',
    '      Generalização para outros domínios requer validação adicional',
], CX, CY, CW, CH, size=14)


# ===========================================================================
# Slide 16 — Conclusões
# ===========================================================================
s = slide_base(prs, 'Conclusões')

bullets(s, [
    '✅  ANFIS supera o MLP em acurácia, F1 e AUC nesta execução',
    '✅  228 parâmetros treináveis vs 2.881 do MLP  (13× mais eficiente)',
    '✅  Regras linguísticas auditáveis revelam os padrões clínicos aprendidos',
    '✅  Pipeline reproduzível: K-Means → inicialização → treino end-to-end',
    '✅  Penalidade de separação garante MFs linguisticamente coerentes',
    '',
    '→  ANFIS é uma alternativa viável quando interpretabilidade é requisito,',
    '    sem sacrifício — e neste caso com ganho — de desempenho preditivo.',
], CX, CY, CW, CH, size=16, gap=Pt(7))


# ===========================================================================
# Slide 17 — Trabalho Futuro
# ===========================================================================
s = slide_base(prs, 'Limitações e Trabalho Futuro')

tb(s, 'Limitações atuais', CX, CY, Inches(5.9), Inches(0.38),
   size=14, bold=True, color=NAVY)
bullets(s, [
    '• Testado em único dataset (n=918)',
    '• Categóricas sem MFs formalmente definidas',
    '• Pool de regras depende da semente K-Means',
    '• Treinamento ~3× mais lento que MLP',
], CX, CY + Inches(0.42), Inches(5.9), Inches(2.3), size=13)

tb(s, 'Próximos passos', CX, CY + Inches(2.9), Inches(5.9), Inches(0.38),
   size=14, bold=True, color=NAVY)
bullets(s, [
    '• Validar em datasets maiores e multi-classe',
    '• Incorporar conhecimento de especialistas',
    '  na inicialização das MFs Gaussianas',
    '• Comparar com XGBoost + SHAP como baseline',
    '• Interface de extração em linguagem natural',
], CX, CY + Inches(3.35), Inches(5.9), Inches(2.3), size=13)

img(s, os.path.join(RES, 'confusion_matrix.png'),
    Inches(6.5), CY, Inches(6.4), Inches(5.85))


# ===========================================================================
# Slide 18 — Obrigado
# ===========================================================================
s = prs.slides.add_slide(BL)
rect(s, 0, 0, W, H, BRANCO)
rect(s, 0, 0, W, Inches(1.1), VERDE)
if os.path.exists(LOGO):
    s.shapes.add_picture(LOGO, Inches(0.12), Inches(0.1), Inches(1.6), Inches(0.9))

rect(s, 0, Inches(2.4), W, Inches(0.06), VERDE)

tb(s, 'Obrigado!',
   CX, Inches(2.6), CW, Inches(1.3),
   size=48, bold=True, color=PRETO)
tb(s, 'victor.m.bertini@gmail.com',
   CX, Inches(4.1), CW, Inches(0.5), size=16, color=CINZA)
tb(s, 'github.com/vm-bertini/Fuzzy-Projeto-Final',
   CX, Inches(4.65), CW, Inches(0.5), size=14, color=CINZA)
tb(s, '"ANFIS: interpretabilidade sem sacrificar performance"',
   CX, Inches(5.5), CW, Inches(0.5),
   size=14, italic=True, color=VERDE)

rect(s, 0, H - Inches(0.28), W, Inches(0.28), NAVY)
tb(s, 'Victor M. Bertini  |  FEEC / Unicamp  |  Junho 2026',
   Inches(0.3), H - Inches(0.27), W - Inches(0.6), Inches(0.25),
   size=8, color=BRANCO)


# ===========================================================================
# Apêndice A — Heatmap
# ===========================================================================
s = slide_base(prs, 'Apêndice A — Heatmap das Regras ANFIS')
img(s, os.path.join(RES, 'rule_comparison.png'), CX, CY, CW, CH)


# ===========================================================================
# Apêndice B — K-Means
# ===========================================================================
s = slide_base(prs, 'Apêndice B — Partição K-Means (pré-ANFIS)')
img(s, os.path.join(RES, 'mfs_kmeans.png'), CX, CY, CW, CH)


# ===========================================================================
# Apêndice C — Glossário do Dataset
# ===========================================================================
s = slide_base(prs, 'Apêndice C — Glossário das Features do Dataset')

colunas = [
    ('Age',             'Numérica',    'Idade do paciente (anos)'),
    ('Sex',             'Categórica',  'Sexo biológico: M = masculino, F = feminino'),
    ('ChestPainType',   'Categórica',  'Tipo de dor torácica: ATA = dor atípica, NAP = dor não-anginosa, ASY = assintomático, TA = angina típica'),
    ('RestingBP',       'Numérica',    'Pressão arterial em repouso (mmHg); valores 0 substituídos pela mediana'),
    ('Cholesterol',     'Numérica',    'Colesterol sérico (mg/dL); valores 0 substituídos pela mediana'),
    ('FastingBS',       'Categórica',  'Glicemia em jejum: 1 = glicemia > 120 mg/dL (possível diabetes), 0 = normal'),
    ('RestingECG',      'Categórica',  'Resultado do ECG em repouso: Normal, ST = anormalidade onda ST-T, LVH = hipertrofia ventricular esquerda'),
    ('MaxHR',           'Numérica',    'Frequência cardíaca máxima atingida durante teste de esforço (bpm)'),
    ('ExerciseAngina',  'Categórica',  'Angina induzida por exercício: Y = sim, N = não'),
    ('Oldpeak',         'Numérica',    'Depressão do segmento ST induzida por exercício em relação ao repouso (mm)'),
    ('ST_Slope',        'Categórica',  'Inclinação do segmento ST no pico do exercício: Up = ascendente (saudável), Flat = plano, Down = descendente (risco)'),
]

# Cabeçalho da tabela
hdr_cols = [('Feature', Inches(2.0)), ('Tipo', Inches(1.4)), ('Descrição', Inches(9.4))]
hx = CX
hy = CY
hh = Inches(0.4)
for label, cw2 in hdr_cols:
    b = rect(s, hx, hy, cw2 - Inches(0.03), hh, VERDE)
    tf2 = b.text_frame; tf2.paragraphs[0].alignment = PP_ALIGN.CENTER
    r2 = tf2.paragraphs[0].add_run()
    r2.text = label; r2.font.size = Pt(12); r2.font.bold = True; r2.font.color.rgb = BRANCO
    hx += cw2

rh3 = Inches(0.465)
for ri, (feat, tipo, desc) in enumerate(colunas):
    bg  = VERDE_C if ri % 2 == 0 else RGBColor(0xF5, 0xF5, 0xF5)
    ty3 = hy + hh + ri * rh3
    rx  = CX
    for val, cw2 in [(feat, Inches(2.0)), (tipo, Inches(1.4)), (desc, Inches(9.4))]:
        b = rect(s, rx, ty3, cw2 - Inches(0.03), rh3 - Inches(0.02), bg)
        tf2 = b.text_frame; tf2.word_wrap = True
        tf2.paragraphs[0].alignment = PP_ALIGN.LEFT
        r2 = tf2.paragraphs[0].add_run()
        r2.text = val
        r2.font.size = Pt(10)
        r2.font.bold = (val == feat)
        r2.font.color.rgb = PRETO
        rx += cw2


# ---------------------------------------------------------------------------
out = 'apresentacao_anfis_final.pptx'
prs.save(out)
print(f'Salvo: {out}  ({len(prs.slides)} slides)')
