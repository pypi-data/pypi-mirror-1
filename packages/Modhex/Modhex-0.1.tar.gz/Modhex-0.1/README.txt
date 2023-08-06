modhex
======

The Yubikey is a one-time password device that acts as a USB
keyboard, emitting a unique sequence of keycodes each time the button
is pressed. These codes produce different characters depending on
your keyboard layout. This can be frustrating if your keyboard layout
is incompatible with the Yubico server. 

`modhex.translate(otp)` compares the unicode output of a Yubikey
against the characters the Yubikey would emit in a variety of keyboard
layouts, returning the set of possible translations. In the likely
case `len(set(otp)) == 16`, almost every keyboard layout has an
unambigous translation into Yubico-compatible modhex, what the
Yubikey types under the QWERTY keyboard layout.

>>> import modhex
>>> modhex.translate(u"jjjjjjjjnhe.ngcgjeiuujjjdtgihjuecyixinxunkhj")
set([u'ccccccccljdeluiucdgffccchkugjcfditgbglbflvjc'])

>>> modhex.translate(u"jjjjjjjjnhe.ngcgjeiuujjjdtgihjuecyixinxunkhj",
... modhex.HEX)
set([u'00000000a823ae7e0254400069e580427d515a14af80'])
