from dataclasses import replace

from app.simulation.actions import execute_program
from app.simulation.constants import WELL_FED_ENERGY
from app.simulation.environment import Apple, Tree
from app.simulation.genome import Genome, Morphology, Traits
from app.simulation.learning import apply_learning, needs_food, start_think, think_step
from app.simulation.organism import Organism
from app.simulation.world import World


def _traits(**overrides: float) -> Traits:
    data = {
        "bravery": 1.0,
        "stress": 0.0,
        "stupidity": 0.0,
        "hunger_threshold": 0.4,
        "reproduction_threshold": 0.9,
    }
    data.update(overrides)
    return Traits(**data)


def _organism() -> Organism:
    return Organism(
        id="org_test",
        x=50.0,
        y=50.0,
        direction=0.0,
        energy=500.0,
        age=0,
        generation=1,
        genome=Genome(
            traits=_traits(),
            morphology=Morphology(size_base=8),
        ),
    )


def test_needs_food_when_energy_starts_falling() -> None:
    organism = _organism()
    organism.energy = 800.0
    organism.energy_peak = 800.0
    assert needs_food(organism) is False
    organism.energy = 620.0
    assert needs_food(organism) is True
    organism.energy = 300.0
    organism.energy_peak = 300.0
    assert needs_food(organism) is True


def test_positive_energy_delta_raises_move_score() -> None:
    organism = _organism()
    organism.last_action = "MOVE"
    apply_learning(organism, 20)
    apply_learning(organism, 20)
    assert organism.prediction_score["MOVE"] >= 0.2


def test_large_negative_delta_lowers_move_score() -> None:
    organism = _organism()
    organism.last_action = "MOVE"
    apply_learning(organism, -15)
    apply_learning(organism, -15)
    assert organism.prediction_score["MOVE"] <= -0.2


def test_learning_is_not_inherited() -> None:
    world = World(seed=1, mutation_rate=0.0)
    parent = world.organisms[0]
    mate = world.organisms[1]
    parent.x, parent.y = 80.0, 80.0
    mate.x, mate.y = 90.0, 80.0
    parent.energy = mate.energy = WELL_FED_ENERGY + 100
    parent.energy_peak = mate.energy_peak = WELL_FED_ENERGY + 100
    parent.prediction_score["MOVE"] = 0.8
    parent.genome = Genome(
        traits=replace(parent.genome.traits, reproduction_threshold=0.5),
        program=parent.genome.program,
        morphology=parent.genome.morphology,
    )
    mate.genome = parent.genome
    from app.simulation.actions import reproduce

    child = reproduce(parent, world)
    assert child is not None
    assert child.prediction_score == {}
    assert parent.prediction_score["MOVE"] == 0.8


def test_eat_rewards_hunting_actions() -> None:
    organism = _organism()
    organism.last_action = "EAT"
    apply_learning(organism, 40)
    assert organism.prediction_score["EAT"] >= 0.1
    assert organism.prediction_score["MOVE"] >= 0.1
    assert organism.prediction_score["ACCEL"] >= 0.1
    assert organism.hunt_streak == 0


def test_reproduce_is_not_punished_for_birth_cost() -> None:
    organism = _organism()
    organism.last_action = "REPRODUCE"
    apply_learning(organism, -200)
    assert organism.prediction_score["REPRODUCE"] >= 0.1


def test_think_sets_flag_and_quality() -> None:
    organism = _organism()
    start_think(organism)
    assert organism.is_thinking is True
    think_step(organism)
    assert organism.last_action == "THINK"
    assert organism.thinking_quality > 0
    think_step(organism)
    assert organism.is_thinking is False


def test_comfortable_energy_does_not_chase_food() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.x = 50.0
    organism.y = 50.0
    organism.direction = 0.0
    organism.energy = 800.0
    organism.energy_peak = 800.0
    organism.prediction_score["MOVE"] = -1.0
    organism.genome = Genome(
        traits=_traits(bravery=1.0, stupidity=0.0),
        program=organism.genome.program,
        morphology=organism.genome.morphology,
    )
    world.trees = [
        Tree(
            id="tree_1",
            x=50.0,
            y=50.0,
            apples=[Apple(id="apple_1_1", tree_id="tree_1", x=80.0, y=50.0)],
        )
    ]
    world.bushes = []
    execute_program(organism, world)
    assert organism.last_action != "EAT"
    assert len(world.trees[0].apples) == 1


def test_falling_energy_chases_food_despite_bad_move_memory() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.x = 50.0
    organism.y = 50.0
    organism.direction = 0.0
    organism.energy = 500.0
    organism.energy_peak = 900.0
    organism.prediction_score["MOVE"] = -1.0
    organism.genome = Genome(
        traits=_traits(bravery=1.0, stupidity=0.0),
        program=organism.genome.program,
        morphology=organism.genome.morphology,
    )
    world.trees = [
        Tree(
            id="tree_1",
            x=50.0,
            y=50.0,
            apples=[Apple(id="apple_1_1", tree_id="tree_1", x=80.0, y=50.0)],
        )
    ]
    world.bushes = []
    start = (organism.x, organism.y)
    execute_program(organism, world)
    assert organism.last_action in {"MOVE", "ACCEL"}
    assert (organism.x, organism.y) != start
    assert organism.x > start[0]
