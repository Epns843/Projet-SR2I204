# Projet SR2I204 : Authentification par TOTP 

## Roadmap

- Documentation sur l'algorithme
- Implémentation:
    [+] Génération d'un TOTP : 
        [+] Génération d'une clé secrète pour la fonction de hashage 
        [+] Utilisation de la clé pour obtenir le hash du timestamp par HMAC-SHA512
        [+] Troncage du hash pour obtenir un TOTP court 
        [+] Transformation du hash en un TOTP de 6 chiffres 
    [-] Création d'un processus d'authentification : 
        [+] Première connexion avec login et passwd  
        [+] Stockage sécurisé de login, passwd et clé unique pour chaque utilisateur 
        [+] Transmission grâce à un scan de QR code  
        [+] Connexion suivante possible avec passwd ou TOTP généré du côté utilisateur 
        [+] Modélisation d'un service end-user générant les TOTP pour un utilisateur à partir de sa clé 
    [-] Création d'un service nécessitant un TOTP : 
        [-] Création d'une interface web permettant la requête d'un TOTP 
        [-] Interfaçage de l'interface web avec le générateur de TOTP 
        [-] Déverouillage de contenu si TOTP soumis correct 
    [-] Échange sécurisé du TOTP -> assuré par connexion chiffrée au service web  


- Premier rendu: implémentation fonctionnelle répondant aux contraintes de confidentialité
- Documentation sur les attaques
- *Pentesting* de l'implémentation
- Corriger les failles éventuelles mises à jour 