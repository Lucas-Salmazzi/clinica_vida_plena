"""Gera o dataset 'Clínica Vida Plena' (modelo estrela, já tratado). Seed fixa = reproduzível."""
import os
from datetime import date, timedelta

import numpy as np
import pandas as pd

rng = np.random.default_rng(20261102)
START, END = date(2025, 1, 1), date(2026, 10, 31)
OUT = "dados"
os.makedirs(f"{OUT}/csv", exist_ok=True)

HOLIDAYS = {
    date(2025, 1, 1), date(2025, 3, 3), date(2025, 3, 4), date(2025, 4, 18), date(2025, 4, 21),
    date(2025, 5, 1), date(2025, 6, 19), date(2025, 7, 9), date(2025, 9, 7), date(2025, 10, 12),
    date(2025, 11, 2), date(2025, 11, 15), date(2025, 11, 20), date(2025, 12, 25),
    date(2026, 1, 1), date(2026, 2, 16), date(2026, 2, 17), date(2026, 4, 3), date(2026, 4, 21),
    date(2026, 5, 1), date(2026, 6, 4), date(2026, 7, 9), date(2026, 9, 7), date(2026, 10, 12),
}

# ---------------------------------------------------------------- dimensões pequenas
conv = pd.DataFrame({
    "id_convenio": [1, 2, 3, 4, 5],
    "convenio": ["Particular", "Vida Saúde", "Medfácil", "Prime Care", "Bem Estar"],
    "tipo": ["Particular", "Plano de saúde", "Plano de saúde", "Plano de saúde", "Plano de saúde"],
    "percentual_tabela": [1.00, 0.80, 0.75, 0.85, 0.70],
    "prazo_pagamento_dias": [0, 30, 45, 30, 60],
})

med = pd.DataFrame([
    (1, "Dra. Helena Duarte", "Clínica Geral", "Sócio", date(2019, 3, 4)),
    (2, "Dr. Marcos Tavares", "Clínica Geral", "CLT", date(2021, 8, 16)),
    (3, "Dra. Beatriz Nogueira", "Pediatria", "Sócio", date(2019, 3, 4)),
    (4, "Dr. Caio Albuquerque", "Pediatria", "PJ", date(2022, 2, 7)),
    (5, "Dr. Rodrigo Siqueira", "Cardiologia", "PJ", date(2020, 6, 1)),
    (6, "Dra. Marina Vasconcelos", "Dermatologia", "PJ", date(2021, 1, 11)),
    (7, "Dr. Rafael Moura", "Ortopedia", "PJ", date(2022, 9, 5)),
    (8, "Dra. Larissa Campos", "Ginecologia", "CLT", date(2020, 10, 19)),
    (9, "Dra. Patrícia Lemos", "Ginecologia", "PJ", date(2023, 4, 3)),
    (10, "Dr. André Barreto", "Endocrinologia", "PJ", date(2023, 1, 9)),
    (11, "Dra. Juliana Prado", "Oftalmologia", "PJ", date(2022, 5, 23)),
    (12, "Dr. Felipe Cardoso", "Psiquiatria", "PJ", date(2024, 2, 5)),
], columns=["id_medico", "nome_medico", "especialidade", "tipo_vinculo", "data_contratacao"])

procs_raw = [
    ("Consulta Clínica Geral", "Consulta", "Clínica Geral", 260, 30),
    ("Consulta Pediátrica", "Consulta", "Pediatria", 280, 30),
    ("Consulta Cardiológica", "Consulta", "Cardiologia", 380, 40),
    ("Consulta Dermatológica", "Consulta", "Dermatologia", 340, 30),
    ("Consulta Ortopédica", "Consulta", "Ortopedia", 350, 30),
    ("Consulta Ginecológica", "Consulta", "Ginecologia", 320, 40),
    ("Consulta Endocrinológica", "Consulta", "Endocrinologia", 360, 40),
    ("Consulta Oftalmológica", "Consulta", "Oftalmologia", 300, 30),
    ("Consulta Psiquiátrica", "Consulta", "Psiquiatria", 400, 50),
    ("Eletrocardiograma", "Exame", "Cardiologia", 120, 20),
    ("Ecocardiograma", "Exame", "Cardiologia", 450, 40),
    ("Hemograma Completo", "Exame", "Clínica Geral", 90, 15),
    ("Ultrassom Abdominal", "Exame", "Clínica Geral", 240, 30),
    ("Glicemia e Hemoglobina Glicada", "Exame", "Endocrinologia", 110, 15),
    ("Ultrassom Pélvico", "Exame", "Ginecologia", 230, 30),
    ("Mapeamento de Retina", "Exame", "Oftalmologia", 280, 25),
    ("Radiografia Osteoarticular", "Exame", "Ortopedia", 160, 20),
    ("Pequena Cirurgia Dermatológica", "Procedimento", "Dermatologia", 520, 60),
    ("Infiltração Articular", "Procedimento", "Ortopedia", 480, 40),
]
proc = pd.DataFrame(procs_raw, columns=["procedimento", "categoria", "especialidade", "valor_tabela", "duracao_min"])
proc.insert(0, "id_procedimento", range(1, len(proc) + 1))

spec_consulta, spec_extras = {}, {}
for r in proc.itertuples():
    if r.categoria == "Consulta":
        spec_consulta[r.especialidade] = r.id_procedimento
    else:
        spec_extras.setdefault(r.especialidade, []).append(r.id_procedimento)
extra_prob = {"Cardiologia": 0.35, "Clínica Geral": 0.22, "Endocrinologia": 0.25, "Ginecologia": 0.22,
              "Oftalmologia": 0.30, "Ortopedia": 0.28, "Dermatologia": 0.18}
valor_tab = dict(zip(proc.id_procedimento, proc.valor_tabela))
cat_proc = dict(zip(proc.id_procedimento, proc.categoria))
spec_doc = dict(zip(med.id_medico, med.especialidade))

# ---------------------------------------------------------------- pacientes (pool inicial)
N_POOL = 2300
sexo = rng.choice(["Feminino", "Masculino"], size=N_POOL, p=[0.57, 0.43])
is_kid = rng.random(N_POOL) < 0.21
age_end = np.where(is_kid, rng.uniform(0.1, 14.9, N_POOL), np.clip(rng.normal(43, 15, N_POOL), 17, 88))
nasc = [END - timedelta(days=int(a * 365.25)) for a in age_end]
cidades = ["São Paulo", "Guarulhos", "Osasco", "Santo André", "São Bernardo do Campo", "Barueri", "Taboão da Serra"]
cidade = rng.choice(cidades, size=N_POOL, p=[0.55, 0.12, 0.09, 0.07, 0.07, 0.05, 0.05])
conv_pat = rng.choice([1, 2, 3, 4, 5], size=N_POOL, p=[0.24, 0.28, 0.18, 0.18, 0.12])
freq_w = rng.lognormal(0, 0.9, N_POOL)
is_old = rng.random(N_POOL) < 0.36
entered = is_old.copy()  # pacientes antigos já existem desde o início

cls_idx = {
    "ped": np.where(is_kid)[0],
    "gin": np.where((~is_kid) & (sexo == "Feminino"))[0],
    "adult": np.where(~is_kid)[0],
}
new_cands = {k: [i for i in rng.permutation(v) if not is_old[i]] for k, v in cls_idx.items()}


def pick_patient(cls, day_used):
    idx = cls_idx[cls]
    if rng.random() < 0.115 and new_cands[cls]:
        while new_cands[cls]:
            cand = new_cands[cls].pop()
            if not entered[cand]:
                entered[cand] = True
                return int(cand), True
    for _ in range(8):
        w = freq_w[idx] * entered[idx]
        cs = np.cumsum(w)
        p = idx[int(np.searchsorted(cs, rng.random() * cs[-1]))]
        if (int(p), day_used["d"]) not in day_used["set"]:
            return int(p), False
    return int(p), False


# ---------------------------------------------------------------- fato
month_f = {1: 0.80, 2: 0.90, 3: 1.05, 4: 1.00, 5: 1.05, 6: 1.00, 7: 0.85, 8: 1.10, 9: 1.05, 10: 1.05, 11: 1.00, 12: 0.80}
dow_f = {0: 1.10, 1: 1.05, 2: 1.00, 3: 1.00, 4: 0.90, 5: 1.00}
w_doc_base = np.array([1.4, 1.3, 1.0, 0.9, 0.8, 0.8, 0.8, 0.9, 0.8, 0.6, 0.6, 0.6])
sat_docs = {1, 3, 5, 6, 8, 12}
hour_w = np.array([0.6, 1.2, 1.4, 1.4, 1.0, 0.4, 0.7, 1.2, 1.3, 1.1, 0.7])  # 07h..17h
tele_specs = {"Clínica Geral", "Cardiologia", "Dermatologia", "Endocrinologia", "Psiquiatria"}
primary_specs = {"Clínica Geral", "Pediatria"}
lead_ranges = [(0, 2), (3, 14), (15, 30), (31, 60)]

rows, used_slot = [], set()
day_used = {"d": None, "set": set()}
first_seen = {}
d = START
while d <= END:
    dow = d.weekday()
    if dow == 6 or d in HOLIDAYS:
        d += timedelta(days=1)
        continue
    mi = (d.year - 2025) * 12 + d.month - 1
    lam = (11 if dow == 5 else 22) * dow_f[dow] * month_f[d.month] * (1 + 0.006 * mi)
    n = rng.poisson(lam)
    w_doc = w_doc_base.copy()
    if d.month in (6, 7, 8):
        w_doc[[0, 1, 2, 3]] *= 1.35
    if dow == 5:
        for k in range(12):
            if (k + 1) not in sat_docs:
                w_doc[k] = 0
    w_doc = w_doc / w_doc.sum()
    hrs = np.arange(7, 18) if dow != 5 else np.arange(7, 13)
    hw = hour_w[: len(hrs)] / hour_w[: len(hrs)].sum()
    day_used["d"] = d
    for _ in range(n):
        doc = int(rng.choice(np.arange(1, 13), p=w_doc))
        spec = spec_doc[doc]
        cls = "ped" if spec == "Pediatria" else "gin" if spec == "Ginecologia" else "adult"
        pat, is_first = pick_patient(cls, {"d": d, "set": day_used["set"]})
        day_used["set"].add((pat, d))
        # horário único por médico/dia
        for _try in range(30):
            hh = int(rng.choice(hrs, p=hw))
            mm = int(rng.choice([0, 15, 30, 45]))
            key = (doc, d, hh, mm)
            if key not in used_slot:
                used_slot.add(key)
                break
        hora = f"{hh:02d}:{mm:02d}"
        # procedimento
        if spec in extra_prob and rng.random() < extra_prob[spec]:
            pid = int(rng.choice(spec_extras[spec]))
        else:
            pid = int(spec_consulta[spec])
        cat = cat_proc[pid]
        # antecedência
        probs = [0.38, 0.42, 0.15, 0.05] if spec in primary_specs else [0.12, 0.38, 0.28, 0.22]
        lo, hi = lead_ranges[int(rng.choice(4, p=probs))]
        lead = min(int(rng.integers(lo, hi + 1)), (d - START).days)
        # modalidade
        tele = False
        if cat == "Consulta" and spec in tele_specs:
            p_t = (0.03 + 0.27 * mi / 21) * (1.5 if spec == "Psiquiatria" else 1.0)
            tele = rng.random() < min(p_t, 0.6)
        if tele:
            canal = rng.choice(["App", "Site", "WhatsApp"], p=[0.55, 0.25, 0.20])
        else:
            canal = rng.choice(["App", "WhatsApp", "Telefone", "Site", "Presencial"], p=[0.34, 0.28, 0.20, 0.10, 0.08])
        # status
        pf = 0.085
        pf += 0.10 if lead > 30 else (0.02 if lead >= 15 else 0)
        pf += 0.04 if dow == 0 else (0.03 if dow == 4 else 0)
        pf += 0.04 if spec == "Dermatologia" else (0.03 if spec == "Psiquiatria" else 0)
        pf += 0.03 if tele else 0
        pf -= 0.03 if canal == "WhatsApp" else 0
        pf = float(np.clip(pf, 0.02, 0.6))
        pc = 0.055 + (0.03 if lead > 30 else (0.01 if lead >= 15 else 0))
        status = str(rng.choice(["Falta", "Cancelado", "Realizado"], p=[pf, pc, 1 - pf - pc]))
        cv = int(conv_pat[pat])
        cobrado = glosa = liquido = 0.0
        espera = nota = pd.NA
        if status == "Realizado":
            cobrado = round(valor_tab[pid] * float(conv.loc[cv - 1, "percentual_tabela"]), 2)
            p_g = 0.0 if cv == 1 else (0.30 if cv == 3 else 0.06)
            if rng.random() < p_g:
                glosa = round(cobrado * float(rng.uniform(0.3, 1.0)), 2)
            liquido = round(cobrado - glosa, 2)
            if tele:
                mean = 4
            else:
                mean = 10 if cat != "Consulta" else 16
                if doc == 7:
                    mean = 36
                mean += 4 if hh >= 12 else 0
                mean += 3 if dow == 0 else 0
            espera = int(np.clip(round(rng.gamma(2.2, mean / 2.2)), 0, 120))
            if rng.random() < (0.70 if tele else 0.58):
                mu = 4.75 - 0.03 * max(espera - 10, 0) - (0.10 if tele else 0)
                nota = int(np.clip(round(mu + rng.normal(0, 0.55)), 1, 5))
        rows.append(dict(
            data_atendimento=d, hora_inicio=hora, data_agendamento=d - timedelta(days=lead), dias_antecedencia=lead,
            pat=pat, id_medico=doc, id_convenio=cv, id_procedimento=pid, canal_agendamento=str(canal),
            modalidade="Telemedicina" if tele else "Presencial", status=status,
            primeira_visita="Sim" if is_first else "Não", tempo_espera_min=espera,
            valor_cobrado=cobrado, valor_glosa=glosa, valor_liquido=liquido, nota_satisfacao=nota,
        ))
    d += timedelta(days=1)

f = pd.DataFrame(rows).sort_values(["data_atendimento", "hora_inicio", "id_medico"]).reset_index(drop=True)
f.insert(0, "id_atendimento", range(1, len(f) + 1))
f["periodo_dia"] = np.where(f.hora_inicio < "12:00", "Manhã", "Tarde")
f["faixa_antecedencia"] = pd.cut(f.dias_antecedencia, [-1, 2, 14, 30, 999],
                                 labels=["00-02 dias", "03-14 dias", "15-30 dias", "31+ dias"]).astype(str)

# ---------------------------------------------------------------- pacientes que apareceram
first_rec = f.sort_values(["data_atendimento", "hora_inicio"]).groupby("pat").first()
used = sorted(f.pat.unique())
cad = {}
for p in used:
    if is_old[p]:
        cad[p] = date(2019, 1, 1) + timedelta(days=int(rng.integers(0, 2191)))
    else:
        cad[p] = first_rec.loc[p, "data_agendamento"]
pac = pd.DataFrame({
    "pat": used,
    "sexo": [sexo[p] for p in used],
    "data_nascimento": [nasc[p] for p in used],
    "cidade": [cidade[p] for p in used],
    "data_cadastro": [cad[p] for p in used],
}).sort_values(["data_cadastro", "pat"]).reset_index(drop=True)
pac.insert(0, "id_paciente", range(1, len(pac) + 1))
idmap = dict(zip(pac.pat, pac.id_paciente))
f["id_paciente"] = f.pat.map(idmap)
pac = pac.drop(columns="pat")
ref = END
pac["idade"] = [int((ref - n).days // 365.25) for n in pac.data_nascimento]
pac["faixa_etaria"] = pd.cut(pac.idade, [-1, 12, 17, 29, 44, 59, 200],
                             labels=["00-12", "13-17", "18-29", "30-44", "45-59", "60+"]).astype(str)
pac = pac[["id_paciente", "sexo", "data_nascimento", "idade", "faixa_etaria", "cidade", "data_cadastro"]]

fato = f[["id_atendimento", "data_agendamento", "data_atendimento", "hora_inicio", "periodo_dia",
          "dias_antecedencia", "faixa_antecedencia", "id_paciente", "id_medico", "id_convenio",
          "id_procedimento", "canal_agendamento", "modalidade", "status", "primeira_visita",
          "tempo_espera_min", "valor_cobrado", "valor_glosa", "valor_liquido", "nota_satisfacao"]].copy()
fato["tempo_espera_min"] = fato.tempo_espera_min.astype("Int64")
fato["nota_satisfacao"] = fato.nota_satisfacao.astype("Int64")

# ---------------------------------------------------------------- calendário
dn = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
mn = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
cal = []
dd = START
while dd <= END:
    wd = dd.weekday()
    hol = dd in HOLIDAYS
    cal.append(dict(
        data=dd, ano=dd.year, trimestre=f"T{(dd.month - 1) // 3 + 1}", mes_num=dd.month, mes_nome=mn[dd.month - 1],
        ano_mes=f"{dd.year}-{dd.month:02d}", dia=dd.day, dia_semana_num=wd + 1, dia_semana=dn[wd],
        fim_de_semana="Sim" if wd >= 5 else "Não", feriado="Sim" if hol else "Não",
        dia_util="Sim" if (wd < 5 and not hol) else "Não"))
    dd += timedelta(days=1)
cal = pd.DataFrame(cal)

med_out = med.copy()
tabelas = {"fato_atendimentos": fato, "dim_calendario": cal, "dim_pacientes": pac, "dim_medicos": med_out,
           "dim_procedimentos": proc, "dim_convenios": conv}
for nome, df in tabelas.items():
    df.to_csv(f"{OUT}/csv/{nome}.csv", index=False, encoding="utf-8")
    print(f"{nome:20s} {len(df):>6} linhas  {df.shape[1]} colunas")
pd.to_pickle(tabelas, f"{OUT}/tabelas.pkl")
