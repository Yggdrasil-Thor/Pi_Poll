from pymongo.errors import PyMongoError,WriteConcernError
from models.Poll import Poll
from models.Payment import Payment
from models.User import User
from utils.db import db_instance
from flask import jsonify,request
from datetime import datetime, timezone
from bson import ObjectId
from utils.redis_session import get_session
from controllers.interactionController import InteractionController
import time

# Initialize Poll, User and Payment models
poll_model = Poll()
payment_model = Payment()
user_model = User()

class PollController:
    def __init__(self):
        self.poll_model = poll_model
        self.payment_model = payment_model
        self.user_model = user_model
        self.db_client = db_instance.client  # Get the client for transactions

    def get_user_id_from_session(self):
        """Helper function to retrieve user_id from session."""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return None, "Unauthorized"
        
        session_data = get_session(session_id)
        if not session_data:
            return None, "Session expired or invalid"
        
        user_id = session_data.get("user_id")
        if not user_id:
            return None, "Invalid session"
        
        return user_id, None


    def handle_create_poll(self, request):
        data = request.json
        user_id, error = self.get_user_id_from_session()

        # Ensure user_id is a valid ObjectId
        """try:
            user_id = ObjectId(user_id)  # Convert user_id to ObjectId
        except Exception:
            return jsonify({"success": False, "message": "Invalid user_id format", "data": None}), 400"""

        session = self.db_client.start_session()  # Start a new session

        try:
            with session.start_transaction():  # Begin transaction
                poll_id = self.poll_model.create_poll(
                    title=data["title"],
                    description=data["description"],
                    options=data["options"],
                    created_by=user_id,
                    topics=data["topics"],
                    visibility=data.get("visibility", "public"),
                    expires_at=data.get("expiresAt"),
                    required_votes=data.get("requiredVotes", 0),
                    requires_payment_for_creation=data.get("requiresPaymentForCreation", False),
                    payment_amount_for_creation=data.get("paymentAmountForCreation", 0),
                    session=session  # Pass session
                )

                if data.get("requiresPaymentForCreation", False):
                    self.payment_model.create_payment(
                        user_id=str(user_id),  # Ensure it's a string
                        poll_id=poll_id,
                        amount=data["paymentAmountForCreation"],
                        payment_type="creation",
                        transaction_id=data.get("paymentId"),
                        status="completed",
                        session=session  # Pass session
                    )

                    # Validate and Convert payment_id
                    payment_id = data.get("paymentId")
                    try:
                        payment_id = ObjectId(payment_id)  # Convert payment_id to ObjectId
                    except Exception:
                        return jsonify({"success": False, "message": "Invalid payment_id format", "data": None}), 400

                    self.user_model.add_payment_to_user(user_id, payment_id)

                self.user_model.add_poll_to_user(user_id, poll_id)

                session.commit_transaction()  # Commit the transaction
                return jsonify({"success": True, "data": {"pollId": str(poll_id)}}), 201

        except Exception as e:
            if session.in_transaction:  # ✅ Only abort if transaction is still active
                session.abort_transaction()
            return jsonify({"success": False, "message": f"Failed to create poll: {str(e)}", "data": None}), 500

        finally:
            session.end_session()  # Always end the session


    def handle_update_poll(self, request, poll_id):
        data = request.json
        user_id,error=self.get_user_id_from_session()
        try:
            session = self.db_client.start_session()  # Start a new session
            # Convert poll_id if necessary
            #print(f"poll_id type in controller 1: {type(poll_id)} | value: {poll_id}")
            if not isinstance(poll_id, ObjectId):
                poll_id = ObjectId(poll_id)
            #print(f"poll_id type in controller 2: {type(poll_id)} | value: {poll_id}")
            poll = self.poll_model.get_poll(poll_id)
            #print("updated by ",user_id)
            if not poll or poll['createdBy'] != user_id:
                return jsonify({"success": False, "message": "Unauthorized: You can only update your own poll."}), 403

            with session.start_transaction():
                result = self.poll_model.update_poll(
                    poll_id=poll_id,
                    updates=data,
                    session=session
                )

                if result.modified_count > 0 and data.get("requiresPaymentForUpdate", False):
                    self.payment_model.create_payment(
                        user_id=data["updatedBy"],
                        poll_id=poll_id,
                        amount=data["paymentAmountForUpdate"],
                        payment_type="update",
                        transaction_id=data.get("paymentId"),
                        status="completed",
                        session=session
                    )
                session.commit_transaction()
                return jsonify({"success": True, "message": "Poll updated successfully"}), 200
        except PyMongoError as e:
            if session.in_transaction:  # ✅ Only abort if transaction is still active
                session.abort_transaction()
            return jsonify({"success": False, "message": "Failed to update poll. Please try again."}), 500

    #Gives Write concurrency error
    """   def handle_add_vote(self, request, poll_id):
            data = request.json
            user_id,error=self.get_user_id_from_session()
            option_id = data["optionId"]
            try:
                poll = self.poll_model.get_poll(poll_id)
                if not poll:
                    return jsonify({"success": False, "message": "Poll not found."}), 404
                
                # Check if the poll is active before adding a vote
                if not poll.get("isActive", False):  
                    return jsonify({"success": False, "message": "Voting is closed for this poll."}), 400

                if self.user_model.has_user_voted(poll_id, user_id):
                    return jsonify({"success": False, "message": "You have already voted on this poll."}), 400
                session = self.db_client.start_session()
                with session.start_transaction():
                    self.poll_model.add_vote(poll_id, option_id, user_id,session)
                    self.poll_model.update_poll_engagement(poll_id, "vote", session)
                    self.user_model.add_vote_to_user( user_id, poll_id, option_id,session)
                    # Log the interaction using InteractionController
                    interaction_controller = InteractionController()  
                    interaction_response = interaction_controller.handle_log_interaction(request, "vote")  
                    if not interaction_response[0].json["success"]:  
                        session.abort_transaction()  
                        return jsonify({"success": False, "message": "Failed to log the interaction. Transaction aborted."}), 500  

                    #print("Model add vote done")
                    requires_payment, amount = self.payment_model.check_if_payment_required(poll_id, "voting")
                    #print("chekc if payment required done")
                    if requires_payment:
                        self.payment_model.create_payment(
                            user_id=user_id,
                            poll_id=poll_id,
                            amount=amount,
                            payment_type="voting",
                            transaction_id=data.get("paymentId"),
                            status="completed"
                        )
                    session.commit_transaction()
                    #print("transaction coomit done")
                    return jsonify({"success": True, "message": "Vote added successfully"}), 200
            except PyMongoError as e:
                if session.in_transaction:  # ✅ Only abort if transaction is still active
                    session.abort_transaction()
                return jsonify({"success": False, "message": "Failed to add vote. Please try again."}), 500
    """

    def handle_add_vote(self, request, poll_id):
        data = request.json
        user_id, error = self.get_user_id_from_session()
        option_id = data["optionId"]

        try:
            poll = self.poll_model.get_poll(poll_id)
            if not poll:
                return jsonify({"success": False, "message": "Poll not found."}), 404

            if not poll.get("isActive", False):  
                return jsonify({"success": False, "message": "Voting is closed for this poll."}), 400

            if self.user_model.has_user_voted(poll_id, user_id):
                return jsonify({"success": False, "message": "You have already voted on this poll."}), 400

            MAX_RETRIES = 3  # Retry count for both voting & engagement update
            for attempt in range(MAX_RETRIES):
                try:
                    with self.db_client.start_session() as session:
                        with session.start_transaction():
                            self.poll_model.add_vote(poll_id, option_id, user_id, session)
                            self.user_model.add_vote_to_user(user_id, poll_id, option_id, session)

                            # Log interaction
                            interaction_controller = InteractionController()  
                            interaction_response = interaction_controller.handle_log_interaction(request, "vote")  
                            if not interaction_response[0].json["success"]:  
                                session.abort_transaction()  
                                return jsonify({"success": False, "message": "Failed to log the interaction. Transaction aborted."}), 500  

                        session.commit_transaction()
                        print(f"✅ Vote added successfully (Attempt {attempt + 1})")

                        # ✅ Emit WebSocket event for live updates
                        self.emit_vote_update(poll_id, option_id)


                    # ✅ Engagement Update (Retries if needed)
                    for engagement_attempt in range(MAX_RETRIES):
                        try:
                            self.poll_model.update_poll_engagement(poll_id, "vote")
                            break  # Success, exit loop
                        except WriteConcernError:
                            print(f"⚠️ Engagement Write Conflict (Attempt {engagement_attempt + 1}) - Retrying...")
                            time.sleep(0.1)  # Small delay before retry
                    else:
                        print("❌ Max retries reached for engagement update. Poll engagement may be inconsistent.")

                    # ✅ Payment Handling
                    requires_payment, amount = self.payment_model.check_if_payment_required(poll_id, "voting")
                    if requires_payment:
                        self.payment_model.create_payment(
                            user_id=user_id,
                            poll_id=poll_id,
                            amount=amount,
                            payment_type="voting",
                            transaction_id=data.get("paymentId"),
                            status="completed"
                        )

                    return jsonify({"success": True, "message": "Vote added successfully"}), 200

                except WriteConcernError:
                    print(f"⚠️ Write Conflict (Attempt {attempt + 1}) - Retrying...")
                    time.sleep(0.1)  # Small delay before retry

                except PyMongoError as e:
                    print(f"❌ Database Error: {e}")
                    return jsonify({"success": False, "message": "Failed to add vote. Please try again."}), 500

        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return jsonify({"success": False, "message": "An error occurred. Please try again later."}), 500

        return jsonify({"success": False, "message": "Failed after multiple attempts. Try again later."}), 500
    
    def emit_vote_update(self, poll_id, option_id):
        from app import socketio
        print(f"📢 Emitting vote_update: poll_id={poll_id}, vote={option_id}")
        
        try:
            socketio.emit("vote_update", {"poll_id": poll_id, "vote": option_id})
            socketio.sleep(0)  # 🔥 Forces instant emission
            print("✅ Emission successful!")
        except Exception as e:
            print(f"❌ Emission failed: {e}")



    def handle_get_poll(self, request, poll_id):
        try:
            poll = self.poll_model.get_poll(poll_id)
            poll["_id"] = str(poll["_id"])  # ✅ Convert ObjectId to string
            return jsonify({"success": True, "data": str(poll)}), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    def handle_get_user_polls(self, request, user_id):
        try:
            user_id,error=self.get_user_id_from_session()
            polls = self.poll_model.get_user_polls(user_id)
            polls["_id"] = str(polls["_id"])  # ✅ Convert ObjectId to string
            return jsonify({"success": True, "data": polls}), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    def handle_delete_poll(self, request, poll_id):
        #data = request.json
        user_id,error=self.get_user_id_from_session()
        try:
            poll = self.poll_model.get_poll(poll_id)
            if not poll or poll['createdBy'] != user_id:
                return jsonify({"success": False, "message": "Unauthorized: You can only delete your own poll."}), 403
            self.poll_model.delete_poll(poll_id, user_id)
            return jsonify({"success": True, "message": "Poll deleted successfully"}), 200
        except PyMongoError as e:
            return jsonify({"success": False, "message": "Failed to delete poll. Please try again."}), 500

    def handle_get_active_polls(self, request):
        try:
            active_polls = self.poll_model.get_active_polls()
            return jsonify({"success": True, "data": active_polls}), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    def handle_get_polls_by_topic(self, request, topic):
        try:
            polls = self.poll_model.get_polls_by_topic(topic)
            return jsonify({"success": True, "data": polls}), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        
    def handle_extend_poll_votes(self, request, poll_id):
        """Handles increasing the allowed votes for a poll and reactivates if conditions are met."""
        data = request.json
        user_id, error = self.get_user_id_from_session()

        if error or not user_id:
            return jsonify({"success": False, "message": "Authentication required."}), 401

        additional_votes = data.get("additionalVotes", 0)
        requires_payment = data.get("requires_payment_for_update", False)
        payment_amount = data.get("payment_amount_for_update", 0)

        if additional_votes < 0:
            return jsonify({"success": False, "message": "You cannot decrease the allowed votes"}), 400
        try:
            poll = self.poll_model.get_poll(poll_id)
            #print(f"🔹 Retrieved Poll: {poll}")

            if not poll:
                return jsonify({"success": False, "message": "Poll not found."}), 404

            if str(poll["createdBy"]) != str(user_id):
                return jsonify({"success": False, "message": "Unauthorized: You can only update your own poll."}), 403

            current_votes = poll.get("currentVotes", 0)  # Assuming we store votes in 'currentVotes'
            required_votes = poll.get("requiredVotes", 0)

            session = self.db_client.start_session()
            with session.start_transaction():
                # Extend votes in the database
                new_vote_count = current_votes + additional_votes
                update_data = {"currentVotes": new_vote_count}

                # If new votes exceed requiredVotes, activate the poll
                if new_vote_count >= required_votes:
                    update_data["isActive"] = True  # Reactivating the poll

                self.poll_model.update_poll(poll_id, update_data)

                # Handle payment if required
                if requires_payment:
                    self.payment_model.create_payment(
                        user_id=user_id,
                        poll_id=poll_id,
                        amount=payment_amount,
                        payment_type="vote_extension",
                        transaction_id=data.get("paymentId"),
                        status="completed"
                    )

                session.commit_transaction()
                #print("🔹 Transaction committed successfully")

            return jsonify({"success": True, "message": "Poll vote limit updated successfully."}), 200

        except PyMongoError as e:
            if session.in_transaction:
                session.abort_transaction()
            #print(f"🔴 PyMongoError in handle_extend_poll_votes: {e}")
            return jsonify({"success": False, "message": "Failed to extend poll votes. Please try again."}), 500
