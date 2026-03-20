from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Region

if TYPE_CHECKING:
    from .world import rocketleagueWorld

def create_and_connect_regions(world: rocketleagueWorld) -> None:
    create_all_regions(world)
    connect_regions(world)

def create_all_regions(world: rocketleagueWorld) -> None:
    # Creating a region is as simple as calling the constructor of the Region class.
    freeplay = Region("Freeplay", world.player, world.multiworld)
    matchagainstbots = Region("Match against bots", world.player, world.multiworld)

    # Let's put all these regions in a list.
    regions = [freeplay, matchagainstbots]

    # Some regions may only exist if the player enables certain options.
    # In our case, the Hammer locks the top middle chest in its own room if the hammer option is enabled.
    if world.options.workshop:
        workshopmap1 = Region("workshopmap1", world.player, world.multiworld)
        regions.append(workshopmap1)

    # We now need to add these regions to multiworld.regions so that AP knows about their existence.
    world.multiworld.regions += regions

def connect_regions(world: rocketleagueWorld) -> None:
    # We have regions now, but still need to connect them to each other.
    # But wait, we no longer have access to the region variables we created in create_all_regions()!
    # Luckily, once you've submitted your regions to multiworld.regions,
    # you can get them at any time using world.get_region(...).
    freeplay = world.get_region("Freeplay")
    matchagainstbots = world.get_region("Match against bots")

    # An even easier way is to use the region.connect helper.
    freeplay.connect(matchagainstbots, "Freeplay to bot match")

    # Some Entrances may only exist if the player enables certain options.
    # In our case, the Hammer locks the top middle chest in its own room if the hammer option is enabled.
    # In this case, we previously created an extra "Top Middle Room" region that we now need to connect to Overworld.
    if world.options.workshop:
        workshopmap1 = world.get_region("workshopmap1")
        workshopmap1.connect(freeplay, "Freeplay to workshopmap1")