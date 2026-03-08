# AI Grading Service - Virtual Classroom

This repository contains the **AI Grading Microservice** for the AI-Powered Virtual Classroom project. 

While the Core LMS Service handles the deterministic academic workflows (managing classes, students, and assignment deadlines), this service acts as an **Asynchronous AI Worker**. Its sole responsibility is to evaluate essay submissions using Generative AI and return actionable feedback.

**[Click here to view the Main Repository] (https://github.com/tienthuan19/project-virtual-classroom-microservices.git)**

---

## ⚙️ How It Works

To ensure the main application remains fast and responsive, this service operates entirely asynchronously via a Message Broker:

1. **Consume:** Listens to a specific RabbitMQ queue for new essay grading requests published by the Core LMS Service.
2. **Process:** Constructs a highly specific prompt containing the teacher's rubric, model answer, and the student's submission. It then calls the **Google Gemini API** to evaluate the response.
3. **Publish:** Parses the AI's response (suggested score + detailed feedback) and publishes the result back to another RabbitMQ queue for the Core LMS to update the database.

---

## 🛠 Tech Stack

Since this service primarily handles API integrations and JSON parsing, it is built with a lightweight and asynchronous Javascript stack:

* **Runtime:** Node.js
* **Framework:** Express.js
* **Database ORM:** Sequelize (PostgreSQL)
* **AI Integration:** Google Gemini API
* **Message Broker:** RabbitMQ (`amqplib`)
