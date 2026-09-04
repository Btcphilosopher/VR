"""
JEDI FORCE HAPTICS ENGINE
==========================

VR haptic-feedback engine for a lightsaber / Force-based VR game.

Designed around events such as:

    FORCE_GRAB
    FORCE_PUSH
    FORCE_PULL
    FORCE_THROW
    FORCE_CRUSH
    FORCE_LIFT
    FORCE_HOLD
    FORCE_RELEASE

Plus lightsaber events:

    SABER_IGNITE
    SABER_SWING
    SABER_HIT
    SABER_BLOCK
    SABER_CLASH

The engine produces abstract HapticCommand objects.

Connect HapticOutput to:
    - OpenXR
    - SteamVR/OpenVR
    - Meta Quest
    - PS VR2
    - haptic gloves
    - haptic vest
    - custom controller hardware

This is a game-development prototype, not a medical or safety system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import math
import random
import time


# ============================================================
# HANDS
# ============================================================

class Hand(Enum):
    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"


# ============================================================
# FORCE EVENTS
# ============================================================

class ForceEvent(Enum):
    FORCE_GRAB = "force_grab"
    FORCE_PUSH = "force_push"
    FORCE_PULL = "force_pull"
    FORCE_THROW = "force_throw"
    FORCE_CRUSH = "force_crush"
    FORCE_LIFT = "force_lift"
    FORCE_HOLD = "force_hold"
    FORCE_RELEASE = "force_release"

    SABER_IGNITE = "saber_ignite"
    SABER_RETRACT = "saber_retract"
    SABER_SWING = "saber_swing"
    SABER_HIT = "saber_hit"
    SABER_BLOCK = "saber_block"
    SABER_CLASH = "saber_clash"


# ============================================================
# HAPTIC COMMAND
# ============================================================

@dataclass
class HapticCommand:

    hand: Hand

    amplitude: float

    duration_ms: float

    frequency_hz: float

    event: str

    channel: str = "controller"

    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):

        self.amplitude = max(0.0, min(1.0, self.amplitude))

        self.duration_ms = max(
            0.0,
            self.duration_ms
        )

        self.frequency_hz = max(
            0.0,
            self.frequency_hz
        )


# ============================================================
# FORCE STATE
# ============================================================

@dataclass
class ForceState:

    force_energy: float = 0.0

    grip_strength: float = 0.0

    object_mass: float = 1.0

    resistance: float = 0.0

    velocity: float = 0.0

    concentration: float = 1.0

    is_holding: bool = False


# ============================================================
# HAPTIC OUTPUT
# ============================================================

class HapticOutput:

    """
    Hardware abstraction layer.

    Replace send() with an OpenXR / SteamVR implementation.
    """

    def send(self, command: HapticCommand):

        print(
            f"[HAPTIC] "
            f"{command.hand.value.upper():5s} | "
            f"{command.event:16s} | "
            f"amp={command.amplitude:.2f} | "
            f"freq={command.frequency_hz:5.0f} Hz | "
            f"{command.duration_ms:5.0f} ms"
        )


# ============================================================
# HAPTIC MIXER
# ============================================================

class HapticMixer:

    """
    Prevents dozens of simultaneous events from becoming
    an unpleasant continuous vibration.

    Higher intensity events override weaker ones.
    """

    def __init__(self, output: HapticOutput):

        self.output = output

        self.last_event = {}

    def play(self, command: HapticCommand):

        key = command.hand.value

        now = time.time()

        previous = self.last_event.get(key)

        # Simple event suppression.
        if previous:

            elapsed = (now - previous.timestamp) * 1000

            if elapsed < 15 and \
               command.amplitude < previous.amplitude:

                return

        self.last_event[key] = command

        self.output.send(command)


# ============================================================
# FORCE HAPTICS ENGINE
# ============================================================

class JediForceHaptics:

    def __init__(self):

        self.output = HapticOutput()

        self.mixer = HapticMixer(self.output)

        self.left = ForceState()

        self.right = ForceState()

        self.event_queue = deque()

    # --------------------------------------------------------
    # HAND STATE
    # --------------------------------------------------------

    def state(self, hand: Hand) -> ForceState:

        if hand == Hand.LEFT:
            return self.left

        return self.right

    # --------------------------------------------------------
    # LOW LEVEL HAPTIC
    # --------------------------------------------------------

    def pulse(
        self,
        hand: Hand,
        amplitude: float,
        duration_ms: float,
        frequency_hz: float,
        event: str
    ):

        command = HapticCommand(
            hand=hand,
            amplitude=amplitude,
            duration_ms=duration_ms,
            frequency_hz=frequency_hz,
            event=event
        )

        self.mixer.play(command)

    # ========================================================
    # FORCE GRAB
    # ========================================================

    def force_grab(
        self,
        hand: Hand,
        distance_m: float,
        object_mass: float
    ):

        """
        Pulling an object toward the Jedi.

        The closer the object gets, the stronger the pulse.
        """

        distance_factor = max(
            0.0,
            min(1.0, 1.0 - distance_m / 15.0)
        )

        mass_factor = min(
            1.0,
            object_mass / 100.0
        )

        amplitude = (
            0.25
            + distance_factor * 0.35
            + mass_factor * 0.25
        )

        frequency = (
            90
            + mass_factor * 110
        )

        self.pulse(
            hand,
            amplitude,
            55,
            frequency,
            "FORCE_GRAB"
        )

    # ========================================================
    # FORCE PULL
    # ========================================================

    def force_pull(
        self,
        hand: Hand,
        resistance: float,
        mass: float
    ):

        resistance = max(
            0.0,
            min(1.0, resistance)
        )

        mass_factor = min(
            1.0,
            mass / 100.0
        )

        amplitude = (
            0.25
            + resistance * 0.45
            + mass_factor * 0.2
        )

        frequency = (
            75
            + resistance * 180
        )

        self.pulse(
            hand,
            amplitude,
            70,
            frequency,
            "FORCE_PULL"
        )

    # ========================================================
    # FORCE PUSH
    # ========================================================

    def force_push(
        self,
        hand: Hand,
        object_mass: float,
        acceleration: float
    ):

        mass_factor = min(
            1.0,
            object_mass / 100.0
        )

        acceleration = max(
            0.0,
            min(1.0, acceleration)
        )

        amplitude = (
            0.35
            + acceleration * 0.45
            + mass_factor * 0.15
        )

        duration = (
            40
            + acceleration * 100
        )

        self.pulse(
            hand,
            amplitude,
            duration,
            120,
            "FORCE_PUSH"
        )

    # ========================================================
    # FORCE THROW
    # ========================================================

    def force_throw(
        self,
        hand: Hand,
        velocity: float
    ):

        velocity_factor = min(
            1.0,
            velocity / 30.0
        )

        self.pulse(
            hand,
            0.45 + velocity_factor * 0.5,
            90,
            180 + velocity_factor * 180,
            "FORCE_THROW"
        )

    # ========================================================
    # FORCE CRUSH
    # ========================================================

    def force_crush(
        self,
        hand: Hand,
        resistance: float
    ):

        resistance = max(
            0.0,
            min(1.0, resistance)
        )

        # Pulsing "strain" sensation.
        for i in range(3):

            amplitude = (
                0.35
                + resistance * 0.6
            )

            frequency = (
                60
                + i * 25
            )

            self.pulse(
                hand,
                amplitude,
                85,
                frequency,
                "FORCE_CRUSH"
            )

    # ========================================================
    # FORCE LIFT
    # ========================================================

    def force_lift(
        self,
        hand: Hand,
        mass: float,
        height: float
    ):

        mass_factor = min(
            1.0,
            mass / 150.0
        )

        height_factor = min(
            1.0,
            height / 10.0
        )

        amplitude = (
            0.25
            + mass_factor * 0.45
            + height_factor * 0.15
        )

        self.pulse(
            hand,
            amplitude,
            100,
            70,
            "FORCE_LIFT"
        )

    # ========================================================
    # FORCE HOLD
    # ========================================================

    def force_hold(
        self,
        hand: Hand,
        resistance: float
    ):

        resistance = max(
            0.0,
            min(1.0, resistance)
        )

        # Very subtle continuous-feeling pulse.
        amplitude = (
            0.08
            + resistance * 0.20
        )

        self.pulse(
            hand,
            amplitude,
            45,
            45 + resistance * 70,
            "FORCE_HOLD"
        )

    # ========================================================
    # FORCE RELEASE
    # ========================================================

    def force_release(self, hand: Hand):

        self.pulse(
            hand,
            0.30,
            45,
            180,
            "FORCE_RELEASE"
        )

    # ========================================================
    # LIGHTSABER IGNITION
    # ========================================================

    def saber_ignite(self, hand: Hand):

        # Rising vibration sequence.
        frequencies = [
            55,
            70,
            95,
            130,
            180
        ]

        for i, frequency in enumerate(frequencies):

            self.pulse(
                hand,
                0.15 + i * 0.12,
                45,
                frequency,
                "SABER_IGNITE"
            )

    # ========================================================
    # LIGHTSABER RETRACTION
    # ========================================================

    def saber_retract(self, hand: Hand):

        frequencies = [
            180,
            130,
            95,
            70,
            55
        ]

        for frequency in frequencies:

            self.pulse(
                hand,
                0.25,
                40,
                frequency,
                "SABER_RETRACT"
            )

    # ========================================================
    # LIGHTSABER SWING
    # ========================================================

    def saber_swing(
        self,
        hand: Hand,
        angular_velocity: float
    ):

        velocity_factor = min(
            1.0,
            angular_velocity / 12.0
        )

        amplitude = (
            0.05
            + velocity_factor * 0.22
        )

        frequency = (
            100
            + velocity_factor * 200
        )

        self.pulse(
            hand,
            amplitude,
            25,
            frequency,
            "SABER_SWING"
        )

    # ========================================================
    # LIGHTSABER HIT
    # ========================================================

    def saber_hit(
        self,
        hand: Hand,
        impact_velocity: float,
        target_mass: float
    ):

        velocity_factor = min(
            1.0,
            impact_velocity / 15.0
        )

        mass_factor = min(
            1.0,
            target_mass / 100.0
        )

        amplitude = (
            0.55
            + velocity_factor * 0.30
            + mass_factor * 0.15
        )

        frequency = (
            120
            + target_mass * 2
        )

        self.pulse(
            hand,
            amplitude,
            80,
            frequency,
            "SABER_HIT"
        )

    # ========================================================
    # LIGHTSABER BLOCK
    # ========================================================

    def saber_block(
        self,
        hand: Hand,
        incoming_energy: float
    ):

        energy = max(
            0.0,
            min(1.0, incoming_energy)
        )

        self.pulse(
            hand,
            0.45 + energy * 0.50,
            60,
            160 + energy * 250,
            "SABER_BLOCK"
        )

    # ========================================================
    # SABER CLASH
    # ========================================================

    def saber_clash(
        self,
        hand: Hand,
        force: float
    ):

        force = max(
            0.0,
            min(1.0, force)
        )

        # Main impact.
        self.pulse(
            hand,
            0.60 + force * 0.40,
            70,
            180 + force * 220,
            "SABER_CLASH"
        )

        # Secondary resonance.
        self.pulse(
            hand,
            0.30 + force * 0.30,
            110,
            70 + force * 90,
            "SABER_RESONANCE"
        )

    # ========================================================
    # TWO-HANDED FORCE
    # ========================================================

    def two_hand_force(
        self,
        event: ForceEvent,
        intensity: float
    ):

        intensity = max(
            0.0,
            min(1.0, intensity)
        )

        frequency = 60 + intensity * 180

        self.pulse(
            Hand.LEFT,
            0.20 + intensity * 0.65,
            70,
            frequency,
            event.value.upper()
        )

        self.pulse(
            Hand.RIGHT,
            0.20 + intensity * 0.65,
            70,
            frequency,
            event.value.upper()
        )


# ============================================================
# FORCE INPUT SIMULATOR
# ============================================================

class ForceController:

    """
    Simulates the player's Force gesture.

    In a real VR game, these values would come from:

        controller grip
        hand tracking
        trigger pressure
        wrist velocity
        arm movement
        gesture recognition
        eye/head direction
    """

    def __init__(
        self,
        haptics: JediForceHaptics
    ):

        self.haptics = haptics

    def simulate_force_pull(self):

        print("\n--- FORCE PULL ---")

        for resistance in [
            0.1,
            0.25,
            0.45,
            0.65,
            0.85
        ]:

            self.haptics.force_pull(
                Hand.RIGHT,
                resistance,
                25
            )

            time.sleep(0.08)

    def simulate_force_push(self):

        print("\n--- FORCE PUSH ---")

        for acceleration in [
            0.2,
            0.4,
            0.7,
            1.0
        ]:

            self.haptics.force_push(
                Hand.RIGHT,
                50,
                acceleration
            )

            time.sleep(0.08)

    def simulate_lightsaber(self):

        print("\n--- LIGHTSABER ---")

        self.haptics.saber_ignite(
            Hand.RIGHT
        )

        time.sleep(0.2)

        self.haptics.saber_swing(
            Hand.RIGHT,
            8
        )

        self.haptics.saber_hit(
            Hand.RIGHT,
            12,
            80
        )

        self.haptics.saber_clash(
            Hand.RIGHT,
            0.9
        )

        time.sleep(0.2)

        self.haptics.saber_retract(
            Hand.RIGHT
        )


# ============================================================
# FORCE TRAINING SCENARIO
# ============================================================

def training_demo():

    engine = JediForceHaptics()

    controller = ForceController(
        engine
    )

    print()
    print("====================================")
    print("       JEDI FORCE HAPTICS")
    print("====================================")

    controller.simulate_force_pull()

    controller.simulate_force_push()

    print("\n--- FORCE THROW ---")

    engine.force_throw(
        Hand.RIGHT,
        velocity=22
    )

    print("\n--- FORCE CRUSH ---")

    engine.force_crush(
        Hand.RIGHT,
        resistance=0.8
    )

    print("\n--- TWO-HANDED FORCE ---")

    engine.two_hand_force(
        ForceEvent.FORCE_LIFT,
        0.85
    )

    controller.simulate_lightsaber()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    training_demo()
    
