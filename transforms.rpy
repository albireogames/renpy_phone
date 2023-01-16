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

