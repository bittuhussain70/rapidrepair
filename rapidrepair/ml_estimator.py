from dataclasses import dataclass
from typing import Dict, Iterable, List


SERVICE_BASE = {
    "ac-general-service": 499,
    "ac-jet-cleaning": 899,
    "ac-repair": 349,
    "ac-gas-refill": 2199,
    "ac-installation": 1499,
    "ac-uninstallation": 799,
    "ac-deep-repair": 1299,
    "refrigerator-repair": 399,
    "washing-machine-repair": 449,
    "ro-service": 399,
    "electrician-visit": 299,
}

SERVICE_TIME = {
    "ac-general-service": 45,
    "ac-jet-cleaning": 70,
    "ac-repair": 55,
    "ac-gas-refill": 90,
    "ac-installation": 120,
    "ac-uninstallation": 75,
    "ac-deep-repair": 110,
    "refrigerator-repair": 65,
    "washing-machine-repair": 70,
    "ro-service": 55,
    "electrician-visit": 45,
}


@dataclass
class Estimate:
    price: int
    minutes: int
    confidence: float
    note: str


class RapidRepairEstimator:
    """Tiny trained estimator for quotes without requiring heavy ML packages."""

    def __init__(self) -> None:
        self.weights = [0.0] * 7
        self._train()

    def _features(self, row: Dict[str, float]) -> List[float]:
        service = str(row.get("service", "ac-general-service"))
        return [
            1.0,
            SERVICE_BASE.get(service, 499) / 1000,
            float(row.get("urgency", 1)),
            float(row.get("tonnage", 1.5)),
            float(row.get("unit_age", 3)) / 10,
            float(row.get("inverter", 0)),
            float(row.get("distance_km", 4)) / 10,
        ]

    def _training_rows(self) -> Iterable[Dict[str, float]]:
        for service, base in SERVICE_BASE.items():
            for urgency in (1, 2, 3):
                for age in (1, 4, 8):
                    for tonnage in (1.0, 1.5, 2.0):
                        inverter = 1 if tonnage >= 1.5 else 0
                        distance = 3 + urgency * 2
                        price = (
                            base
                            + (urgency - 1) * 180
                            + max(age - 3, 0) * 55
                            + max(tonnage - 1.0, 0) * 160
                            + inverter * 90
                            + distance * 18
                        )
                        yield {
                            "service": service,
                            "urgency": urgency,
                            "unit_age": age,
                            "tonnage": tonnage,
                            "inverter": inverter,
                            "distance_km": distance,
                            "target": price,
                        }

    def _train(self) -> None:
        rows = list(self._training_rows())
        learning_rate = 0.015
        for _ in range(1500):
            gradients = [0.0] * len(self.weights)
            for row in rows:
                x = self._features(row)
                predicted = sum(w * v for w, v in zip(self.weights, x))
                error = predicted - (float(row["target"]) / 1000)
                for index, value in enumerate(x):
                    gradients[index] += error * value / len(rows)
            self.weights = [
                weight - learning_rate * gradient
                for weight, gradient in zip(self.weights, gradients)
            ]

    def predict(self, payload: Dict[str, object]) -> Estimate:
        urgency_map = {"standard": 1, "today": 2, "emergency": 3}
        service = str(payload.get("service", "ac-general-service"))
        urgency_key = str(payload.get("urgency", "standard"))
        unit_age = _float(payload.get("unit_age"), 3)
        tonnage = _float(payload.get("tonnage"), 1.5)
        distance = _float(payload.get("distance_km"), 4)
        row = {
            "service": service,
            "urgency": urgency_map.get(urgency_key, 1),
            "unit_age": unit_age,
            "tonnage": tonnage,
            "inverter": 1 if str(payload.get("ac_type", "")).lower() == "inverter" else 0,
            "distance_km": distance,
        }
        raw_price = sum(w * v for w, v in zip(self.weights, self._features(row))) * 1000
        base = SERVICE_BASE.get(service, 499)
        price = max(base, int(round(raw_price / 10) * 10))
        minutes = SERVICE_TIME.get(service, 60)
        minutes += int(max(unit_age - 3, 0) * 4)
        minutes += {1: 0, 2: 10, 3: 20}.get(row["urgency"], 0)
        confidence = 0.88
        if service not in SERVICE_BASE:
            confidence -= 0.2
        if unit_age > 10:
            confidence -= 0.08
        note = "Final price depends on inspection, spare parts, and gas leakage condition."
        return Estimate(price=price, minutes=minutes, confidence=round(confidence, 2), note=note)


def _float(value: object, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback
