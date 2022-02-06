# Projet SR2I-204 : Authentification par TOTP

## Utilisation 

On trouvera dans `requirements.txt` les packages python nécessaires pour faire fonctionner le projet : 

    $ pip install -r requirements.txt 


Le service Web se lance depuis le répertoire src/server par la commande : 

    $ python server_flask.py 

Le serveur est ensuite accessible à l'URL https://127.0.0.1:5000/. Utilisant un certificat auto-signé non reconnu par le navigateur, celui-ci avertira d'un potentiel risque lors de la connexion au service, qu'il faudra accepter. 
Pour son fonctionnement, le serveur demande à son lancement un mot de passe maître, utilisé pour décrypter les clés privées des utilisateurs. Le mot de passe configuré est **master**, et est vérifié par comparaison à son mac obtenu par la fonction de hachage `argon2`. 


Le script `totp.py` présent dans src/ permet de simuler le fonctionnement d'un générateur de TOTP du côté end-user. Il se lance par la commande suivante : 

    $ python totp.py 

L'utilisateur aura alors à entrer sa clé secrète qui lui est donnée lors de la connexion au serveur. Un TOTP sera ensuite généré à chaque fois que l'utilisateur appuiera sur la touche `entrée` . 
Ce script simule le fonctionnement d'une application du côté end-user, qui stockerait la clé privée de l'utilisateur, et lui permettrait de générer un TOTP à la demande. 
Le TOTP généré est valable pour une durée de 30 sec, et permet de se connecter au service. 



## Fonctionnement du service 

### Côté utilisateur 

#### Première connexion 

Lors de sa première connexion au serveur, l'utilisateur peut cliquer sur le lien `Create Account` pour être redirigé vers la page de création de compte. Il devra alors fournir un nom d'utilisateur, ainsi qu'un mot de passe d'au moins 10 caractères, contenant au moins un minuscule, une majuscule, un chiffre, et un caractère spécial parmi [@$_?!], et confirmer ce mot de passe. 

Si le nom d'utilisateur est disponible, un compte sera créé, et l'utilisateur sera renvoyé vers sa page personnelle. Il y trouvera sa clé privée de chiffrement qui lui permettra de générer des TOTP pour les connexions suivantes, ainsi qu'un QR code qu'il pourra scanner avec Google Authenticator. 


#### Connexion à un compte existant 

Pour se connecter à un compte existant, l'utilisateur peut fournir avec son login, soit son mot de passe, soit un TOTP valide pour la période courante. 

Sont valides pour la période courante, le TOTP généré dans la période de 30 sec au moment de la demande de connexion, ainsi que celui généré dans les 30 sec précédant la période de connexion, à condition qu'ils n'aient pas déjà été utilisés. 

Au bout de trois tentatives infructueuses de connexion, l'utilisateur devra attendre cinq minutes avant que sa prochaine tentative de connexion soit traitée par le serveur. 


### Côté serveur

#### Implémentation de l'authentification par TOTP

L'implémentation du générateur de TOTP suit la description faite dans https://datatracker.ietf.org/doc/html/rfc6238, et est compatible avec celle d'application certifiée, comme Google Authenticator pour laquelle les QR codes sont générés. Le service Web simuler s'efforce de respecter toutes les mesures de sécurités décrites dans RFC 6238. 

Les clés privées sont générées par le fonction `os.urandom()`, considérée comme un générateur pseudo-aléatoire cryptographiquement sûr. 

Les clés priées de 32-bytes de longueur sont donc plus longues que la sorties de HMAC-SHA-1. 

Les communications ont lieu par l'intermédiaire du protocole HTTPS (RFC 5246). 

L'identifiant, le hash du mot de passe, ainsi que la clé privée chiffrée sont stockés dans la fichier `logins.txt`, et lu depuis ce fichier à chaque connexion ou à chaque fois que nécessaire. De cette façon, on minimise la RAM utilisée pour stockée les utilisateurs, et on minimise le risque de DoS par inondation du serveur de nouveaux utilisateurs (bien que ce risque est en pratique primairement géré par le fire-wall). De plus, les identifiants d'un utilisateur ne se trouve donc que temporairement dans la RAM. 
Le hash du mot de passe est obtenu en utilisant la fonction `argon2` (RFC 9106). La clé privée est chiffrée par AES. 

La clé privée de chaque utilisateur est déchiffrer uniquement lors de la création de son QR code, ou lors de la vérification du TOTP s'il est fourni, limitant ainsi son exposition dans la RAM. 

La période de validité d'un TOTP est de 30 sec, et l'implémentation accepte également le TOTP de la période précédente. La fenêtre de vulnérabilité est donc d'une longueur maximale de 1 minute. Or, l'utilisateur ne pouvant faire que 3 essais infructueux de connexion toutes les 5 minutes, cela supprime la risque d'attaque *brut force*, ce qui d'après la RFC 6238, section 5.1, est la meilleure attaque si l'implémentation est respectée. 

Le serveur garde également en mémoire pour chaque utilisateur les 3 derniers TOTP valides qu'il a utilisé pour se connecter. Si le TOTP fournit pour une nouvelle connexion par cet utilisateur se retrouve dans cette liste, l'accès n'est pas accordé. Cette mémoire des TOTP déjà utilisés permet d'assurer le caractère "à usage unique" de l'identification par TOTP. 


#### Contre-mesures contre l'usurpation d'identité 

Seul les pages "/", "/new_user" et "/jail" sont accessibles à tous. 

Lorsqu'un utilisateur se connecte, il est redirigé vers la page "/user/<user>". Lors de la redirection, il reçoit un cookie de connexion qui lui est propre, qu'il va également utilisé pour sa requête à "/user/<user>". Si l'utilisateur ne fournit pas de cookie, ou si le cookie qui est fourni lors de la requête à cette page n'est pas valide, l'utilisateur est redirigé vers "/jail". 

De même, le même cookie de session est nécessaire pour accéder à "/static/qrcode/<image>", restreignant également l'accès à cette page pour une requête ne disposant pas d'un cookie valide. 

Un cookie n'est valide tant que l'utilisateur est connecté, et pour une durée d'au plus 14 minutes (durée configurable dans la fonction `get_session_id()` de auth.py : 420 -> 7 minutes x 2 périodes = 14 minutes). Le cookie qu'un utilisateur expire donc automatiquement au plus tard après 14 minutes, et celui-ci devra se reconnecter s'il souhaite accéder de nouveau au service. Lorsque l'utilisateur clique sur le bouton *Disconnect*, son cookie est invalidé, et le fichier de son QR code est automatiquement supprimé. 

Le cookie étant dérivé de la clé privée de chaque utilisateur, même un utilisateur connecté ne peut pas accéder aux pages propres à un autre utilisateur, et ne peut inférer d'information sur la clé ou le cookie d'un autre utilisateur en observant son cookie de part l'utilisation d'un générateur pseudo-aléatoire cryptographiquement sûr. 

Afin d'accéder à la clé d'un autre utilisateur, un attaquant devra donc casser le chiffrement SSL/TLS en moins de 14 minutes à compter du moment où la cible se connecte, et avant que celle-ci se déconnecte. 

Même si l'attaquant parvient à récupérer un ancien cookie de connexion en cassant le chiffrement SSL/TLS, il ne pourra pas en inférer d'information sur la clé de l'utilisateur qui est utilisée pour générer le cookie. En effet, ce dernier est constitué des 24 premiers octets du résultat de HMAC-SHA-512 avec pour message la période temporelle au moment de la connexion, période faisant 420 secondes, et pour clé la clé privée de l'utilisateur. D'après les RFC 6238 et 4226, cette information ne donnerait pas d'avantage par rapport à un attaquant essayant de trouver un cookie par une attaque *brut force*. D'autant plus que l'attaquant ne dispose pas de l'information sur le moment de création du cookie, c'est-à-dire sur le message passé à HMAC-SHA-512. 

Enfin, les données sur un utilisateur ne seraient disponibles que lorsque celui-ci serait connecté, ce que l'attaquant n'a aucun moyen de déterminer. 

En outre, une attaque *brut force* essayant séquentiellement tous les mots de passe ou TOTP pour un certain utilisateur prendrait un temps trop important pour être pertinente, du fait de la présence d'un délai d'attente après 3 tentatives de connexions infructueuses. Cette contre-mesure pourrait être renforcée en augmentant de manière exponentielle le temps avant de pouvoir faire une nouvelle tentative de connexion après 3 échecs, cependant cette contre-mesure pourrait alors elle-même être exploitée pour empêcher un utilisateur de se connecter, en faisant intentionnellement des tentatives infructueuses. 

La seule attaque qui aurait donc une chance de fonctionner serait une attaque qui ferait continuellement une requête pour "/user/<user>" ou "/static/qrcode/<image>", en changeant à chaque fois le cookie de connexion, espérant ainsi trouver le bon cookie alors que l'utilisateur est connecté. Un cookie étant la chaine de caractère obtenu par application de la fonction `hex()` sur les 24 premiers octets du résultat de HMAC-SHA-512, cette chaine fait donc 48 caractères de long, chacun étant un chiffre dans la base hexadécimale (de 0 à f donc). Une telle attaque nécessiterait donc de tester 16^48 combinaisons en 14 minutes pour garantir sa réussite, ce qui est peu réaliste. De plus, cette attaque serait préalablement détectée par un pare-feu derrière lequel se trouverait le serveur, ce qui rend son succès d'autant moins réaliste. 


#### Sandboxing

Seules les requêtes pour "/", "/new_user", "/user/<user>", "/static/css/main.css", "/static/qrcode/<image>" et "/jail" sont traitées, il n'est donc pas possible d'accéder à d'autres fichiers. 

De plus, la seule ouverture de fichier se fait lors de la requête pour "/static/qrcode/<image>", et par l'intermédiaire de la fonction `send_from_directory()`, qui assure le *sandboxing*. 

Enfin, un nom d'utilisateur ne peut contenir les caractères ".", " ", ";" ou "/" par exemple, et `<user>` dans "/user/<user>" ou `<image>` dans "/static/qrcode/<image>" ne peut contenir "/". 
