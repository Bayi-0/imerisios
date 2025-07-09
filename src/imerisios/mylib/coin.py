import random
import toga
from toga.style import Pack
from toga.constants import COLUMN


class CoinFlip:
    def __init__(self, app):
        self.app = app

        self.strings = self.app.strings["coin"]
    

    @property
    def clrs(self):
        return self.app.clrs
    

    def reg(self, widgets=[]):
        self.app.reg(widgets)


    def get_coinside_boxes(self):
        boxes = []
        for side in ["heads", "tails"]:
            title = toga.Label(
                self.strings[side], 
                style=Pack(padding=(14,0,2), text_align="center", font_weight="bold", font_size=38, color=self.clrs[2])
            )
            img = toga.ImageView(
                toga.Image(f"resources/images/coin/{side}.png"), 
                style=Pack(flex=0.5)
            )
            question = toga.Label(
                self.strings["fate_question"], 
                style=Pack(padding=(4,8,10), text_align="center", font_size=14, color=self.clrs[2])
            )
            button = toga.Button(
                self.strings["shall"], on_press=self.app.open_coin, 
                style=Pack(height=120, padding=11, font_size=18, color=self.clrs[2], background_color=self.clrs[1])
            )

            box = toga.Box(
                children=[title, img, question, button], 
                style=Pack(direction=COLUMN, background_color=self.clrs[0])
            )
            boxes.append(box)

            self.reg([title, question, button, box])

        return boxes
        

    def get_coin_box(self):
        def get_quotes_box(quotes):
            box = toga.Box(style=Pack(direction=COLUMN, flex=0.4, padding=4))
            for i in range(0, len(quotes)-1, 2):
                l1 = toga.Label(quotes[i], style=Pack(padding=(4,4,0), font_size=7, color=self.clrs[2]))
                l2 = toga.Label(
                    quotes[i+1], 
                    style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color=self.clrs[2])
                )
                box.add(l1)
                box.add(l2)
                self.reg([l1, l2])
            return box
        
        quotes_top = [
            "“You can do anything. Doesn't mean you have to.”", "— Geralt, The Witcher by Andrzej Sapkowski", 
            "“Fate invariably finds a way to thwart the schemes of men.”", "— Andrzej Sapkowski, The Witcher",
            "“Even the smallest person can change the course of the future.”", "— Galadriel, The Lord of the Rings by J. R. R. Tolkien",
            "“Fate, in my view, is just a glorified analysis of probabilities.”", "— The Malefic Viper, The Primal Hunter by Zogarth",
            "“Destiny helps people believe there's an order to this horseshit. There isn't. But a promise made\nmust be honored.”", "— Geralt, The Witcher by Andrzej Sapkowski",
            "“Life's but a walking shadow, a poor player that struts and frets his hour upon the stage and\nthen is heard no more. It is a tale told by an idiot, full of sound and fury, signifying nothing.”", "Macbeth, by William Shakespear",
            "“The mystery of life isn't a problem to solve, but a reality to experience.”", "— Frank Herbert, The Dune",
            "“Destiny is a double-edged sword. You are one edge, the other is death.”", "— Queen Calanthe, The Witcher by Andrzej Sapkowski"
        ]
        quotes_bottom = [
            "“But now, if I have to choose between one evil and another, then I prefer not to choose at all.”", "— Geralt, The Witcher by Andrzej Sapkowski", 
            "“Fate is the same for the man who holds back, the same if he fights hard. We are all held in a\nsingle honor, the brave with the weaklings. A man dies still if he has done nothing, as one who\nhas done much.”", "— Achilles, The Iliad by Homer",
            "“Destiny is just the embodiment of the soul's desire to grow.”", "— Jaskier, The Witcher by Andrzej Sapkowski",
            "“Keep telling destiny how much of a little bitch it is, and reach for power that was never fated\nto be yours. Because fuck fate, fuck destiny. The path you forge is your own, and don't ever\nlet anyone tell you otherwise.”", "— The Malefic Viper, The Primal Hunter by Zogarth",
            "“Even the darkest night will end and the sun will rise.”", "— Victor Hugo, Les Misérables",
            "“All we have to decide is what to do with the time that is given us.”", "— Gandalf, The Lord of the Rings by J. R. R. Tolkien",
            "“There is no destiny. It's but a slow death. But you're right, I must fulfil my destiny.”", "— Geralt, The Witcher by Andrzej Sapkowski"
        ]  
        quotes_boxes = [get_quotes_box(quotes) for quotes in (quotes_top, quotes_bottom)] 
            
        self.coin_sides = self.get_coinside_boxes()

        flip_button = toga.Button(
            self.strings["flip_coin"], on_press=self.flip_coin, 
            style=Pack(flex=0.2, height=140, padding=18, font_size=18, color=self.clrs[2], background_color=self.clrs[1])
        )
        
        coin_box = toga.Box(
            children=[quotes_boxes[0], flip_button, quotes_boxes[1]],
            style=Pack(direction=COLUMN, background_color=self.clrs[0])
        )
        
        self.reg([coin_box, flip_button])
        
        return coin_box
        

    def flip_coin(self, widget):
        self.app.main_window.content = self.coin_sides[random.randint(0,1)]