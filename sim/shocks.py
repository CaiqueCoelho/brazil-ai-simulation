import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Shock:
    commodity: float
    global_rate: float
    drought: float
    scandal: bool
    pandemic: float

    def describe(self) -> str:
        parts = []
        if self.commodity > 0.4:
            parts.append("preços das commodities exportadas em forte alta")
        elif self.commodity < -0.4:
            parts.append("preços das commodities exportadas em forte queda")
        if self.global_rate > 0.4:
            parts.append("juros dos EUA subindo e tirando capital dos emergentes")
        elif self.global_rate < -0.4:
            parts.append("juros globais caindo e capital entrando nos emergentes")
        if self.drought:
            parts.append("seca severa atinge lavouras e reservatórios das hidrelétricas")
        if self.scandal:
            parts.append("escândalo de corrupção envolvendo aliados do governo domina o noticiário")
        if self.pandemic:
            parts.append("nova onda epidêmica obriga a restrições temporárias")
        return "; ".join(parts) or "nenhum choque externo relevante no trimestre"


def shock_schedule(seed: int, ticks: int) -> list[Shock]:
    """Intensity 1.0 means the calibrated historical event (2020 pandemic, 2021 water crisis); random draws match 2018-2026 frequencies: small commodity swings, half-strength droughts, a once-a-century pandemic."""
    rng = random.Random(f"shocks-{seed}")
    return [
        Shock(
            commodity=max(-1.0, min(1.0, rng.gauss(0, 0.2))),
            global_rate=max(-1.0, min(1.0, rng.gauss(0, 0.4))),
            drought=0.5 if rng.random() < 0.10 else 0.0,
            scandal=rng.random() < 0.10,
            pandemic=1.0 if rng.random() < 0.0025 else 0.0,
        )
        for _ in range(ticks)
    ]
