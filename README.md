# -AI-Interview-Platform
Automated recruitment with intelligent voice interviews

# AI Interview Platform Backend

This Flask backend will power the AI-driven voice interview platform. Key features:

- Document upload and text extraction (PDF, DOCX, TXT)
- AI question generation using Google Gemini
- Real-time voice interaction (Speech-to-Text, Text-to-Speech)
- Interview session storage and scoring

## Directory Structure
- `app.py`: Main Flask app
- `routes/`: API endpoints
- `services/`: Core logic (document processing, AI, voice)
- `static/` and `templates/`: For frontend (if using Flask templates)

## How its work (output) 

1. Document Intelligence: Implement PDF/Resume upload with automated text extraction to personalize interview questions.

2. AI Question Engine: Integration with Google Gemini for dynamic, role-specific question generation.

3. Voice-Enabled Interviews: Add Speech-to-Text (STT) and Text-to-Speech (TTS) for a natural, hands-free interview experience.

4. Analytics Dashboard: Build an automated scoring system and session history storage using Drizzle ORM & PostgreSQL.


### **1. Core Framework & Language**
Next.js (React): Serves as the Frontend & Orchestration layer. It handles user authentication, the dashboard interface, and real-time webcam/voice interaction.

Python: Serves as the AI & Data Intelligence layer. It is used for backend tasks where Python’s AI ecosystem excels, such as complex document parsing or advanced Natural Language Processing (NLP).

TypeScript: Used within the Next.js environment to ensure Type Safety, reducing runtime errors and making the communication between the frontend and the AI backend more predictable.

### **2. Frontend & Styling**

* **Tailwind CSS:** Used for utility-first styling, allowing for rapid UI development and a responsive design.
* **Shadcn UI:** A collection of reusable components built on top of Tailwind CSS and Radix UI, giving the dashboard and interface a clean, modern look.
* **Lucide React:** Used for the consistent and scalable iconography throughout the application.

### **3. Backend & Database**

* **Drizzle ORM:** A lightweight and performant TypeScript ORM used to interact with your database.
* **PostgreSQL (Neon DB):** Based on the configuration, you are using Neon, a serverless PostgreSQL database, to store user data, interview questions, and feedback.

### **4. Authentication**

* **Clerk:** This is used for managing user authentication (Sign up, Login, Profile management) securely and easily.

### **5. Artificial Intelligence (AI)**

* **Google Gemini AI (Google Generative AI SDK):** This is the core engine of the project. It is used to:
* Generate interview questions based on the job description and years of experience.
* Analyze user answers and provide feedback and ratings.

### **6. Media & APIs**

* **Webcam API:** Used to access the user's camera during the mock interview session to simulate a real interview environment.
* **Speech-to-Text:** Likely integrated to capture and transcribe the user's verbal answers for analysis by the AI.

### **7. Tools & Deployment**

* **Vercel:** Typically used for deploying Next.js applications like this one.
* **ESLint / Prettier:** For maintaining code quality and consistent formatting.

### **Summary of Workflow:**

1. **User Input:** Users provide a Job Description and Experience.
2. **AI Generation:** The app calls the **Gemini API** to create specific technical questions.
3. **Interview Session:** Users record their answers via **Webcam** and audio.
4. **Feedback Loop:** The app sends the transcribed answer back to **Gemini**, which compares it with the expected answer and saves the result in the **PostgreSQL** database using **Drizzle**.
