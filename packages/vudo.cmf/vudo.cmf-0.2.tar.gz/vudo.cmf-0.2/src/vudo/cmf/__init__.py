from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory("vudo.cmf")

def provide_skin():
    from vudo.skinsetup import provide_skin
    return provide_skin(
            package="vudo.cmf",
            name="cmf",
            skin_path="skin")
