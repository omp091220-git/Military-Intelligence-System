# AI Military Intelligence Dashboard — Setup Guide
(Might help)

```
your_project/
├── app.py
├── train_attack_model.py
├── requirements.txt
├── data/
│   └── globalterrorism.csv      <-- yahan apni real CSV daalo
├── models/                       <-- train_attack_model.py chalane ke baad auto ban jayega
├── utils/
│   ├── theme.py
│   └── data_loader.py
├── pages/
│   ├── 1_🏠_Home.py
│   ├── 2_🌍_Global_Threat_Map.py
│   ├── 3_🌎_Country_Analysis.py
│   ├── 4_🤖_Attack_Prediction.py
│   ├── 5_🚨_Threat_Level.py
│   ├── 6_📈_Forecasting.py
│   ├── 7_🧠_AI_Intelligence.py
│   ├── 8_📊_Data_Explorer.py
│   ├── 9_⚙_Setting.py
│   └── 10_🧠_Strategic_Copilot.py
└── .streamlit/
    └── secrets.toml               <-- optional, sirf Copilot ke liye
```

## Steps (seedhe order mein karo)

### 1. Folder banao
Ek naya folder banao (jo bhi naam chahiye), aur usme upar wali structure ke hisaab se saari files rakh do — jo maine bheji hain.

### 2. Apna dataset daalo
Apni Global Terrorism Database wali CSV file ka naam `globalterrorism.csv` rakho, aur `data/` folder ke andar daal do.

### 3. Python packages install karo
Terminal/CMD mein apne project folder ke andar jaake:
```
pip install -r requirements.txt
```

### 4. Attack Prediction model train karo (sirf ek baar karna hai)
```
python train_attack_model.py
```
Ye `models/` folder banayega aur 3 `.pkl` files save karega. Isse sirf ek dafa chalana hai — jab tak dataset change nahi karte, dobara chalane ki zaroorat nahi.

### 5. (Optional) Strategic Copilot ke liye API key
Agar chat-wala Copilot page use karna hai, `.streamlit/secrets.toml` file banao aur likho:
```
ANTHROPIC_API_KEY = "yaha apni key daalo"
```
Agar abhi nahi karna, koi baat nahi — baaki sab pages bina iske chalenge.

### 6. App run karo
```
streamlit run app.py
```
Browser mein khud khul jayega. Sidebar se koi bhi page select karo.

### 7. Check karo
- Home pe KPIs aur trend dikhna chahiye
- Global Threat Map pe 3D globe rotate karke dekho
- Country Analysis mein koi country select karo — sunburst + radar chart dikhega
- Threat Level aur Attack Prediction mein sliders/dropdown change karo — prediction turant update hogi
- AI Intelligence mein anomaly wali table dikhegi
- Agar koi error aaye, error ka poora message copy karke yahan bhej do — turant fix kar dunga
