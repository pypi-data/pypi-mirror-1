import dm.application
import kforge.builder

class Application(dm.application.Application):
    "Provides single entry point for clients."

    builderClass = kforge.builder.ApplicationBuilder



