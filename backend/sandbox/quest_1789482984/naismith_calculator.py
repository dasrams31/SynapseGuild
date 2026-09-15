"""Modul perhitungan estimasi waktu perjalanan berdasarkan Aturan Naismith."""
from typing import Dict, Union


def _validate_numeric_input(value: Union[int, float], param_name: str) -> None:
    """Memvalidasi tipe dan nilai input untuk aturan Naismith."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{param_name} harus bertipe int atau float, didapatkan {type(value).__name__}.")
    if value < 0:
        raise ValueError(f"{param_name} tidak boleh bernilai negatif (diterima: {value}).")


def calculate_naismith_time(distance_km: float, elevation_gain_m: float) -> float:
    """
    Menghitung estimasi waktu tempuh hiking (dalam jam) menggunakan Aturan Naismith standar.
    
    Rumus:
        Waktu (jam) = (distance_km / 5.0) + (elevation_gain_m / 600.0)

    Args:
        distance_km (float): Jarak horizontal rute dalam kilometer.
        elevation_gain_m (float): Total kenaikan elevasi rute dalam meter.

    Returns:
        float: Estimasi total durasi dalam satuan jam.

    Raises:
        TypeError: Jika input bukan numerik (int/float) atau bertipe bool.
        ValueError: Jika nilai input bernilai negatif.
    """
    _validate_numeric_input(distance_km, "distance_km")
    _validate_numeric_input(elevation_gain_m, "elevation_gain_m")

    horizontal_time = distance_km / 5.0
    vertical_time = elevation_gain_m / 600.0
    return float(horizontal_time + vertical_time)


def calculate_naismith_breakdown(distance_km: float, elevation_gain_m: float) -> Dict[str, Union[int, float]]:
    """
    Menghitung estimasi waktu tempuh dan membaginya ke dalam format jam dan menit.

    Args:
        distance_km (float): Jarak horizontal rute dalam kilometer.
        elevation_gain_m (float): Total kenaikan elevasi rute dalam meter.

    Returns:
        dict: Kamus berisi rincian {'hours': int, 'minutes': int, 'total_hours': float}.
    """
    total_hours = calculate_naismith_time(distance_km, elevation_gain_m)
    total_minutes = round(total_hours * 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    return {
        "hours": int(hours),
        "minutes": int(minutes),
        "total_hours": float(total_hours),
    }
