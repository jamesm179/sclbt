import logging
from typing import Dict

class TrailingStopManager:
    """Manages dynamic trailing stop-loss functionality"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.trailing_data = {}  # Store trailing stop data for each position

    def calculate_trailing_stop(self, position: Dict, current_price: float) -> Dict:
        try:
            # Get latest config values for real-time adjustments
            activation_profit = self.config_manager.get('trailing_activation_profit', 20.0)
            initial_distance = self.config_manager.get('initial_trail_distance', 10.0)
            tightening_step = self.config_manager.get('trail_tightening_step', 6.0)
            profit_increment = self.config_manager.get('profit_increment_threshold', 10.0)
            method = self.config_manager.get('trailing_method', 'percentage')

            pair = position.get('pair', '')
            entry_price = float(position.get('entry_price', 0))
            direction = position.get('direction', 'long')
            position_id = position.get('id', f"{pair}_{direction}")

            if entry_price == 0:
                return None

            if direction == 'long':
                profit_pct = ((current_price - entry_price) / entry_price) * 100
            else:
                profit_pct = ((entry_price - current_price) / entry_price) * 100

            if profit_pct < activation_profit:
                return None

            if position_id not in self.trailing_data:
                self.trailing_data[position_id] = {
                    'activated': True, 'highest_profit': profit_pct,
                    'current_trail_distance': initial_distance,
                    'last_trail_level': None, 'method': method
                }

            trail_info = self.trailing_data[position_id]

            if profit_pct > trail_info['highest_profit']:
                trail_info['highest_profit'] = profit_pct
                if method == "percentage":
                    profit_above_activation = profit_pct - activation_profit
                    tightening_steps = int(profit_above_activation / profit_increment)
                    new_trail_distance = initial_distance - (tightening_steps * tightening_step)
                    new_trail_distance = max(new_trail_distance, 1.0)
                    trail_info['current_trail_distance'] = new_trail_distance

            if method == "percentage":
                if direction == 'long':
                    high_price = entry_price * (1 + trail_info['highest_profit'] / 100)
                    new_trail_level = high_price * (1 - trail_info['current_trail_distance'] / 100)
                else:
                    low_price = entry_price * (1 - trail_info['highest_profit'] / 100)
                    new_trail_level = low_price * (1 + trail_info['current_trail_distance'] / 100)
            elif method == "ema":
                new_trail_level = self._calculate_ema_trailing_level(pair, direction, current_price)

            if trail_info['last_trail_level'] is not None:
                if direction == 'long':
                    new_trail_level = max(new_trail_level, trail_info['last_trail_level'])
                else:
                    new_trail_level = min(new_trail_level, trail_info['last_trail_level'])

            trail_info['last_trail_level'] = new_trail_level
            return trail_info

        except Exception as e:
            logging.error(f"Error calculating trailing stop for {position.get('pair', 'unknown')}: {e}")
            return None

    def _calculate_ema_trailing_level(self, pair, direction, current_price):
        return current_price * (0.95 if direction == 'long' else 1.05)

    def check_trailing_exit(self, position: Dict, current_price: float) -> bool:
        try:
            pair = position.get('pair', '')
            direction = position.get('direction', 'long')
            position_id = position.get('id', f"{pair}_{direction}")
            if position_id not in self.trailing_data: return False
            trail_info = self.trailing_data[position_id]
            trail_level = trail_info.get('last_trail_level')
            if trail_level is None: return False
            return current_price <= trail_level if direction == 'long' else current_price >= trail_level
        except Exception as e:
            logging.error(f"Error checking trailing exit for {position.get('pair', 'unknown')}: {e}")
            return False

    def remove_position(self, position_id: str):
        if position_id in self.trailing_data:
            del self.trailing_data[position_id]

    def reset_all(self):
        self.trailing_data.clear()
