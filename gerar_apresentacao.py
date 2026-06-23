"""
Geração da apresentação PPTX — Projeto ANFIS
Execução: python gerar_apresentacao.py
Saída:    apresentacao_anfis.pptx
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree

# ---------------------------------------------------------------------------
# Paleta de cores
# ---------------------------------------------------------------------------
AZUL      = RGBColor(0x15, 0x65, 0xC0)
AZUL_ESC  = RGBColor(0x0D, 0x47, 0xA1)
ROXO      = RGBColor(0x6A, 0x1B, 0x9A)
CINZA     = RGBColor(0x45, 0x5A, 0x64)
CINZA_CLR = RGBColor(0xEC, 0xEF, 0xF1)
BRANCO    = RGBColor(0xFF, 0xFF, 0xFF)
PRETO     = RGBColor(0x21, 0x21, 0x21)
VERDE     = RGBColor(0x1B, 0x5E, 0x20)
VERDE_CLR = RGBColor(0xA5, 0xD6, 0xA7)
AMARELO   = RGBColor(0xF5, 0x7F, 0x17)
VERMELHO  = RGBColor(0xB7, 0x1C, 0x1C)

W  = Inches(13.33)
H  = Inches(7.5)
RESULTS_DIR = os.path.join('src', 'results', '2026_06_23_03_02')


# ---------------------------------------------------------------------------
# Helpers de forma e texto
# ---------------------------------------------------------------------------

def _add_rect(slide, x, y, w, h, fill, alpha=None):
    shape = slide.shapes.add_shape(1, x, y, w, h)   # MSO_SHAPE_TYPE.RECTANGLE = 1
    shape.line.fill.background()
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    return shape


def _tf(shape, text, size, bold=False, color=BRANCO, align=PP_ALIGN.LEFT, italic=False):
    tf = shape.text_frame
    tf.word_wrap = True
    p  = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return tf


def _add_textbox(slide, text, x, y, w, h, size=14, bold=False,
                 color=PRETO, align=PP_ALIGN.LEFT, italic=False):
    txb = slide.shapes.add_textbox(x, y, w, h)
    tf  = txb.text_frame
    tf.word_wrap = True
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return txb


def _header(slide, title, subtitle=None):
    """Faixa azul no topo com título."""
    bar = _add_rect(slide, Inches(0), Inches(0), W, Inches(1.3), AZUL_ESC)
    _tf(bar, title, 28, bold=True, color=BRANCO, align=PP_ALIGN.CENTER)
    if subtitle:
        _add_textbox(slide, subtitle,
                     Inches(0.4), Inches(1.35), W - Inches(0.8), Inches(0.45),
                     size=13, color=CINZA, italic=True)


def _bullets(slide, items, x, y, w, h, size=14, color=PRETO, bold_first=False):
    txb = slide.shapes.add_textbox(x, y, w, h)
    tf  = txb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        p.space_before = Pt(4)
        run = p.add_run()
        run.text = item
        run.font.size  = Pt(size)
        run.font.color.rgb = color
        run.font.bold  = (bold_first and i == 0)
    return txb


def _add_image(slide, path, x, y, w, h=None):
    if not os.path.exists(path):
        return
    if h:
        slide.shapes.add_picture(path, x, y, w, h)
    else:
        slide.shapes.add_picture(path, x, y, w)


def _footer(slide, text='Victor M. Bertini  |  Mestrado — Lógica Fuzzy  |  2026'):
    _add_rect(slide, Inches(0), H - Inches(0.32), W, Inches(0.32), AZUL)
    _add_textbox(slide, text,
                 Inches(0.3), H - Inches(0.30), W - Inches(0.6), Inches(0.28),
                 size=8, color=BRANCO)


# ---------------------------------------------------------------------------
# Criação da apresentação
# ---------------------------------------------------------------------------

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H
blank = prs.slide_layouts[6]   # blank


# ---- Slide 1 — Título -------------------------------------------------------
s = prs.slides.add_slide(blank)
_add_rect(s, Inches(0), Inches(0), W, H, AZUL_ESC)
_add_rect(s, Inches(0), Inches(2.6), W, Inches(2.8), AZUL)

_add_textbox(s,
    'Sistemas Neuro-Fuzzy para Classificação de Risco Cardíaco',
    Inches(0.6), Inches(2.7), W - Inches(1.2), Inches(1.4),
    size=34, bold=True, color=BRANCO, align=PP_ALIGN.CENTER)

_add_textbox(s,
    'Comparação entre ANFIS e MLP: Acurácia vs Interpretabilidade',
    Inches(0.6), Inches(4.05), W - Inches(1.2), Inches(0.7),
    size=18, color=CINZA_CLR, align=PP_ALIGN.CENTER, italic=True)

_add_textbox(s,
    'Victor M. Bertini',
    Inches(0.6), Inches(5.1), W - Inches(1.2), Inches(0.5),
    size=16, color=BRANCO, align=PP_ALIGN.CENTER, bold=True)

_add_textbox(s,
    'Junho 2026',
    Inches(0.6), Inches(5.6), W - Inches(1.2), Inches(0.4),
    size=13, color=CINZA_CLR, align=PP_ALIGN.CENTER)


# ---- Slide 2 — Motivação ----------------------------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Motivação: O Custo da Caixa-Preta')
_footer(s)

_bullets(s, [
    '📌  Modelos de ML alcançam alta acurácia em diagnóstico cardíaco',
    '⚠️   Mas médicos precisam ENTENDER a decisão — não apenas confiar nela',
    '🏥  "Por que este paciente foi classificado como alto risco?"',
    '📋  Regulações e protocolos clínicos exigem rastreabilidade das decisões',
    '🔍  Redes neurais tradicionais (MLP) são completamente opacas',
    '',
    '→  Pergunta central: é possível ter desempenho comparável COM interpretabilidade?',
], Inches(0.7), Inches(1.5), W - Inches(1.4), Inches(5.5),
   size=16, color=PRETO, bold_first=False)


# ---- Slide 3 — Lacuna e pergunta de pesquisa --------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'A Lacuna: Acurácia vs Interpretabilidade')
_footer(s)

# Caixa esquerda — MLP
b1 = _add_rect(s, Inches(0.5), Inches(1.6), Inches(5.5), Inches(4.6), CINZA_CLR)
_add_textbox(s, 'MLP (Caixa-Preta)', Inches(0.6), Inches(1.7),
             Inches(5.2), Inches(0.5), size=15, bold=True, color=AZUL_ESC)
_bullets(s, [
    '✓  Alta acurácia (AUC ≈ 0.91)',
    '✓  Treinamento rápido',
    '✗  Zero interpretabilidade',
    '✗  Não gera regras auditáveis',
    '✗  Inaceitável em contextos regulados',
], Inches(0.7), Inches(2.2), Inches(5.0), Inches(3.5), size=14, color=PRETO)

# Caixa direita — ANFIS
b2 = _add_rect(s, Inches(6.6), Inches(1.6), Inches(5.5), Inches(4.6), VERDE_CLR)
_add_textbox(s, 'ANFIS (Neuro-Fuzzy)', Inches(6.7), Inches(1.7),
             Inches(5.2), Inches(0.5), size=15, bold=True, color=VERDE)
_bullets(s, [
    '✓  Acurácia comparável (AUC ≈ 0.90)',
    '✓  Regras linguísticas auditáveis',
    '✓  Parâmetros com significado físico',
    '✓  13× menos parâmetros que MLP',
    '?  Treinamento mais lento',
], Inches(6.8), Inches(2.2), Inches(5.0), Inches(3.5), size=14, color=PRETO)

# Seta central
_add_textbox(s, '←  vs  →', Inches(5.6), Inches(3.5), Inches(1.2), Inches(0.5),
             size=18, bold=True, color=CINZA, align=PP_ALIGN.CENTER)


# ---- Slide 4 — Roteiro ------------------------------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Estrutura da Apresentação')
_footer(s)

items = [
    '1.  Framework Teórico — Sistemas Fuzzy TS e arquitetura ANFIS',
    '2.  Dataset e Configuração Experimental',
    '3.  Pipeline de Geração de Regras via K-Means',
    '4.  Resultados: Métricas, MFs Aprendidas e Regras Extraídas',
    '5.  Análise Comparativa ANFIS × MLP',
    '6.  Conclusões e Trabalho Futuro',
]
_bullets(s, items, Inches(1.5), Inches(1.6), W - Inches(2.0), Inches(5.5),
         size=17, color=PRETO)


# ---- Slide 5 — Framework Teórico -------------------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Framework Teórico: ANFIS como TS Treinável')
_footer(s)

# Pipeline ANFIS
boxes = [
    ('Entrada\n[batch, n_feat]',    Inches(0.3),  AZUL),
    ('MixedFuzzyLayer\n[batch, n_feat, max_mfs]', Inches(2.5), ROXO),
    ('ClusterRuleLayer\n[batch, n_rules]',         Inches(5.1), ROXO),
    ('DefuzzyLayer\n[batch, 1]',    Inches(7.7),  ROXO),
    ('Sigmoid\n→ P(doença)',        Inches(10.3), VERDE),
]
for label, x, color in boxes:
    b = _add_rect(s, x, Inches(2.0), Inches(2.0), Inches(1.2), color)
    _tf(b, label, 10, bold=True, color=BRANCO, align=PP_ALIGN.CENTER)
    # seta
    if x < Inches(10.3):
        _add_textbox(s, '→', x + Inches(2.0), Inches(2.4), Inches(0.5), Inches(0.4),
                     size=18, bold=True, color=CINZA, align=PP_ALIGN.CENTER)

_bullets(s, [
    'MixedFuzzyLayer  — MFs Gaussianas treináveis (numéricas) + one-hot suavizado (categóricas)',
    'ClusterRuleLayer — T-norma produto sobre combinações de MFs geradas por K-Means',
    'DefuzzyLayer     — nn.Linear(n_regras → 1): pesos = consequentes Takagi-Sugeno',
    'Loss: BCEWithLogits + penalidade de separação de centros (evita MFs sobrepostas)',
], Inches(0.5), Inches(3.5), W - Inches(1.0), Inches(3.5), size=13, color=PRETO)


# ---- Slide 6 — Dataset e configuração --------------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Dataset e Configuração Experimental')
_footer(s)

# Coluna esquerda
_add_textbox(s, 'Heart Failure Prediction Dataset', Inches(0.5), Inches(1.5),
             Inches(6.0), Inches(0.45), size=14, bold=True, color=AZUL_ESC)
_bullets(s, [
    '918 pacientes adultos',
    'Variável alvo: HeartDisease (0/1) — prevalência 55%',
    'Split: 80% treino / 20% teste',
    '',
    'Features numéricas (5):',
    '   Age, RestingBP, Cholesterol, MaxHR, Oldpeak',
    '',
    'Features categóricas (6):',
    '   Sex, ChestPainType, FastingBS,',
    '   RestingECG, ExerciseAngina, ST_Slope',
], Inches(0.5), Inches(2.0), Inches(6.2), Inches(5.0), size=13, color=PRETO)

# Coluna direita — configuração
_add_textbox(s, 'Configuração do Experimento', Inches(7.0), Inches(1.5),
             Inches(5.5), Inches(0.45), size=14, bold=True, color=AZUL_ESC)
_bullets(s, [
    'NUM_MFS = 3  (baixo / médio / alto)',
    'ANFIS_N_CLUSTERS = 200',
    'Épocas ANFIS = 200  |  Épocas MLP = 200',
    'Batch size = 32  |  lr = 1e-3  (Adam)',
    'MLP: [64, 32] neurônios ocultos',
    '',
    'Pré-processamento:',
    '   PartialScaler — z-score apenas nas numéricas',
    '   Categóricas: códigos inteiros preservados',
], Inches(7.0), Inches(2.0), Inches(5.8), Inches(5.0), size=13, color=PRETO)


# ---- Slide 7 — Pipeline de regras K-Means ----------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Geração de Regras: K-Means como Inicializador')
_footer(s)

_bullets(s, [
    '1.  K-Means (200 clusters) particiona o espaço de entrada em regiões densas',
    '2.  Para cada centro de cluster → mapeamento de MF dominante por feature:',
    '       • Numérica:   argmax da MF triangular (picos = percentis da distribuição)',
    '       • Categórica: arredondamento para código inteiro',
    '3.  Deduplicação: clusters com mesmo padrão de MFs → uma única regra',
    '4.  Resultado: pool de N regras únicas como esqueleto antecedente do ANFIS',
    '5.  Centros Gaussianos do ANFIS inicializados nos percentis dos centros K-Means',
    '6.  ANFIS refina centros, variâncias e pesos consequentes via backpropagation',
], Inches(0.6), Inches(1.5), W - Inches(1.2), Inches(5.5), size=15, color=PRETO)


# ---- Slide 8 — Resultados: Métricas ----------------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Resultados: Métricas de Desempenho')
_footer(s)

# Tabela manual
rows = [
    ('Modelo',       'Parâmetros', 'Treino (s)', 'Acurácia', 'F1-Score', 'AUC-ROC'),
    ('ANFIS',        '228',        '13,8 s',     '83,2 %',   '84,7 %',  '0,903'),
    ('MLP',          '2.881',      '4,6 s',      '83,7 %',   '85,0 %',  '0,910'),
]
cols_x = [Inches(0.4), Inches(2.5), Inches(4.3), Inches(6.1), Inches(8.1), Inches(10.2)]
col_w  = [Inches(2.0), Inches(1.7), Inches(1.7), Inches(1.9), Inches(2.0), Inches(2.0)]
row_h  = Inches(0.75)
row_y  = [Inches(1.7), Inches(2.55), Inches(3.35)]

for ri, row in enumerate(rows):
    bg = AZUL_ESC if ri == 0 else (CINZA_CLR if ri % 2 == 0 else BRANCO)
    fg = BRANCO   if ri == 0 else PRETO
    for ci, (cell, cx, cw) in enumerate(zip(row, cols_x, col_w)):
        b = _add_rect(s, cx, row_y[ri], cw - Inches(0.05), row_h - Inches(0.05), bg)
        _tf(b, cell, 14, bold=(ri == 0), color=fg, align=PP_ALIGN.CENTER)

# Destaques abaixo da tabela
_bullets(s, [
    '▸  ANFIS atinge AUC 0,903 com apenas 228 parâmetros treináveis',
    '▸  MLP precisa de 13× mais parâmetros para ganhar apenas 0,007 de AUC',
    '▸  Diferença de acurácia e F1 é estatisticamente negligenciável',
], Inches(0.7), Inches(4.4), W - Inches(1.4), Inches(2.6), size=15, color=PRETO)


# ---- Slide 9 — MFs Aprendidas ----------------------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Funções de Pertinência Aprendidas pelo ANFIS')
_footer(s)
_add_image(s, os.path.join(RESULTS_DIR, 'mfs_anfis.png'),
           Inches(0.3), Inches(1.4), W - Inches(0.6), Inches(5.7))


# ---- Slide 10 — Regras extraídas -------------------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Regras Linguísticas Extraídas (Top-5 por Ativação)')
_footer(s)

_bullets(s, [
    'Regra 1 (alto risco):',
    '   SE Age=idoso E ChestPainType=ASY E MaxHR=baixa E ExerciseAngina=Y',
    '   E Oldpeak=elevado E ST_Slope=Flat  →  ENTÃO risco = ALTO',
    '',
    'Regra 2 (baixo risco):',
    '   SE Age=jovem E ChestPainType=ATA E MaxHR=alta E ExerciseAngina=N',
    '   E Oldpeak=normal E ST_Slope=Up  →  ENTÃO risco = BAIXO',
    '',
    'Regra 3 (alto risco):',
    '   SE Age=idoso E ChestPainType=ASY E Cholesterol=desejável',
    '   E ExerciseAngina=Y E ST_Slope=Flat  →  ENTÃO risco = ALTO',
], Inches(0.7), Inches(1.5), W - Inches(1.4), Inches(5.6), size=13, color=PRETO)


# ---- Slide 11 — Comparação de risco ----------------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Comparação de Risco: ANFIS vs MLP por Paciente')
_footer(s)
_add_image(s, os.path.join(RESULTS_DIR, 'risk_comparison.png'),
           Inches(0.3), Inches(1.4), W - Inches(0.6), Inches(5.7))


# ---- Slide 12 — Análise crítica --------------------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Análise: ANFIS como Alternativa Interpretável ao MLP')
_footer(s)

# Caixa de destaque
h = _add_rect(s, Inches(0.5), Inches(1.6), W - Inches(1.0), Inches(1.0), VERDE_CLR)
_tf(h, 'ANFIS perde apenas 0,007 de AUC em relação ao MLP, com 13× menos parâmetros'
       ' e regras linguísticas auditáveis.',
    15, bold=True, color=VERDE, align=PP_ALIGN.CENTER)

_bullets(s, [
    'Eficiência paramétrica:',
    '   228 vs 2.881 parâmetros — MFs e pesos têm interpretação direta',
    '',
    'Interpretabilidade genuína:',
    '   Centros Gaussianos treinados revelam os limiares clínicos aprendidos',
    '   ST_Slope=Flat + ExerciseAngina=Y + Oldpeak elevado → padrão de alto risco',
    '',
    'Tradeoff de velocidade:',
    '   ANFIS: 13,8 s (200 épocas) vs MLP: 4,6 s — aceitável em produção offline',
], Inches(0.7), Inches(2.8), W - Inches(1.4), Inches(4.2), size=14, color=PRETO)


# ---- Slide 13 — Análise: pontos de atenção ---------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Pontos de Atenção e Limitações')
_footer(s)

_bullets(s, [
    '1.  Explosão de regras',
    '       n_regras = n_mfs^n_inputs → inviável sem seleção de features',
    '       Solução aplicada: K-Means como filtro + deduplicação de combos',
    '',
    '2.  Features categóricas em sistemas fuzzy',
    '       Não existe "grau de pertinência" natural entre categorias discretas',
    '       MixedFuzzyLayer usa one-hot suavizado como aproximação',
    '',
    '3.  Sensibilidade à inicialização',
    '       K-Means determinístico com semente fixa — resultados podem variar',
    '       Penalidade de separação mitiga colapso de MFs durante treino',
], Inches(0.7), Inches(1.55), W - Inches(1.4), Inches(5.5), size=14, color=PRETO)


# ---- Slide 14 — Conclusões -------------------------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Conclusões')
_footer(s)

_bullets(s, [
    '✅  ANFIS atinge AUC 0,903 — comparável ao MLP (0,910) neste dataset',
    '✅  228 parâmetros treináveis vs 2.881 do MLP (13× mais eficiente)',
    '✅  Regras linguísticas auditáveis por especialistas médicos',
    '✅  Pipeline reproduzível: K-Means → inicialização → treino end-to-end',
    '',
    '→  ANFIS é uma alternativa viável quando interpretabilidade é requisito,',
    '    sem sacrifício significativo de desempenho preditivo.',
], Inches(0.8), Inches(1.6), W - Inches(1.6), Inches(5.5), size=16, color=PRETO)


# ---- Slide 15 — Trabalho Futuro --------------------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Limitações e Trabalho Futuro')
_footer(s)

_bullets(s, [
    'Limitações atuais:',
    '   • Testado em um único dataset (Heart Failure, 918 amostras)',
    '   • Features categóricas sem MFs formalmente definidas',
    '   • Tempo de treino superior ao MLP',
    '',
    'Próximos passos:',
    '   • Validar em datasets maiores e multi-classe',
    '   • Incorporar conhecimento especialista na inicialização das MFs',
    '   • Comparar com XGBoost + SHAP como baseline explicável',
    '   • Interface de extração de regras em linguagem natural',
], Inches(0.7), Inches(1.55), W - Inches(1.4), Inches(5.5), size=14, color=PRETO)


# ---- Slide 16 — Obrigado ---------------------------------------------------
s = prs.slides.add_slide(blank)
_add_rect(s, Inches(0), Inches(0), W, H, AZUL_ESC)
_add_rect(s, Inches(0), Inches(2.8), W, Inches(2.0), AZUL)

_add_textbox(s, 'Obrigado!',
             Inches(0.6), Inches(2.9), W - Inches(1.2), Inches(1.1),
             size=48, bold=True, color=BRANCO, align=PP_ALIGN.CENTER)

_add_textbox(s, 'victor.m.bertini@gmail.com',
             Inches(0.6), Inches(5.0), W - Inches(1.2), Inches(0.5),
             size=16, color=CINZA_CLR, align=PP_ALIGN.CENTER)

_add_textbox(s, 'github.com/vm-bertini/Fuzzy-Projeto-Final',
             Inches(0.6), Inches(5.5), W - Inches(1.2), Inches(0.5),
             size=14, color=CINZA_CLR, align=PP_ALIGN.CENTER)

_add_textbox(s,
    '"ANFIS: interpretabilidade sem sacrificar performance"',
    Inches(0.6), Inches(6.2), W - Inches(1.2), Inches(0.5),
    size=14, color=BRANCO, align=PP_ALIGN.CENTER, italic=True)


# ---- Slide 17 (Apêndice) — Matriz de Confusão ------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Apêndice — Matriz de Confusão')
_footer(s)
_add_image(s, os.path.join(RESULTS_DIR, 'confusion_matrix.png'),
           Inches(1.0), Inches(1.4), W - Inches(2.0), Inches(5.7))


# ---- Slide 18 (Apêndice) — Heatmap de Regras ------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Apêndice — Heatmap das Regras ANFIS')
_footer(s)
_add_image(s, os.path.join(RESULTS_DIR, 'rule_comparison.png'),
           Inches(0.3), Inches(1.4), W - Inches(0.6), Inches(5.7))


# ---- Slide 19 (Apêndice) — K-Means partition ------------------------------
s = prs.slides.add_slide(blank)
_header(s, 'Apêndice — Partição K-Means (pré-ANFIS)')
_footer(s)
_add_image(s, os.path.join(RESULTS_DIR, 'mfs_kmeans.png'),
           Inches(0.3), Inches(1.4), W - Inches(0.6), Inches(5.7))


# ---------------------------------------------------------------------------
# Salvar
# ---------------------------------------------------------------------------
out = 'apresentacao_anfis.pptx'
prs.save(out)
print(f'Apresentação salva em: {out}  ({len(prs.slides)} slides)')
