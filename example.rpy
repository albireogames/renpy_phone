label phone_test:

    call nvl_phone(True, "11:11", lark)

    lp "This is a test message!"

    mcp "This is another test message!"

    menu(nvl=True):
        "Choice 1":
            mcp "Choice 1 selected"

        "Choice 2":
            mcp "Choice 2 selected"

    lp "Test message"

    call nvl_phone(False)

    