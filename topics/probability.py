from helpers import *

from mobject import Mobject
from mobject.vectorized_mobject import VGroup, VMobject, VectorizedPoint
from mobject.svg_mobject import SVGMobject
from mobject.tex_mobject import TextMobject, TexMobject

from topics.geometry import Circle, Line, Rectangle, Square, Arc, Polygon


class SampleSpace(VGroup):
    CONFIG = {
        "full_space_config" : {
            "height" : 3,
            "width" : 3,
            "fill_color" : DARK_GREY,
            "fill_opacity" : 0.8,
            "stroke_width" : 0,
        }
    }
    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        full_space = Rectangle(**self.full_space_config)
        self.full_space = full_space
        self.add(full_space)

    def add_title(self, title = "Sample space", buff = MED_SMALL_BUFF):
        title_mob = TextMobject(title)
        if title_mob.get_width() > self.get_width():
            title_mob.scale_to_fit_width(self.get_width())
        title_mob.next_to(self.full_space, UP, buff = buff)
        self.title = title_mob
        self.add(title_mob)
    
    def divide_along_dimension(self, p, dim, colors):
        perp_dim = 1-dim
        if dim == 0:
            vects = [UP, DOWN]
        else:
            vects = [LEFT, RIGHT]
        parts = VGroup()
        for factor, vect, color in zip([p, 1-p], vects, colors):
            part = self.full_space.copy()
            part.set_fill(color, 1)
            part.stretch(factor, perp_dim)
            part.move_to(self.full_space, vect)
            parts.add(part)
        return parts

    def divide_horizontally(self, p, colors = [GREEN_E, RED_E]):
        result = self.divide_along_dimension(p, 0, colors)
        self.top_part, self.bottom_part = result
        return result

    def divide_vertically(self, p, colors = [MAROON_B, YELLOW]):
        result = self.divide_along_dimension(p, 1, colors)
        self.left_part, self.right_part = result
        return result

### Cards ###

class DeckOfCards(VGroup):
    def __init__(self, **kwargs):
        possible_values = map(str, range(1, 11)) + ["J", "Q", "K"]
        possible_suits = ["hearts", "diamonds", "spades", "clubs"]
        VGroup.__init__(self, *[
            PlayingCard(value = value, suit = suit, **kwargs)
            for value in possible_values
            for suit in possible_suits
        ])

class PlayingCard(VGroup):
    CONFIG = {
        "value" : None,
        "suit" : None,
        "key" : None, ##String like "8H" or "KS"
        "height" : 2,
        "height_to_width" : 3.5/2.5,
        "card_height_to_symbol_height" : 7,
        "card_width_to_corner_num_width" : 10,
        "card_height_to_corner_num_height" : 10,
        "color" : LIGHT_GREY,
        "turned_over" : False,
        "possible_suits" : ["hearts", "diamonds", "spades", "clubs"],
        "possible_values" : map(str, range(2, 11)) + ["J", "Q", "K", "A"],
    }

    def __init__(self, key = None, **kwargs):
        VGroup.__init__(self, key = key, **kwargs)

    def generate_points(self):
        self.add(Rectangle(
            height = self.height,
            width = self.height/self.height_to_width,
            stroke_color = WHITE,
            stroke_width = 2,
            fill_color = self.color,
            fill_opacity = 1,
        ))
        if self.turned_over:
            self.set_fill(DARK_GREY)
            self.set_stroke(LIGHT_GREY)
            contents = VectorizedPoint(self.get_center())
        else:
            value = self.get_value()
            symbol = self.get_symbol()
            design = self.get_design(value, symbol)
            corner_numbers = self.get_corner_numbers(value, symbol)
            contents = VGroup(design, corner_numbers)
            self.design = design
            self.corner_numbers = corner_numbers
        self.add(contents)

    def get_value(self):
        value = self.value
        if value is None:
            if self.key is not None:
                value = self.key[:-1]
            else:
                value = random.choice(self.possible_values)
        value = string.upper(str(value))
        if value == "1":
            value = "A"
        if value not in self.possible_values:
            raise Exception("Invalid card value")

        face_card_to_value = {
            "J" : 11, 
            "Q" : 12, 
            "K" : 13, 
            "A" : 14, 
        }
        try:
            self.numerical_value = int(value)
        except:
            self.numerical_value = face_card_to_value[value]
        return value

    def get_symbol(self):
        suit = self.suit
        if suit is None:
            if self.key is not None:
                suit = dict([
                    (string.upper(s[0]), s)
                    for s in self.possible_suits
                ])[string.upper(self.key[-1])]
            else:
                suit = random.choice(self.possible_suits)
        if suit not in self.possible_suits:
            raise Exception("Invalud suit value")
        self.suit = suit
        symbol_height = float(self.height) / self.card_height_to_symbol_height
        symbol = SuitSymbol(suit, height = symbol_height)
        return symbol

    def get_design(self, value, symbol):
        if value == "A":
            return self.get_ace_design(symbol)
        if value in map(str, range(2, 11)):
            return self.get_number_design(value, symbol)
        else:
            return self.get_face_card_design(value, symbol)

    def get_ace_design(self, symbol):
        design = symbol.copy().scale(1.5)
        design.move_to(self)
        return design

    def get_number_design(self, value, symbol):
        num = int(value)
        n_rows = {
            2 : 2, 
            3 : 3, 
            4 : 2, 
            5 : 2, 
            6 : 3, 
            7 : 3, 
            8 : 3, 
            9 : 4, 
            10 : 4,
        }[num]
        n_cols = 1 if num in [2, 3] else 2
        insertion_indices = {
            5 : [0], 
            7 : [0], 
            8 : [0, 1], 
            9 : [1], 
            10 : [0, 2],
        }.get(num, [])

        top = self.get_top() + symbol.get_height()*DOWN
        bottom = self.get_bottom() + symbol.get_height()*UP
        column_points = [
            interpolate(top, bottom, alpha)
            for alpha in np.linspace(0, 1, n_rows)
        ]

        design = VGroup(*[
            symbol.copy().move_to(point)
            for point in column_points
        ])
        if n_cols == 2:
            space = 0.2*self.get_width()
            column_copy = design.copy().shift(space*RIGHT)
            design.shift(space*LEFT)
            design.add(*column_copy)
        design.add(*[
            symbol.copy().move_to(
                center_of_mass(column_points[i:i+2])
            )
            for i in insertion_indices
        ])
        for symbol in design:
            if symbol.get_center()[1] < self.get_center()[1]:
                symbol.rotate_in_place(np.pi)
        return design

    def get_face_card_design(self, value, symbol):
        from topics.characters import PiCreature
        sub_rect = Rectangle(
            stroke_color = BLACK,
            fill_opacity = 0,
            height = 0.9*self.get_height(),
            width = 0.6*self.get_width(),
        )
        sub_rect.move_to(self)

        pi_color = average_color(symbol.get_color(), GREY)
        pi_mode = {
            "J" : "plain",
            "Q" : "thinking",
            "K" : "hooray"
        }[value]
        pi_creature = PiCreature(
            mode = pi_mode,
            color = pi_color,
        )
        pi_creature.scale_to_fit_width(0.8*sub_rect.get_width())
        if value in ["Q", "K"]:
            prefix = "king" if value == "K" else "queen"
            crown = SVGMobject(file_name = prefix + "_crown")
            crown.set_stroke(width = 0)
            crown.set_fill(YELLOW, 1)
            crown.stretch_to_fit_width(0.5*sub_rect.get_width())
            crown.stretch_to_fit_height(0.17*sub_rect.get_height())
            crown.move_to(pi_creature.eyes.get_center(), DOWN)
            pi_creature.add_to_back(crown)
            to_top_buff = 0
        else:
            to_top_buff = SMALL_BUFF*sub_rect.get_height()
        pi_creature.next_to(sub_rect.get_top(), DOWN, to_top_buff)
        # pi_creature.shift(0.05*sub_rect.get_width()*RIGHT)

        pi_copy = pi_creature.copy()
        pi_copy.rotate(np.pi, about_point = sub_rect.get_center())

        return VGroup(sub_rect, pi_creature, pi_copy)

    def get_corner_numbers(self, value, symbol):
        value_mob = TextMobject(value)
        width = self.get_width()/self.card_width_to_corner_num_width
        height = self.get_height()/self.card_height_to_corner_num_height
        value_mob.scale_to_fit_width(width)
        value_mob.stretch_to_fit_height(height)
        value_mob.next_to(
            self.get_corner(UP+LEFT), DOWN+RIGHT,
            buff = MED_LARGE_BUFF*width
        )
        value_mob.highlight(symbol.get_color())
        corner_symbol = symbol.copy()
        corner_symbol.scale_to_fit_width(width)
        corner_symbol.next_to(
            value_mob, DOWN, 
            buff = MED_SMALL_BUFF*width
        )
        corner_group = VGroup(value_mob, corner_symbol)
        opposite_corner_group = corner_group.copy()
        opposite_corner_group.rotate(
            np.pi, about_point = self.get_center()
        )

        return VGroup(corner_group, opposite_corner_group)

class SuitSymbol(SVGMobject):
    CONFIG = {
        "height" : 0.5,
        "fill_opacity" : 1,
        "stroke_width" : 0,
        "red" : "#D02028",
        "black" : BLACK,
    }
    def __init__(self, suit_name, **kwargs):
        digest_config(self, kwargs)
        suits_to_colors = {
            "hearts"   : self.red, 
            "diamonds" : self.red,
            "spades"   : self.black, 
            "clubs"    : self.black,
        }
        if suit_name not in suits_to_colors:
            raise Exception("Invalid suit name")
        SVGMobject.__init__(self, file_name = suit_name, **kwargs)

        color = suits_to_colors[suit_name]
        self.set_stroke(width = 0)
        self.set_fill(color, 1)
        self.scale_to_fit_height(self.height)
