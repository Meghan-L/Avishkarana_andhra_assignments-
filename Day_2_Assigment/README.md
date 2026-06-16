🚀 Project Overview

In real-world organizations, support teams receive thousands of tickets daily.
Manual categorization and prioritization of tickets is time-consuming and inefficient.

This project builds an automated Support Ticket Classification & Priority Prediction System using Natural Language Processing (NLP) and Machine Learning.

The system:

Automatically classifies support tickets into predefined categories.

Assigns a priority level (High / Medium / Low).

Provides evaluation metrics and confusion matrix analysis.

🎯 Problem Statement

Support teams face major challenges:

Tickets are not categorized properly.

Urgent issues get delayed.

Manual sorting wastes valuable time.

This project aims to solve these problems using ML-based automation.

🛠️ Technologies Used

Python

Jupyter Notebook

NLTK (Text preprocessing)

Scikit-learn

TF-IDF Vectorization

Logistic Regression

Matplotlib & Seaborn (Visualization)

📂 Dataset Used

IT Service Ticket Classification Dataset

47,837 support tickets

8 predefined categories

Real-world ticket text

Clean, labeled topic groups

Columns used:

Document → Ticket text

Topic_group → Category label

⚙️ Project Workflow
1️⃣ Text Preprocessing

Performed:

Lowercasing

Removing punctuation

Removing numbers

Stopword removal (NLTK)

Purpose: Clean raw text before feature extraction.

2️⃣ Feature Extraction

Used:

TF-IDF (Term Frequency – Inverse Document Frequency)

TfidfVectorizer(max_features=5000)

Converted text into 5000 numerical features.

3️⃣ Ticket Category Classification

Model used:

Logistic Regression

Train/Test Split: 80/20

Training on 47,837 tickets

Evaluated on 9,568 test samples

📊 Model Performance

Accuracy: 85%

Strong precision and recall across classes

Balanced class performance

4️⃣ Confusion Matrix

A confusion matrix was generated to visualize:

Correct classifications (strong diagonal dominance)

Misclassification patterns

Class-wise prediction behavior

The matrix confirms strong predictive performance.

5️⃣ Priority Prediction

The dataset does not contain labeled priority levels (High/Medium/Low).

Therefore, a rule-based priority assignment system was implemented.

Priority assignment logic:

High → Contains keywords like "urgent", "critical", "down", "immediately"

Medium → Contains keywords like "request", "issue", "help"

Low → Default if no urgency detected

This simulates real-world urgency detection in support systems.

Future improvement:
Priority prediction can be upgraded to a supervised ML model using labeled urgency data.

📈 Business Impact

This system can:

Automatically route tickets to correct departments

Reduce manual sorting effort

Improve response time

Increase SLA compliance

Enhance operational efficiency

🧠 Key Learnings

End-to-end NLP pipeline design

Text preprocessing techniques

TF-IDF feature engineering

Multi-class classification

Confusion matrix analysis

Debugging environment & execution order issues

Implementing rule-based decision systems

🔮 Future Improvements

Deploy as a web application

Add real-time prediction API

Train ML-based priority classifier

Try advanced models (SVM, Naive Bayes)

Integrate into helpdesk software

📌 Conclusion

This project demonstrates how Natural Language Processing and Machine Learning can solve real operational challenges in support systems.

It provides a scalable foundation for automated ticket management and intelligent routing.

