from concurrent import futures
import uuid
import grpc
from pymongo import MongoClient
import posts_pb2
import posts_pb2_grpc

class PostService(posts_pb2_grpc.PostServiceServicer):
    def __init__(self, db):
        self.db = db

    def CreatePost(self, request, context):
        max_post = self.db.posts.find_one(sort=[("_id", -1)])
        post_id = 1
        if max_post:
            post_id = int(max_post['_id']) + 1

        post = {
            "_id": post_id,
            "user_id": request.user_id,
            "title": request.title,
            "content": request.content,
        }
        self.db.posts.insert_one(post)
        return posts_pb2.CreatePostResponse(post=posts_pb2.Post(id=post_id, user_id=request.user_id, title=request.title, content=request.content))

    def UpdatePost(self, request, context):
        post = self.db.posts.find_one({"_id": request.id})
        if not post:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
        if post["user_id"] != request.user_id:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission denied")
        self.db.posts.update_one({"_id": request.id}, {"$set": {"title": request.title, "content": request.content}})
        post["title"] = request.title
        post["content"] = request.content
        return posts_pb2.UpdatePostResponse(post=posts_pb2.Post(id=request.id, user_id=request.user_id, title=request.title, content=request.content))

    def DeletePost(self, request, context):
        post = self.db.posts.find_one({"_id": request.id})
        if not post:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
        if post["user_id"] != request.user_id:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission denied")
        self.db.posts.delete_one({"_id": request.id})
        return posts_pb2.DeletePostResponse(success=True)

    def GetPost(self, request, context):
        post = self.db.posts.find_one({"_id": request.id})
        if not post:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
        return posts_pb2.GetPostResponse(post=posts_pb2.Post(id=post["_id"], user_id=post["user_id"], title=post["title"], content=post["content"]))

    def ListPosts(self, request, context):
        posts = self.db.posts.find({"user_id": request.user_id})
        response = posts_pb2.ListPostsResponse()
        for post in posts:
            response.posts.add(id=post["_id"], user_id=post["user_id"], title=post["title"], content=post["content"])
        return response

def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    db_client = MongoClient('mongodb://mongo:27017/')
    db = db_client['post_db']

    posts_pb2_grpc.add_PostServiceServicer_to_server(PostService(db), server)
    server.add_insecure_port('post_service:50051')
    server.start()
    server.wait_for_termination(timeout=None)

if __name__ == '__main__':
    main()  
