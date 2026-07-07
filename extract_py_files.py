from github import Github, Auth
import os
import dotenv

dotenv.load_dotenv()

token = os.getenv('GITHUB_TOKEN')
auth = Auth.Token(token)
g = Github(auth=auth)
repo = g.get_repo("TheAlgorithms/Python")

print(repo.full_name)


for pr in repo.get_pulls(state="closed"):
    for comment in pr.get_review_comments():
        
        if(comment.path.endswith(".py") and comment.line is not None):
            content = repo.get_contents(comment.path, ref=comment.commit_id)
            file_content = content.decoded_content.decode("utf-8")
            lines = file_content.splitlines()
            line_no = comment.line
            start_index = line_no - 5 if line_no-5 > 0 else 0
            end_index = line_no + 5 if line_no + 5 < len(lines) else len(lines)-1

            print("comment path: ", comment.path)
            print("comment line: ", comment.line)
            print("comment body: ", comment.body)      
            print("snippet: ")      
            for i in range(start_index, end_index):
                print(lines[i])
            
            print("-------------------------------------------------------------------------")
