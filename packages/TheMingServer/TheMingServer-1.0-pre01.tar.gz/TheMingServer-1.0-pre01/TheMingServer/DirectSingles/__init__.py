# __init__ for TheMingServer.direct_singles package

from PurchaseButton import PurchaseButton
from DirectSinglesMaker import DirectSinglesMaker

MAKERS = {"html": DirectSinglesMaker,
		  "pre": DirectSinglesMaker}
