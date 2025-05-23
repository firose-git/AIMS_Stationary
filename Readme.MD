# 📚 AcadStationary Portal – AIMS Stationery Management System

AcadStationary is a powerful web-based Stationery Management System built using **Django** and **MongoDB** (via **Djongo**). Tailored for academic institutions, it streamlines stationery requests, inventory tracking, and administrative oversight with a modern and responsive interface.

---

## 🚀 Features

- 🗂️ Manage multiple categories of stationery items  
- 📦 Real-time inventory tracking and department-specific orders  
- 👥 Secure user authentication (Register/Login)  
- 🛒 Department cart with seamless checkout system  
- 🧾 Admin dashboard for order and inventory management  
- 📊 Interactive UI with custom dashboards  
- 📬 Contact form for inquiries and support  
- 🎨 Fully responsive and modern UI using Bootstrap and custom CSS  

---

## 🛠️ Tech Stack

- **Backend**: Django  
- **Database**: MongoDB (via Djongo v1.3.7)  
- **Frontend**: HTML5, CSS3, Bootstrap, JavaScript  

---

## ⚙️ Setup & Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/firose-git/AIMS_Stationary.git
    cd Aims_pro
    ```

2. **Create a Virtual Environment**

    ```bash
    python -m venv venv
    venv\Scripts\activate  --> On Windows: 
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run Migrations**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Start the Server**

    ```bash
    python manage.py runserver
    ```

6. **Access the App**

    Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🖼️ Template Overview

| Template File     | Description                              |
|-------------------|------------------------------------------|
| `base.html`       | Shared layout with header, navbar, footer |
| `index.html`      | Main dashboard & homepage                 |
| `about.html`      | About the system                         |
| `contact.html`    | Inquiry contact form                     |
| `category.html`   | List of stationery categories            |
| `myaccount.html`  | Login & registration page                |

---

## 🎨 Static Files

| File         | Purpose                             |
|--------------|-------------------------------------|
| `styles.css` | Custom styling & layout             |
| `scripts.js` | JavaScript interactivity and logic  |

---

## 🔐 Authentication & Roles

- **Admin Users**: Full access to admin dashboard, order management, and inventory controls  
- **Department Users**: Place and track stationery requests only  

---

## 🧠 Backend Overview

- `views.py` – Handles user logic and page rendering  
- `urls.py` – URL routing and view mapping  
- `models.py` – MongoDB-compatible models for users, products, orders  
- `settings.py` – Project configuration and environment setup  

---

## 🤝 Contributors

- 👨‍💻 **Developed by**: Mohamed Firose  
- 🚀 **Deployed by**: Mohammed Shoaib  
- 📊 **Report Created by**: Kiran Raj  
- 🎓 **Institution**: AIMS Institutes – MCA, School of IT Department  

---

## 🌐 Live Project

🔗 [Visit Live Site](https://aims-stationary.onrender.com/)

---

## 🤝 Contribution Guide

We welcome contributions! Here's how you can help:

1. Fork the repository  
2. Create a new branch: `git checkout -b feature-name`  
3. Commit changes: `git commit -m 'Add new feature'`  
4. Push your branch: `git push origin feature-name`  
5. Create a Pull Request 🎉  

---

## 💬 Contact

For suggestions or queries, feel free to open an issue or contact the maintainer via the repository.

---

## 🎉 Happy Coding!

Bring innovation to campus management — one stationery item at a time!

---

                #Aims Institutes

