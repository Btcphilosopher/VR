from dataclasses import dataclass
from enum import Enum
import math
import random
import time


class Hand(Enum):
    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"


class BodyZone(Enum):
    THUMB = "thumb"
    INDEX = "index"
    MIDDLE = "middle"
    RING = "ring"
    LITTLE = "little"
    PALM = "palm"
    WRIST = "wrist"
    FOREARM = "forearm"
    CHEST = "chest"


@dataclass
class HapticPulse:
    hand: Hand
    zone: BodyZone

    amplitude: float
    frequency: float
    duration_ms: int

    effect: str = "force_lightning"


class ForceLightningHaptics:

    def __init__(self):

        self.enabled = True

        # Maximum software intensity.
        # This is deliberately an abstract haptic scale,
        # NOT electrical current or voltage.
        self.max_intensity = 1.0

    def emit(self, pulse: HapticPulse):

        if not self.enabled:
            return

        pulse.amplitude = max(
            0.0,
            min(
                self.max_intensity,
                pulse.amplitude
            )
        )

        print(
            f"⚡ {pulse.effect:16s} "
            f"{pulse.hand.value:5s} "
            f"{pulse.zone.value:8s} "
            f"amp={pulse.amplitude:.2f} "
            f"freq={pulse.frequency:.0f}Hz "
            f"time={pulse.duration_ms}ms"
        )

    # ---------------------------------------------------------
    # ELECTRICAL "TINGLING"
    # ---------------------------------------------------------

    def electrical_tingle(
        self,
        hand: Hand,
        intensity: float
    ):

        """
        Creates the perception of electrical tingling
        using rapid haptic pulses.
        """

        intensity = max(
            0.0,
            min(1.0, intensity)
        )

        fingers = [
            BodyZone.THUMB,
            BodyZone.INDEX,
            BodyZone.MIDDLE,
            BodyZone.RING,
            BodyZone.LITTLE
        ]

        for finger in fingers:

            pulse = HapticPulse(
                hand=hand,
                zone=finger,

                amplitude=(
                    0.10
                    + intensity * 0.25
                ),

                frequency=(
                    90
                    + random.random() * 180
                ),

                duration_ms=random.randint(
                    15,
                    35
                )
            )

            self.emit(pulse)

    # ---------------------------------------------------------
    # LIGHTNING ARC
    # ---------------------------------------------------------

    def lightning_arc(
        self,
        hand: Hand,
        intensity: float
    ):

        """
        Simulates lightning jumping around the hand.
        """

        intensity = max(
            0.0,
            min(1.0, intensity)
        )

        zones = [
            BodyZone.INDEX,
            BodyZone.MIDDLE,
            BodyZone.PALM,
            BodyZone.THUMB,
            BodyZone.RING,
            BodyZone.LITTLE
        ]

        # Random electrical-looking propagation.
        random.shuffle(zones)

        for zone in zones:

            self.emit(
                HapticPulse(
                    hand=hand,
                    zone=zone,

                    amplitude=(
                        0.15
                        + intensity * 0.40
                    ),

                    frequency=(
                        120
                        + random.random() * 250
                    ),

                    duration_ms=random.randint(
                        12,
                        45
                    )
                )
            )

    # ---------------------------------------------------------
    # BUILDING FORCE LIGHTNING
    # ---------------------------------------------------------

    def charge_up(
        self,
        hand: Hand,
        duration: float = 2.0
    ):

        """
        Force lightning charging sensation.

        Starts subtle and becomes increasingly intense.
        """

        start = time.time()

        while time.time() - start < duration:

            progress = (
                time.time() - start
            ) / duration

            intensity = (
                progress ** 1.8
            )

            self.electrical_tingle(
                hand,
                intensity
            )

            time.sleep(
                0.08
            )

    # ---------------------------------------------------------
    # LIGHTNING ATTACK
    # ---------------------------------------------------------

    def fire_lightning(
        self,
        intensity: float = 1.0,
        duration: float = 2.0
    ):

        """
        Full two-handed Force Lightning attack.
        """

        start = time.time()

        while time.time() - start < duration:

            # Slightly different pattern on each hand.
            left_intensity = (
                intensity *
                random.uniform(
                    0.75,
                    1.0
                )
            )

            right_intensity = (
                intensity *
                random.uniform(
                    0.75,
                    1.0
                )
            )

            self.lightning_arc(
                Hand.LEFT,
                left_intensity
            )

            self.lightning_arc(
                Hand.RIGHT,
                right_intensity
            )

            time.sleep(
                random.uniform(
                    0.03,
                    0.09
                )
            )

    # ---------------------------------------------------------
    # LIGHTNING IMPACT
    # ---------------------------------------------------------

    def impact(
        self,
        intensity: float
    ):

        intensity = max(
            0.0,
            min(1.0, intensity)
        )

        for hand in [
            Hand.LEFT,
            Hand.RIGHT
        ]:

            self.emit(
                HapticPulse(
                    hand=hand,
                    zone=BodyZone.PALM,

                    amplitude=(
                        0.45
                        + intensity * 0.50
                    ),

                    frequency=220,

                    duration_ms=70
                )
            )

    # ---------------------------------------------------------
    # COOL DOWN
    # ---------------------------------------------------------

    def discharge(
        self,
        hand: Hand
    ):

        """
        Fading residual Force sensation.
        """

        for intensity in [
            0.35,
            0.25,
            0.17,
            0.10,
            0.04
        ]:

            self.electrical_tingle(
                hand,
                intensity
            )

            time.sleep(
                0.10
            )


if __name__ == "__main__":

    force = ForceLightningHaptics()

    print("\n=== JEDI FORCE LIGHTNING ===\n")

    print("Charging Force...")
    force.charge_up(
        Hand.BOTH,
        duration=1.5
    )

    print("\n⚡ LIGHTNING RELEASE ⚡")

    force.fire_lightning(
        intensity=1.0,
        duration=1.5
    )

    print("\n💥 IMPACT")

    force.impact(
        intensity=1.0
    )

    print("\nDischarging...")

    force.discharge(
        Hand.BOTH
    )
