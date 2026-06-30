"""
Gerador de paper IEEE — ANFIS Heart Failure Classification
Gera duas versões: anfis_paper_en.pdf  e  anfis_paper_ptbr.pdf
"""
import os
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, KeepTogether,
    NextPageTemplate,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
PW, PH   = LETTER
ML = MR  = 0.70 * inch
MT       = 0.75 * inch
MB       = 1.00 * inch
GUTTER   = 0.20 * inch
BODY_W   = PW - ML - MR
COL_W    = (BODY_W - GUTTER) / 2
BODY_H   = PH - MT - MB
HEADER_H = 2.90 * inch

RES = os.path.join('src', 'results', '2026_06_23_03_55')

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def make_styles():
    S = {}
    S['title']         = ParagraphStyle('title',  fontName='Times-Bold',   fontSize=16, leading=20, alignment=TA_CENTER, spaceAfter=4)
    S['authors']       = ParagraphStyle('authors',fontName='Times-Bold',   fontSize=10, leading=13, alignment=TA_CENTER, spaceAfter=2)
    S['affil']         = ParagraphStyle('affil',  fontName='Times-Italic', fontSize=9,  leading=11, alignment=TA_CENTER, spaceAfter=6)
    S['abstract']      = ParagraphStyle('abs',    fontName='Times-Roman',  fontSize=9,  leading=11, alignment=TA_JUSTIFY, spaceAfter=4)
    S['keywords']      = ParagraphStyle('kw',     fontName='Times-Roman',  fontSize=9,  leading=11, alignment=TA_JUSTIFY, spaceAfter=6)
    S['body']          = ParagraphStyle('body',   fontName='Times-Roman',  fontSize=10, leading=13, alignment=TA_JUSTIFY, spaceAfter=4)
    S['section']       = ParagraphStyle('sec',    fontName='Times-Bold',   fontSize=10, leading=13, alignment=TA_CENTER, spaceBefore=8, spaceAfter=4)
    S['subsection']    = ParagraphStyle('subsec', fontName='Times-Italic', fontSize=10, leading=13, alignment=TA_LEFT,   spaceBefore=5, spaceAfter=3)
    S['caption']       = ParagraphStyle('cap',    fontName='Times-Roman',  fontSize=8,  leading=10, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)
    S['math']          = ParagraphStyle('math',   fontName='Times-Italic', fontSize=10, leading=14, alignment=TA_CENTER, spaceBefore=4, spaceAfter=4)
    S['table_header']  = ParagraphStyle('th',     fontName='Times-Bold',   fontSize=9,  leading=11, alignment=TA_CENTER)
    S['table_body']    = ParagraphStyle('tb',     fontName='Times-Roman',  fontSize=9,  leading=11, alignment=TA_CENTER)
    S['table_body_l']  = ParagraphStyle('tbl',    fontName='Times-Roman',  fontSize=9,  leading=11, alignment=TA_LEFT)
    return S

S = make_styles()

def p(text, style='body'):   return Paragraph(text, S[style])
def sp(h=4):                 return Spacer(1, h)
def hr():                    return HRFlowable(width='100%', thickness=0.5, color=colors.black, spaceAfter=4, spaceBefore=4)
def sec(num, title):         return p(f'{num}. {title.upper()}', 'section')
def subsec(ltr, title):      return p(f'<i>{ltr}. {title}</i>', 'subsection')

def fig(path, caption, label):
    elems = []
    if os.path.exists(path):
        from PIL import Image as PILImage
        ar = PILImage.open(path)
        h  = COL_W * 0.98 * ar.size[1] / ar.size[0]
        elems.append(Image(path, width=COL_W * 0.98, height=h))
    else:
        elems.append(p(f'[{caption}]', 'caption'))
    elems.append(p(f'<b>Fig. {label}.</b> {caption}', 'caption'))
    return elems

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 8)
    canvas.drawCentredString(PW / 2, 0.5 * inch, str(doc.page))
    canvas.restoreState()

def tbl_style(col_header=True):
    s = [
        ('GRID',          (0,0), (-1,-1), 0.4, colors.HexColor('#BBBBBB')),
        ('TOPPADDING',    (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING',   (0,0), (-1,-1), 3),
    ]
    if col_header:
        s += [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F5F5F5'), colors.white]),
        ]
    return TableStyle(s)

# ---------------------------------------------------------------------------
# Text content — both languages
# ---------------------------------------------------------------------------
T = {
    'en': {
        # header
        'title':   ('ANFIS-Based Cardiac Risk Classification: '
                    'Comparing Neuro-Fuzzy Systems and MLP for Accuracy and Interpretability'),
        'affil':   ('School of Electrical and Computer Engineering (FEEC) — '
                    'University of Campinas (Unicamp)<br/>'
                    'Campinas, SP, Brazil — RA: 194761 — victor.m.bertini@gmail.com'),
        'abstract': (
            '<b>Abstract</b>—This paper investigates the tradeoff between predictive '
            'accuracy and interpretability in machine learning models applied to cardiac '
            'risk classification. We propose and evaluate an ANFIS (Adaptive Neuro-Fuzzy '
            'Inference System) with Takagi-Sugeno zero-order inference and mixed '
            'fuzzification—Gaussian membership functions for numerical variables and '
            'smoothed one-hot encoding for categorical variables—whose rule pool is '
            'generated via K-Means clustering. Experiments on the Heart Failure Prediction '
            'Dataset (918 patients, 11 features) show that ANFIS achieves an AUC-ROC of '
            '0.912, accuracy of 84.2%, and F1-Score of 85.9%, outperforming the MLP '
            'baseline (AUC 0.901; accuracy 81.5%; F1 82.5%) with only 228 trainable '
            'parameters versus 2,881 in the MLP. Beyond superior performance, ANFIS '
            'produces 10 auditable IF-THEN linguistic rules revealing clinical patterns '
            'consistent with the ischemia literature.'
        ),
        'keywords': '<b>Keywords</b>—ANFIS; Fuzzy Logic; Neural Networks; Heart Disease; Interpretability; Takagi-Sugeno; K-Means',
        # sections
        's1': 'Introduction',
        's2': 'Dataset and Preprocessing',
        's3': 'ANFIS Architecture',
        's4': 'Rule Pool Generation via K-Means',
        's5': 'Experimental Setup',
        's6': 'Results and Discussion',
        's7': 'Conclusion',
        's_ref': 'References',
        # subsections
        'ss2a': 'Heart Failure Prediction Dataset',
        'ss2b': 'Preprocessing',
        'ss3a': 'MixedFuzzyLayer',
        'ss3b': 'ClusterRuleLayer',
        'ss3c': 'DefuzzyLayer',
        'ss3d': 'Loss Function',
        'ss6a': 'Performance Metrics',
        'ss6b': 'Learned Membership Functions',
        'ss6c': 'Confusion Matrices',
        'ss6d': 'Extracted Linguistic Rules',
        # table headers
        'feat_hdr':  ['Feature', 'Type', 'Description'],
        'hp_hdr':    ['Parameter', 'ANFIS', 'MLP'],
        'res_hdr':   ['Model', 'Params.', 'Train (s)', 'Accuracy', 'F1-Score', 'AUC-ROC'],
        'rule_hdr':  ['#', 'Antecedent (abbrev.)', 'Risk'],
        # table captions
        'cap_feat':  'Dataset features.',
        'cap_hp':    'Experimental hyperparameters.',
        'cap_res':   'Comparative results (Heart Failure, 80/20 split).',
        'cap_rules': 'Top-10 ANFIS rules by mean firing strength. '
                     'CPT=ChestPainType, RBP=RestingBP, Ang=ExerciseAngina, OP=Oldpeak, FBS=FastingBS.',
        # figure captions
        'cap_mfs':   ('Gaussian Membership Functions learned by ANFIS after 200 epochs '
                      '(numerical features) and fixed triangular output MFs.'),
        'cap_cm':    'Confusion matrices on the test set: ANFIS (left) and MLP (right).',
        # feature table rows
        'feat_rows': [
            ('Age',            'Numerical',   'Patient age (years)'),
            ('RestingBP',      'Numerical',   'Resting blood pressure (mmHg)'),
            ('Cholesterol',    'Numerical',   'Serum cholesterol (mg/dL)'),
            ('MaxHR',          'Numerical',   'Maximum heart rate achieved (bpm)'),
            ('Oldpeak',        'Numerical',   'ST segment depression induced by exercise (mm)'),
            ('Sex',            'Categorical', 'M / F'),
            ('ChestPainType',  'Categorical', 'ATA / NAP / ASY / TA'),
            ('FastingBS',      'Categorical', 'Fasting blood sugar > 120 mg/dL: 1=yes, 0=no'),
            ('RestingECG',     'Categorical', 'Normal / ST / LVH'),
            ('ExerciseAngina', 'Categorical', 'Y / N'),
            ('ST_Slope',       'Categorical', 'Up / Flat / Down'),
        ],
        # hyperparameter table
        'hp_rows': [
            ('Epochs',         '200',              '200'),
            ('Batch size',     '32',               '32'),
            ('Learning rate',  '1×10⁻³',           '1×10⁻³'),
            ('Architecture',   '3 MFs, 197 rules', '[64, 32]'),
            ('Parameters',     '228',              '2,881'),
            ('Regularization', 'Sep. penalty λ=0.1', '—'),
            ('Seed',           '42',               '42'),
        ],
        # rules table
        'rule_rows': [
            ('1',  'Age=young, CPT=ATA, MaxHR=high, Ang=N, OP=normal, ST=Up',          'LOW'),
            ('2',  'Age=young, CPT=ASY, MaxHR=low, Ang=Y, OP=high, ST=Flat',           'HIGH'),
            ('3',  'Age=old, CPT=ASY, ECG=ST, MaxHR=low, Ang=Y, OP=high, ST=Flat',     'HIGH'),
            ('4',  'Age=young, CPT=ATA, RBP=high, MaxHR=low, Ang=N, OP=normal, ST=Up', 'LOW'),
            ('5',  'Age=young, CPT=ATA, RBP=opt, MaxHR=low, Ang=N, OP=normal, ST=Up',  'LOW'),
            ('6',  'Age=young, Sex=F, CPT=ATA, MaxHR=low, Ang=N, OP=normal, ST=Up',    'LOW'),
            ('7',  'Age=old, CPT=ASY, ECG=LVH, MaxHR=low, Ang=Y, OP=high, ST=Flat',   'HIGH'),
            ('8',  'Age=young, CPT=NAP, MaxHR=high, Ang=N, OP=normal, ST=Up',          'LOW'),
            ('9',  'Age=young, CPT=ASY, FBS=1, MaxHR=low, Ang=N, OP=normal, ST=Flat',  'HIGH'),
            ('10', 'Age=young, CPT=ASY, RBP=high, MaxHR=low, Ang=Y, OP=high, ST=Flat', 'HIGH'),
        ],
        'risk_low':  'LOW',
        'risk_high': 'HIGH',
        # body paragraphs
        'intro': [
            ('Clinical decision support systems based on machine learning achieve high '
             'accuracy in diagnostic tasks, yet frequently operate as black boxes, '
             'producing predictions without intelligible justification [1]. In the medical '
             'context, decision traceability is both an ethical and regulatory requirement: '
             'a specialist must understand <i>why</i> a patient was flagged as high-risk '
             'in order to validate or challenge the recommendation.'),
            ('Neuro-Fuzzy systems—and ANFIS in particular—combine the learning capability '
             'of neural networks with the interpretability of fuzzy inference systems [2]. '
             'Linguistic rules of the form IF <i>antecedent</i> THEN <i>consequent</i> '
             'enable clinicians and auditors to inspect decision criteria without '
             'requiring machine learning expertise.'),
            ('This paper contributes: (i) an ANFIS architecture with mixed fuzzification '
             'to handle numerical and categorical features in a unified pipeline; '
             '(ii) a K-Means-based rule pool generation method that scales to datasets '
             'with multiple categorical variables; and (iii) a quantitative comparison '
             'with an MLP on the Heart Failure Prediction Dataset [3], showing that '
             'ANFIS outperforms the MLP on all metrics with 13× fewer parameters.'),
        ],
        'ds_a': [
            ('The dataset combines records from five distinct clinical sources, totalling '
             '918 adult patients. The target variable, <b>HeartDisease</b>, is binary '
             '(0=healthy, 1=cardiovascular disease) with approximately 55% positive '
             'prevalence. The train/test split follows an 80/20 ratio with class stratification.'),
            ('The 11 features comprise 5 numerical and 6 categorical variables:'),
        ],
        'ds_b': [
            ('Zero values in <b>RestingBP</b> and <b>Cholesterol</b> (clinically '
             'implausible) are replaced by the median of non-zero entries. Categorical '
             'features are integer-encoded via <i>pd.Categorical.codes</i>. Normalization '
             'is performed by a custom <b>PartialScaler</b>: z-score only on the 5 '
             'numerical features, preserving integer codes for categoricals. '
             'This distinction is essential for <i>MixedFuzzyLayer</i>, which applies '
             'different fuzzification mechanisms to each group.'),
        ],
        'arch_intro': [
            ('The proposed ANFIS follows the zero-order Takagi-Sugeno paradigm and '
             'consists of three trainable layers. The data flow is:'),
            ('<i>X</i> [B,11] → MixedFuzzyLayer → [B,11,M] → ClusterRuleLayer '
             '→ [B,R] → DefuzzyLayer → [B,1] → sigmoid → P(disease)', ),
            ('where B is the batch size, M the number of membership functions per '
             'numerical feature, and R the number of rules in the pool.'),
        ],
        'mfl': [
            ('<u>Numerical features</u>: Trainable Gaussian MFs with center c and '
             'variance σ:'),
            ('μ(x) = exp(−½ · ((x − c) / σ)²)',),
            ('Parameters c and σ are optimized by backpropagation. Variances are '
             'clamped at σ ≥ 10⁻⁶ to prevent numerical instability and initialized '
             'as σ = |N(0,1)| + 0.1 to guarantee positivity.'),
            ('<u>Categorical features</u>: Smoothed one-hot encoding without trainable '
             'parameters:'),
            ('μ<sub>j</sub>(cat) = 0.95 if j=cat, else 0.05/(n<sub>cats</sub>−1)',),
            ('This scheme preserves the discrete structure of the variable while '
             'providing a non-zero gradient signal to other positions, preventing '
             'rule collapse during training.'),
        ],
        'crl': [
            ('The firing strength of rule k is computed by the product T-norm:'),
            ('w<sub>k</sub> = ∏<sub>i</sub> μ<sub>i, combo[k,i]</sub>(x<sub>i</sub>)',),
            ('where <i>combo[k,i]</i> is the MF index of rule k in feature i. '
             'The combination table <i>rule_idx</i> is stored as a <i>register_buffer</i>, '
             'enabling automatic GPU migration. The layer has no trainable parameters.'),
        ],
        'dfl': [
            ('Normalized Takagi-Sugeno defuzzification:'),
            ('w̃<sub>k</sub> = w<sub>k</sub> / (Σ<sub>j</sub> w<sub>j</sub> + ε)',),
            ('ŷ = Σ<sub>k</sub> w̃<sub>k</sub> · c<sub>k</sub>',),
            ('The consequents c<sub>k</sub> are the weights of an <i>nn.Linear(R→1)</i> '
             'optimized by backpropagation. Normalization keeps the output scale '
             'independent of how many rules fire simultaneously, preserving the TS '
             'interpretation of each consequent.'),
        ],
        'loss': [
            ('The loss combines binary cross-entropy with a center-separation penalty:'),
            ('L = BCE(σ(ŷ), y) + λ · Σ<sub>i&lt;j</sub> relu(σ<sub>i</sub> + σ<sub>j</sub> − |c<sub>i</sub> − c<sub>j</sub>|)',),
            ('The penalty term (λ=0.1) is zero when adjacent MF centers are at least '
             'σ<sub>i</sub>+σ<sub>j</sub> apart, and grows linearly otherwise, '
             'preventing a narrow MF from collapsing inside a wider one and '
             'ensuring a coherent linguistic partition.'),
        ],
        'kmeans': [
            ('The number of possible antecedent combinations grows exponentially with '
             'features: n<sub>rules</sub> = M<sup>n<sub>inputs</sub></sup>. '
             'For 11 features with M=3, this yields 177,147 rules—infeasible. '
             'A five-step pipeline before training mitigates this:'),
            ('<b>Step 1 — Percentile peaks</b> (mapping artifact): For each numerical '
             'feature, n<sub>mfs</sub> uniformly spaced percentiles of the training '
             'distribution (P25, P50, P75 for n<sub>mfs</sub>=3) serve as auxiliary '
             'triangular MF peaks for index mapping only—not the ANFIS Gaussian MFs.'),
            ('<b>Step 2 — K-Means clustering</b>: K-Means with 200 clusters on the '
             'training feature space identifies the highest-density regions.'),
            ('<b>Step 3 — Dominant MF mapping</b>: For each cluster center, the '
             'dominant MF is determined per feature: '
             'numerical → argmax of triangular MF at peaks; '
             'categorical → round(center) → integer code.'),
            ('<b>Step 4 — Deduplication</b>: Clusters sharing the same dominant MF '
             'vector are collapsed into a single rule. '
             '200 clusters yielded 197 unique combinations in this run.'),
            ('<b>Step 5 — Initialization</b>: ANFIS Gaussian centers are initialized '
             'at percentiles of K-Means cluster centers per feature, '
             'providing an informed starting point for end-to-end training.'),
        ],
        'setup': [
            ('Hyperparameters are fixed as in Table II. Both models are trained with '
             'the Adam optimizer, a learning rate plateau scheduler, and early stopping '
             'with patience of 20 epochs.'),
            ('Evaluation metrics computed on the test set (20% of data): AUC-ROC '
             '(threshold-independent), accuracy (threshold 0.5), and F1-Score '
             '(harmonic mean of precision and recall, preferred for imbalanced classes). '
             'Randomness is controlled by seed 42 in numpy, torch, and sklearn.'),
        ],
        'res_a': [
            ('Table III shows the quantitative results. ANFIS outperforms the MLP '
             'on all three metrics, most notably in AUC-ROC (Δ=+0.011) and '
             'F1-Score (Δ=+3.4 p.p.), indicating better class separation.'),
            ('The parametric efficiency is noteworthy: ANFIS uses 13× fewer parameters '
             'than the MLP (228 vs. 2,881), reducing overfitting risk and facilitating '
             'model inspection. The trade-off is a roughly 3× slower training time '
             '(14.9 s vs. 4.8 s), acceptable for offline diagnostic applications.'),
        ],
        'res_b': [
            ('Fig. 1 shows the Gaussian MFs after training for all 5 numerical features, '
             'along with the fixed triangular output MFs. Learned centers reveal '
             'clinically coherent thresholds: in <b>Age</b>, the three MFs separate '
             'young (~40 yrs), middle-aged (~55 yrs), and elderly (~65 yrs) patients; '
             'in <b>MaxHR</b>, the "low" MF concentrates around ~120 bpm, below the '
             'expected exercise response frequency; in <b>Oldpeak</b>, the "high" MF '
             'captures ST depressions above ~1.5 mm, aligned with the ischemia '
             'diagnostic criterion.'),
        ],
        'res_c': [
            ('ANFIS produces 18 fewer false negatives (FN) than the MLP on the test set. '
             'In a clinical context—where an undetected disease is the costlier error—'
             'this represents a significant diagnostic advantage and directly explains '
             'the higher F1-Score.'),
        ],
        'res_d': [
            ('Table IV lists the top-10 rules by mean firing strength. '
             'Two patterns emerge consistently:'),
            ('• <b>High risk</b>: ChestPainType=ASY (asymptomatic), low MaxHR, '
             'ExerciseAngina=Y, high Oldpeak, ST_Slope=Flat—established markers '
             'of coronary ischemia [4].'),
            ('• <b>Low risk</b>: ChestPainType=ATA (atypical), high MaxHR, '
             'ExerciseAngina=N, normal Oldpeak, ST_Slope=Up—consistent with '
             'normal physiological response to exercise.'),
        ],
        'conc': [
            ('This work demonstrated that ANFIS with mixed fuzzification and a '
             'K-Means-generated rule pool is a viable and superior alternative to '
             'the MLP for cardiac risk classification, achieving AUC-ROC of 0.912 '
             'with only 228 trainable parameters—13× fewer than the MLP—while '
             'producing 10 auditable linguistic rules aligned with clinical literature.'),
            ('The genuine interpretability obtained—Gaussian centers with physical '
             'meaning, per-rule TS consequents, and intelligible IF-THEN rules—'
             'differentiates ANFIS from post-hoc methods such as SHAP, where the '
             'explanation is generated after the fact and is not part of the '
             'decision process itself.'),
            ('<b>Limitations and future work</b>: The model was tested on a single '
             'dataset (n=918). Future work should: (i) validate on larger and '
             'multi-class datasets; (ii) incorporate domain expert knowledge into '
             'MF initialization; (iii) compare with classical ANFIS (Jang, 1993) '
             'and Mamdani fuzzy systems; and (iv) investigate formal MF definitions '
             'for categorical variables.'),
        ],
        'refs': [
            ('[1] A. Holzinger, G. Langs, H. Denk, K. Zatloukal, and H. Müller, '
             '"Causability and explainability of artificial intelligence in medicine," '
             '<i>WIREs Data Mining Knowl. Discov.</i>, vol. 9, no. 4, 2019.'),
            ('[2] J.-S. R. Jang, "ANFIS: Adaptive-network-based fuzzy inference '
             'system," <i>IEEE Trans. Syst. Man Cybern.</i>, vol. 23, no. 3, '
             'pp. 665–685, 1993.'),
            ('[3] F. Fedesoriano, "Heart Failure Prediction Dataset," Kaggle, 2021.'),
            ('[4] R. A. Gibbons et al., "ACC/AHA 2002 Guideline Update for Exercise '
             'Testing," <i>J. Am. Coll. Cardiol.</i>, vol. 40, no. 8, '
             'pp. 1531–1540, 2002.'),
            ('[5] L. A. Zadeh, "Fuzzy sets," <i>Inf. Control</i>, '
             'vol. 8, no. 3, pp. 338–353, 1965.'),
            ('[6] J. C. Bezdek, R. Ehrlich, and W. Full, "FCM: The fuzzy c-means '
             'clustering algorithm," <i>Comput. Geosci.</i>, vol. 10, '
             'pp. 191–203, 1984.'),
        ],
    },
}

# ---------------------------------------------------------------------------
# Portuguese — same structure
# ---------------------------------------------------------------------------
T['ptbr'] = {
    'title':   ('Classificação de Risco Cardíaco com ANFIS: '
                'Comparação entre Sistemas Neuro-Fuzzy e MLP com Foco em Interpretabilidade'),
    'affil':   ('Faculdade de Engenharia Elétrica e de Computação (FEEC) — '
                'Universidade Estadual de Campinas (Unicamp)<br/>'
                'Campinas, SP, Brasil — RA: 194761 — victor.m.bertini@gmail.com'),
    'abstract': (
        '<b>Resumo</b>—Este trabalho investiga o tradeoff entre acurácia preditiva e '
        'interpretabilidade em modelos de aprendizado de máquina aplicados à classificação '
        'de risco de doença cardíaca. Propomos e avaliamos um sistema ANFIS (Adaptive '
        'Neuro-Fuzzy Inference System) de Takagi-Sugeno com fuzzificação mista—funções '
        'Gaussianas para variáveis numéricas e codificação one-hot suavizada para '
        'variáveis categóricas—cujo pool de regras é gerado por agrupamento K-Means. '
        'Os experimentos no Heart Failure Prediction Dataset (918 pacientes, 11 features) '
        'mostram que o ANFIS atinge AUC-ROC de 0,912, acurácia de 84,2% e F1-Score de 85,9%, '
        'superando o MLP baseline (AUC 0,901; acurácia 81,5%; F1 82,5%) com apenas 228 '
        'parâmetros treináveis frente a 2.881 do MLP. Além do desempenho superior, '
        'o ANFIS produz 10 regras linguísticas SE-ENTÃO auditáveis que revelam padrões '
        'clínicos alinhados à literatura sobre isquemia cardíaca.'
    ),
    'keywords': '<b>Palavras-chave</b>—ANFIS; Lógica Fuzzy; Redes Neurais; Doença Cardíaca; Interpretabilidade; Takagi-Sugeno; K-Means',
    's1': 'Introdução', 's2': 'Dataset e Pré-Processamento',
    's3': 'Arquitetura ANFIS', 's4': 'Geração do Pool de Regras via K-Means',
    's5': 'Configuração Experimental', 's6': 'Resultados e Discussão',
    's7': 'Conclusão', 's_ref': 'Referências',
    'ss2a': 'Heart Failure Prediction Dataset', 'ss2b': 'Pré-Processamento',
    'ss3a': 'MixedFuzzyLayer', 'ss3b': 'ClusterRuleLayer',
    'ss3c': 'DefuzzyLayer', 'ss3d': 'Função de Perda',
    'ss6a': 'Métricas de Desempenho', 'ss6b': 'Funções de Pertinência Aprendidas',
    'ss6c': 'Matrizes de Confusão', 'ss6d': 'Regras Linguísticas Extraídas',
    'feat_hdr': ['Feature', 'Tipo', 'Descrição'],
    'hp_hdr':   ['Parâmetro', 'ANFIS', 'MLP'],
    'res_hdr':  ['Modelo', 'Parâm.', 'Treino (s)', 'Acurácia', 'F1-Score', 'AUC-ROC'],
    'rule_hdr': ['#', 'Antecedente (abrev.)', 'Risco'],
    'cap_feat':  'Features do dataset.',
    'cap_hp':    'Hiperparâmetros experimentais.',
    'cap_res':   'Resultados comparativos (Heart Failure, split 80/20).',
    'cap_rules': ('Top-10 regras ANFIS por força de disparo média. '
                  'CPT=ChestPainType, RBP=RestingBP, Ang=ExerciseAngina, OP=Oldpeak, FBS=FastingBS.'),
    'cap_mfs':   ('Funções de Pertinência Gaussianas aprendidas pelo ANFIS após 200 épocas '
                  '(features numéricas) e MFs triangulares de saída (hardcoded).'),
    'cap_cm':    'Matrizes de confusão no conjunto de teste: ANFIS (esq.) e MLP (dir.).',
    'feat_rows': [
        ('Age',            'Numérica',    'Idade do paciente (anos)'),
        ('RestingBP',      'Numérica',    'Pressão arterial em repouso (mmHg)'),
        ('Cholesterol',    'Numérica',    'Colesterol sérico (mg/dL)'),
        ('MaxHR',          'Numérica',    'Frequência cardíaca máxima atingida (bpm)'),
        ('Oldpeak',        'Numérica',    'Depressão do segmento ST induzida por exercício (mm)'),
        ('Sex',            'Categórica',  'M / F'),
        ('ChestPainType',  'Categórica',  'ATA / NAP / ASY / TA'),
        ('FastingBS',      'Categórica',  'Glicemia em jejum > 120 mg/dL: 1=sim, 0=não'),
        ('RestingECG',     'Categórica',  'Normal / ST / LVH'),
        ('ExerciseAngina', 'Categórica',  'Y / N'),
        ('ST_Slope',       'Categórica',  'Up / Flat / Down'),
    ],
    'hp_rows': [
        ('Épocas',         '200',              '200'),
        ('Batch size',     '32',               '32'),
        ('Learning rate',  '1×10⁻³',           '1×10⁻³'),
        ('Arquitetura',    '3 MFs, 197 regras', '[64, 32]'),
        ('Parâmetros',     '228',              '2.881'),
        ('Regularização',  'Sep. penalty λ=0,1', '—'),
        ('Semente',        '42',               '42'),
    ],
    'rule_rows': [
        ('1',  'Age=jovem, CPT=ATA, MaxHR=alta, Ang=N, OP=normal, ST=Up',           'BAIXO'),
        ('2',  'Age=jovem, CPT=ASY, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat',       'ALTO'),
        ('3',  'Age=idoso, CPT=ASY, ECG=ST, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat','ALTO'),
        ('4',  'Age=jovem, CPT=ATA, RBP=elevado, MaxHR=baixa, Ang=N, OP=normal, ST=Up','BAIXO'),
        ('5',  'Age=jovem, CPT=ATA, RBP=otimo, MaxHR=baixa, Ang=N, OP=normal, ST=Up','BAIXO'),
        ('6',  'Age=jovem, Sex=F, CPT=ATA, MaxHR=baixa, Ang=N, OP=normal, ST=Up',   'BAIXO'),
        ('7',  'Age=idoso, CPT=ASY, ECG=LVH, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat','ALTO'),
        ('8',  'Age=jovem, CPT=NAP, MaxHR=alta, Ang=N, OP=normal, ST=Up',           'BAIXO'),
        ('9',  'Age=jovem, CPT=ASY, FBS=1, MaxHR=baixa, Ang=N, OP=normal, ST=Flat', 'ALTO'),
        ('10', 'Age=jovem, CPT=ASY, RBP=elevado, MaxHR=baixa, Ang=Y, OP=elevado, ST=Flat','ALTO'),
    ],
    'risk_low': 'BAIXO', 'risk_high': 'ALTO',
    'intro': [
        ('Sistemas de apoio a decisão clínica baseados em aprendizado de máquina atingem '
         'alta acurácia em tarefas de diagnóstico, porém frequentemente operam como '
         'caixas-pretas, fornecendo predições sem justificativa inteligível [1]. No '
         'contexto médico, a rastreabilidade das decisões é tanto um requisito ético '
         'quanto regulatório: um especialista precisa entender <i>por que</i> um paciente '
         'foi classificado como alto risco para validar ou contestar a recomendação.'),
        ('Sistemas Neuro-Fuzzy—em particular o ANFIS—combinam a capacidade de '
         'aprendizado de redes neurais com a interpretabilidade de sistemas de inferência '
         'fuzzy [2]. Regras linguísticas do tipo SE <i>antecedente</i> ENTÃO '
         '<i>consequente</i> permitem que clínicos e auditores inspecionem os critérios '
         'decisórios sem exigir expertise em aprendizado de máquina.'),
        ('Este trabalho apresenta: (i) uma arquitetura ANFIS com fuzzificação mista '
         'para lidar com features numéricas e categóricas no mesmo pipeline; '
         '(ii) um método de geração de pool de regras por K-Means que escala para '
         'datasets com múltiplas variáveis categóricas; e (iii) uma comparação '
         'quantitativa com MLP no Heart Failure Prediction Dataset [3], demonstrando '
         'que o ANFIS supera o MLP em todas as métricas com 13× menos parâmetros.'),
    ],
    'ds_a': [
        ('O dataset combina registros de cinco fontes clínicas distintas, totalizando '
         '918 pacientes adultos. A variável alvo, <b>HeartDisease</b>, é binária '
         '(0=saudável, 1=doença cardiovascular) com prevalência de ~55% de positivos. '
         'A divisão treino/teste segue a proporção 80/20 com estratificação por classe.'),
        ('As 11 features compreendem 5 variáveis numéricas e 6 categóricas:'),
    ],
    'ds_b': [
        ('Valores zerados em <b>RestingBP</b> e <b>Cholesterol</b> (clinicamente '
         'impossíveis) são substituídos pela mediana das entradas não-nulas. '
         'Features categóricas são codificadas como inteiros via <i>pd.Categorical.codes</i>. '
         'A normalização é realizada pelo <b>PartialScaler</b>: z-score exclusivamente '
         'nas 5 features numéricas, preservando os códigos inteiros das categóricas. '
         'Esta distinção é fundamental para a <i>MixedFuzzyLayer</i>, que trata os '
         'dois grupos com mecanismos de fuzzificação distintos.'),
    ],
    'arch_intro': [
        ('O modelo ANFIS proposto segue o paradigma Takagi-Sugeno de ordem zero e '
         'é composto por três camadas treináveis encadeadas. O fluxo de dados é:'),
        ('<i>X</i> [B,11] → MixedFuzzyLayer → [B,11,M] → ClusterRuleLayer '
         '→ [B,R] → DefuzzyLayer → [B,1] → sigmoid → P(doença)',),
        ('onde B é o tamanho do batch, M o número de funções de pertinência por '
         'feature numérica, e R o número de regras no pool.'),
    ],
    'mfl': [
        ('<u>Features numéricas</u>: MFs Gaussianas treináveis com centro c e variância σ:'),
        ('μ(x) = exp(−½ · ((x − c) / σ)²)',),
        ('Os parâmetros c e σ são otimizados por retropropagação. Variâncias são '
         'clampeadas em σ ≥ 10⁻⁶ e inicializadas como σ = |N(0,1)| + 0,1.'),
        ('<u>Features categóricas</u>: Codificação one-hot suavizada sem parâmetros treináveis:'),
        ('μ<sub>j</sub>(cat) = 0,95 se j=cat, senão 0,05/(n<sub>cats</sub>−1)',),
        ('Este esquema preserva a estrutura discreta da variável e fornece gradiente '
         'não-nulo às demais posições, evitando colapso de regras no treinamento.'),
    ],
    'crl': [
        ('A força de disparo da regra k é calculada por T-norma produto:'),
        ('w<sub>k</sub> = ∏<sub>i</sub> μ<sub>i, combo[k,i]</sub>(x<sub>i</sub>)',),
        ('onde <i>combo[k,i]</i> é o índice da MF da regra k na feature i. '
         'A tabela <i>rule_idx</i> é armazenada como <i>register_buffer</i>, '
         'garantindo migração automática para GPU. A camada não possui parâmetros treináveis.'),
    ],
    'dfl': [
        ('Defuzzificação Takagi-Sugeno normalizada:'),
        ('w̃<sub>k</sub> = w<sub>k</sub> / (Σ<sub>j</sub> w<sub>j</sub> + ε)',),
        ('ŷ = Σ<sub>k</sub> w̃<sub>k</sub> · c<sub>k</sub>',),
        ('Os consequentes c<sub>k</sub> são os pesos de uma <i>nn.Linear(R→1)</i>. '
         'A normalização garante que a escala da saída seja independente do número '
         'de regras que disparam simultaneamente.'),
    ],
    'loss': [
        ('A função de perda combina entropia cruzada binária com uma penalidade de separação de centros:'),
        ('L = BCE(σ(ŷ), y) + λ · Σ<sub>i&lt;j</sub> relu(σ<sub>i</sub> + σ<sub>j</sub> − |c<sub>i</sub> − c<sub>j</sub>|)',),
        ('A penalidade (λ=0,1) é zero quando os centros adjacentes estão afastados '
         'por pelo menos σ<sub>i</sub>+σ<sub>j</sub>, prevenindo que uma MF estreita '
         'fique contida dentro de outra mais larga e garantindo partição linguística coerente.'),
    ],
    'kmeans': [
        ('O número de combinações possíveis cresce exponencialmente: '
         'n<sub>rules</sub> = M<sup>n<sub>inputs</sub></sup>. '
         'Para 11 features com M=3 seriam 177.147 regras—inviável. '
         'Um pipeline de 5 passos antes do treinamento mitiga isso:'),
        ('<b>Passo 1 — Picos percentílicos</b> (artifício de mapeamento): Para cada '
         'feature numérica, n<sub>mfs</sub> percentis uniformes da distribuição de treino '
         '(P25, P50, P75) servem de picos de MFs triangulares auxiliares—não são as '
         'MFs Gaussianas do ANFIS.'),
        ('<b>Passo 2 — K-Means</b>: 200 clusters identificam as regiões mais densas do espaço de entrada.'),
        ('<b>Passo 3 — Mapeamento dominante</b>: Para cada centro de cluster, '
         'determina-se a MF dominante: numérica → argmax da MF triangular; '
         'categórica → round(centro).'),
        ('<b>Passo 4 — Deduplicação</b>: Clusters com o mesmo vetor dominante '
         'colapsam em uma regra. 200 clusters → 197 combos únicos nesta execução.'),
        ('<b>Passo 5 — Inicialização</b>: Centros Gaussianos do ANFIS são inicializados '
         'nos percentis dos centros K-Means, fornecendo ponto de partida informado.'),
    ],
    'setup': [
        ('Os hiperparâmetros foram fixados conforme a Tabela II. Ambos os modelos '
         'são treinados com otimizador Adam, scheduler de learning rate por plateau '
         'e early stopping com paciência de 20 épocas.'),
        ('As métricas são calculadas no conjunto de teste (20% dos dados): '
         'AUC-ROC (independente de limiar), acurácia (limiar 0,5) e F1-Score '
         '(média harmônica de precisão e revocação). '
         'A aleatoriedade é controlada pela semente 42 em numpy, torch e sklearn.'),
    ],
    'res_a': [
        ('A Tabela III apresenta os resultados quantitativos. O ANFIS supera o '
         'MLP em todas as três métricas, com destaque para a AUC-ROC (Δ=+0,011) '
         'e o F1-Score (Δ=+3,4 p.p.).'),
        ('A eficiência paramétrica é notável: o ANFIS usa 13× menos parâmetros '
         '(228 vs. 2.881), reduzindo o risco de overfitting e facilitando auditoria '
         'do modelo. O custo é um treinamento ~3× mais lento (14,9 s vs. 4,8 s), '
         'aceitável em diagnóstico offline.'),
    ],
    'res_b': [
        ('A Fig. 1 mostra as MFs Gaussianas pós-treinamento para as 5 features '
         'numéricas. Os centros aprendidos revelam limiares clinicamente coerentes: '
         'em <b>Age</b>, as três MFs separam jovens (~40 anos), meia-idade (~55) e '
         'idosos (~65); em <b>MaxHR</b>, a MF "baixa" concentra-se em ~120 bpm; '
         'em <b>Oldpeak</b>, a MF "elevado" captura depressões acima de ~1,5 mm, '
         'alinhado ao critério diagnóstico de isquemia.'),
    ],
    'res_c': [
        ('O ANFIS apresenta 18 falsos negativos a menos que o MLP no conjunto de teste. '
         'Em contexto clínico—onde doença não detectada é o erro mais custoso—'
         'isso representa uma vantagem diagnóstica significativa e explica '
         'diretamente o maior F1-Score observado.'),
    ],
    'res_d': [
        ('A Tabela IV lista as top-10 regras por força de disparo média. '
         'Dois padrões emergem consistentemente:'),
        ('• <b>Alto risco</b>: ChestPainType=ASY, MaxHR baixa, ExerciseAngina=Y, '
         'Oldpeak elevado, ST_Slope=Flat — marcadores estabelecidos de isquemia coronariana [4].'),
        ('• <b>Baixo risco</b>: ChestPainType=ATA, MaxHR alta, ExerciseAngina=N, '
         'Oldpeak normal, ST_Slope=Up — compatível com resposta fisiológica normal ao esforço.'),
    ],
    'conc': [
        ('Este trabalho demonstrou que o ANFIS com fuzzificação mista e pool de '
         'regras gerado por K-Means é uma alternativa viável e superior ao MLP '
         'para classificação de risco cardíaco, atingindo AUC-ROC de 0,912 com '
         'apenas 228 parâmetros—13× menos que o MLP—e produzindo 10 regras '
         'linguísticas auditáveis alinhadas à literatura clínica.'),
        ('A interpretabilidade genuína—centros Gaussianos com significado físico, '
         'consequentes TS por regra e regras SE-ENTÃO inteligíveis—diferencia o '
         'ANFIS de métodos post-hoc como SHAP, onde a explicação é gerada após '
         'o fato e não integra o processo decisório.'),
        ('<b>Limitações e trabalho futuro</b>: Testado em único dataset (n=918). '
         'Trabalhos futuros devem: (i) validar em datasets maiores e multi-classe; '
         '(ii) incorporar conhecimento de especialistas na inicialização das MFs; '
         '(iii) comparar com ANFIS clássico (Jang, 1993) e sistemas Mamdani; '
         '(iv) investigar definições formais de MFs para variáveis categóricas.'),
    ],
    'refs': [
        ('[1] A. Holzinger, G. Langs, H. Denk, K. Zatloukal e H. Müller, '
         '"Causability and explainability of artificial intelligence in medicine," '
         '<i>WIREs Data Mining Knowl. Discov.</i>, vol. 9, no. 4, 2019.'),
        ('[2] J.-S. R. Jang, "ANFIS: Adaptive-network-based fuzzy inference system," '
         '<i>IEEE Trans. Syst. Man Cybern.</i>, vol. 23, no. 3, pp. 665–685, 1993.'),
        ('[3] F. Fedesoriano, "Heart Failure Prediction Dataset," Kaggle, 2021.'),
        ('[4] R. A. Gibbons et al., "ACC/AHA 2002 Guideline Update for Exercise '
         'Testing," <i>J. Am. Coll. Cardiol.</i>, vol. 40, no. 8, pp. 1531–1540, 2002.'),
        ('[5] L. A. Zadeh, "Fuzzy sets," <i>Inf. Control</i>, vol. 8, no. 3, pp. 338–353, 1965.'),
        ('[6] J. C. Bezdek, R. Ehrlich e W. Full, "FCM: The fuzzy c-means clustering '
         'algorithm," <i>Comput. Geosci.</i>, vol. 10, pp. 191–203, 1984.'),
    ],
}

# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------
def build_story(lang):
    t   = T[lang]
    sto = []

    # — Header ---------------------------------------------------------------
    sto += [
        p(t['title'], 'title'), sp(2),
        p('Victor M. Bertini', 'authors'),
        p(t['affil'], 'affil'),
        sp(4), hr(),
        p(t['abstract'], 'abstract'), sp(3),
        p(t['keywords'], 'keywords'),
        hr(), sp(4),
        NextPageTemplate('later'),
    ]

    # — I. Intro -------------------------------------------------------------
    sto += [sec('I', t['s1'])]
    for txt in t['intro']:
        sto.append(p(txt))
    sto.append(sp(2))

    # — II. Dataset ----------------------------------------------------------
    sto += [sec('II', t['s2']), subsec('A', t['ss2a'])]
    for txt in t['ds_a']:
        sto.append(p(txt))

    feat_data = [[p(h, 'table_header') for h in t['feat_hdr']]] + [
        [p(f, 'table_body'), p(tp, 'table_body'), p(d, 'table_body_l')]
        for f, tp, d in t['feat_rows']
    ]
    ft = Table(feat_data, colWidths=[COL_W*0.28, COL_W*0.22, COL_W*0.50])
    ft.setStyle(tbl_style())
    sto += [KeepTogether([ft, p(f'<b>TABELA I.</b> {t["cap_feat"]}', 'caption')]), sp(2)]

    sto += [subsec('B', t['ss2b'])]
    for txt in t['ds_b']:
        sto.append(p(txt))
    sto.append(sp(2))

    # — III. Architecture ----------------------------------------------------
    sto += [sec('III', t['s3'])]
    arch = t['arch_intro']
    sto.append(p(arch[0]))
    sto.append(p(arch[1][0] if isinstance(arch[1], tuple) else arch[1], 'math'))
    sto.append(p(arch[2]))
    sto += [sp(2), subsec('A', t['ss3a'])]
    mfl = t['mfl']
    sto.append(p(mfl[0]))
    sto.append(p(mfl[1][0] if isinstance(mfl[1], tuple) else mfl[1], 'math'))
    sto.append(p(mfl[2]))
    sto.append(p(mfl[3]))
    sto.append(p(mfl[4][0] if isinstance(mfl[4], tuple) else mfl[4], 'math'))
    sto.append(p(mfl[5]))
    sto += [sp(2), subsec('B', t['ss3b'])]
    for i, txt in enumerate(t['crl']):
        txt0 = txt[0] if isinstance(txt, tuple) else txt
        sto.append(p(txt0, 'math' if isinstance(txt, tuple) else 'body'))
    sto += [sp(2), subsec('C', t['ss3c'])]
    for txt in t['dfl']:
        txt0 = txt[0] if isinstance(txt, tuple) else txt
        sto.append(p(txt0, 'math' if isinstance(txt, tuple) else 'body'))
    sto += [sp(2), subsec('D', t['ss3d'])]
    for txt in t['loss']:
        txt0 = txt[0] if isinstance(txt, tuple) else txt
        sto.append(p(txt0, 'math' if isinstance(txt, tuple) else 'body'))
    sto.append(sp(2))

    # — IV. K-Means ----------------------------------------------------------
    sto += [sec('IV', t['s4'])]
    for txt in t['kmeans']:
        sto.append(p(txt))
    sto.append(sp(2))

    # — V. Setup -------------------------------------------------------------
    sto += [sec('V', t['s5'])]
    sto.append(p(t['setup'][0]))

    hp_data = [[p(h, 'table_header') for h in t['hp_hdr']]] + [
        [p(a, 'table_body'), p(b, 'table_body'), p(c, 'table_body')]
        for a, b, c in t['hp_rows']
    ]
    ht = Table(hp_data, colWidths=[COL_W*0.42, COL_W*0.30, COL_W*0.28])
    ht.setStyle(tbl_style())
    sto += [KeepTogether([ht, p(f'<b>TABELA II.</b> {t["cap_hp"]}', 'caption')]), sp(2)]
    sto.append(p(t['setup'][1]))
    sto.append(sp(2))

    # — VI. Results ----------------------------------------------------------
    sto += [sec('VI', t['s6']), subsec('A', t['ss6a'])]
    sto.append(p(t['res_a'][0]))

    res_data = [[p(h, 'table_header') for h in t['res_hdr']]] + [
        [p('ANFIS','table_body'), p('228','table_body'), p('14,9' if lang=='ptbr' else '14.9','table_body'),
         p('84,2%' if lang=='ptbr' else '84.2%','table_body'),
         p('85,9%' if lang=='ptbr' else '85.9%','table_body'), p('<b>0,912</b>' if lang=='ptbr' else '<b>0.912</b>','table_body')],
        [p('MLP','table_body'), p('2.881' if lang=='ptbr' else '2,881','table_body'), p('4,8' if lang=='ptbr' else '4.8','table_body'),
         p('81,5%' if lang=='ptbr' else '81.5%','table_body'),
         p('82,5%' if lang=='ptbr' else '82.5%','table_body'), p('0,901' if lang=='ptbr' else '0.901','table_body')],
    ]
    rt = Table(res_data, colWidths=[COL_W*0.15, COL_W*0.14, COL_W*0.16, COL_W*0.17, COL_W*0.18, COL_W*0.20])
    rt.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), colors.HexColor('#2E7D32')),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('BACKGROUND',     (0,1), (-1,1), colors.HexColor('#C8E6C9')),
        ('BACKGROUND',     (0,2), (-1,2), colors.white),
        ('GRID',           (0,0), (-1,-1), 0.4, colors.HexColor('#BBBBBB')),
        ('TOPPADDING',     (0,0), (-1,-1), 2),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 2),
        ('LEFTPADDING',    (0,0), (-1,-1), 2),
    ]))
    sto += [KeepTogether([rt, p(f'<b>TABELA III.</b> {t["cap_res"]}', 'caption')]), sp(2)]
    sto.append(p(t['res_a'][1]))

    sto += [sp(2), subsec('B', t['ss6b'])]
    sto.append(p(t['res_b'][0]))
    sto += fig(os.path.join(RES, 'mfs_anfis.png'), t['cap_mfs'], '1')

    sto += [sp(2), subsec('C', t['ss6c'])]
    sto += fig(os.path.join(RES, 'confusion_matrix.png'), t['cap_cm'], '2')
    sto += [sp(2), p(t['res_c'][0])]

    sto += [sp(2), subsec('D', t['ss6d'])]
    for txt in t['res_d']:
        sto.append(p(txt))

    rule_data = [[p(h, 'table_header') for h in t['rule_hdr']]] + [
        [p(n,'table_body'), p(ante,'table_body_l'), p(risk,'table_body')]
        for n, ante, risk in t['rule_rows']
    ]
    rk = Table(rule_data, colWidths=[COL_W*0.07, COL_W*0.77, COL_W*0.16])
    HIGH = t['risk_high']
    alto_idx = [i+1 for i,(_, _, r) in enumerate(t['rule_rows']) if r == HIGH]
    rs = tbl_style()
    for idx in alto_idx:
        rs.add('BACKGROUND', (2, idx), (2, idx), colors.HexColor('#FFCDD2'))
    rk.setStyle(rs)
    sto += [KeepTogether([rk, p(f'<b>TABELA IV.</b> {t["cap_rules"]}', 'caption')]), sp(2)]

    # — VII. Conclusion ------------------------------------------------------
    sto += [sec('VII', t['s7'])]
    for txt in t['conc']:
        sto.append(p(txt))
    sto.append(sp(4))

    # — References -----------------------------------------------------------
    sto += [sec('', t['s_ref'])]
    for ref in t['refs']:
        sto.append(p(ref))
        sto.append(sp(2))

    return sto

# ---------------------------------------------------------------------------
# Generate both PDFs
# ---------------------------------------------------------------------------
outputs = [
    ('en',   'anfis_paper_en.pdf'),
    ('ptbr', 'anfis_paper_ptbr.pdf'),
]

for lang, outfile in outputs:
    doc = BaseDocTemplate(
        outfile, pagesize=LETTER,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT, bottomMargin=MB,
        showBoundary=False,
    )

    header_frame = Frame(ML, PH - MT - HEADER_H, BODY_W, HEADER_H,
                         id='header', showBoundary=False, topPadding=0)
    col1_p1 = Frame(ML,                   MB, COL_W, BODY_H - HEADER_H,
                    id='col1', showBoundary=False, topPadding=0)
    col2_p1 = Frame(ML + COL_W + GUTTER,  MB, COL_W, BODY_H - HEADER_H,
                    id='col2', showBoundary=False, topPadding=0)
    col1_pn = Frame(ML,                   MB, COL_W, BODY_H,
                    id='col1', showBoundary=False, topPadding=0)
    col2_pn = Frame(ML + COL_W + GUTTER,  MB, COL_W, BODY_H,
                    id='col2', showBoundary=False, topPadding=0)

    doc.addPageTemplates([
        PageTemplate('first', [header_frame, col1_p1, col2_p1], onPage=on_page),
        PageTemplate('later', [col1_pn, col2_pn],               onPage=on_page),
    ])

    doc.build(build_story(lang))
    from pathlib import Path
    size_kb = round(Path(outfile).stat().st_size / 1024, 1)
    print(f'Gerado: {outfile}  ({size_kb} KB)')
