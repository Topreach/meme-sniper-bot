import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from src.utils.logger import get_logger

logger = get_logger('pattern_predictor')

class PatternPredictor:
    def __init__(self, lookback=60, features=5):
        self.model = self.build_model(lookback, features)
        self.lookback = lookback
        self.features = features
        
    def build_model(self, lookback, features):
        model = Sequential([
            LSTM(64, input_shape=(lookback, features), 
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model
        
    def train(self, X_train, y_train, epochs=50, batch_size=32):
        logger.info(f"Training pattern predictor with {len(X_train)} samples")
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.2)
        
    def predict(self, sequence):
        if len(sequence) != self.lookback:
            raise ValueError(f"Sequence length must be {self.lookback}")
            
        # Prepare input
        input_seq = np.array([sequence])
        prediction = self.model.predict(input_seq)[0][0]
        return float(prediction)
