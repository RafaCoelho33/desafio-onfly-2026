## Defeitos corrigidos e causa raiz

1. Busca de status errada (src/onfly_report/services/status_policy.py)
   - Causa raiz: "is_billable" verificava "status != "CANCELLED", fazendo com que reservas NO_SHOW fossem contabilizadas nos totais de noites, valores, by_month e top_hotels em vez de apenas CONFIRMED.
   - Correção: alterado para "return status == "CONFIRMED".

2. Cálculo de noites em virada de mês/ano (src/onfly_report/services/stay_calculator.py)
   - Causa raiz: "calculate_room_nights" pegava apenas o dia do mês "(checkout.day - checkin.day)", gerando valores negativos ou incorretos quando o check-out ocorria em mês ou ano diferente do check-in.
   - Correção: alterado para "(checkout - checkin).days * rooms".

3. Conversão para BRL (src/onfly_report/services/currency_converter.py)
   - Causa raiz: "convert_to_brl" dividia o valor pela taxa de câmbio (amount / rate) em vez de multiplicar (amount * rate).
   - Correção: alterado para multiplicação pelo rate da moeda.

4. Ordenação do ranking top_hotels (src/onfly_report/services/report_builder.py)
   - Causa raiz: a ordenação de ranked_hotels usava "item[1]["amount"]" em ordem crescente em vez de decrescente.
   - Correção: alterado para "key=lambda item: (-item[1]["amount"], item[0])", invertendo a ordem que o ".sort()" gera, e mantendo hotel_id ascendente como critério de desempate.

5. Limite na leitura do CSV de reservas (src/onfly_report/repositories/csv_reservation_repository.py)
   - Causa raiz: "CsvReservationRepository.read()" interrompia a leitura ao atingir 200 linhas "(if len(rows) == 200: break)", ignorando as 100 reservas restantes de "data/reservas_hoteis.csv".
   - Correção: removido o "break" para processar todas as linhas do arquivo.

## Como o problema foi investigado

1. Execução inicial do pytest para identificar quais estavam falhando (test_status_rules, test_nights, test_currency, test_top_hotels e test_regression_report).
2. Inspeção de cada arquivo em "src/onfly_report/services/", verificando no README.md cada regra de negócio descrita.
3. Ajuste de cada arquivo e validação com a amostra de exemplo "(data/exemplo-validacao.csv)".
4. Execução do CLI sobre o dataset completo "(data/reservas_hoteis.csv)" e verificação via Python, o que revelou a exclusão de 100 registros no resultado final (300 esperados x 200 retornados).
5. Adição de testes extras em "tests/test_extra.py" (cenário sem reservas CONFIRMED e soma antes do arredondamento) e "tests/test_final_json.py" (validação do "output/report.json", feito pela IA).

## Como validar

### 1. Rodar os testes
```powershell
.\.venv\Scripts\pytest.exe -v
```


### 2. Validar o resultado com a amostra inicial (exemplo-validacao.csv)
```powershell
$env:PYTHONPATH="src"; .\.venv\Scripts\python.exe -m onfly_report --input data/exemplo-validacao.csv --rates data/taxas_cambio.csv --output output/exemplo.json
```

Conferir se output/exemplo.json corresponde exatamente à tabela da seção Amostra de validação do README.md.

### 3. Gerar e validar o relatório completo (reservas_hoteis.csv)
```powershell
$env:PYTHONPATH="src"; .\.venv\Scripts\python.exe -m onfly_report --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv --output output/report.json
```

Totais esperados em summary:
- total_reservations: 300
- confirmed_reservations: 235
- cancelled_reservations: 31
- no_show_reservations: 34
- total_room_nights: 1347
- total_amount_brl: "396170.00"
- average_nightly_rate_brl: "294.11"

## Resultado do pytest

Última execução do comando  .\.venv\Scripts\pytest.exe -v:

8 passed in 1.09s


Testes executados:
- tests/test_currency.py::test_currency_conversion_to_brl — PASSED
- tests/test_extra.py::test_zero_confirmed_reservations — PASSED
- tests/test_extra.py::test_decimal_sum_rounds — PASSED
- tests/test_final_json.py::test_final_json — PASSED
- tests/test_nights.py::test_nights_across_month_boundary — PASSED
- tests/test_regression_report.py::test_regression_report_on_sample — PASSED
- tests/test_status_rules.py::test_status_rules_exclude_cancelled_and_no_show — PASSED
- tests/test_top_hotels.py::test_top_hotels_are_ranked_descending — PASSED
