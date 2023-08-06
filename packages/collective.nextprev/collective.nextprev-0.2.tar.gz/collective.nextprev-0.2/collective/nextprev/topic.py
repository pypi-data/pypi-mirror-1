from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import topic

orig_schema = topic.ATTopic.schema

def patch():
    topic.ATTopic.schema = (
        topic.ATTopic.schema + schemata.NextPreviousAwareSchema)
    topic.ATTopic.getNextPreviousParentValue = (
        folder.ATFolder.getNextPreviousParentValue.im_func)
    topic.ATTopic.getNextPreviousEnabled = (
        folder.ATFolder.getNextPreviousEnabled.im_func)
    topic.ATTopic.getRawNextPreviousEnabled = (
        folder.ATFolder.getRawNextPreviousEnabled.im_func)
    topic.ATTopic.setNextPreviousEnabled = (
        folder.ATFolder.setNextPreviousEnabled.im_func)
    
def unpatch():
    topic.ATTopic.schema = orig_schema
    del topic.ATTopic.getNextPreviousParentValue
