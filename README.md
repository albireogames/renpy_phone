# Phone interface for Ren'Py

An implementation of a text messaging interface for our visual novel, DRACONID. You're free to use any code in this repo without permission. Credit is appreciated but not necessary.

Check out the game: https://demyurge.itch.io/dragongame

<img src="https://i.gyazo.com/ebaa8e7ce4bda96e140bd0346fb0fd12.gif" width="666" height="372" />

## Basic structure

The easiest way to do this is to hijack the NVL dialogue screen and make a phone-shaped variation of it. We can reuse NVL’s built-in features (such as continuing to show past dialogue to the player) to make a messaging screen that’s easy and intuitive to use.

As of version 8.0.3, the default NVL code that comes in screens.rpy has two components: nvl and nvl_dialogue. The nvl screen takes in a list of dialogue and a list of menu items (if given), and uses nvl_dialogue to display the dialogue text itself. We’ll be using the same structure for the phone screen, with an encapsulating screen that takes in the same parameters and uses a second screen to display the dialogue. (The exact format of the default NVL screen code may change with new versions of Renpy, but the basic idea is still the same.)

To start, the inside screen is made by copying the nvl_dialogue screen and trimming it down to only include the dialogue text:

```
screen phone_messages(dialogue):
  for d in dialogue:
    window:
      text d.what:
        id d.what_id
```

(“id d.what_id” on line 58 is the only required id property—[the game will actually crash without it](https://www.renpy.org/doc/html/screen_special.html#nvl). This presents an interesting problem with styling that will be covered in a later section.)

Likewise, the containing screen is based on the nvl screen:

```
screen phone_display(dialogue, items=None):
  window:
    viewport:
      area (22, 145, 430, 500)
      mousewheel True
      scrollbars "vertical"
      yinitial 1.0

      vbox:
        use phone_messages(dialogue, items)

        for i in items:
          button:
            action i.action
            text i.caption
```

Instead of just using a regular vbox (or vpgrid), we add a viewport to allow the player to scroll up to view previous texts. Set the “mousewheel” property to True and scrollbars to “vertical” to allow scrolling (unfortunately, you can’t set “draggable” or “arrowkeys” to True without preventing the player from being able to click inside the viewport itself to advance the text). Finally, set yinitial to 1.0 (not 1, because that indicates a 1 pixel offset instead of 100%) to keep the viewport at the bottom where the most recent messages will appear. 

If you aren’t planning to use regular NVL anywhere else in your game, you can probably just replace the contents of the nvl and nvl_dialogue definitions entirely instead of making new ones (I won’t cover this option in depth in this post). Otherwise, you’ll need to add a few lines to the top of your nvl screen that tells it whether to use your new phone_display screen:

```
screen nvl(dialogue, items=None):
  if phone_display_header["phone"]:
    use phone_display(dialogue, items)
  else:
    window:
      ...
```

Because this depends on reading the state of a variable, a dict is (probably) the easiest way to do this since it’s automatically a global variable when declared in Renpy. For convenience, I put it in a dict named phone_display_header that also keeps track of other display elements I’ll add later:

```
init -20 python:
  phone_display_header = {
    "phone": False,
    "clock": "",
    "icon" : "",
    "name" : "",
    "slide": 1
  }
```

(Using a simple “default phone_mode = False” and then toggling with “$ phone_mode = True” in your game script will only change the value of the variable in the local scope of your label, so the nvl screen will never read your variable as True. You could probably get around this with environment variables or something instead, but that’s a pain.)

Just set the dict value to True (and set the value for the visual elements you want) before a line of NVL dialogue, and it should use the phone_display screen instead. I put it all in a function for ease of use:

```
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
```

In short, to enable the phone mode, this function clears the NVL dialogue screen, sets the global phone toggle, disables rollback, and then shows the NVL window to bring up the phone. To disable it, it does the opposite in reverse.

This is also where I set the values for displayables that can change depending on the story scenario, like the phone clock, a user icon, and the name that displays at the top of the message screen by taking them as parameters and updating the global dict. The phone_display screen will be able to read this dict and place these elements accordingly. You can add, change, or remove these as you need, since they’re just for visual customization and making the phone look more phone-y and have no impact on the functionality. (The dr parameter is a “dragon” object that keeps track of each character’s icon, name, story flags, etc.) 

The slide paramater allows you to keep messages from a previous text conversation on the screen if you also set clear_screen to false - you can see an example [here](https://github.com/albireogames/renpy_phone/blob/e18b1b4b22bf008e8eda6d187a6491c8fec02342/example.rpy#L22). slide should be set to the number of previous messages you wish to keep plus 1 for the new message (you can see in nvl_phone above that slide defaults to 1 because even on a clean slate it will need to display at least one message).

If your game contains rollback, you might want to disable it while the phone interface is active, since it a) doesn’t make sense for texts to unsend themselves and b) the player can see all previous texts anyway so there’s not really a point. Blocking rollback after the phone screen is hidden is also optional. I’d recommend having a debug toggle that allows it to stay enabled though.

Lastly, you DO need “window show” specifically. “window show” not only shows the nvl window but keeps it from being hidden during certain transitions such as when the game brings up dialogue menus. “nvl show” is technically redundant and not necessary but I’m keeping it in just in case. “$ nvl_hide(Pause(0))” is kind of weird and will be explained later.

At this point your phone display should theoretically run without crashing, although it probably looks nothing like a phone yet…

## Styling

I won’t go over all of the styles in detail, since most of it is pretty mundane and just setting stuff like xpos/ypos and background images, but there are definitely some weirdly difficult parts. 

After adding style properties, the new phone_messages screen looks like this:

```
screen phone_messages(dialogue):
  $ prev_who = ""
  for d in dialogue:
    if prev_who == d.who:
      null height 5
    else:
      null height 14
    $ prev_who - d.who

    window:
      if d.who is not None:
        style d.who+"_message_window"
      else: #prevents it from crashing on reload when d.who is None
        $ phone_display_header["phone"] = False

      text d.what:
        id d.what_id
```

The first if/else branch changes the spacing between messages depending on whether it is attributed to the same sender as the previous message—for instance, two consecutive messages sent by the player character will only have a 5px separation while a message from the player character followed by a message from Lark will have a 14px separation between them.

For the text message window style, if you want the message bubbles to look different depending on who is sending the message (you probably do), you can use the “who” attribute of the current dialogue object as a prefix to determine which style to apply to the window. The d.who is the string you passed as the “name” arg for the Character objects we defined above, so make sure it’ll match the name of your style. (It took me forever to realize that the name of a style to apply doesn’t have to just be a string literal, it can be an expression as long as it evaluates to a string lol…) As a side note, I like to add a check for the value of d.who for convenience during development—if you reload/autoreload while on the phone screen, d.who will initialize to None which can’t be concatenated with a string, so the game crashes. To handle this I just set the global phone toggle to False so that it loads in the dialogue on the regular NVL screen instead of crashing, and then I rollback to when the toggle gets set to True again to bring the phone back up. If you’ve replaced the NVL screen with your phone code, uhhhhhhhh I guess you could set the style to a default value or something.  

You may have noticed the text itself (on the second to last line) doesn’t have any style properties applied to it. This is because the required id property overrides any style properties you put on the displayable, so…

```
default lp = Character("lark", kind=nvl,
    what_style="dr_message_body",
    callback=phone_continue
)
default mcp = Character("mc", kind=nvl,
    what_style="mc_message_body",
    callback=phone_continue
)

########

style phone_message_body:
    font "fonts/Cabin-Regular.ttf"
    line_spacing -4
    size 22
    slow_cps 0

style mc_message_body is phone_message_body:
    color "#000000"
    
style dr_message_body is phone_message_body:
    color "#ffffff"
```

We have to define Character objects to specify which style we want through the what_style argument [(more info here)](https://www.renpy.org/doc/html/dialogue.html#Character). Because of the id property on the dialogue text, the phone_messages screen will (more or less) look at the “speaking” character associated with the current dialogue object and apply that character’s what_style to the text. As always, when you modify an object while your game is running, remember to close your game completely and relaunch it, as the changes won’t be detected by autoreload.

The callback is optional—it’s just a function to play a sound every time a message is “sent” or “received” (when the player clicks to advance).

```
init -2 python:
    def phone_continue(event, interact, **kwargs):
        if event == "begin" and not config.skipping: #using "begin" prevents it from playing on the textbox after the phone goes away
            renpy.play(audio.phone_cont, channel="sound")
```

The phone_display screen is relatively simple—here’s where I added the clock, icon, and name displayables, and added a frame around the menu choices (if they exist). 

```
screen phone_display(dialogue, items=None):
    window:
        style "phone_display_window"
        text phone_display_header["clock"] style "phone_display_clock"
        add phone_display_header["icon"] zoom 0.47 xpos 70 ypos 85 #this has to be inline bc of zoom
        text phone_display_header["name"] style "phone_display_name"
        add "gui/phone_display/phone2.png" xpos 40 ypos 660

        viewport:
            area (22, 145, 430, 500)
            mousewheel True
            scrollbars "vertical" #"both"
            yinitial 1.0

            vbox:
                style "phone_display_vbox"
                use phone_messages(dialogue, items)

                if items:
                    null height 7
                    frame:
                        style phone_display_header["name"].lower()+"_phone_display_choice"

                        vbox:
                            for i in items:
                                null height 5
                                button:
                                    action i.action
                                    style "phone_display_choice_button"
                                    text i.caption style "phone_display_choice_text"

style phone_display_choice:
    xsize 350
    # ysize 119
    yminimum 119
    xanchor 1.0
    xpos 415
    top_padding 10
    bottom_padding 15

style lark_phone_display_choice is phone_display_choice:
    background Frame("gui/phone_display/lark_choice_bg.png", Borders(20, 20, 20, 20))

style phone_display_choice_button:
    background Frame("gui/phone_display/button.png")
    hover_background Frame("gui/phone_display/button_hover.png")
    xanchor 1.0
    xpos 335
    xsize 324
    ysize 44
    xpadding 15
    ypadding 5
    hover_sound audio.phone_mh
    activate_sound audio.phone_cont
```

For the frame, we decided we wanted the background color to match the character’s text bubbles for some visual cohesion, so I used the same method as the text message window styles to determine which style to apply.

For the menu buttons, I like to add a hover background image and maybe hover and activate sounds to make it feel responsive (line 176). As always, putting your background images into [Frames](https://www.renpy.org/doc/html/displayables.html#Frame) will save you some grief.

At this point, you can run the screen code by calling the nvl_phone function to enable the phone mode and then using the newly defined NVL characters as you would for normal NVL dialogue:

```
call nvl_phone(active=True, clock="11:11", dr=lark)

    lp "This is a test message!"

    mcp "This is another test message!"

    menu(nvl=True):
        "Choice 1":
            mcp "Choice 1 selected"

        "Choice 2":
            mcp "Choice 2 selected"

    lp "Test message"

    call nvl_phone(False)
```

<img src="https://64.media.tumblr.com/a8bf27d4ad368b75ee4b45f54f53574b/7bb6d116491dd696-d7/s500x750/e5b3f430b466e78fa439fb35822de1360e8ccf04.pnj" width="428" height="589" />

Your phone should now look like a phone! However, there’s still more we can add.

## Animations

We can use some simple ATL to add small animations and make the interface really pop. I have two transforms to show and hide the phone screen, and two to show and… continue to show the message bubbles.

```
transform phone_slide:
    on show:
        xanchor 0 yanchor 0 xpos 396 ypos 2000
        easein 0.5 xpos 396 ypos 0

transform phone_stay:
    xanchor 0 yanchor 0 xpos 396 ypos 0 
    
    on hide:
        easeout 0.5 xpos 396 ypos 2000


transform message_appear(who):
    alpha 0.0
    
    choice who == "mc": #select placement
        xanchor 1.0 xpos 415
    choice who != "mc":
        xanchor 0.0 xpos 10 

    linear 0.2 alpha 1.0


transform message_stay(who):
    choice who == "mc":
        xanchor 1.0 xpos 415
    choice who != "mc": 
        xanchor 0.0 xpos 10
```

The animations themselves are very simple—the first two transforms slide the phone on and off the screen for a clean, diegetic-ish transition to and from the usual ADV mode. The third one places the message on the left or right side of the phone screen depending on who sent it and does a quick fade-in for it to appear smoothly, while the fourth keeps the message at the appropriate location on the screen without doing a fade-in.

With the transforms applied to the window displayable, the phone_messages screen looks like this:

```
screen phone_messages(dialogue, items=None):
    $ prev_who = ""
    for d in dialogue:
        if prev_who == d.who:
            null height 5
        else:
            null height 14
        $ prev_who = d.who

        window:
            if d.current and not items: #only play animation if there's no menu coming up. prevents a blip when it re-displays the preceding txt
                at message_appear(d.who)
            else:
                at message_stay(d.who)

            if d.who is not None:
                style d.who.lower()+"_message_window"
            else: #prevents it from crashing on reload when d.who is None
                $ phone_display_header["phone"] = False
            text d.what:
                id d.what_id
```

The “at” property can be put inside an if/else block (right at the start of the window block) to determine which transform to use. If the message is the most recent one in the list of NVL dialogue objects, as indicated by d.current, the message_appear transform that does the fade-in is applied. If not, the message is shown using the message_stay transform without a fade-in, otherwise the animation would replay on every message with each new line of dialogue that appears. 

(It might be possible to move the check into a choice block within the transform and pass d.current as an arg, but I had trouble getting the choice blocks to function the way I wanted when combined with the choice blocks that determine whether to place the message on the left or right, so it’s easier to have it in two separately defined transforms.)

Additionally, the function signature has been changed to include “items”, the list of menu choices if provided to the NVL screen, and added to the check for the transform. This is because (when you don’t put a menu caption, at least) the line of dialogue before the menu will have its fade-in animation replay because its d.current is still True, so we have to check if a menu is being displayed when determining which transform to apply.

Adding the transforms to the phone_display screen is pretty similar:

```
screen phone_display(dialogue, items=None):
    window at phone_stay:
        if len(dialogue) == phone_display_header["slide"] and not items: #first msg can't be a menu
            at phone_slide

        style "phone_display_window"
        text phone_display_header["clock"] style "phone_display_clock"
        add phone_display_header["icon"] zoom 0.47 xpos 70 ypos 85 #this has to be inline bc of zoom
        text phone_display_header["name"] style "phone_display_name"
        add "gui/phone_display/phone2.png" xpos 40 ypos 660

        viewport:
            area (22, 145, 430, 500)
            mousewheel True
            scrollbars "vertical" 
            yinitial 1.0

            vbox:
                style "phone_display_vbox"
                use phone_messages(dialogue, items)

                if items:
                    null height 7
                    frame at message_appear("mc"):
                        style phone_display_header["name"].lower()+"_phone_display_choice"

                        vbox:
                            for i in items:
                                null height 5
                                button:
                                    action i.action
                                    style "phone_display_choice_button"
                                    text i.caption style "phone_display_choice_text"
```

The check this time is for the length of the list of dialogue objects (third line from the top). If the length is 1, that means that the current message is the first one and will bring up the phone screen, so it should apply the phone_slide transform that gives it the slide-in animation. Otherwise, it’ll use the phone_stay transform that just keeps it on the screen without any animations, and slides it off the screen when returning to ADV mode. (Combining the two transforms into one won’t work—it’ll run the “on show” block every time and the phone will slide onscreen repeatedly, I’m assuming because the NVL screen re-shows itself every time a new line of dialogue appears on screen.)

I also added the message fade-in to the frame holding the menu choices to make it look nicer.

Now that we have animations, I can explain a certain line in my nvl_phone function that I mentioned earlier in the nvl_phone utility function:

```
$ nvl_hide(Pause(0))
```

For some reason, “window hide” and “nvl hide” will hide the screen without running the ATL in the “on hide” block in the phone_stay transform, so the phone will just blip out of existence jarringly. However, the python equivalent, nvl_hide(), does not have the same problem and I don’t know why!!! It needs one argument, the transition to use to hide the window, and since we already have an animation defined in phone_stay, we can just pass Pause(0) so that it doesn’t do any additional transitions, and the “on hide” animation will play so that the phone will slide off the screen nicely. (Unfortunately, passing easeoutbottom as the transition doesn’t work, even though transitions such as dissolve and fade work fine…)

Another side note: if you have a function that filters your dialogue text and adds pauses after punctuation like periods and ellipses, you probably don’t want that to apply to your text messages, since the screen will re-display the message with its fade-in animation after every pause. To get around this, you can add a special character to the beginning of every text message and then catch them in your text filtering function:

```
call nvl_phone(active=True, clock="11:11", dr=lark)

    lp ">This is a test message!"

    mcp ">This is another test message!"

    menu(nvl=True):
        "Choice 1":
            mcp ">Choice 1 selected"

        "Choice 2":
            mcp ">Choice 2 selected"

    lp ">Test message"

    call nvl_phone(False)

########

init -1 python:
    def add_pauses(say_str):
        str_map = {
            ". "     : ". {w=0.2}",
            "? "     : "? {w=0.2}",
            "! "     : "! {w=0.2}",
            "......" : ". {w=0.02}. {w=0.02}. {w=0.02}. {w=0.02}. {w=0.02}. {w=0.02}",
            "..."    : ".{w=0.02}.{w=0.02}.{w=0.02}",
        }

        if say_str[0] == ">": #txt msg, don't add pauses
            return say_str[1:]
        else:
            for key in str_map:
                say_str = say_str.replace(key, str_map[key])
            return say_str
```

You can also send images with the {image} text tag! You’ll have to make sure the image fits within the maximum size you set for the message window, otherwise it’ll clip past the edges. An alternative is to define a separate NVL character for sending images to allow them to take up the width of the phone “screen” and not have the colored text bubble as the background, but I’ll leave that as an exercise for the reader.

```
call nvl_phone(True, "11:11", lark)

lp ">Hey look at this ticket"
lp ">{image=images/items/raffle_ticket.png"
```

<img src="https://64.media.tumblr.com/1922c49ae0c228d07acd61bd14c6309b/7bb6d116491dd696-15/s500x750/10852e201a168c6b6bbcb979e2e04ba4a6875af2.pnj" width="417" height="582" />

And that’s it! Your phone should look like the gif at the beginning.

## Room for improvement

While this phone screen is totally functional and works for my purposes, there are a few small things I’d like to fix or add at some point.

It’s not super noticeable so I’ve decided to leave it for now, but when the phone slides off the screen, the last message has its message_appear animation play again because it’s still the “current” message. Not sure how to approach this one besides maybe untangling the weird spaghetti of how the NVL screen gets shown and hidden lol.

## Links

Thanks for checking this out! You can find the full screen code in this repo. If any of the images are broken, you can see them in the original tumblr post I made [here](https://www.tumblr.com/albireogames/706652365674217473/renpy-stuff-part-2-phone-tutorial).

I referenced [this phone screen implementation](github.com/NightenDushi/yet-another-phone-for-renpy) a few times while trying to figure out my own, which was really helpful, especially for how to replace the nvl screen with the phone.

Thank god for the Lemmasoft Forums, without which I would never have seen [this really good thread](https://lemmasoft.renai.us/forums/viewtopic.php?t=32817) and figured out that I should use the python function nvl_hide() and would still be tearing my hair out trying to get the animation to work. I still don’t know why it works!! 

And finally, please check out our game [here](https://demyurge.itch.io/dragongame)! 
