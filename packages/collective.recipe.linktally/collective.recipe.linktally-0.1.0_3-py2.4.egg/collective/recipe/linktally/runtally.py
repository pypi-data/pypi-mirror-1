from linktally import runLinkTally
from linktally.config import LinkTallyConfig

def run(configfile):
    runLinkTally(LinkTallyConfig(configfile))
