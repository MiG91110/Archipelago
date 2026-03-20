from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items

if TYPE_CHECKING:
    from .world import rocketleagueWorld

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.
LOCATION_NAME_TO_ID = {
    "Score a goal free play": 1,
    "Win a match against bots in exhibition": 2,
    "Clear Level 1 of Dribble Overhaul 2": 3,
}

# Each Location instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Location class and override the "game" field.
class rocketleagueLocation(Location):
    game = "rocketleague"

# Let's make one more helper method before we begin actually creating locations.
# Later on in the code, we'll want specific subsections of LOCATION_NAME_TO_ID.
# To reduce the chance of copy-paste errors writing something like {"Chest": LOCATION_NAME_TO_ID["Chest"]},
# let's make a helper method that takes a list of location names and returns them as a dict with their IDs.
# Note: There is a minor typing quirk here. Some functions want location addresses to be an "int | None",
# so while our function here only ever returns dict[str, int], we annotate it as dict[str, int | None].
def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}

def create_all_locations(world: rocketleagueWorld) -> None:
    create_regular_locations(world)
    #create_events(world)

def create_regular_locations(world: rocketleagueWorld) -> None:
    # Finally, we need to put the Locations ("checks") into their regions.
    # Once again, before we do anything, we can grab our regions we created by using world.get_region()
    freeplay = world.get_region("Freeplay")
    matchagainstbots = world.get_region("Match against bots")

    # A simpler way to do this is by using the region.add_locations helper.
    # For this, you need to have a dict of location names to their IDs (i.e. a subset of location_name_to_id)
    # Aha! So that's why we made that "get_location_names_with_ids" helper method earlier.
    # You also need to pass your overridden Location class.
    freeplay_locations = get_location_names_with_ids(
        ["Score a goal free play"]
    )
    freeplay.add_locations(freeplay_locations, rocketleagueLocation)

    matchagainstbots_locations = get_location_names_with_ids(
        ["Win a match against bots in exhibition"]
    )
    matchagainstbots.add_locations(matchagainstbots_locations, rocketleagueLocation)

    # Locations may exist only if the player enables certain options.
    # In our case, the extra_starting_chest option adds the Bottom Left Extra Chest location.
    if world.options.workshop:
        # Once again, it is important to stress that even though the Bottom Left Extra Chest location doesn't always
        # exist, it must still always be present in the world's location_name_to_id.
        # Whether the location actually exists in the seed is purely determined by whether we create and add it here.
        workshopmap1 = world.get_region("workshopmap1")
        workshopmap1_locations = get_location_names_with_ids(["Clear Level 1 of Dribble Overhaul 2"])
        workshopmap1.add_locations(workshopmap1_locations, rocketleagueLocation)

def create_events(world: rocketleagueWorld) -> None:
    # Sometimes, the player may perform in-game actions that allow them to progress which are not related to Items.
    # In our case, the player must press a button in the top left room to open the final boss door.
    # AP has something for this purpose: "Event locations" and "Event items".
    # An event location is no different than a regular location, except it has the address "None".
    # It is treated during generation like any other location, but then it is discarded.
    # This location cannot be "sent" and its item cannot be "received", but the item can be used in logic rules.
    # Since we are creating more locations and adding them to regions, we need to grab those regions again first.
    final_boss_room = world.get_region("Match against bots")

    # A way simpler way to do create an event location/item pair is by using the region.create_event helper.
    # Luckily, we have another event we want to create: The Victory event.
    # We will use this event to track whether the player can win the game.
    # The Victory event is a completely optional abstraction - This will be discussed more in set_rules().
    final_boss_room.add_event(
        "Final Boss Defeated", "Victory", location_type=rocketleagueLocation, item_type=items.rocketleagueItem
    )

    # If you create all your regions and locations line-by-line like this,
    # the length of your create_regions might get out of hand.
    # Many worlds use more data-driven approaches using dataclasses or NamedTuples.
    # However, it is worth understanding how the actual creation of regions and locations works,
    # That way, we're not just mindlessly copy-pasting! :)