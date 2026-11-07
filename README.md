# Clínica Vida Plena — Onde a clínica está perdendo receita?

Relatório em **Power BI** sobre uma clínica médica fictícia de São Paulo: faltas, cancelamentos, glosas de convênios, receita e tempo de espera, de jan/2025 a out/2026.

> **Dados 100% fictícios.** Médicos, pacientes e convênios foram inventados. Os dados foram gerados por um script em Python (`scripts/gerar_dataset.py`, com semente fixa, então o resultado é reprodutível).

![Visão geral do relatório](imagens/pagina_1_visao_geral.png)

## Pergunta central

**Onde a Clínica Vida Plena está perdendo receita, e o que dá para fazer a respeito?**

O relatório responde:

- Quanto a clínica fatura de verdade (receita líquida) e como isso evoluiu contra 2025?
- Quanto se perde com faltas, cancelamentos e glosas dos convênios?
- Quem falta mais: em que dia da semana, com quanta antecedência, por qual canal, em qual especialidade?
- Algum convênio ou médico destoa dos demais?
- A espera no consultório afeta a nota de satisfação?
- A telemedicina está crescendo, e ela falta mais ou menos que o presencial?

## Páginas do relatório

| Página | Pergunta | Destaques |
|---|---|---|
| **Visão geral** | Quanto a clínica fatura e como evoluiu? | Receita líquida, atendimentos, ticket médio, taxa de falta, taxa de glosa, nota média; comparação 2026 x 2025 |
| **Faltas** | Quem não aparece, e por quê? | Taxa de falta por dia da semana, antecedência, canal, especialidade e modalidade; mapa de calor dia x período |
| **Financeiro** | Onde o dinheiro fica no caminho? | Receita bruta, glosa e líquida por convênio; composição por especialidade e procedimento |
| **Operação** | A espera custa nota? | Espera x nota por médico, % de esperas acima de 30 min, crescimento da telemedicina |
| **Sobre os dados** | Que dados são esses? | Cenário, período, tabelas e aviso de dados fictícios |

**Faltas**

![Página Faltas](imagens/pagina_2_faltas.png)

**Financeiro**

![Página Financeiro](imagens/pagina_3_financeiro.png)

**Operação**

![Página Operação](imagens/pagina_4_operacao.png)

## Principais achados

1. **Segunda-feira é o dia com mais faltas:** 15,1%, contra 10,3% a 11,7% nos outros dias (média geral de 11,7%).
2. **Agendar com mais de 30 dias de antecedência dobra a falta:** 20,2%, contra 9,8% a 11,4% nas outras faixas.
3. **WhatsApp é o canal com menos faltas:** 9,2%, contra 12,4% a 12,8% nos demais canais.
4. **Dermatologia (16,9%) e Psiquiatria (16,5%) são as especialidades com mais faltas**; a menor taxa é a de Oftalmologia (8,5%).
5. **Telemedicina falta mais que o presencial:** 15,8% contra 11,3%.
6. **A telemedicina cresce rápido:** de 1,6% dos atendimentos realizados no 1º trimestre de 2025 para 14,4% em outubro de 2026.
7. **O convênio Medfácil concentra a glosa:** 20,1% do valor cobrado, contra 3,6% a 4,6% nos outros planos com glosa (o Particular não tem). São R$ 76.589 dos R$ 128.522 glosados (60%).
8. **Dr. Rafael Moura (Ortopedia) tem a maior espera e a pior nota:** 39 min de espera e nota 3,88, contra 14,6 a 19,8 min e notas de 4,38 a 4,55 nos outros 11 médicos.
9. **Espera longa derruba a nota:** 4,66 com até 10 min de espera e 3,18 acima de 45 min.
10. **Faltas e cancelamentos custam caro:** R$ 620 mil em valor de tabela, o equivalente a 28% da receita líquida.

Outros números: a receita líquida de jan a out/2026 está 6,5% acima do mesmo período de 2025; Clínica Geral lidera a receita (R$ 484 mil, 22% do total), seguida de Pediatria (R$ 392 mil) e Ginecologia (R$ 348 mil).

## Modelo de dados

Modelo estrela com uma tabela fato e cinco dimensões.

```
dim_calendario ──┐ (data_atendimento: ativo | data_agendamento: inativo, via USERELATIONSHIP)
dim_pacientes ───┤
dim_medicos ─────┼──► fato_atendimentos
dim_procedimentos┤
dim_convenios ───┘
```

| Tabela | Linhas | Descrição |
|---|---|---|
| `fato_atendimentos` | 11.401 | Um agendamento por linha (realizado, falta ou cancelado) |
| `dim_calendario` | 669 | Um dia por linha, 01/01/2025 a 31/10/2026 |
| `dim_pacientes` | 2.085 | Pacientes |
| `dim_medicos` | 12 | Médicos e especialidades |
| `dim_procedimentos` | 19 | Consultas, exames e procedimentos, com valor de tabela |
| `dim_convenios` | 5 | Planos de saúde e Particular |

Dicionário de colunas em [`dados/dicionario_de_dados.md`](dados/dicionario_de_dados.md).

## Medidas DAX

36 medidas organizadas por tema (volume, taxas, financeiro, espera e satisfação, agenda e canais, comparações no tempo, ranking), mais 2 colunas calculadas. Todas em [`dax/medidas.md`](dax/medidas.md).

## O que foi usado

- **Power BI Desktop**: modelagem, DAX, visuais, navegação entre páginas e tooltips
- **Power Query**: tipagem das colunas e colunas calculadas
- **DAX**: medidas de volume, taxas, inteligência de tempo e ranking
- **Python (pandas, numpy)**: geração e validação do dataset
- **Design**: logo, ícones dos KPIs e botões de navegação criados em SVG (pasta `assets/`)

## Estrutura do repositório

```
├── relatorio/      relatório Power BI (.pbix)
├── imagens/        prints das páginas
├── dados/
│   ├── csv/        as 6 tabelas em CSV (UTF-8, ponto como decimal)
│   ├── clinica_vida_plena.xlsx   as mesmas tabelas, uma aba por tabela
│   └── dicionario_de_dados.md
├── dax/            medidas e colunas calculadas
├── scripts/        geração e validação do dataset (Python)
└── assets/         logo, ícones dos KPIs e botões de navegação
```

## Como abrir

1. Baixe `relatorio/clinica_vida_plena.pbix` e abra no Power BI Desktop.
2. Se o Power BI pedir para localizar a fonte de dados, aponte para `dados/clinica_vida_plena.xlsx` (Transformar dados > Configurações da fonte de dados).

Para gerar o dataset de novo:

```bash
pip install pandas numpy openpyxl
python scripts/gerar_dataset.py
python scripts/validar_dataset.py
```

## Autor

**Lucas Salmazzi** · [LinkedIn](https://www.linkedin.com/in/SEU-PERFIL) · [GitHub](https://github.com/SEU-USUARIO)
