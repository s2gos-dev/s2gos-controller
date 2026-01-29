#  Copyright (c) 2026 by the Eozilla team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

"""MTR Demo Processors - Self-contained generation and simulation workflows.

This module provides two processors for the MTR (Multi-Temporal Radiometric) demo:
1. mtr_demo.generation - Creates scene with seasonal variations
2. mtr_demo.simulation - Runs simulation with configurable observation types

The demo showcases:
- Seasonal variations (December=summer, June=winter in Patagonia)
- Multiple observation types (CHIME, MSI, HYPSTAR, RGB camera, satellite HDRF)
- Fixed demonstration dates (21st of month), flexible time
"""

import enum
from typing import Annotated

from pydantic import Field

from procodile import JobContext
from wraptile.services.local import LocalService


service = LocalService(
    title="S2GOS Test-Server",
    description="Local DTE-S2GOS process server for testing",
)

registry = service.process_registry

# ============================================================================
# Constants
# ============================================================================

PNP_LAT = -46.917
PNP_LON = -72.450
PNP_SIZE_KM = 10.0
TOWER_COORDS = (-220.0, 850.0)  # meters in scene coordinates

# ============================================================================
# Enums
# ============================================================================


class Month(enum.StrEnum):
    """Month selection for MTR demo (limited to solstice dates)."""

    DECEMBER = "december"  # Summer in Patagonia
    JUNE = "june"  # Winter in Patagonia


class ObservationType(enum.StrEnum):
    """Available observation types for MTR demo."""

    CHIME = "chime"
    MSI = "msi"
    SATELLITE_HDRF = "satellite_hdrf"
    HYPSTAR = "hypstar"
    RGB_CAMERA = "rgb_camera"


# ============================================================================
# Processor 1: Scene Generation
# ============================================================================


# noinspection PyUnusedLocal
@registry.process(id="mtr_demo_generation", title="Scene Generation Demo")
def mtr_demo_generation(
    month: Annotated[
        Month,
        Field(
            default=Month.DECEMBER,
            description="Month for simulation (December=summer, June=winter in Patagonia)",
            title="Month",
        ),
    ],
    random_seed: Annotated[
        int,
        Field(
            default=13,
            description="RNG seed for vegetation placement",
            title="Vegetation RNG seed",
        ),
    ],
    scene_name: Annotated[
        str,
        Field(
            ...,
            description="Name of scene",
            title="Scene name",
        ),
    ] = None,
) -> str | None:
    """Generate 3D scene for MTR demo with seasonal variations.

    This processor:
    1. Creates a scene generation configuration based on season/month
    2. Immediately runs the generation pipeline
    3. Returns path to the generated scene description YAML

    The scene includes:
    - PNP location with 10km target area
    - Seasonal vegetation (summer/winter variants)
    - Heterogeneous atmosphere with aerosol layer
    - Tower XML scene at fixed location
    - Optional snow cover (June only)

    Args:
        month: Month for simulation (controls seasonal variations)
        random_seed: Random seed for reproducible vegetation placement
        scene_name: Filename for scene description YAML

    Returns:
        Path to generated scene description YAML file, or None if validation fails
    """
    ctx = JobContext.get()

    print("\n")
    print("=" * 60)
    print("MTR DEMO - SCENE GENERATION")
    print("=" * 60)
    print(f"Season: {month.value}")
    print(f"Random seed: {random_seed}")
    print()

    # Run generation pipeline
    print("\n" + "=" * 60)
    print("Running scene generation pipeline...")
    print("=" * 60)
    ctx.report_progress(message="Running scene generation pipeline...")

    scene_path = generation_from_config()
    if scene_path:
        print("\n" + "=" * 60)
        print("SCENE GENERATION COMPLETE")
        print("=" * 60)
        print(f"Scene description: {scene_path}")
        print()
        ctx.report_progress(message=f"Scene description: {scene_path}")

    return scene_path


# ============================================================================
# Processor 2: Simulation
# ============================================================================


# noinspection PyUnusedLocal
@registry.process(id="mtr_demo_simulation", title="Simulation Demo")
def mtr_demo_simulation(
    scene_name: Annotated[
        str,
        Field(
            ...,
            description="Scene to sue for simulation",
            title="Scene name",
        ),
    ],
    month: Annotated[
        Month,
        Field(
            default=Month.DECEMBER,
            description="Month for simulation (December=summer, June=winter)",
            title="Month",
        ),
    ],
    hour_utc: Annotated[
        float,
        Field(
            ...,
            description="Hour of observation in UTC (0-23) of the 21st of the chosen month, affects sun position ",
            title="Hour (UTC)",
        ),
    ],
    observation: Annotated[
        ObservationType,
        Field(..., description="Observation type (enum value)", title="Observation"),
    ],
    spp: Annotated[
        int,
        Field(
            ...,
            description="Samples per pixel for Monte Carlo simulation",
            title="Samples per pixel",
        ),
    ] = 8,
    sim_name: Annotated[
        str,
        Field(
            ...,
            description="Simulation run name",
            title="Name of run",
        ),
    ] = None,
) -> str | None:
    """Run simulation for MTR demo with configurable observation types.

    This processor:
    1. Creates a simulation configuration based on observation type
    2. Immediately runs the simulation
    3. Returns path to the simulation output directory

    Supported observation types:
    - CHIME: Hyperspectral satellite sensor
    - MSI: Sentinel-2 multispectral sensor (configurable bands)
    - HYPSTAR: Ground-based hyperspectral sensor with HCRF processing
    - RGB_CAMERA: Perspective camera viewing tower from configurable position
    - SATELLITE_HDRF: [PLACEHOLDER - To be implemented]

    Args:
        scene_name: Filename of the scene YAML from generation step
        month: Month for simulation (determines observation date)
        hour_utc: Hour of observation in UTC
        observation: Observation type configuration
        spp: Samples per pixel for Monte Carlo simulation
        sim_name: Filename for the for simulation config JSON

    Returns:
        Path to simulation output directory, or None if observation type
        is not yet implemented or simulation fails
    """
    ctx = JobContext.get()

    print("\n")
    print("=" * 60)
    print("MTR DEMO - SIMULATION")
    print("=" * 60)

    print(f"Observation type: {observation}")
    print()

    # Check for placeholder observation type
    if observation == ObservationType.SATELLITE_HDRF:
        print("=" * 60)
        print("SATELLITE HDRF (3x3 pixels around tower)")
        print("Status: TO BE IMPLEMENTED")
        print()
        print("This observation type requires implementation of:")
        print("  - Pixel coordinate calculation for tower location")
        print("  - 3x3 grid generation around tower pixel")
        print("  - Multiple HDRF measurements creation")
        print("=" * 60)
        return None

    # Run simulation
    print("\n" + "=" * 60)
    print("Running simulation...")
    print("=" * 60)

    ctx.report_progress(message="Running simulation...")

    # TODO
    output_path = simulation_from_config(scene_name)

    if output_path:
        print("\n" + "=" * 60)
        print("SIMULATION COMPLETE")
        print("=" * 60)
        print(f"Output directory: {output_path}")
        print()

    ctx.report_progress(message=f"Output directory: {output_path}")

    return output_path


def generation_from_config(scene_name: str) -> str:
    return f"/outputs/scenes/{scene_name}"


def simulation_from_config(sim_name: str):
    return f"/outputs/simulations/{sim_name}"
