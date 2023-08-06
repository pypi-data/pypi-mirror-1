import bottle
import cuttlefish

cuttlefish.Config.loadFromVicinity(__file__)
application = bottle.default_app()
