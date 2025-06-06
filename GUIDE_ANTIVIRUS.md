# 🛡️ Guide de Résolution - Problèmes Antivirus

## **🚨 Pourquoi l'antivirus détecte l'exe comme un virus ?**

C'est **normal et fréquent** avec PyInstaller ! Voici pourquoi :

- PyInstaller "emballe" Python dans un exécutable
- Les antivirus détectent cela comme "comportement suspect"
- Votre exe est **100% légitime** mais l'antivirus ne le sait pas

## **✅ Solutions Immédiates**

### **1. Whitelist/Exception dans l'antivirus**
```
Windows Defender:
1. Ouvrir "Sécurité Windows"
2. "Protection contre virus et menaces"
3. "Gérer les paramètres" sous "Paramètres de protection..."
4. "Ajouter ou supprimer des exclusions"
5. Ajouter le dossier: C:\Users\maciu\Documents\death_must_pygame\dist\
```

### **2. Désactiver temporairement l'antivirus**
- Clic droit sur l'icône antivirus dans la barre des tâches
- "Désactiver la protection" pendant 10 minutes
- Tester l'exe
- **Réactiver immédiatement après**

### **3. Méthode PowerShell (Admin requis)**
```powershell
# Ouvrir PowerShell en tant qu'administrateur
Add-MpPreference -ExclusionPath "C:\Users\maciu\Documents\death_must_pygame\dist\"

# Vérifier l'exclusion
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

## **🔒 Solutions à Long Terme**

### **1. Signature de Code (Recommandé pour distribution)**
- Acheter un certificat de signature de code (~200€/an)
- Signer l'exe avec `signtool.exe`
- L'antivirus fera confiance aux exes signés

### **2. Scan VirusTotal**
- Aller sur https://www.virustotal.com
- Uploader votre `.exe`
- Partager le rapport (prouve que c'est sûr)

### **3. Build avec UPX (Compresse et change la signature)**
```bash
# Installer UPX
pip install upx-python

# Build avec compression UPX
python build_simple.py --upx
```

## **📋 Checklist de Vérification**

Avant de distribuer à d'autres :
- [ ] Scanner sur VirusTotal
- [ ] Tester sur une machine différente
- [ ] Inclure un README expliquant pourquoi l'antivirus alerte
- [ ] Fournir le code source pour la transparence

## **🎯 Message pour les Utilisateurs**

Quand vous distribuez le jeu, incluez ce message :

```
⚠️ ALERTE ANTIVIRUS NORMALE

Si votre antivirus signale ce jeu comme "menace" :

1. C'est un "faux positif" normal avec les jeux Python
2. Le jeu est 100% sûr (code source disponible)
3. Ajoutez une exception dans votre antivirus pour le dossier
4. Ou scannez sur VirusTotal.com pour vérifier

Le jeu ne contient aucun virus, malware ou code malveillant.
```

## **🔧 Alternative : Distribution Source**

Si les problèmes persistent, distribuez plutôt :
```
Prérequis: Python 3.8+ et pygame
Installation:
1. pip install pygame pillow numpy
2. Extraire le dossier du jeu
3. python launcher.py
```

Cela évite complètement les problèmes d'antivirus ! 