import uuid


def createDefinition(contextManager):

    builder = contextManager.pomsetBuilder()
    executableObject = builder.createExecutableObject([], staticArgs=[])

    # autogenerate the name of the definition
    id = uuid.uuid4().hex
    name = '_'.join(['definition', id[:3]])

    definitionContext = builder.createNewAtomicPomset(
        name=name, executableObject=executableObject)
    definition = definitionContext.pomset()
    definition.id(id)

    contextManager.transientLibrary().addPomsetContext(definitionContext)

    return definitionContext

