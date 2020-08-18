
Brian Ouzomgi
bao5148@psu.edu
CMPSC431W
Section 1

FOR PROGRESS REVIEW

Included in my submission is a Python script that parses and creates my SQLite tables, a Flask script responsible for my website, and 2 HTML documents that make up my starting homepage and personal profile respectively.

My Python script responsible for populating the database, dbgen.py, uses Pandas to read the three Excel spreadsheets and the command to_sql to convert them to SQL tables. I manually created createTable commands for the actual schema, and developed insert commands that will take the Excel values and dump the relevant ones into the correct schema categories. 

foreignBust.py is my Flask script. I use homepage.html as my starting page the user sees when they reach the site. I used mobile sign-in pages as inspiration and I tried to make it look nice. If the user inputs a valid username and password (which is blocked out per the requirements request -I used Bootstrap for that), they are led to the profile.html page, which simply greets them by name. I pass all user information to the profile.html page other than the password. Otherwise, the site shows a message stating the username and password were incorrect.

FOR FINAL SUBMISSION

Main file: start.py

I spent a LOT of time on this project. A LOT. Like I didn't sleep until 3AM for many days of the week that I did the majority of this project. I started building pretty much all of the website right after the progress review was due and I really wanted to build something I was proud of. I had 0 web development experience before this class (HTML, Flask, JS, none of it), and so the whole process took a lot of Googling. However, I learned a ton and love how this website looks, runs, and is organized. Let's review it...

TOOLS

I used Python, Flask, Bootstrap, and SQLite. 

ORGANIZATION

When constructing large-scale software endeavors, organization is key. I quickly learned about HTML template inheritance, and I decided to make the most of it. A couple of my pages work similarly between Professors and TA's/Students, so I had to make decisions if I would just use if statements and separate functionality that way (like in Forums) or completely just separate out the HTML pages (like in User Profile). My base page (the gradient background) is the parent of every page I wrote for the project. 

I decided to go with a tabs-based design, so between that and taking full advantage of inheritance to reduce redundancy, I ended up with 9 HTML templates.

INFORMATION PASSING

Because I went with a tabbed design, I had to pass information between each page to simulate a "logged-in" design. After some Googling, I realized I could store information in the URL to pass content from one page to another, so I stowed away the current users email up there. I thought this was a really cool trick. 

LOGIN

Pretty standard. I included Bootstrap's password validating forms to block out user input and force email input.

USER INFO

All types of users can access this. Professors will have a different view, as they have different information stored as user info. Each person is assigned an random avatar in accordance with their gender as a sort of profile picture. This was tricky to implement, as base HTML pages are easy to insert images into, but on Flask you have to create a special STATIC folder and use a funky command to get things working. This page also allows you to change your password. Clicking the button will trigger a model asking for a current, future, and confirmed future password. 

Here I used Bootstrap form validation, but went one step forward by actually editing the JS that they used to force only letters and numbers as well as requiring the future passwords to match. This is done prior to submission, and took me forever due to the Bootstrap JS code being so unnecessarily complicated. This was my first time writing JS, and I hate it already. A confirmation on this change password modal will trigger a status message and change your password, or not, depending on if your current password was inputted correctly .

STUDENTS/TA's ONLY
ENROLLED CLASSES

Again, presentation was extremely important to me. I took all relevant information about each class the student is enrolled in and tried to rearrange it on screen to be easily understandable. Getting the information into something easy to iterate over in Jinja was tricky, but I managed to do it. I reduced redundant labels to clean everything up. 

If you scroll over the course names, you'll see a pop-up of that course's professor's name, email, and office address. 

Below this is an dropdown for course dropping. It won't let you drop any course after its late drop deadline. 

If you are a TA, below this section is an area for you to see the classes you are TA'ing. It shows all relevant information about that courses' respective Professor that TA is working under.

PROFESSORS ONLY 
MANAGE ASSIGNMENTS

Here is a hub for the Professor of any class to view assignments they have created. Again,  I tried to organize the layout extremely thoughtfully, with an attractive table design.

Below this are sections for creating and deleting assignments. The assignment creation has a text box for the assignment details, and both have dropdown menus for the Professor to select which course, section, and type of assignment he or she is manipulating. Everything (to the best of my ability) is validity checked, and if someone tries to delete an assignment that doesn't exist, it will respond with a message. There is also validation requiring all fields to be filled in before submission.

SUBMIT SCORES

This is my favorite page of the site. The page immediately tells the Professor if he or she has any ungraded assignments. If so, it shows the specific assignments that are ungraded and how many students need to be assessed. Below this is are multiple dropdown menus, which, in tandem allow the Professor to pull up grades. There is a special "subset" option that permits the Professor to choose between only ungraded or all the students of a particular section/ assignment. 

Once a selection has been made, the students' emails and grades show up line by line. Each of the grades are actually text boxes filled in with their current grades, and the Professor can overwrite any grade of their choosing. Like everything on the site, these are validated. Once the user hits submit for the grade changes, if there is any invalid grade submission (>0, <100, an incorrect datatype), there will be a message next to that name that says that that grade was not submitted due to an error. However, every other valid grade will be updated. It works really nicely.

I also wrote some statistics about the current subset of grades in the query, but I couldn't find a good place to put them so I just omitted them. They remain in the backend though. 

ALL USERS 
COURSE FORUMS

Here is my forum page. Students will see all of their enrolled classes as topics with any number of posts and subsequent comments under them. If there is no comments or no posts associated with a post or course, there will be a message saying so. Below the last comment for any post is a comment box for anyone to insert a comment. Similarly, there is a post box with a dropdown to choose courses to generate a post.

Professors will have a similar view, but for courses they teach. They can add comments and posts, as well as delete any post or comment they want. Don't worry: a deleted post will respectively delete its children comments. 

A TA will have both an Enrolled Course Forums, and below this a Teaching Forums. They can only delete posts and comments from the Teaching Forums.

OTHER FILES

Again, to keep proper organization I used two additional Python files: one for my SQL commands called SQLtool.py and one for random auxiliary functions called aux.py. They are both imported into my main start.py Flask file.
 
WRAP-UP

I didn't include any specific EC options, but hopefully you see the extra effort I put into perfecting the required functionality (especially that Submit Scores page). 





