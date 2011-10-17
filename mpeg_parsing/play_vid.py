from pygame import display,movie

overlay = display.set_mode((800,600))
m=movie.Movie('''C:\signaling\Xad_14_12.mpg''')
m.set_display(overlay)
print dir(m)
m.play()