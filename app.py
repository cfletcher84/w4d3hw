from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
# Local import for db connection
from connect_db import connect_db, Error

app = Flask(__name__)
app.json.sort_keys = False #maintain order of your stuff

ma = Marshmallow(app)

# define the customer schema
# makes sure the customer data adheres to a specific format
class WorkoutSchema(ma.Schema):
    sesh_id = fields.Int(dump_only=True)
    date = fields.String(required=True)
    member_id = fields.Int(required=True)
    workout_type = fields.String(required=True)

    class Meta:
        fields = 'sesh_id', 'date', 'member_id', 'workout_type'

workout_schema = WorkoutSchema()
workout_schemas = WorkoutSchema(many=True)


class MemberSchema(ma.Schema):
    member_id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    membership_type = fields.String(required=True)


    class Meta:  
        
        fields = ("member_id", "name", "email", "phone", "membership_type")
# instantiating CustomerSchema class
# based on how many customers we're dealing with
customer_schema = MemberSchema()
customers_schema = MemberSchema(many=True)

@app.route('/')
def home():
    return "Welcome to our super cool Fitness Tracker, time to get swole brah!"

@app.route('/members', methods=['GET'])
def get_members(): 
    print("hello from the get")  
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True) #dictionary=TRUE only for GET
        # SQL query to fetch all customers
        query = "SELECT * FROM Members"

        # executing query with cursor
        cursor.execute(query)

        # accessing stored query
        members = cursor.fetchall()

         # use Marshmallow to format the json response
        return customers_schema.jsonify(members)
    
    except Error as e:
        # error handling for connection/route issues
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/members', methods = ['POST']) 
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        new_customer = (customer_data['name'], customer_data['email'], customer_data['phone'], customer_data['membership_type'])

        query = "INSERT INTO Members (name, email, phone, membership_type) VALUES (%s, %s, %s, %s)"

        cursor.execute(query, new_customer)
        conn.commit()

        return jsonify({"message":"New member added succesfully"}), 201
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 

@app.route('/members/<int:member_id>', methods= ["PUT"])
def update_customer(member_id):
    try:
        customer_data = customer_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_customer = (customer_data['name'], customer_data['email'], customer_data['phone'], customer_data['membership_type'], member_id)

        query = "UPDATE Members SET name = %s, email = %s, phone = %s, membership_type = %s WHERE member_id = %s"

        cursor.execute(query, updated_customer)
        conn.commit()

        return jsonify({"message":"Customer details were succesfully updated!"}), 200
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    

@app.route('/members/<int:member_id>', methods=["DELETE"])
def delete_customer(member_id):
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        customer_to_remove = (member_id,)


        query = "SELECT * FROM Members WHERE member_id = %s"
        cursor.execute(query, customer_to_remove)
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"error": "User does not exist"}), 404

        del_query = "DELETE FROM dank_sesh WHERE member_id = %s"
        del_query2 = "DELETE FROM Members WHERE member_id = %s"
        cursor.execute(del_query, customer_to_remove)
        cursor.execute(del_query2, customer_to_remove)
        conn.commit()

        return jsonify({"message":"Member Removed succesfully"}), 200



    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/dank_sesh', methods=['GET'])
def get_sessions(): 
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True) #dictionary=TRUE only for GET
        # SQL query to fetch all customers
        query = "SELECT * FROM dank_sesh"

        # executing query with cursor
        cursor.execute(query)

        # accessing stored query
        members = cursor.fetchall()

         # use Marshmallow to format the json response
        return workout_schemas.jsonify(members)
    
    except Error as e:
        # error handling for connection/route issues
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        #checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/dank_sesh', methods = ['POST']) 
def add_workout():
    try:
        workout_data = workout_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        new_workout = (workout_data['date'], workout_data['member_id'], workout_data['workout_type'])
                                     
        query = "INSERT INTO dank_sesh (date, member_id, workout_type) VALUES (%s, %s, %s)"

        cursor.execute(query, new_workout)
        conn.commit()

        return jsonify({"message":"New workout added succesfully"}), 201
    
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 



@app.route('/workouts/<int:id>', methods= ["PUT"])
def update_workout(id):
    print("hello")
    try:
        workout_data = workout_schema.load(request.json)
        print(workout_data)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_workout = (workout_data['date'], workout_data['member_id'], workout_data['workout_type'], id)

        query = "UPDATE Dank_sesh SET date = %s, member_id = %s, workout_type = %s WHERE sesh_id = %s"

        cursor.execute(query, updated_workout)
        conn.commit()

        return jsonify({"message":"Workout details were succesfully updated!"}), 200

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app.run(debug=True, port = 5001)
