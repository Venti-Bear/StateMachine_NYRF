# StateMachine project

# Noms

Fabien Juteau Desjardins
Yoan Poulin Truchon
Raphaël Lavoie
Nicolas Drolet

# Pourcentage fait

110% on a fait un bonus

# Infrastructure

La validation de l'instanciation du robot se fait en vérifiant si, après avoir appelé son constructeur, il est null. De plus si une
exception est lancée l'instanciation échoue.

La télécommande est un objet provenant de la classe Controller contenu dans la classe Robot. Elle contient un buffer qui est mis à jour à chaque tick si un nouveau caractère est appuyé sur la télécommande. Elle comporte une bascule pour empêcher le bombardement de caractère lorsqu'un bouton est appuyé.
Pour ce qui en est des commandes demandées dans le mandat, nous avons opté pour une approche légèrement différente.
Lorsque nous sommes dans HOME, on peut appuyer sur plusieurs chiffres ou caractères spéciaux en file, et en appuyant sur "ok", la suite de caractères est lue, et si une tâche est reliée à cette suite de caractères, un état est lancé dans le Robot et le buffer est vidé. S’il n'y a aucune tâche reliée, la transition pointe sur l'état HOME et le buffer est vidé. Pour transitionner vers SHUT_DOWN, on doit appuyer sur "#" et "ok".

Pour le télémètre et le servomoteur, nous sommes capables de recueillir les informations de distances du télémètre à l'aide d'une classe contenue à l'intérieur du Robot. Le servomoteur est contenu dans la classe du télémètre. Nous avons une mécanique qui restreint les angles sécuritairement. Un mécanisme de biais est également présent pour réaligner l'angle de pointe du télémètre. Bien que ce mécanisme soit fonctionnel, nous ne l'avons pas calibré, il n'est donc pas utilisé.

Pour les moteurs, nous sommes capables de contrôler les roues indépendamment l'une de l'autre. Sans nécessairement en faire avancer une et reculer l'autre pour tourner sur soi-même, nous sommes en mesure de faire pivoter le robot sur un axe centré sur une roue ou l'autre roue.
On garde également en mémoire la direction actuelle du déplacement du robot.

Pour les yeux EyeBlinkers, nous gérons les couleurs solides seulement. Il n'y a donc pas de gradient.

Pour la structure du logiciel, nous avons fait une distinction claire
entre la librairie et le logiciel. La librairie vit dans le dossier Lib.

Notre Controller, ainsi que notre EyeBlinker
ont besoin d'être traqués. Cela est fait par l'appel de la fonction track dans la class robot. Cette fonction
est appelée à toutes les itérations de la main loop.

Les différentes tâches sont des sous-machines d'état, c'est à dire qui sont des machines d'état dans une machine d'état
