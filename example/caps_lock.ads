# Turns capslock off
ifj caps turn_off
goto off_done

:turn_off
toggle caps

:off_done


# Turn light on depending on caps state
:light_off
light off
goto loop

:light_on
light on

:loop
wait 100
ifj caps light_on
goto light_off
