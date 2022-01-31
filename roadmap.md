# Projet SR2I204 : Authentification par TOTP 

## Roadmap

- Documentation sur l'algorithme
- Implémentation:
  [+] Génération d'un TOTP : 
      [+] Génération d'une clé secrète pour la fonction de hashage 
      [+] Utilisation de la clé pour obtenir le hash du timestamp par HMAC-SHA512
      [+] Troncage du hash pour obtenir un TOTP court 
  [-] Création d'un processus générant des TOTP à la demande, avec changement de clé à intervalles réguliers 
  [-] Échange sécurisé du TOTP
  [-] Création d'un service nécessitant un TOTP


  
- Premier rendu: implémentation fonctionnelle répondant aux contraintes de confidentialité
- Documentation sur les attaques
- *Pentesting* de l'implémentation
- Corriger les failles éventuelles mises à jour 