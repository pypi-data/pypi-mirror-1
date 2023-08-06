"""Next/Previous navigation through collection results"""

from collective.nextprev import topic

def initialize(context):
    topic.patch()
