# Contribution Workflow:

## Set up your copy of the repo
The first step is to set up a copy of the Git repository of the project you want to contribute to. ***Taco-Price-Index*** follows a "fork, feature-branch, and PR" model for contributions.

On GitHub, "Fork" the ***Taco-Price-Index*** repository, to your own user account using the "Fork" button.

Clone your fork to your local machine and enter the directory:
```
git clone git@github.com:yourusername/Taco-Price-Index.git
cd Taco-Price-Index/
```
Add the "upstream" remote, which allows you to pull down changes from the main project easily:
```
git remote add upstream git@github.com:Alamo-Tech-Collective/Taco-Price-Index.git
```
You will now be ready to begin building or modifying the project.

Make changes to the repo
Once you have your repository, you can get to work.

Rebase your local branches against upstream main so you are working off the latest changes:
```
git fetch --all
git rebase upstream/main
```
Create a local feature branch off of main to make your changes:
```
git checkout -b my-feature main
```
Make your changes and commits to this local feature branch.

Perform the following commands on your local feature branch once you're done your work, to ensure you have no conflicts with other work done since you stated.
```
git fetch --all
git rebase upstream/main
```
Push up your local feature branch to your GitHub fork:
```
git push --set-upstream origin my-feature
```
On GitHub, create a new PR against the upstream main branch following the advice below.

Once your PR is merged, ensure you keep your local branches up-to-date:
```
git fetch --all
git checkout main
git rebase upstream/main
git push -u origin main
```
Delete your local feature branch if you no longer need it:
```
git branch -d my-feature
```
## Pull Request Guidelines
When submitting a new PR, please ensure you do the following things. If you haven't, please read [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/) as it is a great resource for writing useful commit messages.

Write a good title that quickly describes what has been changed.

Why the changes are being made. Reference specific issues with keywords (fixes, closes, addresses, etc.) if at all possible.

# Teams Overview
There are a total of four teams.
- **Lucha De Latency** (backend)
- **Taco Picasso** (frontend) 
- **Guac-a-Code** (data ingestion) ***NOTE: Basically complete***
- **Taco Titans** (ui/ux/content)

# Communication Channels
The following discord channels available for **Taco-Price-Index**:
- **taco-price-chat** - General chat and updates related to the app.
- **lucha-de-latency** - Chat for the backend team.
- **taco-titans** - Chat for the ui/ux/content team.
- **guac-a-code** - Chat for the data ingestion team.
- **taco-picasso** - Chat for the frontend team.