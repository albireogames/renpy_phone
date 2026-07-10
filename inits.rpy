init -20 python:
    phone_display_header = {
        "phone": False,    # True if the phone is currently replacing the nvl screen, False if not
        "clock": "",       # the time displayed onscreen
        "icon" : "",       # image displayed next to the character's name
        "name" : "",       # name of the character you're texting
        "slide": 1         # set this to an int >1 to allow that number of msgs to persist between phone sections
    }


init -2 python:

    def phone_continue(event, interact, **kwargs):
        if event == "begin" and not config.skipping: #using "begin" prevents it from playing on the textbox after the phone goes away
            renpy.play(audio.phone_cont, channel="sound") 

    # a data class that includes character name and icon
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

# transition may not work properly without an adv line between each scene change and phone text
label nvl_phone(active, clock=None, dr=None, slide=1, clear_screen=True):
    if active: # turn on phone mode
        if clear_screen:
            nvl clear
        python:
            phone_display_header["phone"] = True
            phone_display_header["clock"] = clock
            phone_display_header["icon"]  = dr.icon
            phone_display_header["name"]  = dr.name
            phone_display_header["slide"] = slide

        window auto show # (this is REQUIRED to keep the window from trying to hide itself when showing the dialogue menu, etc)
        nvl show

    else: # turn off phone mode
        $ nvl_hide(Pause(0))    # for some reason nvl hide doesn't work but the python nvl_hide() does
        $ phone_display_header["phone"] = False
        if clear_screen:
            nvl clear

    return
        
