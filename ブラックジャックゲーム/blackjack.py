import random
from enum import Enum

class Suit(Enum):
    """スーツの定義"""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Card:
    """カードクラス"""
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank}{self.suit.value}"
    
    def get_value(self):
        """カードの値を取得"""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

class Deck:
    """デッキクラス"""
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        """デッキをリセット"""
        self.cards = []
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        for suit in Suit:
            for rank in ranks:
                self.cards.append(Card(suit, rank))
        random.shuffle(self.cards)
    
    def draw(self):
        """カードを1枚引く"""
        if len(self.cards) < 10:  # カードが10枚以下になったらリセット
            self.reset()
        return self.cards.pop()

class Hand:
    """手札クラス"""
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        """カードを追加"""
        self.cards.append(card)
    
    def get_value(self):
        """手札の合計値を計算"""
        total = 0
        aces = 0
        
        for card in self.cards:
            total += card.get_value()
            if card.rank == 'A':
                aces += 1
        
        # エースを11から1に変更してバストを回避
        while total > 21 and aces > 0:
            total -= 10  # Aを11から1に変更（11-1=10の差分）
            aces -= 1
        
        return total
    
    def display(self, hide_first=False):
        """手札を表示"""
        display_cards = []
        for i, card in enumerate(self.cards):
            if hide_first and i == 0:
                display_cards.append("【非表示】")
            else:
                display_cards.append(str(card))
        
        hand_str = ", ".join(display_cards)
        if hide_first and len(self.cards) > 1:
            print(f"手札: {hand_str} (値: {self.cards[1].get_value()})")
        else:
            print(f"手札: {hand_str} (値: {self.get_value()})")
    
    def clear(self):
        """手札をクリア"""
        self.cards = []

class BlackjackGame:
    """ブラックジャックゲームクラス"""
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.player_balance = 100
        self.current_bet = 0
    
    def start_game(self):
        """ゲームを開始"""
        print("\n" + "="*50)
        print("ブラックジャックへようこそ！")
        print("="*50)
        
        while self.player_balance > 0:
            if not self.play_round():
                break
        
        print(f"\nゲーム終了。最終残高: ${self.player_balance}")
    
    def play_round(self):
        """1ラウンドをプレイ"""
        print(f"\n現在の残高: ${self.player_balance}")
        
        # ベット
        while True:
            try:
                bet_input = input(f"ベット額を入力してください（1-{self.player_balance}）: $")
                self.current_bet = int(bet_input)
                if 1 <= self.current_bet <= self.player_balance:
                    break
                else:
                    print(f"1から{self.player_balance}の範囲で入力してください")
            except ValueError:
                print("有効な数字を入力してください")
        
        self.player_balance -= self.current_bet
        
        # 初期カード配布
        self.player_hand.clear()
        self.dealer_hand.clear()
        
        for _ in range(2):
            self.player_hand.add_card(self.deck.draw())
            self.dealer_hand.add_card(self.deck.draw())
        
        print("\n【ディーラーの手札】")
        self.dealer_hand.display(hide_first=True)
        
        print("\n【プレイヤーの手札】")
        self.player_hand.display()
        
        # プレイヤーのターン
        while True:
            if self.player_hand.get_value() > 21:
                print("\nプレイヤーがバスト！")
                print(f"ディーラーが${self.current_bet}を獲得しました。")
                return True
            
            if self.player_hand.get_value() == 21 and len(self.player_hand.cards) == 2:
                print("\nブラックジャック！")
                break
            
            action = input("\n[H] ヒット, [S] スタンド: ").upper()
            
            if action == 'H':
                self.player_hand.add_card(self.deck.draw())
                print("\n【プレイヤーの手札】")
                self.player_hand.display()
            elif action == 'S':
                break
            else:
                print("HまたはSを入力してください")
        
        # ディーラーのターン
        print("\n【ディーラーの手札】")
        self.dealer_hand.display()
        
        while self.dealer_hand.get_value() < 17:
            print("ディーラーはヒットします...")
            self.dealer_hand.add_card(self.deck.draw())
            self.dealer_hand.display()
        
        # 結果判定
        player_value = self.player_hand.get_value()
        dealer_value = self.dealer_hand.get_value()
        
        print("\n" + "="*50)
        print("【結果】")
        print(f"プレイヤー: {player_value}")
        print(f"ディーラー: {dealer_value}")
        print("="*50)
        
        if dealer_value > 21:
            print("ディーラーがバスト！プレイヤーの勝ち！")
            self.player_balance += self.current_bet * 2
        elif player_value > dealer_value:
            print("プレイヤーの勝ち！")
            self.player_balance += self.current_bet * 2
        elif player_value == dealer_value:
            print("プッシュ（引き分け）")
            self.player_balance += self.current_bet
        else:
            print("ディーラーの勝ち")
        
        print(f"現在の残高: ${self.player_balance}")
        
        if self.player_balance <= 0:
            print("残高がなくなりました。ゲーム終了です。")
            return False
        
        continue_input = input("\nもう1ラウンドプレイしますか？ [Y] はい, [N] いいえ: ").upper()
        return continue_input != 'N'

def main():
    """メイン関数"""
    game = BlackjackGame()
    game.start_game()

if __name__ == "__main__":
    main()
