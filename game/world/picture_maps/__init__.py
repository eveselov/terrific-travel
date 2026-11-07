"""
Picture map definitions, one module per map (or group of maps).

Every module in this package that has a `PICTURE_MAPS: list[PictureMap]` is picked up by
`world.maps` automatically. For example, `world/picture_maps/my_sea.py`:

    from world.maps import PictureMap

    PICTURE_MAPS: list[PictureMap] = [
        PictureMap(
            key="my_sea",
            title="My sea",
            image_url="/static/terrific_travel/maps/my_sea.png",
            width=1200,  # the picture's size in pixels
            height=800,
        ),
    ]

Then put rooms on it in the game: `tag here = my_sea:map` and `set here/map_pos = (x, y)`.
"""
