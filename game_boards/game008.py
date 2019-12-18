# -*- coding: utf-8 -*-

import os
import pygame
import random

import classes.board
import classes.game_driver as gd
import classes.level_controller as lc


class Board(gd.BoardGame):
    def __init__(self, mainloop, speaker, config, screen_w, screen_h):
        self.level = lc.Level(self, mainloop, 15, 3)
        gd.BoardGame.__init__(self, mainloop, speaker, config, screen_w, screen_h, 11, 9)

    def create_game_objects(self, level=1):
        self.board.decolorable = False
        self.board.draw_grid = False
        color = (255, 255, 255, 0)
        mask_color = color
        data = [7, 3]

        # stretch width to fit the screen size
        max_x_count = self.get_x_count(data[1], even=False)
        if max_x_count > 7:
            data[0] = max_x_count

        self.data = data
        self.center = self.data[0] // 2
        self.vis_buttons = [0, 1, 1, 1, 1, 0, 1, 0, 0]
        self.mainloop.info.hide_buttonsa(self.vis_buttons)

        self.layout.update_layout(data[0], data[1])
        scale = self.layout.scale
        self.board.level_start(data[0], data[1], scale)

        self.unit_mouse_over = None
        self.units = []

        if self.level.lvl == 1:
            self.item_count = 3
        elif self.level.lvl == 2:
            self.item_count = 5
        elif self.level.lvl == 3:
            self.item_count = 7

        images = [os.path.join('match_animals', "m_img%da.png" % (i)) for i in range(1, 20)]
        if self.mainloop.scheme is None or not self.mainloop.scheme.dark:
            masks = [os.path.join('memory', "m_img%db.png" % (i)) for i in range(1, 20)]
        else:
            masks = [os.path.join('schemes', "black", "match_animals", "m_img%db.png" % (i)) for i in range(1, 20)]
        choice = [x for x in range(0, 19)]
        shuffled = choice[:]
        random.shuffle(shuffled)
        self.chosen = shuffled[0:self.item_count]
        self.points = 3
        self.shuffled2 = self.chosen[:]
        random.shuffle(self.shuffled2)
        x = (self.data[0] - self.item_count) // 2

        self.solution = []
        for i in range(data[0]):
            if x <= i < x + self.item_count:
                self.solution.append(1)
            else:
                self.solution.append(0)
        fg_tint_color = (30, 30, 30)
        for i in range(self.item_count):
            self.board.add_door(x + i, 0, 1, 1, classes.board.Door, str(self.chosen[i]), mask_color,
                                masks[self.chosen[i]])
            self.board.add_universal_unit(grid_x=x + i, grid_y=2, grid_w=1, grid_h=1, txt=str(self.shuffled2[i]),
                                          fg_img_src=images[self.shuffled2[i]], bg_img_src=images[self.shuffled2[i]],
                                          dc_img_src=None, bg_color=(0, 0, 0, 0), border_color=None, font_color=None,
                                          bg_tint_color=None, fg_tint_color=fg_tint_color,
                                          txt_align=(0, 0), font_type=3, multi_color=False, alpha=True,
                                          immobilized=False, fg_as_hover=True)
            self.units.append(self.board.ships[-1])

            self.board.ships[-1].checkable = True
            self.board.ships[-1].init_check_images()

        for each in self.board.ships:
            self.board.all_sprites_list.move_to_front(each)
            each.outline = False
            each.readable = False

        for each in self.board.units:
            each.outline = False

    def handle(self, event):
        gd.BoardGame.handle(self, event)
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.auto_check_reset()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.board.active_ship >= 0:
                active = self.board.ships[self.board.active_ship]
                active.image.set_alpha(150)
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.board.active_ship >= 0:
                active = self.board.ships[self.board.active_ship]
                active.image.set_alpha(255)
            self.check_result()
        if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
            self.default_hover(event)

    def auto_check_reset(self):
        for each in self.board.ships:
            if each.checkable:
                each.set_display_check(None)

    def update(self, game):
        game.fill((255, 255, 255))
        gd.BoardGame.update(self, game)

    def check_result(self):
        if self.changed_since_check:
            if self.board.grid[0] == self.solution:
                ships = []
                units = []
                # collect value and x position on the grid from ships list
                for i in range(self.item_count):
                    ships.append([self.board.ships[i].grid_x, int(self.board.ships[i].value), self.board.ships[i]])
                    units.append([self.board.units[i].grid_x, int(self.board.units[i].value)])
                ships.sort()
                units.sort()
                correct = True
                for i in range(self.item_count):
                    if ships[i][1] != units[i][1]:
                        ships[i][2].set_display_check(False)
                        correct = False
                    else:
                        ships[i][2].set_display_check(True)
                if correct:
                    self.level.next_board()
        self.mainloop.redraw_needed[0] = True

