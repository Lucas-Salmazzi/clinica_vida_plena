import pandas as pd

t = pd.read_pickle("dados/tabelas.pkl")
f, cal, pac, med, proc, conv = (t[k] for k in
    ["fato_atendimentos", "dim_calendario", "dim_pacientes", "dim_medicos", "dim_procedimentos", "dim_convenios"])

print("=== INTEGRIDADE ===")
print("PK únicas:", f.id_atendimento.is_unique, pac.id_paciente.is_unique, med.id_medico.is_unique,
      proc.id_procedimento.is_unique, conv.id_convenio.is_unique, cal.data.is_unique)
print("FK paciente órfã:", (~f.id_paciente.isin(pac.id_paciente)).sum())
print("FK médico órfã:", (~f.id_medico.isin(med.id_medico)).sum())
print("FK convênio órfã:", (~f.id_convenio.isin(conv.id_convenio)).sum())
print("FK procedimento órfã:", (~f.id_procedimento.isin(proc.id_procedimento)).sum())
print("Datas fora do calendário (atend):", (~f.data_atendimento.isin(cal.data)).sum(),
      "(agend):", (~f.data_agendamento.isin(cal.data)).sum())
print("Pacientes sem atendimento:", (~pac.id_paciente.isin(f.id_paciente)).sum())
print("Duplicatas fato (exceto id):", f.drop(columns="id_atendimento").duplicated().sum())
print("Conflito médico/data/hora:", f.duplicated(["id_medico", "data_atendimento", "hora_inicio"]).sum())
print("Agendamento > atendimento:", (f.data_agendamento > f.data_atendimento).sum())
print("Cadastro > 1º atend:", (pac.set_index("id_paciente").data_cadastro >
      f.groupby("id_paciente").data_atendimento.min()).sum())
print("liquido = cobrado - glosa:", ((f.valor_cobrado - f.valor_glosa - f.valor_liquido).abs() > 0.011).sum(), "erros")
print("Nulos por coluna (fato):"); print(f.isna().sum()[lambda s: s > 0])
nr = f[f.status != "Realizado"]
print("Não realizados com valor/espera/nota:", (nr.valor_cobrado > 0).sum(), nr.tempo_espera_min.notna().sum(), nr.nota_satisfacao.notna().sum())
print("Realizados sem espera:", f[(f.status == "Realizado")].tempo_espera_min.isna().sum())
print("Período:", f.data_atendimento.min(), f.data_atendimento.max())
print("Domingos:", (pd.to_datetime(f.data_atendimento).dt.weekday == 6).sum())

print("\n=== VISÃO GERAL ===")
print(f.status.value_counts(normalize=True).round(3).to_dict(), len(f))
re = f[f.status == "Realizado"]
print("Receita bruta (cobrado):", round(re.valor_cobrado.sum()), " glosa:", round(re.valor_glosa.sum()),
      " líquida:", round(re.valor_liquido.sum()), " taxa glosa:", round(re.valor_glosa.sum() / re.valor_cobrado.sum() * 100, 1))
print("Ticket médio (líquido/realizado):", round(re.valor_liquido.sum() / len(re), 2))
print("Nota média:", round(re.nota_satisfacao.dropna().mean(), 2), " respondentes:", re.nota_satisfacao.notna().mean().round(3))
print("Espera média:", round(re.tempo_espera_min.mean(), 1))

f["ano"] = pd.to_datetime(f.data_atendimento).dt.year
f["mes"] = pd.to_datetime(f.data_atendimento).dt.to_period("M").astype(str)
f["dow"] = pd.to_datetime(f.data_atendimento).dt.weekday
f = f.merge(med[["id_medico", "nome_medico", "especialidade"]], on="id_medico").merge(conv[["id_convenio", "convenio"]], on="id_convenio")
f = f.merge(proc[["id_procedimento", "valor_tabela", "categoria"]], on="id_procedimento")
re = f[f.status == "Realizado"]

print("\n-- por ano (receita líquida, atendimentos):")
print(re.groupby("ano").agg(liq=("valor_liquido", "sum"), n=("id_atendimento", "count")).round(0))
print("\n-- falta % por dia da semana (0=Seg):")
print((f.assign(falta=f.status == "Falta").groupby("dow").falta.mean() * 100).round(1).to_dict())
print("-- falta % por faixa antecedência:")
print((f.assign(falta=f.status == "Falta").groupby("faixa_antecedencia").falta.mean() * 100).round(1).to_dict())
print("-- falta % por canal:")
print((f.assign(falta=f.status == "Falta").groupby("canal_agendamento").falta.mean() * 100).round(1).to_dict())
print("-- falta % por especialidade:")
print((f.assign(falta=f.status == "Falta").groupby("especialidade").falta.mean() * 100).round(1).sort_values(ascending=False).to_dict())
print("-- falta % por modalidade:")
print((f.assign(falta=f.status == "Falta").groupby("modalidade").falta.mean() * 100).round(1).to_dict())
fa = f[f.status == "Falta"]
print("Receita perdida por faltas (valor_tabela):", round(fa.valor_tabela.sum()), " cancel:", round(f[f.status == "Cancelado"].valor_tabela.sum()))
print("\n-- glosa % por convênio:")
g = re.groupby("convenio").agg(cob=("valor_cobrado", "sum"), glo=("valor_glosa", "sum"), n=("id_atendimento", "count"))
g["pct"] = (g.glo / g.cob * 100).round(1); print(g.round(0))
print("\n-- telemedicina share por trimestre (Consultas realizadas):")
f["tri"] = pd.to_datetime(f.data_atendimento).dt.to_period("Q").astype(str)
print((f[f.status == "Realizado"].assign(t=lambda x: x.modalidade == "Telemedicina").groupby("tri").t.mean() * 100).round(1).to_dict())
print("\n-- médico: espera média / nota:")
m = re.groupby("nome_medico").agg(esp=("tempo_espera_min", "mean"), nota=("nota_satisfacao", "mean"), n=("id_atendimento", "count"))
print(m.round(2).sort_values("esp", ascending=False))
print("\n-- nota por faixa de espera:")
re2 = re.dropna(subset=["nota_satisfacao"]).copy()
re2["fe"] = pd.cut(re2.tempo_espera_min, [-1, 10, 20, 30, 45, 200], labels=["0-10", "11-20", "21-30", "31-45", "46+"])
print(re2.groupby("fe", observed=True).nota_satisfacao.mean().round(2).to_dict())
print("\n-- atendimentos por mês:"); print(f.groupby("mes").size().to_dict())
print("\n-- realizados por categoria:", re.categoria.value_counts().to_dict())
print("-- receita líquida por especialidade:"); print(re.groupby("especialidade").valor_liquido.sum().round(0).sort_values(ascending=False).to_dict())
print("-- pacientes novos (primeira_visita=Sim):", (f.primeira_visita == "Sim").sum(), "de", f.id_paciente.nunique(), "pacientes")
