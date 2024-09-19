from flask import Flask, render_template, request

app = Flask(__name__)

# Define the file path to your cleaned job posts
JOB_POSTS_FILE = "cleaned_job_posts.txt"

def read_job_posts():
    job_posts = []
    with open(JOB_POSTS_FILE, 'r', encoding="utf-8") as file:
        job_post = {}
        for line in file:
            line = line.strip()
            if line.startswith("Reference:"):
                if job_post:  # Save the previous job post if it exists
                    job_posts.append(job_post)
                    job_post = {}
                job_post['reference'] = line.split(":")[1].strip()
            elif line.startswith("Title:"):
                job_post['title'] = line.split(":")[1].strip()
            elif line.startswith("Description:"):
                job_post['description'] = line.split(":")[1].strip()
            elif line.startswith("Link:"):
                # Use partition to correctly capture the full URL after the first colon
                job_post['link'] = line.partition(":")[2].strip()
        if job_post:  # Don't forget the last job post
            job_posts.append(job_post)
    return job_posts

@app.route('/')
def index():
    # Read all job posts from the text file
    job_posts = read_job_posts()
    
    # Get the filter (number of posts per page) from the request, default is 10
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get the current page from the request, default is 1
    page = request.args.get('page', 1, type=int)
    
    # Pagination logic to slice the job posts
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(job_posts) + per_page - 1) // per_page
    
    # Filter job posts for the current page
    job_posts_paginated = job_posts[start:end]
    
    # Generate a list of page numbers (pagination links)
    pages = list(range(1, total_pages + 1))
    
    # Pass the job posts, page number, total pages, and pages list to the template
    return render_template('index.html', job_posts=job_posts_paginated, page=page, total_pages=total_pages, pages=pages, per_page=per_page)

# New route to display the job link in an iframe
@app.route('/job/<reference>')
def job_details(reference):
    # Fetch the job with the given reference
    job_posts = read_job_posts()
    job = next((job for job in job_posts if job['reference'] == reference), None)
    
    if job:
        job_link = job['link']
        return render_template('job_details.html', job=job, job_link=job_link)
    else:
        return "Job not found", 404

if __name__ == "__main__":
    app.run(debug=True)
