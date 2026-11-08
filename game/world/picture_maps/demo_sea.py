"""The placeholder map of the map demo (see `world/map_demo/`)."""

from world.maps import PictureMap

DEMO_SEA: PictureMap = PictureMap(
    key="demo_sea",
    title="Demo sea (placeholder map)",
    image_url="/static/terrific_travel/map_demo/demo_sea.svg",
    width=1000,
    height=600,
)

PICTURE_MAPS: list[PictureMap] = [DEMO_SEA]
