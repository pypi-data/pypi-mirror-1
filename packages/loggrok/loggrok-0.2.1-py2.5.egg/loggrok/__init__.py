def getLoggrok():
    import log
    import actions
    import parse
    class ModuleSpace:
        log = log
        actions = actions
        parse = parse
    return ModuleSpace()

