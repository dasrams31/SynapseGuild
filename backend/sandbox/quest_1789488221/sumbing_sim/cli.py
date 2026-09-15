"""Command line interface and reporting for Mount Sumbing Expedition Simulator."""

from sumbing_sim.models import Climber
from sumbing_sim.data import create_standard_gear_kit
from sumbing_sim.engine import ExpeditionSimulator, ExpeditionStatus


def run_expedition_demo() -> None:
    print("=" * 60)
    print("   MOUNT SUMBING EXPEDITION SIMULATOR (3371 MASL)   ")
    print("=" * 60)

    climber = Climber(name="Budi", max_carry_weight_kg=18.0)
    for item in create_standard_gear_kit():
        climber.add_item(item)

    sim = ExpeditionSimulator(climber)
    readiness = sim.validate_gear_readiness()

    print(f"Climber: {climber.name}")
    print(f"Carry Weight: {climber.current_carry_weight:.2f} kg / {climber.max_carry_weight_kg} kg")
    print(f"Readiness Score: {readiness.score}% (Ready: {readiness.is_ready})")
    if readiness.warnings:
        print("Warnings:")
        for w in readiness.warnings:
            print(f"  - {w}")
    print("-" * 60)

    # Simulate climb sequence
    print("Starting expedition...")
    sim.trek(pace="normal")  # Pos 1
    sim.trek(pace="normal")  # Pos 2
    sim.trek(pace="normal")  # Pos 3 Pestan
    sim.trek(pace="slow")    # Pasar Watu
    sim.trek(pace="slow")    # Watu Kotak
    sim.camp(hours=6.0)      # Camp overnight at Watu Kotak
    sim.summit_attack()      # Puncak Sejati

    print("\n--- EXPEDITION LOGS ---")
    for log_entry in sim.log:
        print(log_entry)

    print("=" * 60)
    print(f"FINAL OUTCOME: {sim.status.value}")
    print(f"FINAL STATS -> Stamina: {sim.climber.stamina:.1f} | Temp: {sim.climber.body_temp:.1f}°C | Hydration: {sim.climber.hydration:.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    run_expedition_demo()
