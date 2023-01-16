screen nvl(dialogue, items=None):
    if phone_display_header["phone"]:
        use phone_display(dialogue, items)
    else:
        window:
            style "nvl_window"

            has vbox:
                spacing gui.nvl_spacing

            ## Displays dialogue in either a vpgrid or the vbox.
            if gui.nvl_height:

                vpgrid:
                    cols 1
                    yinitial 1.0

                    use nvl_dialogue(dialogue)

            else:

                use nvl_dialogue(dialogue)

            ## Displays the menu, if given. The menu may be displayed incorrectly if
            ## config.narrator_menu is set to True, as it is above.
            for i in items:

                textbutton i.caption:
                    action i.action
                    style "nvl_button"

        add SideImage() xalign 0.0 yalign 1.0


screen nvl_dialogue(dialogue):

    for d in dialogue:

        window:
            id d.window_id

            fixed:
                yfit gui.nvl_height is None

                if d.who is not None:

                    text d.who:
                        id d.who_id

                text d.what:
                    id d.what_id


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
                style d.who+"_message_window"
            else: #prevents it from crashing on reload when d.who is None
                $ phone_display_header["phone"] = False
            
            text d.what:
                id d.what_id
        

style phone_message_window:
    xfill False
    xpadding 22
    ypadding 8
    xminimum 55
    xmaximum 300
    yminimum 50

style mc_message_window is phone_message_window:
    background Frame("gui/phone_display/mc_msg.png", Borders(26, 25, 26, 25))
   
style lark_message_window is phone_message_window:
    background Frame("gui/phone_display/lark_msg.png", Borders(25, 25, 25, 25))
    
style phone_message_body:
    font "fonts/DUBAI-LIGHT.ttf"
    line_spacing -15
    size 22
    slow_cps 0

style mc_message_body is phone_message_body:
    color "#000000"
    
style dr_message_body is phone_message_body:
    color "#ffffff"



screen phone_display(dialogue, items=None):
    window at phone_stay:
        if len(dialogue) == 1:
            at phone_slide

        style "phone_display_window"
        text phone_display_header["clock"] style "phone_display_clock"
        add phone_display_header["icon"] zoom 0.47 xpos 50 ypos 77
        text phone_display_header["name"] style "phone_display_name"
        add "gui/phone_display/phone2.png" xpos 40 ypos 660

        viewport:
            area (22, 130, 430, 520)
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




style phone_display_clock:
    font "fonts/DUBAI-REGULAR.ttf"
    size 22
    color "#e1e1e1"
    xpos 70
    ypos 38

style phone_display_window:
    background Frame("gui/phone_display/phone1.png")
    xsize 487
    ysize 720

style phone_display_name:
    font "fonts/DUBAI-MEDIUM.ttf"
    size 30
    xpos 120
    ypos 73

style phone_display_vbox: #this allows the sent txts to be on the right. no idea why
    xsize 440

style phone_display_choice:
    xsize 350
    yminimum 119
    xanchor 1.0
    xpos 415
    top_padding 10
    bottom_padding 15

style lark_phone_display_choice is phone_display_choice:
    background Frame("gui/phone_display/lark_choice_bg.png", Borders(25, 25, 25, 25))


style phone_display_choice_button:
    background Frame("gui/phone_display/button.png")
    hover_background Frame("gui/phone_display/button_hover.png")
    xanchor 1.0
    xpos 330
    xsize 324
    ysize 44
    xpadding 15
    ypadding 5
    hover_sound audio.phone_mh
    activate_sound audio.phone_cont

style phone_display_choice_text:
    font "fonts/DUBAI-LIGHT.ttf"
    size 22
    xmaximum 300
    color "#aaaaaa"
    hover_color "#000000"
    xalign 0.5
    
