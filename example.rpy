label phone_test:

    call nvl_phone(active=True, clock="11:11", dr=lark)

    lp "This is a test message!"

    mcp "This is another test message!"

    menu(nvl=True):
        "Choice 1":
            mcp "Choice 1 selected"

        "Choice 2":
            mcp "Choice 2 selected"

    lp "Test message"

    call nvl_phone(False, clear_screen=False) #continue this conversation later

    adv_n "This is a line of adv text before we return to the phone."

    call nvl_phone(True, "11:12", lark, slide=5, clear_screen=False) # keep all previous msgs on screen + 1 new msg

    lp "All our previous messages should still be visible!"

    call nvl_phone(False) #hide the phone and clear all messages
