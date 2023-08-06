.. -*- coding: utf-8 -*-

Créer un nouveau projet
-----------------------
Tout développeur est encouragé à créer un projet. La bonne pratique est de considéré chaque paquet Debian livré comme un projet potentiel. Notez cependant que le dépôt du code dans mercurial n'est pas créer à la volée mais nécessite certainement une demande auprès de votre administrateur.

Sur la page principale, un lien vous est proposé, seul le nom est obligatoire. Il est ensuite visible depuis cette même page.

Si le projet existe déjà dans votre dépôt de source et qu'il est accessible par HTTP, il peut être intéressant de remplir le champ `url du système de gestion de sources`. Ceci vous permettra de naviguer dans le code source du projet directement à partir de la forge.

Ajouter un ticket
-----------------
Un ticket constitue la base de la forge. De part les tickets, nous organisons les priorités, les versions. En leur attribuant un coût (en jour.homme le plus souvent), il est possible de prévoir la charge de travail à effectuer. Un ticket peut ensuite être ajouté à une version, ce qui permet de rapidement avoir une estimation globale de la prochaine livraison. Deux types de tickets existent actuellement:

- les histoires utilisateurs permettent de détecter les besoins des utilisateurs et vise donc à enrichir le logiciel de nouvelles fonctionnalités
- les anomalies concernent des versions de projets existantes et permettent le recencement des dysfonctionnements ou les régressions observées

Un ticket se doit d'être concis, posséder une seule problématique et ne doit pas contenir de textes orientés techniques. Il vaut mieux dans ce cas-là ajouter ce type d'informations sous forme de commentaires. En effet, l'usage montre que la réalisation différe très souvent de la première proposition technique.

Pour ajouter un ticket, vous devez, à partir d'une page de projet, cliquer sur le menu déroulant `ajouter` dans la colonne des actions en haut à gauche de la page de projet. L'entrée `ticket` est alors visible. Après avoir créer un ticket, il est maintenant possible de le modifier et d'ajouter des relations.

Exemple: à partir de la page action `modifier`, vous trouverez en bas de page au dessus du bouton `valider` une boîte déroulante qui permet d'ajouter des relations. Si votre ticket a un lien quelconque avec un autre objet, vous pouvez choisir la relation **voir aussi**. Une liste déroulante vous sera alors proposée pour "tisser" la nouvelle relation. Vous pouvez faire cela autant de fois que vous souhaitez. Plusieurs relations vont sont proposées. Les plus utilisées sont: **see also**, **tagged by**, **depends on**. 

Cycle de vie d'un ticket
~~~~~~~~~~~~~~~~~~~~~~~~
Les tickets peuventt avoir plusieurs états qui sont atteignables par les transitions disponibles. Ainsi chaque état n'est pas forcément atteignable directement. Pour se familiariser avec les états et transitions par défaut, vous pouvez vous référer à sa page de workflow_.

.. _`workflow`: eetype/Ticket/?vid=workflow

Ajouter une fiche de documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Les fiches de documentation sont utiles à un projet lorsque celles-ci sont fréquemment consultées. Elles apparaîtront en bas de la page de projet.


Ajouter une image
~~~~~~~~~~~~~~~~~
Il est possible que la création d'entité d'image ne soit pas immédiatement disponible. Il est alors possible de passer par l'`url suivante`__ pour l'ajout d'une image.

__ add/Image

Pour lister facilement l'ensemble des objets de type Image dans la forge, vous pouvez visiter l'`url suivante`__.

__ image

Ajouter une version
-------------------
Une version représente un certain état de l'avancement du projet. Elles vous permettent de prévoir les prochaines échéances. Il est fortement conseillé de prévoir plusieurs versions. Si jamais la livraison de cette fonctionnalité n'est plus possible à la date prévue de livraison de la prochaine version, il est alors possible de déplacer ce ticket dans une version ultérieure ce qui permettra de ne pas bloquer la sortie.

Les versions possèdent leurs propres workflow__. Il est important de tenir à jour ces informations car ce sont elles qui permettent la planification du projet.

__  eetype/Version/?vid=workflow


