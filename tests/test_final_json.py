import csv, json
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from collections import defaultdict
import pytest


def test_final_json():
    """Valida output/report.json; o relatório deve ser gerado via CLI antes de executar este teste."""
    with open('data/taxas_cambio.csv', encoding='utf-8') as f:
        rates = {r['currency']: Decimal(r['rate_to_brl']) for r in csv.DictReader(f)}

    with open('data/reservas_hoteis.csv', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    try:
        with open('output/report.json', encoding='utf-8') as f:
            rep = json.load(f)
    
    except FileNotFoundError:
        pytest.skip("output/report.json não encontrado, gere-o via CLI antes de executar este teste.")      

    q = lambda d: str(d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    counts = defaultdict(int)
    nights, total = 0, Decimal('0')
    by_m = defaultdict(lambda: [0, 0, Decimal('0')])
    by_h = defaultdict(lambda: ['', 0, Decimal('0')])

    for r in rows:
        counts[r['status']] += 1
        if r['status'] == 'CONFIRMED':
            n = (date.fromisoformat(r['checkout_date']) - date.fromisoformat(r['checkin_date'])).days * int(r['rooms'])
            brl = Decimal(r['amount']) * rates[r['currency']]
            nights += n
            total += brl
            m = r['checkin_date'][:7]
            by_m[m][0] += 1; by_m[m][1] += n; by_m[m][2] += brl
            by_h[r['hotel_id']][0] = r['hotel_name']
            by_h[r['hotel_id']][1] += n; by_h[r['hotel_id']][2] += brl

    expected_summary = {
        'total_reservations': len(rows),
        'confirmed_reservations': counts['CONFIRMED'],
        'cancelled_reservations': counts['CANCELLED'],
        'no_show_reservations': counts['NO_SHOW'],
        'total_room_nights': nights,
        'total_amount_brl': q(total),
        'average_nightly_rate_brl': q(total / nights) if nights else '0.00',
    }
    expected_by_month = [
        {'month': m, 'reservations': v[0], 'room_nights': v[1], 'total_brl': q(v[2])}
        for m, v in sorted(by_m.items())
    ]
    expected_top = [
        {'hotel_id': hid, 'hotel_name': v[0], 'room_nights': v[1], 'total_brl': q(v[2])}
        for hid, v in sorted(by_h.items(), key=lambda x: (-x[1][2], x[0]))[:5]
    ]

    assert rep['report_version'] == '1.0'
    assert rep['generated_at'].endswith('-03:00')
    assert rep['summary'] == expected_summary, f'summary: {rep["summary"]} != {expected_summary}'
    assert rep['by_month'] == expected_by_month, 'by_month divergente'
    assert rep['top_hotels'] == expected_top, 'top_hotels divergente'

