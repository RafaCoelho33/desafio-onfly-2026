from helpers import run_cli


def test_zero_confirmed_reservations(tmp_path):
        """Sem reservas CONFIRMED, average_nightly_rate_brl deve ser '0.00' sem divisão por zero."""
        report = run_cli(
            tmp_path,
            [
                {"reservation_id": "R-1", "status": "CANCELLED", "amount": "500.00"},
                {"reservation_id": "R-2", "status": "NO_SHOW", "amount": "300.00"},
            ],
        )
        summary = report["summary"]
        assert summary["total_reservations"] == 2
        assert summary["confirmed_reservations"] == 0
        assert summary["cancelled_reservations"] == 1
        assert summary["no_show_reservations"] == 1
        assert summary["total_room_nights"] == 0
        assert summary["total_amount_brl"] == "0.00"
        assert summary["average_nightly_rate_brl"] == "0.00"
        assert report["by_month"] == []
        assert report["top_hotels"] == []

def test_decimal_sum_rounds(tmp_path):
        """Valores exatos em USD somam antes do arredondamento half-up final."""
        report = run_cli(
            tmp_path,
            [
                {"reservation_id": "R-1", "currency": "USD", "amount": "1.001"},
                {"reservation_id": "R-2", "currency": "USD", "amount": "1.001"},
            ],
        )
        assert report["summary"]["total_amount_brl"] == "10.85"