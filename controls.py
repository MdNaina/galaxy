from kivy.uix.relativelayout import RelativeLayout

def _keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    self._keyboard.unbind(on_key_up=self._on_keyboard_up)
    self._keyboard = None

def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'right':
        self.current_speed_x = self.SPEED_X
    if keycode[1] == 'left':
        self.current_speed_x = -self.SPEED_X

    return True

def _on_keyboard_up(self, keyboard, keycode):
   self.current_speed_x = 0

   return True

def on_touch_down(self, touch):
    if self.game_has_started and not self.game_over:
        if touch.x > self.perspective_x:
            self.current_speed_x = self.SPEED_X
        else:
            self.current_speed_x = -self.SPEED_X
    return super(RelativeLayout, self).on_touch_down(touch)

def on_touch_up(self, touch):
    self.current_speed_x = 0

