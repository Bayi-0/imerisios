import random
import toga
from toga.style import Pack
from toga.constants import COLUMN


class CoinFlip:
    def __init__(self, app):
        self.app = app


    def get_heads_box(self):
        heads_title = toga.Label(
            "Heads", 
            style=Pack(padding=(14,0,2), text_align="center", font_weight="bold", font_size=48, color="#EBF6F7"))
        heads_image = toga.ImageView(
            toga.Image("resources/coin/heads.png"), 
            style=Pack(flex=0.5, padding=11))
        heads_question = toga.Label(
            "Will you embrace the destiny\ndecided by this coin flip,\naccepting its outcome as the\nguiding force of your fate?", 
            style=Pack(padding=(4,8,10), text_align="center", font_size=18, color="#EBF6F7"))
        heads_button = toga.Button(
            "I shall", on_press=self.app.open_coin, 
            style=Pack(height=140, padding=11, font_size=28, color="#EBF6F7", background_color="#27221F"))

        heads_box = toga.Box(
            children=[heads_title, heads_image, heads_question, heads_button], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return heads_box


    def get_tails_box(self):
        tails_title = toga.Label(
            "Tails", 
            style=Pack(padding=(14,0,2), text_align="center", font_weight="bold", font_size=48, color="#EBF6F7"))
        tails_image = toga.ImageView(toga.Image("resources/coin/tails.png"), style=Pack(flex=0.5, padding=11))
        tails_question = toga.Label(
            "Will you embrace the destiny\ndecided by this coin flip,\naccepting its outcome as the\nguiding force of your fate?", 
            style=Pack(padding=(4,8,10), text_align="center", font_size=18, color="#EBF6F7"))
        tails_button = toga.Button(
            "I shall", on_press=self.app.open_coin, 
            style=Pack(height=140, padding=11, font_size=28, color="#EBF6F7", background_color="#27221F"))
        
        tails_box = toga.Box(
            children=[tails_title, tails_image, tails_question, tails_button], 
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return tails_box
        

    def get_coin_box(self):
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
        coin_box_top = toga.Box(style=Pack(direction=COLUMN, flex=0.4, padding=4))
        for i in range(0, len(quotes_top)-1, 2):
            coin_box_top.add(toga.Label(quotes_top[i], style=Pack(padding=(4,4,0), font_size=7, color="#EBF6F7")))
            coin_box_top.add(
                toga.Label(quotes_top[i+1], 
                style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color="#EBF6F7")))

        quotes_bottom = [
            "“But now, if I have to choose between one evil and another, then I prefer not to choose at all.”", "— Geralt, The Witcher by Andrzej Sapkowski", 
            "“Fate is the same for the man who holds back, the same if he fights hard. We are all held in a\nsingle honor, the brave with the weaklings. A man dies still if he has done nothing, as one who\nhas done much.”", "— Achilles, The Iliad by Homer",
            "“Destiny is just the embodiment of the soul's desire to grow.”", "— Jaskier, The Witcher by Andrzej Sapkowski",
            "“Keep telling destiny how much of a little bitch it is, and reach for power that was never fated\nto be yours. Because fuck fate, fuck destiny. The path you forge is your own, and don't ever\nlet anyone tell you otherwise.”", "— The Malefic Viper, The Primal Hunter by Zogarth",
            "“Even the darkest night will end and the sun will rise.”", "— Victor Hugo, Les Misérables",
            "“All we have to decide is what to do with the time that is given us.”", "— Gandalf, The Lord of the Rings by J. R. R. Tolkien",
            "“There is no destiny. It's but a slow death. But you're right, I must fulfil my destiny.”", "— Geralt, The Witcher by Andrzej Sapkowski"
        ]  
        coin_box_bottom = toga.Box(style=Pack(direction=COLUMN, flex=0.4, padding=4))
        for i in range(0, len(quotes_bottom)-1, 2):
            coin_box_bottom.add(toga.Label(quotes_bottom[i], style=Pack(padding=(4,4,0), font_size=7, color="#EBF6F7")))
            coin_box_bottom.add(toga.Label(
                quotes_bottom[i+1], 
                style=Pack(padding=(0,4,4), text_align="right", font_size=7, font_style="italic", color="#EBF6F7")))
            
        self.coin_sides = [self.get_heads_box(), self.get_tails_box()]
        flip_button = toga.Button(
            "Invert the coin", on_press=self.flip_coin, 
            style=Pack(flex=0.2, height=140, padding=18, font_size=28, color="#EBF6F7", background_color="#27221F"))
        
        coin_box = toga.Box(
            children=[coin_box_top, flip_button, coin_box_bottom],
            style=Pack(direction=COLUMN, background_color="#393432"))
        
        return coin_box
        

    def flip_coin(self, widget):
        self.app.main_window.content = self.coin_sides[random.randint(0,1)]