from flask import Flask, render_template, request, jsonify, session
import random
from enum import Enum
import os

app = Flask(__name__)
app.secret_key = 'blackjack_secret_key_2026'

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
    
    def to_dict(self):
        return {
            "rank": self.rank,
            "suit": self.suit.value
        }
    
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
        if len(self.cards) < 10:
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
        
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def to_dict(self, hide_first=False):
        """手札を辞書形式に変換"""
        cards = []
        for i, card in enumerate(self.cards):
            if hide_first and i == 0:
                cards.append({"rank": "?", "suit": "?"})
            else:
                cards.append(card.to_dict())
        return cards
    
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
        self.game_state = "betting"  # betting, playing, dealer_turn, finished
        self.message = ""
    
    def start_round(self, bet):
        """新しいラウンドを開始"""
        if bet < 1 or bet > self.player_balance:
            return False
        
        self.current_bet = bet
        self.player_balance -= bet
        self.player_hand.clear()
        self.dealer_hand.clear()
        
        for _ in range(2):
            self.player_hand.add_card(self.deck.draw())
            self.dealer_hand.add_card(self.deck.draw())
        
        self.game_state = "playing"
        
        # ブラックジャックチェック
        if self.player_hand.get_value() == 21:
            self.finish_round()
        
        return True
    
    def hit(self):
        """ヒット"""
        if self.game_state != "playing":
            return False
        
        self.player_hand.add_card(self.deck.draw())
        
        if self.player_hand.get_value() > 21:
            self.finish_round()
        
        return True
    
    def stand(self):
        """スタンド"""
        if self.game_state != "playing":
            return False
        
        self.game_state = "dealer_turn"
        
        # ディーラーのターン
        while self.dealer_hand.get_value() < 17:
            self.dealer_hand.add_card(self.deck.draw())
        
        self.finish_round()
        return True
    
    def finish_round(self):
        """ラウンドを終了"""
        self.game_state = "finished"
        
        player_value = self.player_hand.get_value()
        dealer_value = self.dealer_hand.get_value()
        
        if player_value > 21:
            self.message = "プレイヤーがバスト！ディーラーの勝ち"
        elif dealer_value > 21:
            self.message = "ディーラーがバスト！プレイヤーの勝ち！"
            self.player_balance += self.current_bet * 2
        elif player_value == 21 and len(self.player_hand.cards) == 2:
            self.message = "ブラックジャック！プレイヤーの勝ち！"
            self.player_balance += self.current_bet * 2
        elif player_value > dealer_value:
            self.message = "プレイヤーの勝ち！"
            self.player_balance += self.current_bet * 2
        elif player_value == dealer_value:
            self.message = "プッシュ（引き分け）"
            self.player_balance += self.current_bet
        else:
            self.message = "ディーラーの勝ち"
    
    def to_dict(self, show_dealer_cards=False):
        """ゲーム状態を辞書形式に変換"""
        return {
            "player_cards": self.player_hand.to_dict(),
            "player_value": self.player_hand.get_value(),
            "dealer_cards": self.dealer_hand.to_dict(hide_first=(self.game_state not in ["dealer_turn", "finished"])),
            "dealer_value": self.dealer_hand.get_value() if self.game_state in ["dealer_turn", "finished"] else None,
            "balance": self.player_balance,
            "current_bet": self.current_bet,
            "game_state": self.game_state,
            "message": self.message
        }

# ゲームをセッションに保存
def get_game():
    if 'game' not in session:
        session['game'] = {}
    return session['game']

def save_game(game_data):
    session['game'] = game_data
    session.modified = True

@app.route('/')
def index():
    """ホームページ"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_game():
    """ゲーム開始"""
    data = request.json
    bet = data.get('bet', 0)
    
    game = BlackjackGame()
    if game.start_round(bet):
        session['game_obj'] = {
            'player_balance': game.player_balance,
            'current_bet': game.current_bet,
            'player_cards': [(c.rank, c.suit.value) for c in game.player_hand.cards],
            'dealer_cards': [(c.rank, c.suit.value) for c in game.dealer_hand.cards],
            'game_state': game.game_state,
            'message': game.message
        }
        session.modified = True
        
        return jsonify(game.to_dict()), 200
    else:
        return jsonify({'error': 'Invalid bet'}), 400

@app.route('/api/hit', methods=['POST'])
def hit():
    """ヒット"""
    if 'game_obj' not in session:
        return jsonify({'error': 'Game not started'}), 400
    
    game_data = session.get('game_obj', {})
    game = BlackjackGame()
    game.player_balance = game_data.get('player_balance', 100)
    game.current_bet = game_data.get('current_bet', 0)
    game.game_state = game_data.get('game_state', 'playing')
    game.message = game_data.get('message', '')
    
    # カードを復元
    for rank, suit in game_data.get('player_cards', []):
        suit_enum = next((s for s in Suit if s.value == suit), Suit.HEARTS)
        game.player_hand.add_card(Card(suit_enum, rank))
    
    for rank, suit in game_data.get('dealer_cards', []):
        suit_enum = next((s for s in Suit if s.value == suit), Suit.HEARTS)
        game.dealer_hand.add_card(Card(suit_enum, rank))
    
    game.hit()
    
    game_data['player_cards'] = [(c.rank, c.suit.value) for c in game.player_hand.cards]
    game_data['dealer_cards'] = [(c.rank, c.suit.value) for c in game.dealer_hand.cards]
    game_data['game_state'] = game.game_state
    game_data['message'] = game.message
    
    session['game_obj'] = game_data
    session.modified = True
    
    return jsonify(game.to_dict()), 200

@app.route('/api/stand', methods=['POST'])
def stand():
    """スタンド"""
    if 'game_obj' not in session:
        return jsonify({'error': 'Game not started'}), 400
    
    game_data = session.get('game_obj', {})
    game = BlackjackGame()
    game.player_balance = game_data.get('player_balance', 100)
    game.current_bet = game_data.get('current_bet', 0)
    game.game_state = game_data.get('game_state', 'playing')
    game.message = game_data.get('message', '')
    
    # カードを復元
    for rank, suit in game_data.get('player_cards', []):
        suit_enum = next((s for s in Suit if s.value == suit), Suit.HEARTS)
        game.player_hand.add_card(Card(suit_enum, rank))
    
    for rank, suit in game_data.get('dealer_cards', []):
        suit_enum = next((s for s in Suit if s.value == suit), Suit.HEARTS)
        game.dealer_hand.add_card(Card(suit_enum, rank))
    
    game.stand()
    
    game_data['player_cards'] = [(c.rank, c.suit.value) for c in game.player_hand.cards]
    game_data['dealer_cards'] = [(c.rank, c.suit.value) for c in game.dealer_hand.cards]
    game_data['player_balance'] = game.player_balance
    game_data['game_state'] = game.game_state
    game_data['message'] = game.message
    
    session['game_obj'] = game_data
    session.modified = True
    
    return jsonify(game.to_dict(show_dealer_cards=True)), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
