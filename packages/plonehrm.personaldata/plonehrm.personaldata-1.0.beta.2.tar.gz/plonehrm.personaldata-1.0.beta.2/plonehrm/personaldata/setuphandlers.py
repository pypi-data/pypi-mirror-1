def register_personaldata(context):
    # Only run step if a flag file is present.
    if context.readDataFile('personaldata.txt') is None:
        return
    pass # unneeded
