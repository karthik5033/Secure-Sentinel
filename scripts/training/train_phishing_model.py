
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, f1_score
from tqdm import tqdm
import os
import json
import random

# ===========================
# CONFIGURATION
# ===========================
# Check for RTX 4060 (CUDA)
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🚀 Using Device: {DEVICE}")
if DEVICE.type == 'cuda':
    print(f"   GPU: {torch.cuda.get_device_name(0)}")

BATCH_SIZE = 1024  # Large batch size for GPU efficiency
EPOCHS = 15        # Deep learning needs epochs
LEARNING_RATE = 0.001
MAX_LEN = 150      # Truncate/Pad URLs to this length
EMBED_DIM = 64
FILTERS = 128
KERNEL_SIZE = 5
DATA_PATH = r"d:\Downloads\DTLshit\ext_data\refined_training_dataset.csv"
MODEL_SAVE_PATH = r"d:\Downloads\DTLshit\backend\models\best_phishing_model.pth"
METADATA_SAVE_PATH = r"d:\Downloads\DTLshit\backend\models\model_metadata.json"

os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

# ===========================
# 1. DATA PREPARATION
# ===========================
class URLTokenizer:
    def __init__(self):
        self.char2idx = {}
        self.idx2char = {}
        self.vocab_size = 0
        # Common URL characters
        chars = "abcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;=%"
        self.build_vocab(chars)
        
    def build_vocab(self, chars):
        self.char2idx = {char: idx + 1 for idx, char in enumerate(chars)} # 0 is padding
        self.char2idx['<UNK>'] = len(self.char2idx) + 1
        self.vocab_size = len(self.char2idx) + 1
        
    def encode(self, url, max_len=MAX_LEN):
        url = str(url).lower()
        encoding = [self.char2idx.get(c, self.char2idx['<UNK>']) for c in url]
        if len(encoding) < max_len:
            encoding += [0] * (max_len - len(encoding)) # Pad
        else:
            encoding = encoding[:max_len] # Truncate
        return encoding

class PhishingDataset(Dataset):
    def __init__(self, urls, labels, tokenizer):
        self.urls = urls
        self.labels = labels
        self.tokenizer = tokenizer
        
    def __len__(self):
        return len(self.urls)
    
    def __getitem__(self, idx):
        url = self.urls[idx]
        label = self.labels[idx]
        encoded = self.tokenizer.encode(url)
        return torch.tensor(encoded, dtype=torch.long), torch.tensor(label, dtype=torch.float32)

# ===========================
# 2. MODEL DEFINITION (1D-CNN)
# ===========================
class PhishNetCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_filters, kernel_size):
        super(PhishNetCNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        # Convolutional Layers to extract n-gram features (e.g., "log", "in", "pay", "pal")
        self.conv1 = nn.Conv1d(in_channels=embed_dim, out_channels=num_filters, kernel_size=kernel_size)
        self.relu = nn.ReLU()
        self.pool = nn.AdaptiveMaxPool1d(1) # Global Max Pooling
        
        self.dropout = nn.Dropout(0.5)
        
        # Dense Layers
        self.fc1 = nn.Linear(num_filters, 64)
        self.fc2 = nn.Linear(64, 1) # Binary Classification
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        # x shape: [batch, max_len]
        x = self.embedding(x) 
        # permute for conv1d: [batch, embed_dim, max_len]
        x = x.permute(0, 2, 1) 
        
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x).squeeze(2) # [batch, num_filters]
        
        x = self.dropout(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        output = self.sigmoid(x)
        return output

# ===========================
# 3. TRAINING LOOP
# ===========================
def train():
    print("⏳ Loading cleaned dataset...")
    df = pd.read_csv(DATA_PATH)
    # Ensure strings
    df['url'] = df['url'].astype(str)
    
    print(f"📊 Dataset Size: {len(df)}")
    print("Example URLs:", df['url'].head().tolist())
    
    # Split
    X_train, X_val, y_train, y_val = train_test_split(df['url'].values, df['label'].values, test_size=0.15, random_state=42)
    
    # Init Tokenizer
    tokenizer = URLTokenizer()
    
    # Create DataLoaders
    train_ds = PhishingDataset(X_train, y_train, tokenizer)
    val_ds = PhishingDataset(X_val, y_val, tokenizer)
    
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0) # Windows workers=0 typically safer
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)
    
    # Init Model
    model = PhishNetCNN(tokenizer.vocab_size, EMBED_DIM, FILTERS, KERNEL_SIZE).to(DEVICE)
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.BCELoss() # Binary Cross Entropy
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2, verbose=True)
    
    best_acc = 0.0
    
    print("\n🔥 STARTING TRAINING ON RTX 4060 🔥")
    print(f"Total Epochs: {EPOCHS}")
    print("-" * 60)
    
    for epoch in range(EPOCHS):
        # --- TRAIN ---
        model.train()
        train_loss = 0
        correct = 0
        total = 0
        
        loop = tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS} [Train]", unit="batch")
        
        for inputs, labels in loop:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(inputs).squeeze()
            
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            predicted = (outputs > 0.5).float()
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            loop.set_postfix(loss=loss.item(), acc=correct/total)
            
        avg_train_loss = train_loss / len(train_loader)
        train_acc = correct / total
        
        # --- VALIDATION ---
        model.eval()
        val_correct = 0
        val_total = 0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                outputs = model(inputs).squeeze()
                
                predicted = (outputs > 0.5).float()
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        val_acc = val_correct / val_total
        f1 = f1_score(all_labels, all_preds)
        
        print(f"✅ Epoch {epoch+1}: Train Loss={avg_train_loss:.4f}, Train Acc={train_acc:.4f} | Val Acc={val_acc:.4f}, F1-Score={f1:.4f}")
        
        # Scheduler Step
        scheduler.step(val_acc)
        
        # --- SAVE BEST ---
        if val_acc > best_acc:
            best_acc = val_acc
            print(f"💾 Saving New Best Model (Acc: {best_acc:.4f})...")
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            
            # Save Metadata
            metadata = {
                'vocab': tokenizer.char2idx,
                'max_len': MAX_LEN,
                'embed_dim': EMBED_DIM,
                'filters': FILTERS,
                'kernel_size': KERNEL_SIZE,
                'accuracy': best_acc,
                'f1_score': f1
            }
            with open(METADATA_SAVE_PATH, 'w') as f:
                json.dump(metadata, f)
        
        print("-" * 60)

    print("\n🎉 Training Complete!")
    print(f"Best Accuracy: {best_acc:.4f}")
    print(f"Model Saved: {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train()
