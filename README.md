<p align="center">
<a href="https://duckietown.com"><img src="./assets/images/dtlogo.png" alt="Duckietown Logo" width="50%"></a>
</p>

# **Labo 2: Cinématique et odométrie**

# Introduction

Dans ce laboratoire, vous apprendrez comment nous pouvons passer d'un cadre de représentation à un autre, comment nous pouvons exploiter cela pour construire un modèle de la façon dont le robot se déplace (cinématique), et comment cela peut être utilisé pour créer un modèle de la façon dont le robot se déplace au fil du temps en fonction des données provenant des encodeurs (estimation de l'odométrie).


# Instructions

**NOTE:** All commands below are intended to be executed from the root directory of this exercise (i.e., the directory containing this `README`).


## 1. Make sure your exercise is up-to-date

Update your exercise definition and instructions,

    git pull upstream ente

**NOTE:** to pull from upstream, you need to have completed the instructions in the [general procedure for running learning experiences in the Duckietown manual](https://docs.duckietown.com/ente/duckietown-manual/60-learning-experiences/lx-general-procedure.html) to *fork* this repository.


##  Mais d'abord...

Assurez-vous que votre système est à jour.

- 💻 Veillez toujours à ce que votre  Duckietown Shell soit mise à jour vers la dernière version: `pipx upgrade duckietown-shell`

- 💻 Mettre à jour les commandes du shell: `dts update`

- 💻 Assurez-vous que toutes les images Docker présentes sur votre ordinateur sont à jour: `dts desktop update`

- 🚙 Assurez-vous que toutes les images Docker présentes sur votre ordinateur sont à jour: `dts duckiebot update ROBOTNAME`
(where `ROBOTNAME` is the name of your Duckiebot - real or virtual.)


# Comment réaliser cet exercice de laboratoire ?

## Lancez l'éditeur de code.

Ouvrez l'éditeur de code (VSCode) en exécutant la commande suivante:

```
dts code editor
```

Attendez qu'une URL s'affiche dans le terminal, puis cliquez dessus ou copiez-la et collez-la dans la barre d'adresse de votre navigateur pour accéder à l'éditeur de code. Le premier élément que vous verrez dans l'éditeur de code est ce même document. 

**Vous pouvez poursuivre votre travail à partir de là**


## Les notebooks "Jupyter"

**REMARQUE** : Vous devez lire ce message depuis l'éditeur de code de votre navigateur.

Dans l'éditeur de code, utilisez la barre latérale de navigation située à gauche pour accéder au
dossier `notebooks` et ouvrir le premier notebook.

Suivez les instructions du notebook et parcourez les notebooks dans l'ordre.

Une fois que vous avez terminé toutes les tâches des carnets de notes, vous pouvez suivre les instructions suivantes pour tester votre code.

## Exécution de votre code

### Tester avec le Duckiematrix (optionnel)

Il peut être utile de tester votre code dans un environnement de simulation avant de l'essayer sur le robot réel. Pour cela, nous avons le Duckiematrix.

Pour tester votre code dans Duckiematrix, vous aurez besoin d'un robot virtuel. Vous pouvez en créer un avec la commande suivante:

```
dts duckiebot virtual create [VBOT]
```

où `[VBOT]` peut être n'importe quoi (mais n'oubliez pas ce nom pour la suite).

Vous pouvez ensuite démarrer votre robot virtuel avec la commande:

```
dts duckiebot virtual start [VBOT]
```

Vous devriez le voir avec le statut « Booting » (démarrage) et enfin « Ready » (prêt) si vous consultez la commande `dts fleet discover` :

```
     | Hardware |   Type    | Model |  Status  | Hostname 
---  | -------- | --------- | ----- | -------- | ---------
[VBOT] |  virtual | duckiebot | DB21J |  Ready   | [VBOT].local
```

Maintenant que votre robot virtuel est prêt, vous pouvez démarrer Duckiematrix. Depuis ce répertoire d'exercices, exécutez la commande suivante :

```
dts code start_matrix
```

Vous devriez voir le simulateur Duckiematrix, basé sur Unity, démarrer. L'écran de démarrage ressemblera à ceci :

![duckiematrix_start](assets/duckiematrix_start.png)

À partir d'ici, vous pouvez cliquer n'importe où dans la fenêtre et appuyer sur la touche [ENTRÉE] pour l'activer. Vous pouvez ensuite déplacer le petit canard vers le Duckiebot à l'aide des touches « w », « a », « s » et « d », ou modifier l'angle de la caméra pour observer le Duckiebot avec la souris. Vous pouvez également passer à une vue de dessus en appuyant sur la touche « v », ce qui vous donnera une vue similaire à celle-ci :

![duckiematrix_overhead](assets/duckiematrix_overhead.png)


### "Build" votre code

Vous pouvez build le code avec

```
dts code build -R ROBOTNAME
```

où ROBOTNAME peut être un robot réel ou virtuel.

### Tester le code

Vous pouvez ensuite exécuter votre code avec

```
dts code workbench -R ROBOTNAME [-m]
```

où ROBOTNAME peut être un robot réel ou virtuel, mais s'il s'agit d'un robot virtuel, vous devez inclure l'option `-m` pour indiquer que vous souhaitez le tester dans Duckiematrix.



Dans un autre terminal (sur l'ordinateur), vous pouvez lancer le visualiseur `noVNC` pour cet exercice, qui peut être utile pour envoyer des commandes au robot et visualiser l'odométrie que vous calculez dans la fenêtre RViZ.

```
dts code vnc -R [ROBOT_NAME]
```

où `[ROBOT_NAME]` peut être le robot réel ou virtuel (utilisez celui avec lequel vous avez exécuté la commande `dts code workbench`).

Vous pouvez maintenant passer au [premier cahier](./notebooks/01-Representations/pose_representation.ipynb).


## Crédits

Cet exercice a bénéficié de contributions importantes de
[Rey Reza Wiyatno](https://rrwiyatn.github.io/). 
