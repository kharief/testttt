from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import spacy
from flask import Flask, request, jsonify
from rapidfuzz import fuzz, process

# Override the PosLemmaTagger class
class CustomPosLemmaTagger:
    def __init__(self, language):
        self.language = language
        self.nlp = spacy.load("en_core_web_sm")

# Replace the original PosLemmaTagger with the custom one
import chatterbot.tagging
chatterbot.tagging.PosLemmaTagger = CustomPosLemmaTagger

# Load the spacy model
nlp = spacy.load('en_core_web_sm')

# Creating ChatBot Instance
chatbot = ChatBot('<b>CRCE BOT</b>')

chatbot = ChatBot(
    'ChatBot for College Enquiry',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': "Hi there, Welcome to CampusChat! 👋 How can I assist you today? You can ask about hall info, course details, or school fees.",
            'maximum_similarity_threshold': 0.90
        }
    ],
    database_uri='sqlite:///database.sqlite3'
) 
trainer = ListTrainer(chatbot)

# Predefined responses and queries
predefined_queries = {
    "apply for Aston Preston Hall": "To apply for Aston Preston Hall, please visit the following link: https://www.mona.uwi.edu/hall-residence-application-form-new.",
    "apply for Chancellor Hall": "To apply for Chancellor Hall, please visit the following link: https://www.mona.uwi.edu/hall-residence-application-form-new.",
    "apply for Taylor Hall": "To apply for Taylor Hall, please visit the following link: https://www.mona.uwi.edu/hall-residence-application-form-new.",
    "apply for Rex Nettleford Hall": "To apply for Rex Nettleford Hall, please visit the following link: https://www.mona.uwi.edu/hall-residence-application-form-new.",
    "apply for Mary Seacole Hall": "To apply for Mary Seacole Hall, please visit the following link: https://www.mona.uwi.edu/hall-residence-application-form-new.",
    "apply for Elsa Leo-Rhynie Hall": "To apply for Elsa Leo-Rhynie Hall, please visit the following link: https://www.mona.uwi.edu/hall-residence-application-form-new.",
    "apply for AZ Preston Hall": "To apply for AZ Preston Hall, please visit the following link: https://www.mona.uwi.edu/hall-residence-application-form-new.",
    "hall fee for Aston Preston Hall": "The hall fee for Aston Preston Hall is Double - $229,734; Single - $272,084.",
    "hall fee for Chancellor Hall": "The hall fee for Chancellor Hall is Block X - $332,438; Single - $250,585.",
    "hall fee for Taylor Hall": "The hall fee for Taylor Hall is Double - $212,043; Single - $250,585.",
    "hall fee for Rex Nettleford Hall": "The hall fee for Rex Nettleford Hall is Single - $297,046.",
    "hall fee for Mary Seacole Hall": "The hall fee for Mary Seacole Hall is Double - $212,043; Single - $250,585.",
    "hall fee for Elsa Leo-Rhynie Hall": "The hall fee for Elsa Leo-Rhynie Hall is Double - $259,754; Single - $305,578.",
    "hall fee for AZ Preston Hall": "The hall fee for AZ Preston Hall is Double - $229,734; Single - $272,084.",
    "general information for Aston Preston Hall": "Aston Preston Hall was created to provide more student accommodation and focuses on regional student integration and a conducive learning environment.",
    "general information for Chancellor Hall": "Chancellor Hall is known for its strong community spirit and history. It was named after Princess Alice and became an official hall in 1954.",
    "general information for Taylor Hall": "Taylor Hall is known for its rich tradition in academia, sports, and culture. It offers a supportive environment with various facilities and a strong community spirit.",
    "general information for Rex Nettleford Hall": "Rex Nettleford Hall was established to provide affordable housing for a larger number of students. It is known for its inclusive community and modern amenities.",
    "general information for Mary Seacole Hall": "Mary Seacole Hall was built for female students and is named after the pioneer nurse Mary Seacole. It encourages high academic achievement and well-rounded development.",
    "general information for Elsa Leo-Rhynie Hall": "Elsa Leo-Rhynie Hall provides a range of facilities and promotes student success through various programmes.",
    "general information for AZ Preston Hall": "AZ Preston Hall focuses on regional student integration and a conducive learning environment."
}

# Tuition fees for different faculties and degrees
tuition_fees = {
    "Faculty of Engineering": {
        "Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$346,533",
            "Part-Time (Per Credit)": "J$11,551"
        },
        "Non-Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$587,821",
            "Part-Time (Per Credit)": "J$19,594"
        },
        "International Students": {
            "Full-Time (Per Annum)": "US$15,000",
            "Part-Time (Per Credit)": "US$555"
        }
    },
    "Faculty of Humanities & Education": {
        "Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$346,533",
            "Part-Time (Per Credit)": "J$11,551"
        },
        "Non-Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$587,821",
            "Part-Time (Per Credit)": "J$19,594"
        },
        "International Students": {
            "Full-Time (Per Annum)": "US$15,000",
            "Part-Time (Per Credit)": "US$555"
        }
    },
    "Faculty of Law": {
        "Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$375,383",
            "Part-Time (Per Credit)": "J$12,513"
        },
        "Non-Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$587,821",
            "Part-Time (Per Credit)": "J$19,594"
        },
        "International Students": {
            "Full-Time (Per Annum)": "US$15,000",
            "Part-Time (Per Credit)": "US$555"
        }
    },
    "Faculty of Medical Sciences": {
        "Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$608,417",
            "Part-Time (Per Credit)": "J$20,000"
        },
        "Non-Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$1,013,924",
            "Part-Time (Per Credit)": "J$33,000"
        },
        "International Students": {
            "Full-Time (Per Annum)": "US$28,000",
            "Part-Time (Per Credit)": "US$1,000"
        }
    },
    "Faculty of Science & Technology": {
        "Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$346,533",
            "Part-Time (Per Credit)": "J$11,551"
        },
        "Non-Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$587,821",
            "Part-Time (Per Credit)": "J$19,594"
        },
        "International Students": {
            "Full-Time (Per Annum)": "US$15,000",
            "Part-Time (Per Credit)": "US$555"
        },
        "Degrees": {
            "Biomedical Radiation (B.Sc.)": {
                "Full-Time (Per Annum)": "US$15,000"
            },
            "Software Engineering Mobile Application Technology": {
                "Full-Time (Per Annum)": "US$15,000"
            },
            "Biomedical Instrumentation (B.Sc.)": {
                "Full-Time (Per Annum)": "J$800,000"
            },
            "Climate Science & Electronics Systems (B.Sc.)": {
                "Full-Time (Per Annum)": "J$800,000"
            },
            "Computer Science & Electronics (B.Sc.)": {
                "Full-Time (Per Annum)": "J$800,000"
            },
            "Mathematics of Finance (B.Sc.)": {
                "Full-Time (Per Annum)": "J$800,000"
            },
            "Electronics and Alternative Energy Systems (B.Sc.)": {
                "Full-Time (Per Annum)": "J$800,000"
            }
        }
    },
    "Faculty of Social Sciences": {
        "Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$346,533",
            "Part-Time (Per Credit)": "J$11,551"
        },
        "Non-Sponsored Students from Contributing Countries": {
            "Full-Time (Per Annum)": "J$587,821",
            "Part-Time (Per Credit)": "J$19,594"
        },
        "International Students": {
            "Full-Time (Per Annum)": "US$15,000",
            "Part-Time (Per Credit)": "US$555"
        }
    }
}

# Define a function to handle tuition fee queries
def get_fee_response(faculty):
    if faculty in tuition_fees:
        fee_info = tuition_fees[faculty]
        response = f"Tuition Fees for {faculty}:\n"
        for student_type, fees in fee_info.items():
            response += f"\n{student_type}:\n"
            for fee_type, amount in fees.items():
                response += f"  {fee_type}: {amount}\n"
        return response
    else:
        return "I'm sorry, I don't have information about that faculty. Can you please specify another faculty?"

# Define keyword sets for fuzzy matching
apply_keywords = ["apply", "link", "application", "admission"]
fee_keywords = ["fee", "cost", "price", "charges", "what is the fee", "fee for"]
info_keywords = ["information", "info", "details", "about", "tell me", "describe", "give me info"]

# Define a function to handle fuzzy matching
def get_response(user_input):
    user_input_lower = user_input.lower()

    # Check for apply keywords
    if any(keyword in user_input_lower for keyword in apply_keywords):
        relevant_queries = {k: v for k, v in predefined_queries.items() if "apply" in k}
    # Check for fee keywords
    elif any(keyword in user_input_lower for keyword in fee_keywords):
        relevant_queries = {k: v for k, v in predefined_queries.items() if "fee" in k}
        if relevant_queries:
            query, score = process.extractOne(user_input, relevant_queries.keys(), scorer=fuzz.partial_ratio)
            if score >= 75:  # Adjust the threshold as needed
                return relevant_queries[query]
            else:
                # Ask for faculty if fee keyword detected but no match found
                return "Which faculty are you interested in for the fee information?"

    # Check for information keywords
    elif any(keyword in user_input_lower for keyword in info_keywords):
        relevant_queries = {k: v for k, v in predefined_queries.items() if "general information" in k}
    else:
        relevant_queries = {}

    if relevant_queries:
        query, score = process.extractOne(user_input, relevant_queries.keys(), scorer=fuzz.partial_ratio)
        if score >= 75:  # Adjust the threshold as needed
            return relevant_queries[query]

    # If asking about school fee, trigger fee response
    if "school fee" in user_input_lower:
        return "Which faculty are you interested in for the fee information?"

    return "I'm sorry, I didn't understand that. Can you please rephrase?"

# Training with Personal Ques & Ans
conversation = [
    "Hi",
    "Hi there, Welcome to CampusChat! 👋 How can I assist you today? You can ask about hall info, course details, or school fees.",
    
    "hello",
    "Hi there, Welcome to CampusChat! 👋 How can I assist you today? You can ask about hall info, course details, or school fees.",

    "Hey",
    "Hi there, Welcome to CampusChat! 👋 How can I assist you today? You can ask about hall info, course details, or school fees.",

    "hall info",
    "Which hall are you interested in? The halls of residence at the University of the West Indies are: Aston Preston Hall, Chancellor Hall, Taylor Hall, Rex Nettleford Hall, Mary Seacole Hall, Elsa Leo-Rhynie Hall, and AZ Preston Hall.",
    
    "Aston Preston Hall",
    "What would you like to know about Aston Preston Hall? You can ask about the return date, hall fee, hall location, general information about the hall, or how to apply.",
    
    "Chancellor Hall",
    "What would you like to know about Chancellor Hall? You can ask about the return date, hall fee, hall location, general information about the hall, or how to apply.",
    
    "",
    "What would you like to know about Taylor Hall? You can ask about the return date, hall fee, hall location, general information about the hall, or how to apply.",
    
    "Rex Nettleford Hall",
    "What would you like to know about Rex Nettleford Hall? You can ask about the return date, hall fee, hall location, general information about the hall, or how to apply.",
    
    "Mary Seacole Hall",
    "What would you like to know about Mary Seacole Hall? You can ask about the return date, hall fee, hall location, general information about the hall, or how to apply.",
    
    "Elsa Leo-Rhynie Hall",
    "What would you like to know about Elsa Leo-Rhynie Hall? You can ask about the return date, hall fee, hall location, general information about the hall, or how to apply.",
    
    "AZ Preston Hall",
    "What would you like to know about AZ Preston Hall? You can ask about the return date, hall fee, hall location, general information about the hall, or how to apply.",

    "school fee",
    "Which faculty are you interested in for the fee information?"

        "What is the fee for the Computer Science degree?",
    "The fee for the Computer Science degree is J$800,000 per annum for full-time students.",
    
    "How much does it cost to study Computer Science?",
    "The cost to study Computer Science is J$800,000 per annum for full-time students.",
    
    "Tell me the fee structure for Computer Science.",
    "The fee structure for Computer Science is J$800,000 per annum for full-time students.",
    
    # Electrical Engineering Degree
    "What is the fee for the Electrical Engineering degree?",
    "The fee for the Electrical Engineering degree is J$750,000 per annum for full-time students.",
    
    "How much does it cost to study Electrical Engineering?",
    "The cost to study Electrical Engineering is J$750,000 per annum for full-time students.",
    
    "Tell me the fee structure for Electrical Engineering.",
    "The fee structure for Electrical Engineering is J$750,000 per annum for full-time students.",
    
    # Mechanical Engineering Degree
    "What is the fee for the Mechanical Engineering degree?",
    "The fee for the Mechanical Engineering degree is J$700,000 per annum for full-time students.",
    
    "How much does it cost to study Mechanical Engineering?",
    "The cost to study Mechanical Engineering is J$700,000 per annum for full-time students.",
    
    "Tell me the fee structure for Mechanical Engineering.",
    "The fee structure for Mechanical Engineering is J$700,000 per annum for full-time students.",
    
    # Civil Engineering Degree
    "What is the fee for the Civil Engineering degree?",
    "The fee for the Civil Engineering degree is J$720,000 per annum for full-time students.",
    
    "How much does it cost to study Civil Engineering?",
    "The cost to study Civil Engineering is J$720,000 per annum for full-time students.",
    
    "Tell me the fee structure for Civil Engineering.",
    "The fee structure for Civil Engineering is J$720,000 per annum for full-time students.",
    
    # Business Administration Degree
    "What is the fee for the Business Administration degree?",
    "The fee for the Business Administration degree is J$680,000 per annum for full-time students.",
    
    "How much does it cost to study Business Administration?",
    "The cost to study Business Administration is J$680,000 per annum for full-time students.",
    
    "Tell me the fee structure for Business Administration.",
    "The fee structure for Business Administration is J$680,000 per annum for full-time students.",
    
    # Information Technology Degree
    "What is the fee for the Information Technology degree?",
    "The fee for the Information Technology degree is J$780,000 per annum for full-time students.",
    
    "How much does it cost to study Information Technology?",
    "The cost to study Information Technology is J$780,000 per annum for full-time students.",
    
    "Tell me the fee structure for Information Technology.",
    "The fee structure for Information Technology is J$780,000 per annum for full-time students.",


    
    # Electronics and Communication Degree
    "What is the fee for the Electronics and Communication degree?",
    "The fee for the Electronics and Communication degree is J$740,000 per annum for full-time students.",
    
    "How much does it cost to study Electronics and Communication?",
    "The cost to study Electronics and Communication is J$740,000 per annum for full-time students.",
    
    "Tell me the fee structure for Electronics and Communication.",
    "The fee structure for Electronics and Communication is J$740,000 per annum for full-time students.",
 
    "What is the fee for a Computer Science Degree?",
    "The fee for the Computer Science Degree is J$800,000 per annum for full-time students.",
    
    "How much does it cost to study a Computer Science Degree?",
    "The cost to study Computer Science Degree is J$800,000 per annum for full-time students.",
    
    "Tell me the fee structure for a Computer Science Degree?",
    "The fee structure for Computer Science Degree is J$800,000 per annum for full-time students.",

    "What is the fee for sponsored students from contributing countries in the Faculty of Engineering?",
    "The fee for sponsored students from contributing countries in the Faculty of Engineering is J$346,533 per annum for full-time students and J$11,551 per credit for part-time students.",
    
    "What is the fee for non-sponsored students from contributing countries in the Faculty of Engineering?",
    "The fee for non-sponsored students from contributing countries in the Faculty of Engineering is J$587,821 per annum for full-time students and J$19,594 per credit for part-time students.",
    
    "What is the fee for international students in the Faculty of Engineering?",
    "The fee for international students in the Faculty of Engineering is US$15,000 per annum for full-time students and US$555 per credit for part-time students.",
    
    # Faculty of Humanities & Education
    "What is the fee for sponsored students from contributing countries in the Faculty of Humanities & Education?",
    "The fee for sponsored students from contributing countries in the Faculty of Humanities & Education is J$346,533 per annum for full-time students and J$11,551 per credit for part-time students.",
    
    "What is the fee for non-sponsored students from contributing countries in the Faculty of Humanities & Education?",
    "The fee for non-sponsored students from contributing countries in the Faculty of Humanities & Education is J$587,821 per annum for full-time students and J$19,594 per credit for part-time students.",
    
    "What is the fee for international students in the Faculty of Humanities & Education?",
    "The fee for international students in the Faculty of Humanities & Education is US$15,000 per annum for full-time students and US$555 per credit for part-time students.",
    
    # Faculty of Law
    "What is the fee for sponsored students from contributing countries in the Faculty of Law?",
    "The fee for sponsored students from contributing countries in the Faculty of Law is J$375,383 per annum for full-time students and J$12,513 per credit for part-time students.",
    
    "What is the fee for non-sponsored students from contributing countries in the Faculty of Law?",
    "The fee for non-sponsored students from contributing countries in the Faculty of Law is J$587,821 per annum for full-time students and J$19,594 per credit for part-time students.",
    
    "What is the fee for international students in the Faculty of Law?",
    "The fee for international students in the Faculty of Law is US$15,000 per annum for full-time students and US$555 per credit for part-time students.",

        # Existing conversation data...
    
    # Information Technology (B.Sc.)
    "How many credits do I need for a B.Sc. in Information Technology?",
    "A B.Sc. in Information Technology requires a total of fifteen (15) Level 1 credits and a minimum of forty-two (42) credits from Computing Courses at Levels 2 and 3.",
    
    "What courses should I take in my first year for Information Technology?",
    "In your first year for Information Technology, you should take the following courses: COMP1126 Introduction to Computing I, COMP1127 Introduction to Computing II, COMP1161 Object-Oriented Programming, COMP1210 Mathematics for Computing, and COMP1220 Computing and Society.",
    
    "Give me all the courses for the Information Technology degree.",
    "For the Information Technology degree, you need to complete the following courses:\n\n**Level 1:**\n- COMP1126 Introduction to Computing I\n- COMP1127 Introduction to Computing II\n- COMP1161 Object-Oriented Programming\n- COMP1210 Mathematics for Computing\n- COMP1220 Computing and Society\n\n**Levels 2 and 3:**\n- COMP2140 Software Engineering\n- COMP2190 Net-Centric Computing\n- COMP2340 Computer Systems Organization\n- COMP3161 Database Management Systems\n- COMP3901 Capstone Project\n- INFO2100 Mathematics and Statistics for IT\n- INFO2110 Data Structures for IT\n- INFO2180 Web Design and Programming I\n- INFO3105 Computer Systems and Administration\n- INFO3110 Information Systems\n- INFO3155 Information Assurance and Security\n- INFO3170 User Interface Design for IT\n- INFO3180 Dynamic Web Development II\n- Three (3) credits from Levels 2 or 3 courses offered by the Department of Computing\n- Eighteen (18) credits from any discipline including Computing.",
    
    # Computer Science (Major)
    "How many credits do I need for a major in Computer Science?",
    "A major in Computer Science requires a total of fifteen (15) Level 1 credits and a minimum of thirty-nine (39) credits from Computing courses at Levels 2 and 3.",
    
    "What courses should I take in my first year for Computer Science?",
    "In your first year for Computer Science, you should take the following courses: COMP1210 Mathematics for Computing, COMP1220 Computing and Society, COMP1126 Introduction to Computing I, COMP1127 Introduction to Computing II, and COMP1161 Object-Oriented Programming.",
    
    "Give me all the courses for the Computer Science major.",
    "For the Computer Science major, you need to complete the following courses:\n\n**Level 1:**\n- COMP1210 Mathematics for Computing\n- COMP1220 Computing and Society\n- COMP1126 Introduction to Computing I\n- COMP1127 Introduction to Computing II\n- COMP1161 Object-Oriented Programming\n\n**Levels 2 and 3:**\n- COMP2140 Software Engineering\n- COMP2171 Object Oriented Design and Implementation\n- COMP2190 Net-Centric Computing\n- COMP2201 Discrete Mathematics for Computer Science\n- COMP2211 Analysis of Algorithms\n- COMP2340 Computer Systems Organization\n- COMP3101 Operating Systems\n- COMP3161 Introduction to Database Management Systems\n- COMP3220 Principles of Artificial Intelligence\n- COMP3901 Capstone Project\n- Nine (9) credits from Levels 2 or 3 courses offered by the Department of Computing.",
    
    # Software Engineering (Major)
    "How many credits do I need for a major in Software Engineering?",
    "A major in Software Engineering requires a total of fifteen (15) Level 1 credits and a minimum of thirty-nine (39) credits from Levels 2 and 3.",
    
    "What courses should I take in my first year for Software Engineering?",
    "In your first year for Software Engineering, you should take the following courses: COMP1126 Introduction to Computing I, COMP1127 Introduction to Computing II, COMP1161 Object-Oriented Programming, COMP1210 Mathematics for Computing, and COMP1220 Computing and Society.",
    
    "Give me all the courses for the Software Engineering major.",
    "For the Software Engineering major, you need to complete the following courses:\n\n**Level 1:**\n- COMP1126 Introduction to Computing I\n- COMP1127 Introduction to Computing II\n- COMP1161 Object-Oriented Programming\n- COMP1210 Mathematics for Computing\n- COMP1220 Computing and Society\n\n**Levels 2 and 3:**\n- COMP2140 Software Engineering\n- COMP2171 Object Oriented Design and Implementation\n- COMP2190 Net-Centric Computing\n- COMP2201 Discrete Mathematics for Computer Science\n- COMP2211 Analysis of Algorithms\n- COMP3911 Internship in Computing\n- SWEN3130 Software Project Management\n- SWEN3145 Software Modelling\n- SWEN3165 Software Testing\n- SWEN3185 Formal Methods and Software Reliability\n- SWEN3920 Capstone Project (Software Engineering)\n- Three (3) credits from Levels 2 or 3 courses offered by the Department of Computing.",
    
    "Where is the University located?",
    "The University of the West Indies, Mona Campus is located in Kingston, Jamaica.",
    
    "How many halls are on the Mona Campus?",
    "The Mona Campus has ten halls of residence.",

    
    "How many fast food places are on the Mona Campus?",
    "The Mona Campus has several fast food places, including popular chains like KFC, Burger King, and Yaos.",
    
    "When does the Mona Campus open back for semester 1?",
    "The reopening dates for the Mona Campus vary each semester. A safe bet would be to return a week before classes start.",


    # General Information
    "What are you?",
    "Campus Chat is a web application designed to answer queries related to university details, course-related questions, location, fee structure, and more. It uses machine learning algorithms to understand and respond to user queries effectively.",
    
    "Who made you?",
    "I was made by CampusChatters, final year students at the University of the West Indies, embarking on an exciting journey to develop innovative solutions that make a difference. Our passion for technology and commitment to excellence have driven us to create this College Enquiry Chatbot. This project is not just an academic requirement but a testament to our dedication to leveraging technology to solve real-world problems. Join us as we explore the endless possibilities of machine learning and artificial intelligence!",
    
    # Campus Information
    "What can you tell me about the campus?",
    "The University of the West Indies, Mona Campus is a vibrant academic community located in Kingston, Jamaica. It offers a wide range of undergraduate and postgraduate programs and has various facilities including libraries, sports complexes, and student halls.",
    
    "What year was the campus founded?",
    "The University of the West Indies, Mona Campus was founded in 1948.",
    
    "How many halls are on campus?",
    "The Mona Campus has ten halls of residence.",
    
    "What are the halls?",
    "The halls of residence at the Mona Campus include Rex Nettleford Hall, Chancellor Hall, Taylor Hall, Irvine Hall, Mary Seacole Hall, Elsa Leo-Rhynie Hall, and others.",
    
    "Hall info",
    "The halls of residence at the Mona Campus provide accommodation and various amenities for students. Each hall has its own unique culture and community.",
    
    "Tell me about Rex Nettleford Hall",
    "Rex Nettleford Hall is one of the halls of residence at the Mona Campus. It offers modern facilities and a vibrant community for students.",
    
    "Tell me about rex",
    "Rex Nettleford Hall is one of the halls of residence at the Mona Campus. It offers modern facilities and a vibrant community for students.",

    "Tell me about Chancellor Hall",
    "Chancellor Hall is one of the oldest halls of residence at the Mona Campus. It has a rich history and a strong sense of community among its residents.",
    
    "Tell me about taylor",
    "Taylor Hall is known for its strong traditions and active student community. It offers various facilities and activities for its residents.",
    
    "What should I know about Taylor Hall?",
    "Taylor Hall is one of the prominent halls of residence at the Mona Campus. It is known for its vibrant student life and numerous activities.",
    
    "What is the hall fee for rex?",
    "The hall fee for Rex Nettleford Hall is Single - $297,046.",
    
    "Where is the hall located?",
    "The halls of residence are located within the University of the West Indies, Mona Campus in Kingston, Jamaica.",
    
    "Give me some info about the hall",
    "Rex Nettleford Hall was established to provide affordable housing for a larger number of students. It is known for its inclusive community and modern amenities.",
    
    "When is graduation?",
    "Graduation is in early November.",
    
    # Course and Degree Information
    "What courses should I take in my first year for Software Engineering?",
    "In your first year for Software Engineering, you should take the following courses: COMP1126 Introduction to Computing I, COMP1127 Introduction to Computing II, COMP1161 Object-Oriented Programming, COMP1210 Mathematics for Computing, and COMP1220 Computing and Society.",
    
    "How many credits do I need?",
    "A major in Software Engineering requires a total of fifteen (15) Level 1 credits and a minimum of thirty-nine (39) credits from Levels 2 and 3.",
    
    "How many credits do I need for a major in Computer Science?",
    "A major in Computer Science requires a total of fifteen (15) Level 1 credits and a minimum of thirty-nine (39) credits from Computing courses at Levels 2 and 3.",
    
    "Give me all the courses for the Computer Science major",
    "For a major in Computer Science, you need to take the following courses: COMP1210 Mathematics for Computing, COMP1220 Computing and Society, COMP1126 Introduction to Computing I, COMP1127 Introduction to Computing II, COMP1161 Object-Oriented Programming, and additional courses at Levels 2 and 3.",
    
    "How much does it cost to study a Computer Science Degree?",
    "The cost to study a Computer Science Degree varies based on your residency status and other factors. Please check the official university website for the most accurate information.",
    
    "What is the fee for sponsored students for the Faculty of Engineering?",
    "For the 2024/2025 academic year, the fee for sponsored students from contributing countries in the Faculty of Engineering is J$346,533 per annum for full-time students and J$11,551 per credit for part-time students.",
    
    "What is the fee for the Civil Engineering degree?",
    "For the 2024/2025 academic year, the fee for the Civil Engineering degree for international students is US$10,000 per annum for full-time students and US$367 per credit for part-time students.",
    
    "I’m an international student interested in the Faculty of Engineering whats is the price for it?",
    "For the 2024/2025 academic year, the fee for international students in the Faculty of Engineering is US$10,000 per annum for full-time students and US$367 per credit for part-time students."



]

trainer.train(conversation)

# Define Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.json.get("message")
        if "faculty" in user_input.lower():
            faculty = user_input.split("faculty")[-1].strip()
            response = get_fee_response(faculty)
        elif "degree" in user_input.lower():
            degree_query = user_input.split("degree")[-1].strip()
            response = "For which faculty is the degree?"  # Ask for faculty if degree keyword detected but no match found
        else:
            response = get_response(user_input)
        return jsonify({"response": response})
    return '''
        <!doctype html>
        <html>
            <head>
                <title>CampusChat</title>
            </head>
            <body>
                <h1>Welcome to CampusChat! 👋</h1>
                <form action="/" method="post">
                    <input type="text" name="message">
                    <input type="submit" value="Send">
                </form>
            </body>
        </html>
    '''

if __name__ == "__main__":
    app.run()
