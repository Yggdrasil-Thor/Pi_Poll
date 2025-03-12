from flask import request, jsonify
from models.Comments import Comment
from models.User import User  # Import User model
from models.Poll import Poll  # Import Poll model
from utils.redis_session import get_session 
from utils.db import db_instance
from services.sentiment_analysis import analyze_sentiment  # Assuming sentiment analysis service exists
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import asyncio
import concurrent.futures
import threading
import logging
from controllers.interactionController import InteractionController

logger = logging.getLogger(__name__)


class CommentController:
    def __init__(self):
        self.comment_model = Comment()
        self.user_model = User()
        self.poll_model = Poll()
        self.db_client = db_instance.client  # Get the client for transactions
    
    def get_user_id_from_session(self):
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

    def handle_create_comment(self, request):
        logger.info(f"🌍 Flask main thread ID: {threading.get_ident()}")  # ✅ Log Flask thread

        user_id, error = self.get_user_id_from_session()
        if error:
            return jsonify({"success": False, "message": error}), 401
        
        poll_id = request.json.get("pollId")
        text = request.json.get("text")
        parentId = request.json.get("parentId", None)
        
        if not poll_id or not text:
            return jsonify({"success": False, "message": "Missing required parameters: pollId, text"}), 400
        
        session = self.db_client.start_session()  # Start a new session
        try:
            with session.start_transaction():
                comment_result = self.comment_model.create_comment(str(user_id), poll_id, text, parentId, session)
                comment_id = str(comment_result.inserted_id)
                #comment_id = '67c7db2f9b4856288f0f7535'
                self.poll_model.add_comment_to_poll(poll_id, comment_id, session)
                self.poll_model.update_poll_engagement(poll_id, "comment", session)
                self.user_model.add_comment_to_user(str(user_id), comment_id, session)
                # Log the interaction using InteractionController
                interaction_controller = InteractionController()  
                interaction_response = interaction_controller.handle_log_interaction(request, "comment")  
                if not interaction_response[0].json["success"]:  
                    session.abort_transaction()  
                    return jsonify({"success": False, "message": "Failed to log the interaction. Transaction aborted."}), 500  

            executor = concurrent.futures.ThreadPoolExecutor()
            executor.submit(asyncio.run, self.update_sentiment_async(comment_id, text))

            return jsonify({"success": True, "message": "Comment created successfully", "data": comment_id}), 201
        except PyMongoError as e:
            session.abort_transaction()
            return jsonify({"success": False, "message": f"Failed to create comment: {str(e)}"}), 500
        finally:
            session.end_session()

    def handle_get_comment_by_id(self, request,comment_id):
        #comment_id = request.json.get("commentId")
        if not comment_id:
            return jsonify({"success": False, "message": "Missing required parameter: commentId"}), 400
        
        try:
            comment = self.comment_model.get_comment_by_id(comment_id)
            if comment:
                return jsonify({"success": True, "data": comment}), 200
            else:
                return jsonify({"success": False, "message": "Comment not found"}), 404
        except Exception as e:
            return jsonify({"success": False, "message": f"Failed to fetch comment: {str(e)}"}), 500

    def handle_get_comments_by_poll(self, request,poll_id):
        #poll_id = request.args.get("pollId")
        if not poll_id:
            return jsonify({"success": False, "message": "Missing required parameter: pollId"}), 400
        
        try:
            comments = self.comment_model.get_comments_by_poll(poll_id)
            return jsonify({"success": True, "data": comments}), 200
        except Exception as e:
            return jsonify({"success": False, "message": f"Failed to fetch comments: {str(e)}"}), 500

    def handle_get_replies(self, request,parent_id):
        #parentId = request.json.get("parentId", None)
        parentId =parent_id
        if not parentId:
            return jsonify({"success": False, "message": f"No Child Comments"}), 200
        else:
            try:
                replies = self.comment_model.get_replies(parentId)
                return jsonify({"success": True, "data": replies}), 200
            except Exception as e:
                return jsonify({"success": False, "message": f"Failed to fetch comments: {str(e)}"}), 500


    MAX_RETRIES = 3

    async def update_sentiment_async(self, comment_id, text):
        """Runs sentiment analysis with retries and updates the database asynchronously."""
        logger.info(f"🔄 Async Task Running in thread ID: {threading.get_ident()}")  # ✅ Log async thread
        try:
            # Ensure comment_model is available
            if not hasattr(self, "comment_model") or self.comment_model is None:
                logger.info("❌ Error: comment_model not found.")
                return
            
            # Mark comment as "processing"
            await asyncio.to_thread(self.comment_model.update_comment_sentiment, comment_id, None, "processing")
            # ✅ Manually add a delay to simulate long processing
            #await asyncio.sleep(10)  # 🔥 Sleep for 10 seconds so you can check the database
            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    sentiment_score, sentiment_label = await analyze_sentiment(text)
                    # Ensure sentiment_score is a native Python float
                    sentiment_score = float(sentiment_score)
                    # Update database with sentiment result
                    await asyncio.to_thread(self.comment_model.update_comment_sentiment, comment_id, sentiment_score, sentiment_label)
                    logger.info(f"✅ Sentiment updated in thread {threading.get_ident()}")

                    return  # Success, exit function

                except Exception as e:
                    logger.info(f"⚠️ Attempt {attempt}: Sentiment Analysis Failed for {comment_id} - {e}")
                    await asyncio.sleep(2)  # Wait before retrying
            
            # If all retries fail, mark sentiment as "error"
            await asyncio.to_thread(self.comment_model.update_comment_sentiment, comment_id, None, "error")

        except Exception as e:
            logger.info(f"❌ Fatal error in update_sentiment_async: {e}")


    def handle_update_comment_sentiment(self, request, comment_id):
        """Handles comment sentiment asynchronously via background task."""
        if not comment_id:
            return jsonify({"success": False, "message": "Missing required parameter: commentId"}), 400

        try:
            if not hasattr(self, "comment_model") or self.comment_model is None:
                return jsonify({"success": False, "message": "Internal error: comment_model not found"}), 500

            comment = self.comment_model.get_comment_by_id(comment_id)  # Sync call
            if not comment:
                return jsonify({"success": False, "message": "Comment not found"}), 404

            # 🚀 Run async function in background properly
            loop = asyncio.get_running_loop()
            loop.create_task(self.update_sentiment_async(comment_id, comment["text"]))

            return jsonify({"success": True, "message": "Comment received, sentiment update in progress"}), 200

        except RuntimeError:  # If no running event loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.update_sentiment_async(comment_id, comment["text"]))
            return jsonify({"success": True, "message": "Comment received, sentiment updated"}), 200

        except Exception as e:
            return jsonify({"success": False, "message": f"Failed to start sentiment update: {str(e)}"}), 500


    def handle_delete_comment(self, request,comment_id):
        user_id, error = self.get_user_id_from_session()
        if error:
            return jsonify({"success": False, "message": error}), 401
        
        #comment_id = request.json.get("commentId")
        if not comment_id:
            return jsonify({"success": False, "message": "Missing required parameter: commentId"}), 400
        
        try:
            deleted_count = self.comment_model.delete_comment(comment_id)
            if deleted_count > 0:
                return jsonify({"success": True, "message": "Comment deleted successfully"}), 200
            else:
                return jsonify({"success": False, "message": "Comment not found"}), 404
        except Exception as e:
            return jsonify({"success": False, "message": f"Failed to delete comment: {str(e)}"}), 500
