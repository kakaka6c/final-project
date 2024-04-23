from flask import Flask, jsonify, request
import random
import json
import sqlite3
from databaseHelper import UserModel,CreateDatabase,ClassModel,ChapterMoel,TopicModel,QuestionModel,AnswerModel,ExamModel,ExamQuestionModel,ExamResultModel
import hashlib
import latex2mathjax
from datetime import datetime, timedelta
from flask_cors import CORS
from token_manage import generate_token
import utils

app = Flask(__name__)
CORS(app)


DB_CREATE = CreateDatabase()


def before_request_admin(authorization_header,compare_role="ADMIN"):
    role = token_to_role(authorization_header)
    return role!=compare_role


def token_to_role(authorization_header):
    token = None
    user_model = UserModel()
    role = None
    if authorization_header and authorization_header.startswith('Bearer '):
        # Tách chuỗi token từ header 'Authorization'
        token = authorization_header.split(' ')[1]
        try:
            role = user_model.get_role(token)[0]
        except:
            return role
    return role

@app.route("/create_database")
def create_database():
    DB_CREATE.create_tables()
    return "Database created successfully"

################################# API FOR USER ###################################

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data["name"]
    password = str(data["password"])
    email = data["email"]
    status = (data["status"] if "status" in data else "USER")
    password_hash = hashlib.md5(password.encode()).hexdigest()
    dob = data["dob"]
    user_model = UserModel()
    status, message = user_model.add_user(name, password_hash, email, dob, status)
    return jsonify({"message": message}), status
    
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    try:
        email = data["email"]
        password = str(data["password"])
        password_hash = hashlib.md5(password.encode()).hexdigest()
        user_model = UserModel()
        user = user_model.get_user_by_email(email)
        
        if user and user[2] == password_hash:
            token = generate_token()
            
            # update token of user
            user_model.update_user_token(email, token)
            role=user_model.get_role(token)
            return jsonify({"message": "Login successful", "access_token": token,"role":role[0]})
        else:
            return jsonify({"message": "Email or Password is incorrect !!!!", "access_token": "","role": ""}),401
    except Exception as e:
        print(e)
        return jsonify({"message": "Email or Password is incorrect !!!!", "access_token": "","role": ""}),401

@app.route("/api/get_user", methods=["GET"])
def get_user():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header,"USER") and before_request_admin(authorization_header,"VIP"):
        return jsonify({"message": "You are not allow to use this API"}), 401
    token = request.headers.get("Authorization")
    token = token.replace("Bearer ","")
    user_model = UserModel()
    user = user_model.get_user_by_token(token)
    if user:
        user_data={
            "Name": user[1],
            "Email": user[3],
            "DoB": user[4],
            "Status": user[6]
        }
        return jsonify({"message": "Successful", "user_info": user_data})
    else:
        return jsonify({"message": "User not found"}), 404

@app.route("/api/update_info", methods=["PUT"])
def update_info():
    # update user info include password, email, dob, username, must same old password
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header,"USER") and before_request_admin(authorization_header,"VIP"):
        return jsonify({"message": "You are not allow to use this API"}), 401
    token = request.headers.get("Authorization")
    token = token.replace("Bearer ","")
    user_model = UserModel()
    user = user_model.get_user_by_token(token)
    data = request.get_json()
    email = data["email"]
    dob = data["dob"]
    name = data["name"]
    if not user:
        return jsonify({"message": "User not found"}), 404
    try:
        old_password = data.get("old_password")
        
        new_password = data.get("new_password")
        print("xxxx"+new_password)
        if new_password and old_password:
            old_password_hash = hashlib.md5(old_password.encode()).hexdigest()
            if user[2] == old_password_hash:
                new_password_hash = hashlib.md5(new_password.encode()).hexdigest()
                status,message=user_model.update_user_info(user[0],old_password_hash, new_password_hash, email, dob, name)
                return jsonify({"message": message}), status
            else:
                return jsonify({"message": "Old password is incorrect"}), 401
    except:
        status,message=user_model.update_user_info(user[0],user[2], user[2], email, dob, name)
        
        return jsonify({"message": message}), status


################################# API FOR ADMIN #######################################

@app.route("/api/get_all_users_admin", methods=["GET"])
def get_all_users():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    user_model = UserModel()
    status=request.args.get("status")
    users = user_model.get_all_users(status=status)
    if users:
        users_data = []
        for user in users:
            user_data={
                "ID": user[0],
                "Name": user[1],
                "Email": user[3],
                "DoB": user[4],
                "Status": user[6]
            }
            users_data.append(user_data)
        return jsonify({"message": "Successful", "users": users_data})
    else:
        return jsonify({"message": "Users not found"}), 404
    
@app.route("/api/update_user_admin", methods=["PUT"])
def update_user():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    user_model = UserModel()
    data = request.get_json()
    user_id = data["user_id"]
    status = data["status"]
    user_model.update_user_status(user_id, status)
    return jsonify({"message": "Update successful"})

@app.route("/api/add_user_admin", methods=["POST"])
def add_user():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    data = request.get_json()
    name = data["name"]
    password = "123456"
    email = data["email"]
    status = data["status"]
    password_hash = hashlib.md5(password.encode()).hexdigest()
    dob = data["dob"]
    if name == "" or email == "" or dob == "":
        return jsonify({"message": "Name, Email, DoB must not be empty"}), 400
    if not utils.email_validation(email):
        return jsonify({"message": "Email is not valid"}), 400
    user_model = UserModel()
    status,message= user_model.add_user(name, password_hash, email, dob, status)
    return jsonify({"message": message}), status
    

@app.route("/api/delete_user_admin", methods=["DELETE"])
def delete_user():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    user_model = UserModel()
    user_id = request.args.get("user_id")
    user_model.delete_user(user_id)
    return jsonify({"message": "Delete successful"})



    
@app.route("/api/get_class_admin", methods=["GET"])
def get_class():
    user_model = ClassModel()
    classes = user_model.get_all_classes()
    if classes:
        return jsonify({"message": "Successful", "classes": classes})
    else:
        return jsonify({"message": "Classes not found"}), 404

@app.route("/api/add_class_admin", methods=["POST"])
def add_class():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    data = request.get_json()
    class_name = data["class_name"]
    if int(class_name) <1 or int(class_name) > 12:
        return jsonify({"message": "Class name must be from 1 to 12"}), 400
    user_model = ClassModel()
    user_model.add_class(class_name)
    return jsonify({"message": "Add class successful"})

@app.route("/api/update_class_admin", methods=["PUT"])
def update_class():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    
    user_model = ClassModel()
    data = request.get_json()

    class_id = data["class_id"]
    class_name = data["class_name"]
    if int(class_name) <1 or int(class_name) > 12:
        return jsonify({"message": "Class name must be from 1 to 12"}), 400
    user_model.update_class(class_id, class_name)
    return jsonify({"message": "Update class successful"})

@app.route("/api/delete_class_admin", methods=["DELETE"])
def delete_class():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    user_model = ClassModel()
    
    class_id = request.args.get("class_id")
    user_model.delete_class(class_id)
    return jsonify({"message": "Delete class successful"})




@app.route("/api/add_chapter_admin", methods=["POST"])
def add_chapter():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    data = request.get_json()
    chapter_name = data["chapter_name"]
    class_id = data["class_id"]
    user_model = ChapterMoel()
    user_model.add_chapter(chapter_name, class_id)
    return jsonify({"message": "Add chapter successful"})

@app.route("/api/get_chapter_admin", methods=["GET"])
def get_chapter():
    user_model = ChapterMoel()
    class_id = request.args.get("class_id")
    if not class_id:
        chapters = user_model.get_all_chapters()
    else:
        chapters = user_model.get_chapters_by_class_id(class_id)
    if chapters:
        return jsonify({"message": "Successful", "chapters": chapters})
    else:
        return jsonify({"message": "Chapters not found"}), 404

@app.route("/api/update_chapter_admin", methods=["PUT"])
def update_chapter():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    data = request.get_json()
    chapter_id = data["chapter_id"]
    chapter_name = data["chapter_name"]
    user_model = ChapterMoel()
    status,message=user_model.update_chapter(chapter_id, chapter_name)
    return jsonify({"message": message}), status

@app.route("/api/delete_chapter_admin", methods=["DELETE"])
def delete_chapter():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    user_model = ChapterMoel()
    chapter_id = request.args.get("chapter_id")
    user_model.delete_chapter(chapter_id)
    return jsonify({"message": "Delete chapter successful"})

@app.route("/api/get_topic_admin", methods=["GET"])
def get_topic():
    user_model = TopicModel()
    chapter_id = request.args.get("chapter_id")
    topics = user_model.get_topics_by_chapter_id(chapter_id)
    if topics:
        return jsonify({"message": "Successful", "topics": topics})
    else:
        return jsonify({"message": "Topics not found"}), 404

@app.route("/api/add_topic_admin", methods=["POST"])
def add_topic():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    data = request.get_json()
    topic_name = data["topic_name"]
    chapter_id = data["chapter_id"]
    user_model = TopicModel()
    user_model.add_topic(topic_name, chapter_id)
    return jsonify({"message": "Add topic successful"})

@app.route("/api/update_topic_admin", methods=["PUT"])
def update_topic():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    data = request.get_json()
    topic_id = data["topic_id"]
    topic_name = data["topic_name"]
    user_model = TopicModel()
    user_model.update_topic(topic_id, topic_name)
    return jsonify({"message": "Update topic successful"})

@app.route("/api/delete_topic_admin", methods=["DELETE"])
def delete_topic():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    user_model = TopicModel()
    topic_id = request.args.get("topic_id")
    user_model.delete_topic(topic_id)
    return jsonify({"message": "Delete topic successful"})

@app.route("/api/count_member_admin", methods=["GET"])
def count_member():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    user_model = UserModel()
    count = user_model.user_count_to_chart()
    print(count)
    return jsonify(count)

@app.route("/api/get_all_question_admin", methods=["GET"])
def get_all_question():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    user_model = QuestionModel()
    questions = user_model.get_all_questions()
    if questions:
        return jsonify({"message": "Successful", "questions": questions})
    else:
        return jsonify({"message": "Questions not found"}), 404

@app.route("/api/count_question_by_class_admin", methods=["GET"])
def count_question_by_class():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    user_model = QuestionModel()
    count = user_model.count_question_by_class()
    return jsonify(count)

@app.route("/api/count_question_by_chapter_admin", methods=["GET"])
def count_question_by_chapter():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    class_id = request.args.get("class_id")
    user_model = QuestionModel()
    count = user_model.count_question_by_chapter(class_id)
    return jsonify(count)

@app.route("/api/count_question_by_topic_admin", methods=["GET"])
def count_question_by_topic():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    chapter_id = request.args.get("chapter_id")
    user_model = QuestionModel()
    count = user_model.count_question_by_topic(chapter_id)
    return jsonify(count)

@app.route("/api/detail_question", methods=["GET"])
def detail_question():
    question_id = request.args.get("question_id")
    user_model = QuestionModel()
    question = user_model.get_question_by_id(question_id)
    if question:
        return jsonify({"message": "Successful", "question": question})
    else:
        return jsonify({"message": "Question not found"}), 404

@app.route("/api/add_question_admin", methods=["POST"])
def add_question():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    try:
        data = request.get_json()
        question_content = data["content"]
        question_content = latex2mathjax.convert_latex_to_mathjax(question_content,1)
        class_id = data["class_id"]
        chapter_id = data["chapter_id"]
        topic_id = data["topic_id"]
        question_model = QuestionModel()
        question_model.add_question(class_id, topic_id, chapter_id, question_content)
        question_id = question_model.get_id_by_content(question_content)
        answer_options = str(data["options"]).replace("'",'"')
        answer_options = latex2mathjax.convert_latex_to_mathjax(answer_options,2)
        correct_answer = data["correct"]
        correct_answer = latex2mathjax.convert_latex_to_mathjax(correct_answer,1)
        explaination = data["explaination"]
        explaination = latex2mathjax.convert_latex_to_mathjax(explaination,1)
        answer_model = AnswerModel()
        answer_model.add_answer(question_id, answer_options, correct_answer, explaination)
        
        return jsonify({"message": "Add question successful"})
    except Exception as e:
        print(e)
        return jsonify({"message": "Add question failed with error: "+str(e)}), 400

@app.route("/api/update_question_admin", methods=["PUT"])
def update_question():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    data = request.get_json()
    question_id = data["question_id"]
    question_content = data["content"]
    question_model = QuestionModel()
    question_model.update_question(question_id, question_content)
    answer_options = str(data["options"]).replace("'",'"')
    correct_answer = data["correct"]
    explaination = data["explaination"]
    answer_model = AnswerModel()
    answer_model.update_answer(question_id, answer_options, correct_answer, explaination)
    return jsonify({"message": "Update question successful"})

@app.route("/api/delete_question_admin", methods=["DELETE"])
def delete_question():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header):
        return jsonify({"message": "You are not allow to use this API"}), 401
    question_id = request.args.get("question_id")
    question_model = QuestionModel()
    question_model.delete_question(question_id)
    answer_model = AnswerModel()
    answer_model.delete_answer(question_id)
    return jsonify({"message": "Delete question successful"})

@app.route("/api/gen_question", methods=["POST"])
def gen_question():
    try:
        authorization_header = request.headers.get('Authorization')
        token = authorization_header.split(' ')[1]
        user_id = UserModel().get_user_by_token(token)[0]
    except:
        return jsonify({"message": "You are not allowed to use this API"}), 401
    
    if before_request_admin(authorization_header, "USER") and before_request_admin(authorization_header, "VIP"):
        return jsonify({"message": "You are not allowed to use this API"}), 401
    
    data = request.get_json()
    # try:
    class_id = data.get('class_ids', [])
    exam_type=data.get('exam_type',"P")
    chapter_ids = []
    if exam_type == "M":
        if len(class_id) == 0:
            return jsonify({"message": "Please select class !!!"}), 500
        chapter_ids=[]
        num_questions = 40
    else:
        num_questions = data.get("num_questions", 1)
        if len(class_id) > 0:
            chapter_ids =  data.get("chapter_ids", [])
            if chapter_ids == []:
                return jsonify({"message": "Chapter is required"}), 500
    # print(chapter_ids)
    topic_ids = data.get("topic_ids", [])
    
    
    if num_questions > 100 or num_questions < 1:
        return jsonify({"message": "Number of questions must be between 1 and 100 !!!"}), 500
    
    if class_id == [None] :
        return jsonify({"message": "Please select class !!!"}), 500
    
    question_model = QuestionModel()
    exam_id,questions_count = question_model.generate_questions(class_id, topic_ids, chapter_ids, num_questions, token, user_id,exam_type)
    # get all questions and answers
    
    return (jsonify({"message": "Generate question successful", "exam_id": exam_id, "questions_count": questions_count}), 200)
    # except Exception as e:
    #     print(e)
    #     return jsonify({"message": "Something error !!!!!"}), 500

@app.route("/api/get_exam", methods=["GET"])
def get_exam():
    exam_id = request.args.get("exam_id")
    question_model = ExamQuestionModel()
    questions = question_model.get_exam_question_by_id(exam_id)
    # print(questions)
    # Khởi tạo danh sách để lưu các cặp câu hỏi và đáp án
    question_answer_list = []
    
    # Lấy câu hỏi và đáp án của tất cả câu hỏi có question_id trong questions
    for id in questions:
        question_data = QuestionModel().get_question_by_id(id)
        question_content = question_data["content"]
        answers = [json.loads(answer["answer"] )for answer in question_data["answers"]]
        explaination = question_data["answers"][0].get("explaination", "")
        if explaination=="":
            explaination = "No explaination"
        # Tạo từ điển mới chứa nội dung câu hỏi và câu trả lời
        question_answer_dict = {
            "question": question_content,
            "answers": answers,
            "question_id": id,
            "explaination": explaination
            
        }
        
        # Thêm từ điển mới vào danh sách
        question_answer_list.append(question_answer_dict)
        
    # Trả về danh sách chứa tất cả các cặp câu hỏi và đáp án dưới dạng JSON
    return jsonify(question_answer_list)

@app.route("/api/check_answer", methods=["GET"])
def check_answer():
    # return correct answer and explaination
    question_id = request.args.get("question_id")
    question_model = AnswerModel()
    correct = question_model.check_answer(question_id)
    json_data = {
        "correct": correct
    }
    return jsonify(json_data)
    
# create route receive exam_result
@app.route("/api/submit_exam", methods=["POST"])
def submit_exam():
    # get exam_id and user_id
    data = request.get_json()
    exam_id = data["exam_id"]
    try:
        authorization_header = request.headers.get('Authorization')
        token = authorization_header.split(' ')[1]
        user_id = UserModel().get_user_by_token(token)[0]
    except:
        return jsonify({"message": "You are not allowed to use this API"}), 401
    
    if before_request_admin(authorization_header, "USER") and before_request_admin(authorization_header, "VIP"):
        return jsonify({"message": "You are not allowed to use this API"}), 401
    time_taken=data["time_elapsed"]
    user_choices=data["user_choices"]
    # count correct answer
    correct_answer=0
    incorrect_answer=0
    null_answer=0
    
    question_model=AnswerModel()
    # check answer each question
    for question in user_choices:
        correct=question_model.check_answer(question["question_id"])
        # add more value to question
        question["correct"]=correct
        if len(question["user_choice"]) == 0:
            null_answer+=1
        else:
            if question["user_choice"]==correct:
                correct_answer+=1
            else:
                incorrect_answer+=1
    
    score = 100/len(user_choices)*correct_answer
    score=round(score,2)
    if len(user_choices)==correct_answer:
        score=100
    if len(user_choices)==null_answer:
        score=0
    # data.update({"score":score,"correct_answer":correct_answer,"incorrect_answer":incorrect_answer,"null_answer":null_answer}) 
    exam_model=ExamModel()
    exam_model.update_exam(exam_id,score,time_taken)
    exam_result_model=ExamResultModel()
    user_choices_json = json.dumps(user_choices)
    exam_result_model.add_exam_result(exam_id,user_id,correct_answer,incorrect_answer,score,user_choices_json)
    print(user_choices)
    return jsonify({"message":"Submit exam successful","score":score,"correct_answer":correct_answer,"incorrect_answer":incorrect_answer,"null_answer":null_answer})

@app.route("/api/get_exam_result", methods=["GET"])
def get_exam_result():
    exam_id = request.args.get("exam_id")
    exam_result_model = ExamResultModel()
    exam_result = exam_result_model.get_exam_result_by_exam_id(exam_id)
    list_question = json.loads(exam_result["detail"])
    for question in list_question:
        question_data = QuestionModel().get_question_by_id(question["question_id"])
        question_content = question_data["content"]
        explaination = question_data["answers"][0].get("explaination", "")
        if explaination=="":
            explaination = "No explaination"
        question["question"]=question_content
        question["explaination"]=explaination
    exam_model=ExamModel()
    exam_result["time_taken"]=exam_model.get_exam_by_id(exam_id)[3]
    unanswer = len(list_question)-(exam_result["correct_count"]+exam_result["incorrect_count"])
    exam_result["unanswer_count"]=unanswer
    exam_result["detail"]=list_question
    return jsonify(exam_result)

@app.route("/api/get_exam_result_by_user", methods=["GET"])
def get_exam_result_by_user():
    authorization_header = request.headers.get('Authorization')
    if before_request_admin(authorization_header,"USER") and before_request_admin(authorization_header,"VIP"):
        return jsonify({"message": "You are not allow to use this API"}), 401
    user_id = request.args.get("user_id")
    exam_result_model = ExamResultModel()
    exam_result = exam_result_model.get_all_exam_results_user(user_id)
    exam_result = [{"exam_id": result[0], "score": result[1], "correct_answer": result[2], "incorrect_answer": result[3], "time_taken": result[4], "exam_date": result[5]} for result in exam_result]
    
    return jsonify(exam_result)

@app.route("/api/get_exam_type/<exam_id>", methods=["GET"])
def get_exam_type(exam_id):
    exam_model=ExamModel()
    exam_type=exam_model.get_exam_type(exam_id)
    return jsonify({"exam_type":exam_type})

@app.route("/api/get_count_exams", methods=["GET"])
def get_count_exams():
    try:
        authorization_header = request.headers.get('Authorization')
        token = authorization_header.split(' ')[1]
        user_id = UserModel().get_user_by_token(token)[0]
    except:
        return jsonify({"message": "You are not allowed to use this API"}), 401
    
    if before_request_admin(authorization_header, "USER") and before_request_admin(authorization_header, "VIP"):
        return jsonify({"message": "You are not allowed to use this API"}), 401
    exam_model=ExamModel()
    count=exam_model.count_exams(user_id)
    return jsonify(count)

if __name__ == "__main__":    app.run(debug=True, host="0.0.0.0", port=5000)
