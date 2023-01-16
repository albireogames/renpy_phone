init -20 python:
    phone_display_header = {
        "phone": False,
        "clock": "",
        "icon" : "",
        "name" : ""
    }


init -2 python:

    def phone_continue(event, interact, **kwargs):
        if event == "begin" and not config.skipping and not mute_textbox_click: #using "begin" prevents it from playing on the textbox after the phone goes away
            renpy.play(audio.phone_cont, channel="sound") 


    class Dragon(object):
        def __init__(self, flags, name, icon):
            self._flags = flags     # dict of flag names to t/f value
            self._name = name
            self._icon = icon       # image name

        @property
        def flags(self):
            return self._flags

        @property
        def name(self):
            return self._name

        @property
        def icon(self):
            return self._icon

        def clear_flags(self):
            for f, val in self._flags.items():
                val = False

        def toggle_flag(self, f):
            try:
                self._flags[f] = not self._flags[f]
            except IndexError as err:
                e("Dragon: toggle_flag: [err]")

        def set_flag(self, f):
            try:
                self._flags[f] = True
            except IndexError as err:
                e("Dragon: set_flag: [err]")



default lark = Dragon(
    flags = {
        "f_library"  : False,
        "f_melonpan" : False,
        "f_baking"   : False
    },
    name = "Lark",
    icon = "gui/fte/lark_icon.png"
)


default lp = Character("lark", kind=nvl,
    what_style="dr_message_body",
    callback=phone_continue
)
default mcp = Character("mc", kind=nvl,
    what_style="mc_message_body",
    callback=phone_continue
)


label nvl_phone(active, clock=None, dr=None):
    if active: # turn on phone mode
        nvl clear

        python:
            phone_display_header["phone"] = True
            phone_display_header["clock"] = clock
            phone_display_header["icon"]  = dr.icon
            phone_display_header["name"]  = dr.name

            if not debug:
                config.rollback_enabled = False

        window show 
        nvl show

    else: # turn off phone mode
        $ nvl_hide(Pause(0))
        
        if rollback_on: 
            python:
                if not debug:
                    renpy.block_rollback()
                config.rollback_enabled = True

        $ phone_display_header["phone"] = False

        nvl clear

        