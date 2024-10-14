# Site E-commerce de Billetterie - JO 2024

## Description
Ce projet est un site e-commerce interne permettant la vente de billets pour les Jeux Olympiques de 2024. Les utilisateurs peuvent choisir parmi trois formules de billets, tandis que l'administrateur a la possibilité de gérer les sports, les événements et les formules via une interface d'administration. Le site permet également à l'administrateur de consulter les ventes effectuées.

## Fonctionnalités
- **Vente de billets** : Les utilisateurs peuvent acheter des billets pour différents événements des JO 2024, en sélectionnant parmi trois formules.
- **Gestion des sports et événements** : L'administrateur peut ajouter de nouveaux sports et événements via le panneau d'administration.
- **Gestion des formules** : Trois formules de billets sont proposées aux utilisateurs, et l'administrateur peut en ajouter d'autres.
- **Consultation des ventes** : L'administrateur peut consulter les ventes réalisées par formule.


## Utilisation
### Installation
Ce projet est conçu pour une utilisation en interne, sans configuration supplémentaire requise. Cependant, voici les étapes pour le démarrer en local si nécessaire :

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/nom-du-repo
   cd nom-du-repo
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Démarrer le serveur Django :
   ```bash
   python manage.py runserver
   ```

4. Accéder à l'administration :
- **URL** : http://localhost:8000/admin
- **Fonctionnalié**: L'administrateur peut se connecter et gérer les sports, événements, formules, et consulter les ventes.

## Contribuer
Si vous souhaitez apporter des modifications ou des améliorations au projet, veuillez suivre ces étapes :

1. Créez une branche pour vos modifications :
   ```bash
    git checkout -b nom-de-votre-branche
   ```

2. Faites vos modifications, puis effectuez un commit : 
   ```bash
   git commit -m "Description de vos changements"
   ```

3. Poussez vos modifications vers GitHub :
    ```bash
   git push origin nom-de-votre-branche
   ```

4. Soumettez une pull request pour révision.

## Technologies

### Langages & Frameworks
- **Python** : Langage de programmation utilisé pour le développement du projet. [Documentation officielle](https://docs.python.org/3/)
- **Django** : Framework web Python utilisé pour structurer l'application. [Documentation officielle](https://docs.djangoproject.com/en/stable/)
- **Bootstrap** : Framework CSS utilisé pour le design et la réactivité de l'interface utilisateur. [Documentation officielle](https://getbootstrap.com/)

### Outils

#### CI (Intégration Continue)
- **GitHub Actions** : Utilisé pour l'intégration continue et le déploiement automatisé du projet. Il permet d'exécuter des tests et des actions sur chaque push et pull request. [Documentation GitHub Actions](https://docs.github.com/en/actions)
- **Pytest** : Utilisé pour exécuter des tests automatisés sur le code Python. [Documentation officielle](https://docs.pytest.org/en/stable/)

#### Déploiement
- **Heroku** : Plateforme utilisée pour le déploiement du projet. [Documentation officielle](https://devcenter.heroku.com/)
- **Amazon S3** : Utilisé pour le stockage des fichiers statiques et médias. [Documentation officielle](https://aws.amazon.com/s3/)
  
##### Variables et Comptes
- **Heroku Variables** : Variables d'environnement pour la configuration du projet (base de données, clé secrète, etc.).
- **Amazon S3 Variables** : Configuration des clés d'accès pour AWS.

## Gestion des versions
Nous utilisons Git pour la gestion des versions. Pour voir les versions disponibles, consultez les [tags du dépôt](https://github.com/votre-utilisateur/nom-du-repo/tags).

- **Version actuelle** : 1.0.0

## Auteur

- **Rousselot Elsa** - Développeuse principale du projet.
- **Contact** : [Linkedin](https://www.linkedin.com/in/rousselot-elsa-er91112125/)
  
N'hésitez pas à me contacter si vous avez des questions ou des suggestions concernant ce projet.















