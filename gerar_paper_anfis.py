"""
Gerador de paper IEEE — ANFIS Heart Failure Classification
Gera: anfis_paper_en.pdf  e  anfis_paper_ptbr.pdf

Layout:
  Página 1  — coluna única (título + abstract)
  Páginas 2+ — duas colunas (corpo do paper)

Fontes: Times New Roman TTF (suporte Unicode completo — gregos, ∏, Σ, etc.)
Subscripts via tag <sub> do reportlab (sem artefato de caixa preta com TTF).
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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from PIL import Image as PILImage

# ---------------------------------------------------------------------------
# Registrar Times New Roman (TTF) — suporte a Unicode completo
# ---------------------------------------------------------------------------
_FD = 'C:/Windows/Fonts'
pdfmetrics.registerFont(TTFont('TNR',    f'{_FD}/times.ttf'))
pdfmetrics.registerFont(TTFont('TNR-B',  f'{_FD}/timesbd.ttf'))
pdfmetrics.registerFont(TTFont('TNR-I',  f'{_FD}/timesi.ttf'))
pdfmetrics.registerFont(TTFont('TNR-BI', f'{_FD}/timesbi.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('TNR', normal='TNR', bold='TNR-B', italic='TNR-I', boldItalic='TNR-BI')

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
PW, PH  = LETTER                       # 612 × 792 pt
ML = MR = 0.75 * inch
MT      = 0.75 * inch
MB      = 1.00 * inch
GUTTER  = 0.22 * inch
BODY_W  = PW - ML - MR                # 468 pt ≈ 6.5 in  (page 1 single col)
COL_W   = (BODY_W - GUTTER) / 2      # two-col width
BODY_H  = PH - MT - MB

RES = os.path.join('src', 'results', '2026_06_23_03_55')

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def make_styles():
    S = {}
    S['title']        = ParagraphStyle('title',  fontName='TNR-B',  fontSize=16, leading=20, alignment=TA_CENTER, spaceAfter=4)
    S['authors']      = ParagraphStyle('auth',   fontName='TNR-B',  fontSize=10, leading=13, alignment=TA_CENTER, spaceAfter=2)
    S['affil']        = ParagraphStyle('affil',  fontName='TNR-I',  fontSize=9,  leading=11, alignment=TA_CENTER, spaceAfter=6)
    S['abstract']     = ParagraphStyle('abs',    fontName='TNR',    fontSize=9,  leading=12, alignment=TA_JUSTIFY, spaceAfter=4, leftIndent=18, rightIndent=18)
    S['keywords']     = ParagraphStyle('kw',     fontName='TNR',    fontSize=9,  leading=11, alignment=TA_JUSTIFY, spaceAfter=6, leftIndent=18, rightIndent=18)
    S['body']         = ParagraphStyle('body',   fontName='TNR',    fontSize=10, leading=13, alignment=TA_JUSTIFY, spaceAfter=4)
    S['section']      = ParagraphStyle('sec',    fontName='TNR-B',  fontSize=10, leading=13, alignment=TA_CENTER, spaceBefore=8, spaceAfter=4)
    S['subsection']   = ParagraphStyle('sub',    fontName='TNR-I',  fontSize=10, leading=13, alignment=TA_LEFT,   spaceBefore=5, spaceAfter=3)
    S['caption']      = ParagraphStyle('cap',    fontName='TNR',    fontSize=8,  leading=10, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)
    S['eq']           = ParagraphStyle('eq',     fontName='TNR-I',  fontSize=10, leading=14, alignment=TA_CENTER, spaceBefore=3, spaceAfter=3)
    S['th']           = ParagraphStyle('th',     fontName='TNR-B',  fontSize=9,  leading=11, alignment=TA_CENTER)
    S['tb']           = ParagraphStyle('tb',     fontName='TNR',    fontSize=9,  leading=11, alignment=TA_CENTER)
    S['tbl']          = ParagraphStyle('tbl',    fontName='TNR',    fontSize=9,  leading=11, alignment=TA_LEFT)
    return S

S = make_styles()

def p(text, style='body'):  return Paragraph(text, S[style])
def sp(h=4):                return Spacer(1, h)
def hr():                   return HRFlowable(width='100%', thickness=0.5, color=colors.black, spaceAfter=4, spaceBefore=4)
def eq(text):               return p(text, 'eq')
def sec(num, title):        return p(f'{num}. {title.upper()}', 'section')
def subsec(l, title):       return p(f'<i>{l}. {title}</i>', 'subsection')

def embed_fig(path, caption, label, width=None):
    w = width or COL_W * 0.98
    elems = []
    if os.path.exists(path):
        im  = PILImage.open(path)
        h   = w * im.size[1] / im.size[0]
        elems.append(Image(path, width=w, height=h))
    else:
        elems.append(p(f'[{caption}]', 'caption'))
    elems.append(p(f'<b>Fig. {label}.</b> {caption}', 'caption'))
    return elems

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 8)
    canvas.drawCentredString(PW / 2, 0.5 * inch, str(doc.page))
    canvas.restoreState()

def base_tbl_style():
    return TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#2E7D32')),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.HexColor('#F5F5F5'), colors.white]),
        ('GRID',          (0,0), (-1,-1), 0.4, colors.HexColor('#BBBBBB')),
        ('TOPPADDING',    (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING',   (0,0), (-1,-1), 3),
    ])

# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
T = {}

# ===== ENGLISH ==============================================================
T['en'] = dict(
    title = ('ANFIS-Based Cardiac Risk Classification: '
             'Comparing Neuro-Fuzzy Systems and MLP '
             'for Accuracy and Interpretability'),
    affil = ('School of Electrical and Computer Engineering (FEEC) — '
             'University of Campinas (Unicamp)<br/>'
             'Campinas, SP, Brazil · RA 194761 · v194761@dac.unicamp.com.br'),
    abstract = (
        '<b>Abstract</b>—This paper investigates the tradeoff between predictive '
        'accuracy and interpretability in machine learning models applied to cardiac '
        'risk classification. We propose an ANFIS (Adaptive Neuro-Fuzzy Inference '
        'System) with Takagi-Sugeno zero-order inference and mixed '
        'fuzzification—Gaussian membership functions for numerical variables and '
        'smoothed one-hot encoding for categorical variables—whose rule pool is '
        'generated via K-Means clustering. Experiments on the Heart Failure Prediction '
        'Dataset (918 patients, 11 features) show that ANFIS achieves AUC-ROC 0.912, '
        'accuracy 84.2%, and F1-Score 85.9%, outperforming the MLP baseline '
        '(AUC 0.901; accuracy 81.5%; F1 82.5%) with only 228 trainable parameters '
        'versus 2,881 in the MLP. Beyond superior performance, ANFIS produces '
        '10 auditable IF-THEN linguistic rules consistent with the ischemia literature.'
    ),
    keywords = '<b>Keywords</b>—ANFIS; Fuzzy Logic; Neural Networks; Heart Disease; Interpretability; Takagi-Sugeno; K-Means',
    s1='Introduction', s2='Dataset and Preprocessing',
    s3='ANFIS Architecture', s4='Rule Pool Generation via K-Means',
    s5='Experimental Setup', s6='Results and Discussion',
    s7='Conclusion', s_ref='References',
    ss2a='Heart Failure Prediction Dataset', ss2b='Preprocessing',
    ss3a='MixedFuzzyLayer', ss3b='ClusterRuleLayer',
    ss3c='DefuzzyLayer',   ss3d='Loss Function',
    ss6a='Performance Metrics', ss6b='Learned Membership Functions',
    ss6c='Confusion Matrices',  ss6d='Extracted Linguistic Rules',
    feat_hdr  = ['Feature', 'Type', 'Description'],
    hp_hdr    = ['Parameter', 'ANFIS', 'MLP'],
    res_hdr   = ['Model', 'Params.', 'Train (s)', 'Accuracy', 'F1-Score', 'AUC-ROC'],
    rule_hdr  = ['#', 'Antecedent (abbreviated)', 'Risk'],
    cap_feat  = 'Dataset features.',
    cap_hp    = 'Experimental hyperparameters.',
    cap_res   = 'Comparative results — Heart Failure dataset, 80/20 split.',
    cap_rules = ('Top-10 ANFIS rules by mean firing strength. '
                 'CPT=ChestPainType, RBP=RestingBP, Ang=ExerciseAngina, OP=Oldpeak, FBS=FastingBS.'),
    cap_mfs   = ('Gaussian MFs learned by ANFIS after training '
                 '(numerical features) and fixed triangular output MFs.'),
    cap_cm    = 'Confusion matrices on the test set: ANFIS (left) and MLP (right).',
    feat_rows = [
        ('Age',            'Numerical',   'Patient age (years)'),
        ('RestingBP',      'Numerical',   'Resting blood pressure (mmHg); zeros replaced by median'),
        ('Cholesterol',    'Numerical',   'Serum cholesterol (mg/dL); zeros replaced by median'),
        ('MaxHR',          'Numerical',   'Maximum heart rate achieved (bpm)'),
        ('Oldpeak',        'Numerical',   'ST segment depression induced by exercise (mm)'),
        ('Sex',            'Categorical', 'M / F'),
        ('ChestPainType',  'Categorical', 'ATA / NAP / ASY / TA'),
        ('FastingBS',      'Categorical', 'Fasting blood sugar > 120 mg/dL: 1=yes, 0=no'),
        ('RestingECG',     'Categorical', 'Normal / ST / LVH'),
        ('ExerciseAngina', 'Categorical', 'Exercise-induced angina: Y / N'),
        ('ST_Slope',       'Categorical', 'Peak-exercise ST slope: Up / Flat / Down'),
    ],
    hp_rows = [
        ('Epochs',         '200',                '200'),
        ('Batch size',     '32',                 '32'),
        ('Learning rate',  '1e-3',               '1e-3'),
        ('Architecture',   '3 MFs, 197 rules',   '[64, 32]'),
        ('Parameters',     '228',                '2,881'),
        ('Regularization', 'Sep. penalty λ=0.1', '—'),
        ('Seed',           '42',                 '42'),
    ],
    rule_rows = [
        ('1',  'Age=young, CPT=ATA, MaxHR=high, Ang=N, OP=normal, ST=Up',           'LOW'),
        ('2',  'Age=young, CPT=ASY, MaxHR=low, Ang=Y, OP=high, ST=Flat',            'HIGH'),
        ('3',  'Age=old, CPT=ASY, ECG=ST, MaxHR=low, Ang=Y, OP=high, ST=Flat',      'HIGH'),
        ('4',  'Age=young, CPT=ATA, RBP=high, MaxHR=low, Ang=N, OP=normal, ST=Up',  'LOW'),
        ('5',  'Age=young, CPT=ATA, RBP=opt, MaxHR=low, Ang=N, OP=normal, ST=Up',   'LOW'),
        ('6',  'Age=young, Sex=F, CPT=ATA, MaxHR=low, Ang=N, OP=normal, ST=Up',     'LOW'),
        ('7',  'Age=old, CPT=ASY, ECG=LVH, MaxHR=low, Ang=Y, OP=high, ST=Flat',     'HIGH'),
        ('8',  'Age=young, CPT=NAP, MaxHR=high, Ang=N, OP=normal, ST=Up',           'LOW'),
        ('9',  'Age=young, CPT=ASY, FBS=1, MaxHR=low, Ang=N, OP=normal, ST=Flat',   'HIGH'),
        ('10', 'Age=young, CPT=ASY, RBP=high, MaxHR=low, Ang=Y, OP=high, ST=Flat',  'HIGH'),
    ],
    risk_high = 'HIGH',
    # body text
    intro = [
        ('Clinical decision support systems based on machine learning achieve high '
         'accuracy in diagnostic tasks, yet frequently operate as black boxes, '
         'producing predictions without intelligible justification [1]. In the medical '
         'context, decision traceability is both an ethical and regulatory requirement: '
         'a specialist must understand <i>why</i> a patient was flagged as high-risk '
         'in order to validate or challenge the recommendation.'),
        ('Neuro-Fuzzy systems—ANFIS in particular—combine the learning capability '
         'of neural networks with the interpretability of fuzzy inference systems [2]. '
         'Linguistic rules of the form IF <i>antecedent</i> THEN <i>consequent</i> '
         'allow clinicians and auditors to inspect decision criteria without '
         'requiring machine learning expertise.'),
        ('This paper contributes: (i) an ANFIS architecture with mixed fuzzification '
         'to handle numerical and categorical features in a unified pipeline; '
         '(ii) a K-Means-based rule pool generation method that scales to datasets '
         'with multiple categorical variables; and (iii) a quantitative comparison '
         'with an MLP on the Heart Failure Prediction Dataset [3], showing that '
         'ANFIS outperforms the MLP on all metrics with 13× fewer parameters.'),
    ],
    ds_a = [
        ('The dataset combines records from five clinical sources, totalling '
         '918 adult patients. The target variable <b>HeartDisease</b> is binary '
         '(0=healthy, 1=disease) with ~55% positive prevalence. '
         'The train/test split is 80/20 with class stratification.'),
        ('The 11 features comprise 5 numerical and 6 categorical variables (Table I).'),
    ],
    ds_b = [
        ('Zero values in <b>RestingBP</b> and <b>Cholesterol</b> (clinically '
         'implausible) are replaced by the column median. Categorical features are '
         'integer-encoded via <i>pd.Categorical.codes</i>. Normalization uses a custom '
         '<b>PartialScaler</b>: z-score only on the 5 numerical features, preserving '
         'integer codes for categoricals—essential so that <i>MixedFuzzyLayer</i> '
         'can cast categorical indices without corruption.'),
    ],
    arch_intro = [
        ('The proposed ANFIS follows the zero-order Takagi-Sugeno paradigm with '
         'three trainable layers. The data flow is:'),
        'X [B,11] → MixedFuzzyLayer [B,11,M] → ClusterRuleLayer [B,R] → DefuzzyLayer [B,1] → σ → P(disease)',
        ('where B is the batch size, M the number of MFs per numerical feature, '
         'and R the number of rules in the pool.'),
    ],
    mfl = [
        ('<u>Numerical features</u> — trainable Gaussian MFs with center c and '
         'spread σ, optimized by backpropagation:'),
        'μ(x) = exp( −½ · ((x − c) / σ)² )',
        ('Spreads are clamped at σ ≥ 10⁻⁶ and initialized as '
         'σ = |𝒩(0,1)| + 0.1 to guarantee positivity.'),
        ('<u>Categorical features</u> — smoothed one-hot encoding, no trainable '
         'parameters. For a variable with n categories:'),
        'μ<sub>j</sub>(cat) = 0.95  if j = cat,   else  0.05 / (n − 1)',
        ('This provides a non-zero gradient to non-matching positions, '
         'preventing rule collapse during training.'),
    ],
    crl = [
        ('The firing strength of rule k is the product T-norm over all features:'),
        'w<sub>k</sub> = ∏<sub>i</sub> μ<sub>i,k</sub>( x<sub>i</sub> )',
        ('where combo[k,i] is the MF index of rule k in feature i. '
         'The combination table is stored as a register_buffer (automatic GPU migration). '
         'No trainable parameters.'),
    ],
    dfl = [
        ('Normalized Takagi-Sugeno defuzzification:'),
        'w̃<sub>k</sub> = w<sub>k</sub> / ( Σ<sub>j</sub> w<sub>j</sub> + ε )',
        'ŷ = Σ<sub>k</sub> w̃<sub>k</sub> · c<sub>k</sub>',
        ('The consequents c<sub>k</sub> are weights of nn.Linear(R→1). '
         'Normalization keeps output scale independent of how many rules fire '
         'simultaneously, preserving the linguistic interpretation of each c<sub>k</sub>.'),
    ],
    loss = [
        ('The loss combines binary cross-entropy with a center-separation penalty:'),
        'L = BCE( σ(ŷ), y ) + λ · Σ<sub>i&lt;j</sub> relu( σ<sub>i</sub> + σ<sub>j</sub> − |c<sub>i</sub> − c<sub>j</sub>| )',
        ('The penalty (λ=0.1) is zero when adjacent MF centers are at least '
         'σ<sub>i</sub> + σ<sub>j</sub> apart, and grows linearly otherwise, preventing a narrow MF '
         'from collapsing inside a wider one.'),
    ],
    kmeans = [
        ('The number of antecedent combinations grows exponentially: '
         'n_rules = M^n_features. '
         'For 11 features with M=3 this yields 177,147 rules—infeasible. '
         'The following five-step pipeline generates a manageable rule pool before training:'),
        ('<b>Step 1 — Percentile peaks</b> (mapping artifact only): For each '
         'numerical feature, n_mfs uniformly-spaced percentiles of the training '
         'distribution (P25, P50, P75 for M=3) serve as auxiliary triangular MF '
         'peaks for cluster-to-index mapping. These are NOT the ANFIS Gaussian MFs.'),
        ('<b>Step 2 — K-Means</b>: 200 clusters on the training feature space '
         'identify the highest-density regions.'),
        ('<b>Step 3 — Dominant MF mapping</b>: For each cluster center, '
         'the dominant MF index is: numerical → argmax of triangular MF at peaks; '
         'categorical → round(center) → integer code.'),
        ('<b>Step 4 — Deduplication</b>: Clusters with the same dominant-MF vector '
         'collapse into one rule. 200 clusters → 197 unique combinations in this run.'),
        ('<b>Step 5 — Initialization</b>: ANFIS Gaussian centers are initialized at '
         'percentiles of the K-Means cluster centers per feature, providing an '
         'informed starting point for end-to-end training.'),
    ],
    setup = [
        ('Hyperparameters are listed in Table II. Both models use the Adam optimizer '
         'with a plateau learning-rate scheduler and early stopping (patience 20 epochs).'),
        ('Evaluation metrics on the held-out test set (20%): AUC-ROC '
         '(threshold-independent), accuracy (threshold 0.5), and F1-Score '
         '(harmonic mean of precision and recall). '
         'All randomness is seeded at 42 across numpy, torch, and sklearn.'),
    ],
    res_a = [
        ('Table III summarizes the quantitative results. ANFIS outperforms the MLP '
         'on all three metrics: AUC-ROC (+0.011), Accuracy (+2.7 p.p.), F1 (+3.4 p.p.).'),
        ('Parametric efficiency is notable: 228 vs. 2,881 parameters (13× fewer), '
         'reducing overfitting risk. The trade-off is ~3× slower training '
         '(14.9 s vs. 4.8 s), acceptable for offline diagnostic use.'),
    ],
    res_b = [
        ('Fig. 1 shows post-training Gaussian MFs for all 5 numerical features. '
         'Learned centers reveal clinically coherent thresholds: in <b>Age</b>, '
         'the three MFs separate young (~40 yr), middle-aged (~55 yr), and elderly '
         '(~65 yr) patients; in <b>MaxHR</b>, the "low" MF concentrates near '
         '~120 bpm; in <b>Oldpeak</b>, the "high" MF captures depressions above '
         '~1.5 mm—the established ischemia diagnostic threshold.'),
    ],
    res_c = [
        ('ANFIS produces 18 fewer false negatives than the MLP on the test set. '
         'In clinical practice—where an undetected disease is the costlier error—'
         'this represents a meaningful diagnostic advantage and directly explains '
         'the higher F1-Score.'),
    ],
    res_d = [
        ('Table IV lists the top-10 rules by mean firing strength. '
         'Two consistent patterns emerge:'),
        ('• <b>High risk</b>: ChestPainType=ASY, low MaxHR, ExerciseAngina=Y, '
         'high Oldpeak, ST_Slope=Flat — established coronary ischemia markers [4].'),
        ('• <b>Low risk</b>: ChestPainType=ATA, high MaxHR, ExerciseAngina=N, '
         'normal Oldpeak, ST_Slope=Up — consistent with normal exercise physiology.'),
    ],
    conc = [
        ('ANFIS with mixed fuzzification and K-Means-generated rules achieves '
         'AUC-ROC 0.912 with only 228 parameters—13× fewer than the MLP—while '
         'producing 10 auditable linguistic rules that align with clinical literature.'),
        ('The genuine interpretability obtained—Gaussian centers with physical '
         'meaning, per-rule TS consequents, and intelligible IF-THEN rules—'
         'differentiates ANFIS from post-hoc methods such as SHAP, where the '
         'explanation is generated after the fact.'),
        ('<b>Future work</b>: Validate on larger and multi-class datasets; '
         'incorporate domain-expert knowledge in MF initialization; '
         'compare with classical ANFIS [2] and Mamdani systems; '
         'investigate formal MF definitions for categorical variables.'),
    ],
    refs = [
        ('[1] A. Holzinger et al., "Causability and explainability of artificial '
         'intelligence in medicine," <i>WIREs DMKD</i>, vol. 9, no. 4, 2019.'),
        ('[2] J.-S. R. Jang, "ANFIS: Adaptive-network-based fuzzy inference '
         'system," <i>IEEE Trans. SMC</i>, vol. 23, no. 3, pp. 665–685, 1993.'),
        ('[3] F. Fedesoriano, "Heart Failure Prediction Dataset," Kaggle, 2021.'),
        ('[4] R. A. Gibbons et al., "ACC/AHA 2002 Guideline Update for Exercise '
         'Testing," <i>J. Am. Coll. Cardiol.</i>, vol. 40, no. 8, 2002.'),
        ('[5] L. A. Zadeh, "Fuzzy sets," <i>Inf. Control</i>, vol. 8, no. 3, '
         'pp. 338–353, 1965.'),
        ('[6] J. C. Bezdek et al., "FCM: The fuzzy c-means clustering algorithm," '
         '<i>Comput. Geosci.</i>, vol. 10, pp. 191–203, 1984.'),
    ],
)

# ===== PORTUGUESE ===========================================================
T['ptbr'] = dict(
    title = ('Classificação de Risco Cardíaco com ANFIS: '
             'Comparação entre Sistemas Neuro-Fuzzy e MLP '
             'com Foco em Interpretabilidade'),
    affil = ('Faculdade de Engenharia Elétrica e de Computação (FEEC) — '
             'Universidade Estadual de Campinas (Unicamp)<br/>'
             'Campinas, SP, Brasil · RA 194761 · v194761@dac.unicamp.com.br'),
    abstract = (
        '<b>Resumo</b>—Este trabalho investiga o tradeoff entre acurácia preditiva e '
        'interpretabilidade em modelos de aprendizado de máquina para classificação '
        'de risco de doença cardíaca. Propomos um sistema ANFIS (Adaptive Neuro-Fuzzy '
        'Inference System) de Takagi-Sugeno com fuzzificação mista—funções Gaussianas '
        'para variáveis numéricas e codificação one-hot suavizada para variáveis '
        'categóricas—cujo pool de regras é gerado por agrupamento K-Means. '
        'Experimentos no Heart Failure Prediction Dataset (918 pacientes, 11 features) '
        'mostram que o ANFIS atinge AUC-ROC 0,912, acurácia 84,2% e F1-Score 85,9%, '
        'superando o MLP baseline (AUC 0,901; acurácia 81,5%; F1 82,5%) com apenas '
        '228 parâmetros treináveis frente a 2.881 do MLP. O ANFIS produz ainda '
        '10 regras linguísticas SE-ENTÃO auditáveis alinhadas à literatura sobre isquemia.'
    ),
    keywords = '<b>Palavras-chave</b>—ANFIS; Lógica Fuzzy; Redes Neurais; Doença Cardíaca; Interpretabilidade; Takagi-Sugeno; K-Means',
    s1='Introdução', s2='Dataset e Pré-Processamento',
    s3='Arquitetura ANFIS', s4='Geração do Pool de Regras via K-Means',
    s5='Configuração Experimental', s6='Resultados e Discussão',
    s7='Conclusão', s_ref='Referências',
    ss2a='Heart Failure Prediction Dataset', ss2b='Pré-Processamento',
    ss3a='MixedFuzzyLayer', ss3b='ClusterRuleLayer',
    ss3c='DefuzzyLayer',   ss3d='Função de Perda',
    ss6a='Métricas de Desempenho', ss6b='Funções de Pertinência Aprendidas',
    ss6c='Matrizes de Confusão',   ss6d='Regras Linguísticas Extraídas',
    feat_hdr  = ['Feature', 'Tipo', 'Descrição'],
    hp_hdr    = ['Parâmetro', 'ANFIS', 'MLP'],
    res_hdr   = ['Modelo', 'Parâm.', 'Treino (s)', 'Acurácia', 'F1-Score', 'AUC-ROC'],
    rule_hdr  = ['#', 'Antecedente (abreviado)', 'Risco'],
    cap_feat  = 'Features do dataset.',
    cap_hp    = 'Hiperparâmetros experimentais.',
    cap_res   = 'Resultados comparativos — Heart Failure, split 80/20.',
    cap_rules = ('Top-10 regras ANFIS por força de disparo média. '
                 'CPT=ChestPainType, RBP=RestingBP, Ang=ExerciseAngina, OP=Oldpeak, FBS=FastingBS.'),
    cap_mfs   = ('MFs Gaussianas aprendidas pelo ANFIS após treinamento '
                 '(features numéricas) e MFs triangulares de saída (fixas).'),
    cap_cm    = 'Matrizes de confusão no conjunto de teste: ANFIS (esq.) e MLP (dir.).',
    feat_rows = [
        ('Age',            'Numérica',   'Idade do paciente (anos)'),
        ('RestingBP',      'Numérica',   'Pressão arterial em repouso (mmHg); zeros → mediana'),
        ('Cholesterol',    'Numérica',   'Colesterol sérico (mg/dL); zeros → mediana'),
        ('MaxHR',          'Numérica',   'Frequência cardíaca máxima atingida (bpm)'),
        ('Oldpeak',        'Numérica',   'Depressão do segmento ST por exercício (mm)'),
        ('Sex',            'Categórica', 'M / F'),
        ('ChestPainType',  'Categórica', 'ATA / NAP / ASY / TA'),
        ('FastingBS',      'Categórica', 'Glicemia em jejum > 120 mg/dL: 1=sim, 0=não'),
        ('RestingECG',     'Categórica', 'Normal / ST / LVH'),
        ('ExerciseAngina', 'Categórica', 'Angina por exercício: Y / N'),
        ('ST_Slope',       'Categórica', 'Inclinação do ST: Up / Flat / Down'),
    ],
    hp_rows = [
        ('Épocas',         '200',                  '200'),
        ('Batch size',     '32',                   '32'),
        ('Learning rate',  '1e-3',                 '1e-3'),
        ('Arquitetura',    '3 MFs, 197 regras',    '[64, 32]'),
        ('Parâmetros',     '228',                  '2.881'),
        ('Regularização',  'Sep. penalty λ=0,1',   '—'),
        ('Semente',        '42',                   '42'),
    ],
    rule_rows = [
        ('1',  'Age=jovem, CPT=ATA, MaxHR=alta, Ang=N, OP=normal, ST=Up',              'BAIXO'),
        ('2',  'Age=jovem, CPT=ASY, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat',          'ALTO'),
        ('3',  'Age=idoso, CPT=ASY, ECG=ST, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat',  'ALTO'),
        ('4',  'Age=jovem, CPT=ATA, RBP=elevado, MaxHR=baixa, Ang=N, OP=normal, ST=Up','BAIXO'),
        ('5',  'Age=jovem, CPT=ATA, RBP=otimo, MaxHR=baixa, Ang=N, OP=normal, ST=Up',  'BAIXO'),
        ('6',  'Age=jovem, Sex=F, CPT=ATA, MaxHR=baixa, Ang=N, OP=normal, ST=Up',      'BAIXO'),
        ('7',  'Age=idoso, CPT=ASY, ECG=LVH, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat', 'ALTO'),
        ('8',  'Age=jovem, CPT=NAP, MaxHR=alta, Ang=N, OP=normal, ST=Up',              'BAIXO'),
        ('9',  'Age=jovem, CPT=ASY, FBS=1, MaxHR=baixa, Ang=N, OP=normal, ST=Flat',    'ALTO'),
        ('10', 'Age=jovem, CPT=ASY, RBP=elevado, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat','ALTO'),
    ],
    risk_high = 'ALTO',
    intro = [
        ('Sistemas de apoio a decisão clínica baseados em aprendizado de máquina '
         'atingem alta acurácia em tarefas de diagnóstico, porém frequentemente '
         'operam como caixas-pretas, fornecendo predições sem justificativa '
         'inteligível [1]. No contexto médico, a rastreabilidade das decisões é '
         'tanto um requisito ético quanto regulatório.'),
        ('Sistemas Neuro-Fuzzy—em particular o ANFIS—combinam a capacidade de '
         'aprendizado de redes neurais com a interpretabilidade de sistemas de '
         'inferência fuzzy [2]. Regras do tipo SE <i>antecedente</i> ENTÃO '
         '<i>consequente</i> permitem que clínicos e auditores inspecionem os '
         'critérios decisórios sem expertise em aprendizado de máquina.'),
        ('Este trabalho apresenta: (i) arquitetura ANFIS com fuzzificação mista '
         'para features numéricas e categóricas; (ii) método de geração de pool '
         'de regras por K-Means escalável para múltiplas variáveis categóricas; '
         'e (iii) comparação quantitativa com MLP no Heart Failure Prediction '
         'Dataset [3], demonstrando que o ANFIS supera o MLP com 13× menos parâmetros.'),
    ],
    ds_a = [
        ('O dataset combina registros de cinco fontes clínicas, totalizando '
         '918 pacientes adultos. A variável alvo <b>HeartDisease</b> é binária '
         '(0=saudável, 1=doença) com ~55% de positivos. '
         'Split 80/20 com estratificação por classe.'),
        ('As 11 features compreendem 5 numéricas e 6 categóricas (Tabela I).'),
    ],
    ds_b = [
        ('Valores zerados em <b>RestingBP</b> e <b>Cholesterol</b> são substituídos '
         'pela mediana das entradas não-nulas. Features categóricas são codificadas '
         'como inteiros via <i>pd.Categorical.codes</i>. A normalização usa um '
         '<b>PartialScaler</b> customizado: z-score somente nas 5 features numéricas, '
         'preservando os códigos inteiros das categóricas—essencial para que '
         '<i>MixedFuzzyLayer</i> faça o cast correto dos índices categóricos.'),
    ],
    arch_intro = [
        ('O modelo ANFIS segue o paradigma Takagi-Sugeno de ordem zero com '
         'três camadas treináveis encadeadas. O fluxo de dados é:'),
        'X [B,11] → MixedFuzzyLayer [B,11,M] → ClusterRuleLayer [B,R] → DefuzzyLayer [B,1] → σ → P(doença)',
        ('onde B é o batch size, M o número de MFs por feature numérica '
         'e R o número de regras no pool.'),
    ],
    mfl = [
        ('<u>Features numéricas</u> — MFs Gaussianas treináveis com centro c e '
         'dispersão σ, otimizados por retropropagação:'),
        'μ(x) = exp( −½ · ((x − c) / σ)² )',
        ('Dispersões são clampeadas em σ ≥ 10⁻⁶ e inicializadas como '
         'σ = |𝒩(0,1)| + 0,1 para garantir positividade.'),
        ('<u>Features categóricas</u> — codificação one-hot suavizada, sem '
         'parâmetros treináveis. Para uma variável com n categorias:'),
        'μ<sub>j</sub>(cat) = 0,95  se j = cat,   caso contrário  0,05 / (n − 1)',
        ('Fornece gradiente não-nulo às posições não-correspondentes, '
         'evitando colapso de regras no treinamento.'),
    ],
    crl = [
        ('A força de disparo da regra k é a T-norma produto sobre todas as features:'),
        'w<sub>k</sub> = ∏<sub>i</sub> μ<sub>i,k</sub>( x<sub>i</sub> )',
        ('onde combo[k,i] é o índice da MF da regra k na feature i. '
         'A tabela de combinações é armazenada como register_buffer (migração '
         'automática para GPU). Sem parâmetros treináveis.'),
    ],
    dfl = [
        ('Defuzzificação Takagi-Sugeno normalizada:'),
        'w̃<sub>k</sub> = w<sub>k</sub> / ( Σ<sub>j</sub> w<sub>j</sub> + ε )',
        'ŷ = Σ<sub>k</sub> w̃<sub>k</sub> · c<sub>k</sub>',
        ('Os consequentes c<sub>k</sub> são pesos de nn.Linear(R→1). '
         'A normalização mantém a escala da saída independente do número de regras '
         'que disparam simultaneamente, preservando a interpretação linguística de c<sub>k</sub>.'),
    ],
    loss = [
        ('A função de perda combina entropia cruzada binária com penalidade de separação:'),
        'L = BCE( σ(ŷ), y ) + λ · Σ<sub>i&lt;j</sub> relu( σ<sub>i</sub> + σ<sub>j</sub> − |c<sub>i</sub> − c<sub>j</sub>| )',
        ('A penalidade (λ=0,1) é zero quando centros adjacentes estão '
         'afastados por pelo menos σ<sub>i</sub> + σ<sub>j</sub>, e cresce linearmente caso contrário, '
         'impedindo que uma MF estreita fique contida dentro de outra mais larga.'),
    ],
    kmeans = [
        ('O número de combinações de antecedentes cresce exponencialmente: '
         'n_regras = M^n_features. Para 11 features com M=3 seriam 177.147 '
         'regras—inviável. O pipeline a seguir gera um pool gerenciável antes do treino:'),
        ('<b>Passo 1 — Picos percentílicos</b> (artifício de mapeamento): Para cada '
         'feature numérica, n_mfs percentis uniformes da distribuição de treino '
         '(P25, P50, P75 para M=3) servem de picos de MFs triangulares auxiliares '
         'para o mapeamento cluster→índice. NÃO são as MFs Gaussianas do ANFIS.'),
        ('<b>Passo 2 — K-Means</b>: 200 clusters no espaço de features identificam '
         'as regiões de maior densidade.'),
        ('<b>Passo 3 — Mapeamento dominante</b>: Para cada centro de cluster, '
         'determina-se o índice de MF dominante: numérica → argmax da MF triangular; '
         'categórica → round(centro) → código inteiro.'),
        ('<b>Passo 4 — Deduplicação</b>: Clusters com o mesmo vetor dominante '
         'colapsam em uma regra. 200 clusters → 197 combos únicos nesta execução.'),
        ('<b>Passo 5 — Inicialização</b>: Centros Gaussianos do ANFIS são '
         'inicializados nos percentis dos centros K-Means por feature.'),
    ],
    setup = [
        ('Os hiperparâmetros estão na Tabela II. Ambos os modelos usam otimizador '
         'Adam com scheduler de plateau e early stopping com paciência de 20 épocas.'),
        ('Métricas avaliadas no conjunto de teste (20%): AUC-ROC '
         '(independente de limiar), acurácia (limiar 0,5) e F1-Score '
         '(média harmônica de precisão e revocação). '
         'Aleatoriedade controlada pela semente 42 em numpy, torch e sklearn.'),
    ],
    res_a = [
        ('A Tabela III apresenta os resultados quantitativos. O ANFIS supera o MLP '
         'em todas as métricas: AUC-ROC (+0,011), Acurácia (+2,7 p.p.), F1 (+3,4 p.p.).'),
        ('Eficiência paramétrica: 228 vs. 2.881 parâmetros (13× menos), reduzindo '
         'o risco de overfitting. Custo: treinamento ~3× mais lento (14,9 s vs. 4,8 s), '
         'aceitável para diagnóstico offline.'),
    ],
    res_b = [
        ('A Fig. 1 mostra as MFs Gaussianas pós-treinamento para as 5 features '
         'numéricas. Os centros revelam limiares clinicamente coerentes: em '
         '<b>Age</b>, as três MFs separam jovens (~40 anos), meia-idade (~55) e '
         'idosos (~65); em <b>MaxHR</b>, a MF "baixa" concentra-se em ~120 bpm; '
         'em <b>Oldpeak</b>, a MF "elevado" captura depressões acima de ~1,5 mm, '
         'alinhado ao critério diagnóstico de isquemia.'),
    ],
    res_c = [
        ('O ANFIS produz 18 falsos negativos a menos que o MLP no conjunto de teste. '
         'Em contexto clínico—onde doença não detectada é o erro mais custoso—'
         'isso representa uma vantagem diagnóstica significativa.'),
    ],
    res_d = [
        ('A Tabela IV lista as top-10 regras por força de disparo média. '
         'Dois padrões emergem consistentemente:'),
        ('• <b>Alto risco</b>: CPT=ASY, MaxHR baixa, Ang=Y, OP elevado, ST=Flat '
         '— marcadores estabelecidos de isquemia coronariana [4].'),
        ('• <b>Baixo risco</b>: CPT=ATA, MaxHR alta, Ang=N, OP normal, ST=Up '
         '— compatível com resposta fisiológica normal ao esforço.'),
    ],
    conc = [
        ('O ANFIS com fuzzificação mista e pool de regras por K-Means atinge '
         'AUC-ROC 0,912 com apenas 228 parâmetros—13× menos que o MLP—e produz '
         '10 regras linguísticas auditáveis alinhadas à literatura clínica.'),
        ('A interpretabilidade genuína—centros Gaussianos com significado físico, '
         'consequentes TS por regra, e regras SE-ENTÃO inteligíveis—diferencia o '
         'ANFIS de métodos post-hoc como SHAP, onde a explicação é gerada após o fato.'),
        ('<b>Trabalho futuro</b>: Validar em datasets maiores e multi-classe; '
         'incorporar conhecimento de especialistas na inicialização das MFs; '
         'comparar com ANFIS clássico [2] e sistemas Mamdani; investigar definições '
         'formais de MFs para variáveis categóricas.'),
    ],
    refs = [
        ('[1] A. Holzinger et al., "Causability and explainability of artificial '
         'intelligence in medicine," <i>WIREs DMKD</i>, vol. 9, no. 4, 2019.'),
        ('[2] J.-S. R. Jang, "ANFIS: Adaptive-network-based fuzzy inference '
         'system," <i>IEEE Trans. SMC</i>, vol. 23, no. 3, pp. 665–685, 1993.'),
        ('[3] F. Fedesoriano, "Heart Failure Prediction Dataset," Kaggle, 2021.'),
        ('[4] R. A. Gibbons et al., "ACC/AHA 2002 Guideline Update for Exercise '
         'Testing," <i>J. Am. Coll. Cardiol.</i>, vol. 40, no. 8, 2002.'),
        ('[5] L. A. Zadeh, "Fuzzy sets," <i>Inf. Control</i>, vol. 8, no. 3, '
         'pp. 338–353, 1965.'),
        ('[6] J. C. Bezdek et al., "FCM: The fuzzy c-means clustering algorithm," '
         '<i>Comput. Geosci.</i>, vol. 10, pp. 191–203, 1984.'),
    ],
)

# ---------------------------------------------------------------------------
# Story builder
# ---------------------------------------------------------------------------
def build_story(lang):
    t   = T[lang]
    sto = []

    # ---- Page 1: single-column title + abstract ----------------------------
    sto += [
        NextPageTemplate('later'),   # pages 2+ → two columns
        p(t['title'], 'title'), sp(2),
        p('Victor M. Bertini', 'authors'),
        p(t['affil'], 'affil'),
        sp(4), hr(),
        p(t['abstract'], 'abstract'), sp(3),
        p(t['keywords'], 'keywords'),
        hr(),
        PageBreak(),                 # end single-column page cleanly
    ]

    # ---- Two-column body ---------------------------------------------------

    # I. Introduction
    sto += [sec('I', t['s1'])]
    for txt in t['intro']:
        sto.append(p(txt))
    sto.append(sp(2))

    # II. Dataset
    sto += [sec('II', t['s2']), subsec('A', t['ss2a'])]
    for txt in t['ds_a']:
        sto.append(p(txt))

    feat_data = [[p(h, 'th') for h in t['feat_hdr']]] + [
        [p(f, 'tb'), p(tp, 'tb'), p(d, 'tbl')] for f, tp, d in t['feat_rows']
    ]
    ft = Table(feat_data, colWidths=[COL_W*0.27, COL_W*0.22, COL_W*0.51])
    ft.setStyle(base_tbl_style())
    sto += [KeepTogether([ft, p(f'<b>TABELA I.</b> {t["cap_feat"]}', 'caption')]), sp(2)]

    sto += [subsec('B', t['ss2b'])]
    for txt in t['ds_b']:
        sto.append(p(txt))
    sto.append(sp(2))

    # III. Architecture
    sto += [sec('III', t['s3'])]
    sto.append(p(t['arch_intro'][0]))
    sto.append(eq(t['arch_intro'][1]))
    sto.append(p(t['arch_intro'][2]))
    sto += [sp(2), subsec('A', t['ss3a'])]
    mfl = t['mfl']
    sto += [p(mfl[0]), eq(mfl[1]), p(mfl[2]), p(mfl[3]), eq(mfl[4]), p(mfl[5])]
    sto += [sp(2), subsec('B', t['ss3b'])]
    crl = t['crl']
    sto += [p(crl[0]), eq(crl[1]), p(crl[2])]
    sto += [sp(2), subsec('C', t['ss3c'])]
    dfl = t['dfl']
    sto += [p(dfl[0]), eq(dfl[1]), eq(dfl[2]), p(dfl[3])]
    sto += [sp(2), subsec('D', t['ss3d'])]
    lss = t['loss']
    sto += [p(lss[0]), eq(lss[1]), p(lss[2])]
    sto.append(sp(2))

    # IV. K-Means
    sto += [sec('IV', t['s4'])]
    for txt in t['kmeans']:
        sto.append(p(txt))
    sto.append(sp(2))

    # V. Setup
    sto += [sec('V', t['s5']), p(t['setup'][0])]
    hp_data = [[p(h, 'th') for h in t['hp_hdr']]] + [
        [p(a,'tb'), p(b,'tb'), p(c,'tb')] for a, b, c in t['hp_rows']
    ]
    ht = Table(hp_data, colWidths=[COL_W*0.42, COL_W*0.30, COL_W*0.28])
    ht.setStyle(base_tbl_style())
    sto += [KeepTogether([ht, p(f'<b>TABELA II.</b> {t["cap_hp"]}', 'caption')]), sp(2)]
    sto.append(p(t['setup'][1]))
    sto.append(sp(2))

    # VI. Results
    sto += [sec('VI', t['s6']), subsec('A', t['ss6a'])]
    sto.append(p(t['res_a'][0]))

    dec = ',' if lang == 'ptbr' else '.'
    res_data = [
        [p(h, 'th') for h in t['res_hdr']],
        [p('ANFIS','tb'), p('228','tb'), p(f'14{dec}9','tb'),
         p(f'84{dec}2%','tb'), p(f'85{dec}9%','tb'), p(f'<b>0{dec}912</b>','tb')],
        [p('MLP','tb'), p('2{:s}881'.format('.' if lang=='ptbr' else ','),'tb'),
         p(f'4{dec}8','tb'), p(f'81{dec}5%','tb'),
         p(f'82{dec}5%','tb'), p(f'0{dec}901','tb')],
    ]
    rt = Table(res_data, colWidths=[COL_W*0.15, COL_W*0.14, COL_W*0.17,
                                    COL_W*0.17, COL_W*0.18, COL_W*0.19])
    rt.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#2E7D32')),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('BACKGROUND',    (0,1), (-1,1), colors.HexColor('#C8E6C9')),
        ('BACKGROUND',    (0,2), (-1,2), colors.white),
        ('GRID',          (0,0), (-1,-1), 0.4, colors.HexColor('#BBBBBB')),
        ('TOPPADDING',    (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING',   (0,0), (-1,-1), 2),
    ]))
    sto += [KeepTogether([rt, p(f'<b>TABELA III.</b> {t["cap_res"]}', 'caption')]), sp(2)]
    sto.append(p(t['res_a'][1]))

    sto += [sp(2), subsec('B', t['ss6b']), p(t['res_b'][0])]
    sto += embed_fig(os.path.join(RES, 'mfs_anfis.png'), t['cap_mfs'], '1')

    sto += [sp(2), subsec('C', t['ss6c'])]
    sto += embed_fig(os.path.join(RES, 'confusion_matrix.png'), t['cap_cm'], '2')
    sto += [sp(2), p(t['res_c'][0])]

    sto += [sp(2), subsec('D', t['ss6d'])]
    for txt in t['res_d']:
        sto.append(p(txt))

    rule_data = [[p(h, 'th') for h in t['rule_hdr']]] + [
        [p(n,'tb'), p(ante,'tbl'), p(risk,'tb')]
        for n, ante, risk in t['rule_rows']
    ]
    rk = Table(rule_data, colWidths=[COL_W*0.07, COL_W*0.77, COL_W*0.16])
    rs = base_tbl_style()
    HIGH = t['risk_high']
    for idx, (_, _, risk) in enumerate(t['rule_rows'], start=1):
        if risk == HIGH:
            rs.add('BACKGROUND', (2, idx), (2, idx), colors.HexColor('#FFCDD2'))
    rk.setStyle(rs)
    sto += [KeepTogether([rk, p(f'<b>TABELA IV.</b> {t["cap_rules"]}', 'caption')]), sp(2)]

    # VII. Conclusion
    sto += [sec('VII', t['s7'])]
    for txt in t['conc']:
        sto.append(p(txt))
    sto.append(sp(4))

    # References
    sto += [sec('', t['s_ref'])]
    for ref in t['refs']:
        sto.append(p(ref))
        sto.append(sp(2))

    return sto

# ---------------------------------------------------------------------------
# Generate PDFs
# ---------------------------------------------------------------------------
for lang, outfile in [('en', 'anfis_paper_en.pdf'), ('ptbr', 'anfis_paper_ptbr.pdf')]:
    doc = BaseDocTemplate(
        outfile, pagesize=LETTER,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
    )

    # Page 1 — single wide column
    p1_frame = Frame(ML, MB, BODY_W, BODY_H, id='p1', showBoundary=False, topPadding=0)

    # Pages 2+ — two columns
    col1 = Frame(ML,                   MB, COL_W, BODY_H, id='col1', showBoundary=False, topPadding=0)
    col2 = Frame(ML + COL_W + GUTTER,  MB, COL_W, BODY_H, id='col2', showBoundary=False, topPadding=0)

    doc.addPageTemplates([
        PageTemplate('first', [p1_frame], onPage=on_page),
        PageTemplate('later', [col1, col2], onPage=on_page),
    ])

    doc.build(build_story(lang))
    kb = round(Path(outfile).stat().st_size / 1024, 1)
    print(f'Gerado: {outfile}  ({kb} KB)')
