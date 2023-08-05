import os
from Component import CPage
from ZPTKit import ZPTComponent

class ZPTExample(CPage):

    components = [ZPTComponent(os.path.join(os.path.dirname(__file__),
                                            'templates'))]
    

    def writeHTML(self):
        self.writeTemplate()
