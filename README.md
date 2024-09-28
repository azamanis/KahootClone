# KahootClone

Authors: Pablo Cuesta Sierra and Álvaro Zamanillo Sáez.

---

# Django project deployed at https://kahootcloneczwithrestapi.onrender.com

This project is located in the directory ./kahootclone_project/

The user guide is located in ./user_guide.pdf

# Vue project deployed at https://kahootcloneczclient.onrender.com

This project is located in the directory ./vueClient/

# Note on additional functionalities

In addition to the functionalities requested in the statement, we have added the following:

- The creator of a game can remove a participant during the waiting screen by clicking on their alias.

- Once all participants have answered a question, the answer is automatically displayed (without having to wait for the countdown to end).

---

# For execution on laboratory computers

## Start PostgreSQL and "reset" the database, run the server

```bash
cd kahootclone_project
sudo systemctl restart postgresql && dropdb -U alumnodb psi && createdb -U alumnodb psi && make update_models
make runserver
```

## Install the vueClient project and launch it

```bash
cd vueClient
npm install
npm run dev
```
