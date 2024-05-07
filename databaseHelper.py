import sqlite3
import os
# get the current date
from datetime import datetime
import json


DB_NAME="EduSmart.db"

class CreateDatabase:
    def __init__(self):
        self.db_name = DB_NAME
        
    def create_database(self):
        try:
            conn = sqlite3.connect(self.db_name)
            print("Connection to database successful.")
            conn.close()
        except sqlite3.Error as e:
            print("Error connecting to database:", e)

    def create_tables(self): 
        create_table_queries = [
            '''CREATE TABLE IF NOT EXISTS Answers (
                AnswerID INTEGER PRIMARY KEY,
                QuestionID INTEGER,
                AnswerOptions TEXT,
                CorrectAnswer TEXT,
                Explaination TEXT,
                FOREIGN KEY (QuestionID) REFERENCES Question(QuestionID) ON DELETE CASCADE
            )''',
            '''CREATE TABLE IF NOT EXISTS Chapter (
                ChapterID INTEGER PRIMARY KEY,
                ChapterName TEXT UNIQUE,
                ClassID INTEGER,
                FOREIGN KEY (ClassID) REFERENCES Class(ClassID) ON DELETE CASCADE
            )''',
            '''CREATE TABLE IF NOT EXISTS Class (
                ClassID INTEGER PRIMARY KEY,
                ClassName TEXT UNIQUE
            )''',
            '''CREATE TABLE IF NOT EXISTS Exam (
                ExamID INTEGER PRIMARY KEY,
                UserID INTEGER,
                Score REAL,
                TimeTaken INTEGER,
                StartTime DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
            )''',
            '''CREATE TABLE IF NOT EXISTS Exam_Questions (
                ExamQuestionID INTEGER PRIMARY KEY,
                ExamID INTEGER,
                QuestionID INTEGER,
                QuestionOrder INTEGER,
                Score REAL,
                FOREIGN KEY (ExamID) REFERENCES Exam(ExamID) ON DELETE CASCADE,
                FOREIGN KEY (QuestionID) REFERENCES Question(QuestionID) ON DELETE CASCADE
            )''',
            '''CREATE TABLE IF NOT EXISTS ExamResult (
                ExamResultID INTEGER PRIMARY KEY,
                UserID INTEGER,
                ExamID INTEGER,
                CorrectAnswers INTEGER,
                IncorrectAnswers INTEGER,
                Score REAL,
                AnswerDetails TEXT,
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
                FOREIGN KEY (ExamID) REFERENCES Exam(ExamID) ON DELETE CASCADE
            )''',
            '''CREATE TABLE IF NOT EXISTS Question (
                QuestionID INTEGER PRIMARY KEY,
                ClassID INTEGER,
                TopicID INTEGER,
                ChapterID INTEGER,
                QuestionContent TEXT,
                UsageCount INTEGER DEFAULT 0,
                FOREIGN KEY (ClassID) REFERENCES Class(ClassID) ON DELETE CASCADE,
                FOREIGN KEY (TopicID) REFERENCES Topic(TopicID) ON DELETE CASCADE,
                FOREIGN KEY (ChapterID) REFERENCES Chapter(ChapterID) ON DELETE CASCADE
            )''',
            '''CREATE TABLE IF NOT EXISTS Topic (
                TopicID INTEGER PRIMARY KEY,
                TopicName TEXT,
                ChapterID INTEGER,
                FOREIGN KEY (ChapterID) REFERENCES Chapter(ChapterID) ON DELETE CASCADE
            )''',
            '''CREATE TABLE IF NOT EXISTS User (
                UserID INTEGER PRIMARY KEY,
                Name VARCHAR(50) UNIQUE,
                PasswordHash VARCHAR(255),
                Email VARCHAR(100),
                Phone VARCHAR(20),
                ClassID INTEGER,
                DoB DATE,
                AverageScore REAL,
                Status VARCHAR(50),
                ExpiryDate DATE,
                AccessTokens TEXT UNIQUE,
                FOREIGN KEY (ClassID) REFERENCES Class(ClassID) ON DELETE CASCADE
            )''',
            '''CREATE TABLE IF NOT EXISTS Documents (
                DocID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT,
                URL TEXT,
                Thumbnail TEXT,
                ClassID INTEGER,
                Created_at DATE,
                FOREIGN KEY (ClassID) REFERENCES Class(ClassID)  ON DELETE CASCADE
            );
            '''
        ]

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            for query in create_table_queries:
                cursor.execute(query)
            conn.commit()
            print("The tables have been created successfully.")
            conn.close()
        except sqlite3.Error as e:
            print("Error creating table:", e)

class UserModel:
    def __init__(self):
        self.db_name = DB_NAME

    def get_role(self, token):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT Status FROM User WHERE AccessTokens=?", (token,))
            role = cursor.fetchone()
            conn.close()
            return role
        except sqlite3.Error as e:
            print("Lỗi khi lấy quyền người dùng:", e)
            return None
        
    def get_all_users(self,status=None):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM User WHERE Status=?", (status,))
            else:
                cursor.execute("SELECT * FROM User")
            users = cursor.fetchall()
            conn.close()
            return users
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách người dùng:", e)
            return None
    
    def get_user_by_token(self, token):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE AccessTokens=?", (token,))
            user = cursor.fetchone()
            conn.close()
            return user
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin người dùng:", e)
            return False
    
    def add_user(self, Name, password, email,dob, status="USER"):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            if self.get_user_by_email(email):
                return 500, "Email already exists"
            date_now = datetime.now()
            created_at = str(date_now.strftime("%Y-%m-%d"))  
            cursor.execute("INSERT INTO User (Name, PasswordHash, Email, DoB, Status,created_at) VALUES (?, ?, ?, ?, ?,?)", (Name, password, email, dob, status,created_at))
            conn.commit()
            conn.close()
            return 200,"User added successfully"
        except sqlite3.Error as e:
            print("Lỗi khi thêm người dùng:", e)
            return 500, "Failed to add user"

    def get_user_by_email(self, email):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE Email=?", (email,))
            user = cursor.fetchone()
            conn.close()
            return user
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin người dùng:", e)
            return None

    def get_user_by_id(self, user_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE UserID=?", (user_id,))
            user = cursor.fetchone()
            conn.close()
            return user
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin người dùng:", e)
            return None

    def update_user_token(self, email, token):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE User SET AccessTokens=? WHERE Email=?", (token, email))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật token người dùng:", e)
            return False
    
    def update_user_role(self, user_id, status):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE User SET Status=? WHERE UserID=?", (status, user_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật quyền người dùng:", e)
            return False
    
    def update_user_info(self, user_id, old_password, new_password, new_email, new_dob, new_Name):
        if len(new_password) ==0 and len(new_email) == 0 and len(new_Name) == 0 and len(new_dob) == 0:
            return 500, "Nothing to update"
        if len(new_email) == 0:
            return 500, "Email cannot be empty"
        if len(new_Name) == 0:
            return 500, "Name cannot be empty"
        if len(new_dob) == 0:
            return 500, "Date of birth cannot be empty"
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE UserID=?", (user_id,))
            user = cursor.fetchone()
            if user[2] != old_password:
                return 500, "Old password is incorrect"
            cursor.execute("UPDATE User SET PasswordHash=?, Email=?, DoB=?, Name=? WHERE UserID=?", (new_password, new_email, new_dob, new_Name, user_id))
            conn.commit()
            conn.close()
            return 200, "User info updated successfully"
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật thông tin người dùng:", e)
            return 500, "Failed to update user info"
    
    def update_user_status(self, user_id, status):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE User SET Status=? WHERE UserID=?", (status, user_id))
            conn.commit()
            conn.close()
            return 200, "User status updated successfully"
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật trạng thái người dùng:", e)
            return 500, "Failed to update user status"
    
    def delete_user(self, user_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM User WHERE UserID=?", (user_id,))
            conn.commit()
            conn.close()
            return 200, "User deleted successfully"
        except sqlite3.Error as e:
            print("Lỗi khi xóa người dùng:", e)
            return 500, "Failed to deleted user"

    def user_count_to_chart(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT strftime('%Y-%m', created_at) AS Month, Status, COUNT(UserID) FROM User WHERE Status IN ('USER', 'VIP') GROUP BY Month, Status")
            user_count = cursor.fetchall()
            
            # Khởi tạo một từ điển để lưu trữ kết quả
            json_data = {"count": []}
            
            # Duyệt qua kết quả từ cơ sở dữ liệu
            for item in user_count:
                month = item[0]
                status = item[1]
                count = item[2]
                
                # Tìm kiếm xem có mục nào có cùng ngày không
                found = False
                for result in json_data["count"]:
                    if result["Date"] == month:
                        result[status] = count
                        found = True
                        break
                
                # Nếu không tìm thấy, thêm một mục mới
                if not found:
                    new_result = {"Date": month, "USER": 0, "VIP": 0}
                    new_result[status] = count
                    json_data["count"].append(new_result)
            
            conn.close()
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy số lượng người dùng:", e)
            return {"count": [], "message": "Failed"}

    def reset_password(self, email, new_password):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE User SET PasswordHash=? WHERE Email=?", (new_password, email))
            conn.commit()
            conn.close()
            return 200, "Password reset successfully"
        except sqlite3.Error as e:
            print("Lỗi khi đặt lại mật khẩu:", e)
            return 500, "Failed to reset password"

class ClassModel:
    def __init__(self):
        self.db_name = DB_NAME

    def get_all_classes(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Class")
            
            classes = cursor.fetchall()
            json_data = [{"id": item[0], "name": item[1]} for item in classes]
            conn.close()
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách lớp:", e)
            return None

    def get_class_by_id(self, class_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Class WHERE ClassID=?", (class_id,))
            class_info = cursor.fetchone()
            conn.close()
            return class_info
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin lớp:", e)
            return None

    def add_class(self, class_name):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Class (ClassName) VALUES (?)", (class_name,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm lớp:", e)
            return False
    
    def update_class(self, class_id, class_name):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE Class SET ClassName=? WHERE ClassID=?", (class_name, class_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật lớp:", e)
            return False
        
    def delete_class(self, class_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Class WHERE ClassID=?", (class_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi xóa lớp:", e)
            return False
        
class ChapterMoel:
    def __init__(self):
        self.db_name = DB_NAME

    def get_all_chapters(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Chapter")
            chapters = cursor.fetchall()
            json_data = [{"id": item[0], "name": item[1]} for item in chapters]
            conn.close()
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách chương:", e)
            return None

    def get_chapter_by_id(self, chapter_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Chapter WHERE ChapterID=?", (chapter_id,))
            chapter_info = cursor.fetchone()
            conn.close()
            return chapter_info
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin chương:", e)
            return None

    def add_chapter(self, chapter_name, class_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Chapter (ChapterName, ClassID) VALUES (?, ?)", (chapter_name, class_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm chương:", e)
            return False
    
    def update_chapter(self, chapter_id, chapter_name):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE Chapter SET ChapterName=? WHERE ChapterID=?", (chapter_name, chapter_id))
            conn.commit()
            conn.close()
            return 200, "Chapter updated successfully"
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật chương:", e)
            return 500, "Failed to update chapter"
        
    def delete_chapter(self, chapter_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Chapter WHERE ChapterID=?", (chapter_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi xóa chương:", e)
            return False
    
    def get_chapters_by_class_id(self, class_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Chapter WHERE ClassID=?", (class_id,))
            chapters = cursor.fetchall()
            json_data = [{"id": item[0], "name": item[1]} for item in chapters]
            
            conn.close()
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách chương:", e)
            return None
    
class TopicModel:
    def __init__(self):
        self.db_name = DB_NAME

    def get_all_topics(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Topic")
            topics = cursor.fetchall()
            conn.close()
            return topics
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách chủ đề:", e)
            return None

    def get_topic_by_id(self, topic_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Topic WHERE TopicID=?", (topic_id,))
            topic_info = cursor.fetchone()
            conn.close()
            return topic_info
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin chủ đề:", e)
            return None

    def get_topics_by_chapter_id(self, chapter_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Topic WHERE ChapterID=?", (chapter_id,))
            topics = cursor.fetchall()
            conn.close()
            json_data = [{"id": item[0], "name": item[1]} for item in topics]
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách chủ đề:", e)
            return None

    def add_topic(self, topic_name, chapter_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Topic (TopicName, ChapterID) VALUES (?, ?)", (topic_name, chapter_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm chủ đề:", e)
            return False
    
    def update_topic(self, topic_id, topic_name):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE Topic SET TopicName=? WHERE TopicID=?", (topic_name, topic_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật chủ đề:", e)
            return False
        
    def delete_topic(self, topic_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Topic WHERE TopicID=?", (topic_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi xóa chủ đề:", e)
            return False
        
class QuestionModel:
    def __init__(self):
        self.db_name = DB_NAME

    def get_last_question_id(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT QuestionID FROM Question ORDER BY QuestionID DESC LIMIT 1")
            question_id = cursor.fetchone()
            conn.close()
            return question_id[0]
        except sqlite3.Error as e:
            print("Lỗi khi lấy ID câu hỏi cuối cùng:", e)
            return None

    def get_all_questions(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Question")
            questions = cursor.fetchall()
            
            json_data = [{"id": item[0], "class_id": item[1], "topic_id": item[2], "chapter_id": item[3], "content": item[4],"usagecount":item[5]} for item in questions]
            # add answers to json_data
            for item in json_data:
                cursor.execute("SELECT * FROM Answers WHERE QuestionID=?", (item["id"],))
                answers = cursor.fetchall()
                # convert answer[2] to json
                item["answers"] = [{"id": answer[0], "answer": json.loads(answer[2]), "correct": answer[3], "explaination": answer[4]} for answer in answers]
            conn.close()
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách câu hỏi:", e)
            return None
  
    def get_question_by_id(self, question_id):
        # show question and answers of this question.
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Question WHERE QuestionID=?", (question_id,))
            question = cursor.fetchone()
            cursor.execute("SELECT * FROM Answers WHERE QuestionID=?", (question_id,))
            answers = cursor.fetchall()
            json_data = {"id": question[0], "class_id": question[1], "topic_id": question[2], "chapter_id": question[3], "content": question[4], "answers": [{"id": item[0], "answer": item[2], "correct": item[3], "explaination": item[4]} for item in answers]}
            conn.close()
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin câu hỏi:", e)
            return None

    def get_questions_by_topic_id(self, topic_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Question WHERE TopicID=?", (topic_id,))
            questions = cursor.fetchall()
            conn.close()
            return questions
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách câu hỏi:", e)
            return None

    def get_id_by_content(self, question_content):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT QuestionID FROM Question WHERE QuestionContent=?", (question_content,))
            question_id = cursor.fetchone()
            conn.close()
            return question_id[0]
        except sqlite3.Error as e:
            print("Lỗi khi lấy ID câu hỏi:", e)
            return None

    def add_question(self, class_id, topic_id, chapter_id, question_content):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Question (ClassID, TopicID, ChapterID, QuestionContent) VALUES (?, ?, ?, ?)", (class_id, topic_id, chapter_id, question_content))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm câu hỏi:", e)
            return False
    
    def update_question(self, question_id, question_content):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE Question SET  QuestionContent=? WHERE QuestionID=?", ( question_content, question_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật câu hỏi:", e)
            
    def delete_question(self, question_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Question WHERE QuestionID=?", (question_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi xóa câu hỏi:", e)
            return False
    
    def count_question_by_class(self):
        # return the number of questions and class name, class id
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
            SELECT Class.ClassID, ClassName, COUNT(Question.QuestionID)
            FROM Class
            LEFT JOIN Question ON Class.ClassID = Question.ClassID
            GROUP BY Class.ClassID, ClassName
            """)

            questions = cursor.fetchall()
            json_data = [{"class_id": item[0], "class_name": item[1], "question_count": item[2]} for item in questions]
            conn.close()
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy số lượng câu hỏi:", e)
            return None
    
    def count_question_by_chapter(self, class_id):
        # Return the number of questions, chapter name, and chapter id
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Chapter.ChapterID, ChapterName, COUNT(Question.QuestionID)
                FROM Chapter
                
                LEFT JOIN Question ON Chapter.ChapterID = Question.ChapterID AND Question.ClassID=?
                WHERE Chapter.ClassID=?
                GROUP BY Chapter.ChapterID
                """, (class_id, class_id))
            questions = cursor.fetchall()
            json_data = [{"chapter_id": item[0], "chapter_name": item[1], "question_count": item[2]} for item in questions]
            conn.close()
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy số lượng câu hỏi:", e)
            return None

    def count_question_by_topic(self, chapter_id):
        # Return the number of questions, topic name, and topic id
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Topic.TopicID, TopicName, COUNT(Question.QuestionID)
                FROM Topic
                LEFT JOIN Question ON Topic.TopicID = Question.TopicID AND Question.ChapterID=?
                WHERE Topic.ChapterID=?
                GROUP BY Topic.TopicID
                
                """, (chapter_id, chapter_id))
            questions = cursor.fetchall()
            json_data = [{"topic_id": item[0], "topic_name": item[1], "question_count": item[2]} for item in questions]
            conn.close()
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy số lượng câu hỏi:", e)
            return None
           
    def generate_questions(self,class_ids, topic_ids=None, chapter_ids=None, num_questions=1,token=None,user_id=None,type="P"):
        # result_string = f"class_ids: {class_ids}, topic_ids: {topic_ids}, chapter_ids: {chapter_ids}, num_questions: {num_questions}, token: {token}, user_id: {user_id}"
        # print(result_string)

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            # Tạo danh sách các điều kiện WHERE cho class_id, topic_id và chapter_id
            conditions = []
            params = []
            if class_ids:
                conditions.append("q.ClassID IN ({})".format(','.join(['?']*len(class_ids))))
                params.extend(class_ids)
            if topic_ids:
                conditions.append("q.TopicID IN ({})".format(','.join(['?']*len(topic_ids))))
                params.extend(topic_ids)
            
            if chapter_ids == [] and type=="P":
                return 500, "Chapter is required"
            elif chapter_ids == [] and type=="M":
                pass
            else:
                conditions.append("q.ChapterID IN ({})".format(','.join(['?']*len(chapter_ids))))
                params.extend(chapter_ids)
            
            where_clause = " AND ".join(conditions)
            # Thêm điều kiện WHERE vào câu truy vấn
            if not where_clause:
                query = "SELECT q.QuestionID, q.QuestionContent AS Question, a.AnswerID, a.AnswerOptions AS Answer, a.CorrectAnswer, a.Explaination FROM Question q LEFT JOIN Answers a ON q.QuestionID = a.QuestionID ORDER BY q.UsageCount ASC LIMIT ?"
                params.append(num_questions)
            else:
                query = "SELECT q.QuestionID, q.QuestionContent AS Question, a.AnswerID, a.AnswerOptions AS Answer, a.CorrectAnswer, a.Explaination FROM Question q LEFT JOIN Answers a ON q.QuestionID = a.QuestionID WHERE {} ORDER BY q.UsageCount ASC LIMIT ?".format(where_clause)
                params.append(num_questions)
            cursor.execute(query, params)
            questions = cursor.fetchall()

            exam_id=""
            conn.close()
            exam=ExamModel()
            now=datetime.now()
            start_time=now.strftime("%Y-%m-%d %H:%M:%S")
            exam_id=exam.add_exam(user_id,0,start_time,type)
            for question in questions:
                conn=sqlite3.connect(self.db_name)
                cursor=conn.cursor()
                cursor.execute("UPDATE Question SET UsageCount = UsageCount + 1 WHERE QuestionID = ?", (question[0],))
                conn.commit()
                conn.close()
                # create an exam then add the question to the exam
                exam_question=ExamQuestionModel()
                exam_question.add_exam_question(exam_id,question[0],questions.index(question)+1,round(100/len(questions),1))
            # print(exam_id)
            return exam_id, str(len(questions))
        except sqlite3.Error as e:
            print("xnxxxxxx:", e)
            return None
        
class AnswerModel:
    def __init__(self):
        self.db_name = DB_NAME

    def check_answer(self, question_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT CorrectAnswer FROM Answers WHERE QuestionID=?", (question_id,))
            correct_answer = cursor.fetchone()
            conn.close()
            return correct_answer[0]
        except sqlite3.Error as e:
            print("Lỗi khi kiểm tra câu trả lời:", e)
            return None


    def get_all_answers(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Answers")
            answers = cursor.fetchall()
            conn.close()
            return answers
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách câu trả lời:", e)
            return None

    def get_answer_by_id(self, answer_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Answers WHERE AnswerID=?", (answer_id,))
            answer = cursor.fetchone()
            conn.close()
            return answer
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin câu trả lời:", e)
            return None

    def get_answers_by_question_id(self, question_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Answers WHERE QuestionID=?", (question_id,))
            answers = cursor.fetchall()
            conn.close()
            return answers
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách câu trả lời:", e)
            return None

    def add_answer(self, question_id, answer_options, correct_answer, explaination):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Answers (QuestionID, AnswerOptions, CorrectAnswer, Explaination) VALUES (?, ?, ?, ?)", (question_id, answer_options, correct_answer, explaination))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm câu trả lời:", e)
            return False
    
    def update_answer(self, question_id, answer_options, correct_answer, explaination):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE Answers SET AnswerOptions=?, CorrectAnswer=?, Explaination=? WHERE QuestionID=?", (answer_options, correct_answer, explaination, question_id))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật câu trả lời:", e)
    
    def delete_answer(self, question_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Answers WHERE QuestionID=?", (question_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi xóa câu trả lời:", e)
            return False
           
class ExamModel:
    def __init__(self):
        self.db_name = DB_NAME

    def get_exam_type(self, exam_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT Type FROM Exam WHERE ExamID=?", (exam_id,))
            exam_type = cursor.fetchone()
            conn.close()
            return exam_type[0]
        except sqlite3.Error as e:
            print("Lỗi khi lấy loại bài thi:", e)
            return None

    def get_exam_by_id(self, exam_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Exam WHERE ExamID=?", (exam_id,))
            exam = cursor.fetchone()
            conn.close()
            return exam
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin bài thi:", e)
            return None

    def get_all_exam_results_user(self, user_id,exam_type):
        # get all exams by user_id và truy vấn thông tin bài thi dựa vào ID của bài thi trong ExamResult model
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Exam WHERE UserID=? AND Type=?", (user_id,exam_type))
            exams = cursor.fetchall()
            conn.close()
            exam_results = []
            exam_result_model=ExamResultModel()
            for exam in exams:
                exam_result = exam_result_model.get_exam_result_by_exam_id(exam[0])
                correct_count = exam_result["correct_count"]
                incorrect_count = exam_result["incorrect_count"]
                score = exam_result["score"]
                count_question = len(ExamQuestionModel().get_exam_question_by_id(exam[0]))
                unanswered_question=count_question-correct_count-incorrect_count
                if exam[3] == None:
                    status = "Inprogress"
                else:
                    status = "Completed"
                exam_results.append({"exam_id": exam[0], "correct_count": correct_count, "incorrect_count": incorrect_count, "score": score, "unanswered_count": unanswered_question,"status":status})
            return exam_results
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin bài thi:", e)
            return None
        
    def exam_count_to_chart(self):
        # get the number of exams by month and group by Type (P for practice, M for mock)
        # change M to Mock and P to Practice
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
            SELECT COUNT(ExamID), Type, strftime('%Y-%m', StartTime)
            FROM Exam
            GROUP BY Type, strftime('%Y-%m', StartTime)
            """)
            exams = cursor.fetchall()
            json_data = {"count": []}
            for item in exams:
                month = item[2]
                exam_type = "Mock" if item[1] == "M" else "Practice"
                count = item[0]
                # Tìm kiếm xem có mục nào có cùng ngày không
                found = False
                for result in json_data["count"]:
                    if result["Date"] == month:
                        result[exam_type] = count
                        found = True
                        break
                # Nếu không tìm thấy, thêm một mục mới
                if not found:
                    new_result = {"Date": month, "Mock": 0, "Practice": 0}
                    new_result[exam_type] = count
                    json_data["count"].append(new_result)
            conn.close()
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy số lượng bài thi:", e)
            return {"count": [], "message": "Failed"}


    def add_exam(self, user_id, score, start_time,type):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Exam (UserID, Score, StartTime,Type) VALUES (?, ?, ?, ?)", (user_id, score, start_time,type))
            # get ID of the last inserted exam
            exam_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return exam_id
        except sqlite3.Error as e:
            print("Lỗi khi thêm bài thi:", e)
            return False
    
    def update_exam(self, exam_id, score, time_taken):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE Exam SET Score=?, TimeTaken=? WHERE ExamID=?", (score, time_taken, exam_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật bài thi:", e)
            return False
        
    def count_exams(self, user_id):
        # count the number of exams by type (max score, min score, average score , average time taken)
        # group by Month in StartTime
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
            SELECT MAX(Score), MIN(Score), AVG(Score), AVG(TimeTaken),strftime('%Y-%m', StartTime)
            FROM Exam
            WHERE Type = "M" AND UserID = ?
            GROUP BY strftime('%Y-%m', StartTime)
            """, (user_id,))
            exams = cursor.fetchall()
            monthlyScores={}
            monthlyScores["monthlyScores"]={}
            for item in exams:
                monthlyScores["monthlyScores"][item[4]] = [round(item[2],2), round(item[1],2), round(item[0],2)]
            monthlyScores["monthlyCompletionTime"]={}
            for item in exams:
                try:
                    monthlyScores["monthlyCompletionTime"][item[4]] = round(item[3],2)
                except:
                    monthlyScores["monthlyCompletionTime"][item[4]] = 0
            

            conn.close()
            return monthlyScores # Trả về JSON dưới dạng chuỗi
        except sqlite3.Error as e:
            print("Lỗi khi lấy số lượng bài thi:", e)
            return None

    def count_exam_by_user(self,user_id,token):
        # nếu user là "USER", khi số bài thi của user đó >= 1 thì sẽ trả vể {"message": "Please Upgrade to VIP to test more exam"}
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(ExamID) FROM Exam WHERE UserID=?", (user_id,))
            exam_count = cursor.fetchone()[0]
            user=UserModel()
            user_status=user.get_role(token)[0]

            conn.close()
            if user_status=="USER" and exam_count>=1:
                return False
        except sqlite3.Error as e:
            print("Lỗi khi lấy số lượng bài thi:", e)
            return False
        
    def delete_exam(self, exam_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Exam WHERE ExamID=?", (exam_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi xóa bài thi:", e)
            return False
        
class ExamQuestionModel:
    def __init__(self):
        self.db_name = DB_NAME

    def get_all_exam_questions(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Exam_Questions")
            exam_questions = cursor.fetchall()
            conn.close()
            return exam_questions
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách câu hỏi bài thi:", e)
            return None

    def get_exam_question_by_id(self, ExamID):
        """Lấy thông tin câu hỏi bài thi dựa vào ID của câu hỏi bài thi và trả về bản ghi chứa full thông tin của câu hỏi bài thi đó. exam_question[1] sẽ là ID của bài thi, exam_question[2] sẽ là ID của câu hỏi, exam_question[3] sẽ là thứ tự câu hỏi trong bài thi, exam_question[4] sẽ là số điểm của câu hỏi đó.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Exam_Questions WHERE ExamID=? ORDER BY QuestionOrder ASC", (ExamID,) )
            exam_question = cursor.fetchall()
            conn.close()
            # get list question id
            question_ids=[item[2] for item in exam_question]
            return question_ids
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin câu hỏi bài thi:", e)
            return None

    def get_exam_questions_by_exam_id(self, exam_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Exam_Questions WHERE ExamID=?", (exam_id,))
            exam_questions = cursor.fetchall()
            conn.close()
            return exam_questions
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách câu hỏi bài thi:", e)
            return None
        
    def add_exam_question(self, exam_id, question_id, question_order, score):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Exam_Questions (ExamID, QuestionID, QuestionOrder, Score) VALUES (?, ?, ?, ?)", (exam_id, question_id, question_order, score))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm câu hỏi bài thi:", e)
            return False
    
    def update_exam_question(self, exam_question_id, question_id, question_order, score):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE Exam_Questions SET QuestionID=?, QuestionOrder=?, Score=? WHERE ExamQuestionID=?", (question_id, question_order, score, exam_question_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật câu hỏi bài thi:", e)
            return False
        
class ExamResultModel:
    def __init__(self):
        self.db_name = DB_NAME

    def get_all_exam_results_user(self,user_id,exam_type_check=None):
        # tạo cho tôi API lấy tất cả kết quả bài thi của user ( Nếu chưa có điểm thì status sẽ là "Inprogress") gọi cả ExamModel để lấy loại bài thi
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Exam_Results WHERE UserID=?", (user_id,))
            exam_results = cursor.fetchall()
            json_data = []
            for item in exam_results:
                count_question = len(ExamQuestionModel().get_exam_question_by_id(item[2]))
                unanswered_question=count_question-item[3]-item[4]
                exam=ExamModel()
                exam_type=exam.get_exam_type(item[2])
                if item[5]==0:
                    status="Inprogress"
                else:
                    status="Completed"
                if exam_type==exam_type_check:
                    json_data.append({"exam_id": item[2], "correct_count": item[3], "incorrect_count": item[4], "score": item[5], "unanswered_count": unanswered_question,"status":status})
            conn.close()
            return json_data
        except sqlite3.Error as e:
            print("Lỗi khi lấy kết quả bài thi:", e)
            return None

    def get_exam_result_by_exam_id(self, exam_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Exam_Results WHERE ExamID=?", (exam_id,))
            exam_result = cursor.fetchone()
            if exam_result:
                exam_result = { "exam_id": exam_result[2],"correct_count": exam_result[3], "incorrect_count": exam_result[4], "score": exam_result[5], "detail": exam_result[6]}
            else:
                exam_result = {"correct_count": 0, "incorrect_count": 0, "score": 0, "detail": ""}
            conn.close()
            return exam_result
        
        except sqlite3.Error as e:
            print("Lỗi khi lấy kết quả bài thi:", e)
            return None


    def add_exam_result(self, exam_id, user_id, correct_count,incorrect_count, score,detail):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Exam_Results (ExamID, UserID, CorrectAnswers, IncorrectAnswers, Score,AnswerDetails) VALUES (?, ?, ?, ?, ?,?)", (exam_id, user_id, correct_count,incorrect_count, score,detail))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm kết quả bài thi:", e)
            return False
    
    def update_exam_result(self, exam_id, correct_count=None, incorrect_count=None, score=None, detail=None):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            update_query = "UPDATE Exam_Results SET "
            update_params = []
            if correct_count is not None:
                update_query += "CorrectAnswers = ?, "
                update_params.append(correct_count)
            if incorrect_count is not None:
                update_query += "IncorrectAnswers = ?, "
                update_params.append(incorrect_count)
            if score is not None:
                update_query += "Score = ?, "
                update_params.append(score)
            if detail is not None:
                update_query += "AnswerDetails = ?, "
                update_params.append(detail)
            # Xóa dấu phẩy cuối cùng và thêm điều kiện WHERE cho câu lệnh UPDATE
            update_query = update_query.rstrip(", ") + " WHERE ExamID = ?"
            update_params.extend([exam_id])
            cursor.execute(update_query, update_params)
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật kết quả bài thi: %s", e)
            return False
        
class DocumentsModel:
    def __init__(self):
        self.db_name = DB_NAME

    def get_all_documents(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Documents")
            documents = cursor.fetchall()
            conn.close()
            return documents
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách tài liệu:", e)
            return None

    def get_document_by_id(self, document_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Documents WHERE DocID=?", (document_id,))
            document = cursor.fetchone()
            conn.close()
            return document
        except sqlite3.Error as e:
            print("Lỗi khi lấy thông tin tài liệu:", e)
            return None

    def get_documents_by_class_id(self, class_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Documents WHERE ClassID=?", (class_id,))
            documents = cursor.fetchall()
            conn.close()
            return documents
        except sqlite3.Error as e:
            print("Lỗi khi lấy danh sách tài liệu:", e)
            return None

    def add_document(self, ClassID, Name, URL,created_at,thumbnail):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Documents (ClassID, Name, URL,created_at,thumbnail) VALUES (?, ?, ?,?,?)", (ClassID, Name, URL,created_at,thumbnail))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi thêm tài liệu:", e)
            return False
    
    def update_document(self, DocID, Name, URL,thumbnail):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE Documents SET Name=?, URL=?,thumbnail=? WHERE DocID=?", (Name, URL,thumbnail, DocID))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi cập nhật tài liệu:", e)
            return False
        
    def delete_document(self, document_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Documents WHERE DocID=?", (document_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print("Lỗi khi xóa tài liệu:", e)
            return False
        